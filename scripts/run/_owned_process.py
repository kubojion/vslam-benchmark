#!/usr/bin/env python3
"""Run and stop only processes belonging to one saved attempt stage.

A random inherited environment token follows descendants, including ROS nodes
that create their own process groups. Signals use Linux pidfds, with an identity
recheck after opening the descriptor. No process-name kill or PID-only fallback.
The same standalone standard-library code can be sent to an existing container;
it never starts a container or installs anything. Python >=3.8 is supported.
"""
from __future__ import annotations

import argparse
import ctypes
import errno
import fcntl
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time
import uuid

TOKEN_KEY='VSLAM_ATTEMPT_PROCESS_TOKEN'


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+path.name,dir=str(path.parent))
    try:
        with os.fdopen(fd,'w') as stream:
            json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)


def proc_record(pid,token=None):
    try:
        root=Path('/proc')/str(pid)
        stat=(root/'stat').read_text().rsplit(')',1)[1].split()
        if stat[0]=='Z':return None
        if token is not None:
            environ=(root/'environ').read_bytes().split(b'\0')
            if (TOKEN_KEY+'='+token).encode() not in environ:return None
        command=(root/'cmdline').read_bytes().split(b'\0')
        try:executable=Path(os.readlink(str(root/'exe'))).name
        except PermissionError:executable=Path(command[0].decode(errors='replace')).name if command else ''
        return {'pid':int(pid),'start_ticks':int(stat[19]),
                'executable':executable,
                'argument_names':[Path(a.decode(errors='replace')).name for a in command if a]}
    except (OSError,ValueError,IndexError):
        return None


def owned_processes(token,executable=None):
    result=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        record=proc_record(int(p.name),token)
        if record and (executable is None or record['executable']==executable):result.append(record)
    return result


def pidfd_open(pid):
    if hasattr(os,'pidfd_open'):return os.pidfd_open(pid,0)
    # Ubuntu 20.04 container Python 3.8 lacks os.pidfd_open. The host kernel
    # provides these Linux syscalls on the supported server architectures.
    if platform.machine() not in ('x86_64','aarch64'):
        raise RuntimeError('pidfd support unavailable; refusing PID-only signals')
    libc=ctypes.CDLL(None,use_errno=True);fd=libc.syscall(434,int(pid),0)
    if fd<0:raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))
    return fd


def send_pidfd(fd,sig):
    if hasattr(signal,'pidfd_send_signal'):
        signal.pidfd_send_signal(fd,sig,None,0);return
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.syscall(424,int(fd),int(sig),0,0)<0:
        raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))


def signal_owned(token,sig):
    sent=[]
    for record in owned_processes(token):
        try:fd=pidfd_open(record['pid'])
        except ProcessLookupError:continue
        try:
            current=proc_record(record['pid'],token)
            if current and current['start_ticks']==record['start_ticks']:
                send_pidfd(fd,sig);sent.append(record['pid'])
        except ProcessLookupError:pass
        finally:os.close(fd)
    return sent


def stop_stage(state_path,grace=5):
    state_path=Path(state_path)
    state_path.parent.mkdir(parents=True,exist_ok=True)
    # Serialize cancellation with child creation. A stop racing startup cannot
    # miss the child and let it begin after the caller has finished cleanup.
    with state_path.with_suffix('.launch-lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX)
        state_path.with_suffix('.cancel').touch(exist_ok=True)
        if not state_path.is_file():return []
        record=json.loads(state_path.read_text());token=record['token']
    # Signal current owned descendants, then any children created during drain.
    events=[]
    def deliver(sig):
        pids=signal_owned(token,sig)
        if pids:events.append({'signal':int(sig),'pids':pids,'unix':time.time()})
        return pids
    sent=deliver(signal.SIGINT);deadline=time.monotonic()+grace
    while time.monotonic()<deadline and owned_processes(token):time.sleep(.05)
    if owned_processes(token):
        sent+=deliver(signal.SIGTERM);deadline=time.monotonic()+min(grace,2)
        while time.monotonic()<deadline and owned_processes(token):time.sleep(.05)
    sent+=deliver(signal.SIGKILL)
    deadline=time.monotonic()+2
    while time.monotonic()<deadline and owned_processes(token):time.sleep(.05)
    remaining=owned_processes(token)
    if events or remaining:
        with state_path.with_suffix('.stops.jsonl').open('a') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            stream.write(json.dumps({'signals':events,'remaining':remaining})+'\n')
            stream.flush();os.fsync(stream.fileno())
    if remaining:raise RuntimeError('owned processes remain after shutdown; inspect stage evidence')
    return sorted(set(sent))


def run_stage(state_path,command):
    if not command:raise ValueError('empty stage command')
    # Fail before launching anything if the current kernel/container prohibits
    # the identity-safe signalling path needed for eventual cleanup.
    descriptor=pidfd_open(os.getpid())
    try:send_pidfd(descriptor,0)
    finally:os.close(descriptor)
    state_path=Path(state_path);state_path.parent.mkdir(parents=True,exist_ok=True)
    with state_path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if state_path.exists():raise ValueError('stage identity already used; preserve it and plan another attempt')
        token=uuid.uuid4().hex
        state=dict(schema=1,token=token,command=command,status='starting',started_unix=time.time(),
                   supervisor_pid=os.getpid(),signal_requests=[])
        atomic_json(state_path,state)
        env=dict(os.environ);env[TOKEN_KEY]=token
        process=None
        previous={}
        def forward(sig,frame):
            state['signal_requests'].append(int(sig));atomic_json(state_path,state)
        try:
            for sig in (signal.SIGINT,signal.SIGTERM):
                previous[sig]=signal.signal(sig,forward)
            with state_path.with_suffix('.launch-lock').open('a') as gate:
                fcntl.flock(gate,fcntl.LOCK_EX)
                if state_path.with_suffix('.cancel').exists():raise ValueError('stage was cancelled before launch')
                process=subprocess.Popen(command,env=env,start_new_session=True)
                identity=proc_record(process.pid,token)
                state.update(status='running',child_pid=process.pid,child_start_ticks=identity['start_ticks'] if identity else None)
                atomic_json(state_path,state)
            stopped=False
            while process.poll() is None:
                if state['signal_requests'] and not stopped:
                    stop_stage(state_path);stopped=True
                time.sleep(.05)
            code=process.wait()
            remaining=owned_processes(token)
            if remaining:stop_stage(state_path,grace=2)
            state.update(status='exited',exit_code=code,finished_unix=time.time(),
                         descendants_remaining_at_parent_exit=len(remaining))
            atomic_json(state_path,state)
            return code if code>=0 else 128-code
        except BaseException as exc:
            stop_stage(state_path,grace=1)
            if process is not None:
                try:process.wait(timeout=3)
                except subprocess.TimeoutExpired:pass
            state.update(status='supervisor_error',error=type(exc).__name__+': '+str(exc),finished_unix=time.time())
            atomic_json(state_path,state)
            raise
        finally:
            for sig,handler in previous.items():signal.signal(sig,handler)


def busy(names):
    conflicts=[];names=set(names)
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        record=proc_record(int(p.name))
        if record:
            match=names.intersection(record['argument_names'])|names.intersection([record['executable']])
            if match:conflicts.append({'pid':record['pid'],'names':sorted(match)})
    return conflicts


def domain_free(domain):
    if not 0<=domain<=101:raise ValueError('ROS domain must be between 0 and 101 on this host')
    lower=7400+250*domain
    for name in ('udp','udp6'):
        path=Path('/proc/net')/name
        for line in path.read_text().splitlines()[1:]:
            port=int(line.split()[1].rsplit(':',1)[1],16)
            if lower<=port<lower+250:return False
    return True


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--container');ap.add_argument('--container-state')
    ap.add_argument('--state',type=Path)
    ap.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    ap.add_argument('--grace',type=float,default=5)
    ap.add_argument('--executable');ap.add_argument('--name',action='append',default=[])
    ap.add_argument('--domain',type=int)
    ap.add_argument('operation',choices=('run','stop','status','idle','free-port','domain-free'))
    ap.add_argument('command',nargs=argparse.REMAINDER)
    args=ap.parse_args()
    if args.grace<0 or args.grace>60:ap.error('grace must be between 0 and 60 seconds')
    if args.container and not args.worker:
        remote_state=args.container_state
        if args.state is not None and not remote_state:
            ap.error('--container-state required with --state inside a container')
        remote=['--worker','--grace',str(args.grace)]
        if remote_state:remote+=['--state',remote_state]
        if args.executable:remote+=['--executable',args.executable]
        if args.domain is not None:remote+=['--domain',str(args.domain)]
        for name in args.name:remote+=['--name',name]
        remote+=[args.operation,*args.command]
        source=Path(__file__).read_text()
        child=subprocess.Popen(['docker','exec',args.container,'python3','-u','-c',source,*remote])
        old={}
        try:
            def stop_remote(signum,frame):
                if remote_state:
                    subprocess.run(['docker','exec',args.container,'python3','-u','-c',source,
                        '--worker','--state',remote_state,'--grace',str(args.grace),'stop'],check=False)
                else:child.send_signal(signum)
            for sig in (signal.SIGINT,signal.SIGTERM):
                old[sig]=signal.signal(sig,stop_remote)
            return child.wait()
        finally:
            for sig,handler in old.items():signal.signal(sig,handler)
    if args.operation=='idle':
        conflicts=busy(args.name)
        if conflicts:print(json.dumps({'unowned_conflicts':conflicts}),file=sys.stderr)
        return 2 if conflicts else 0
    if args.operation=='domain-free':
        if args.domain is None:ap.error('--domain is required')
        return 0 if domain_free(args.domain) else 2
    if args.operation=='free-port':
        import socket
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));print(sock.getsockname()[1])
        return 0
    if args.state is None:ap.error('--state is required')
    if args.operation=='run':
        command=args.command[1:] if args.command[:1]==['--'] else args.command
        return run_stage(args.state,command)
    if args.operation=='stop':
        stop_stage(args.state,args.grace);return 0
    if not args.state.exists():return 1
    record=json.loads(args.state.read_text())
    active=owned_processes(record['token'],args.executable)
    print(json.dumps({'status':record['status'],'owned_process_count':len(active)}))
    return 0 if active else 1


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError) as exc:
        print('[owned-process] '+str(exc),file=sys.stderr);raise SystemExit(2)
