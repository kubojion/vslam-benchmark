import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

import pytest

SCRIPT=Path(__file__).resolve().parents[2]/'run/_owned_process.py'
spec=importlib.util.spec_from_file_location('owned',SCRIPT)
owned=importlib.util.module_from_spec(spec);spec.loader.exec_module(owned)


def wait_for(predicate,timeout=4):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        try:
            value=predicate()
            if value:return value
        except (OSError,json.JSONDecodeError):pass
        time.sleep(.02)
    raise AssertionError('fixture did not reach expected state')


def launch(state,command):
    return subprocess.Popen([sys.executable,str(SCRIPT),'--state',str(state),'run','--',*command],
                            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)


def test_stop_preserves_unrelated_process_and_reaches_session_detached_descendant(tmp_path):
    state=tmp_path/'stage.json';child_pid=tmp_path/'child.pid'
    unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])
    script=('import subprocess,sys,time; from pathlib import Path; '
            "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'],start_new_session=True); "
            f'Path({str(child_pid)!r}).write_text(str(p.pid)); time.sleep(60)')
    supervisor=launch(state,[sys.executable,'-c',script])
    try:
        wait_for(child_pid.exists);record=json.loads(state.read_text())
        assert len(owned.owned_processes(record['token']))==2
        owned.stop_stage(state,grace=.1)
        supervisor.wait(timeout=4)
        assert owned.owned_processes(record['token'])==[]
        assert unrelated.poll() is None
        assert json.loads(state.read_text())['exit_code']!=0
    finally:
        owned.stop_stage(state,grace=.1)
        if supervisor.poll() is None:supervisor.kill();supervisor.wait()
        unrelated.terminate();unrelated.wait()


def test_stage_exit_is_recorded_and_identity_is_not_reused(tmp_path):
    state=tmp_path/'exit.json'
    first=launch(state,[sys.executable,'-c','raise SystemExit(7)']);assert first.wait(timeout=4)==7
    before=state.read_bytes();record=json.loads(before)
    assert record['status']=='exited' and record['exit_code']==7
    second=launch(state,[sys.executable,'-c','raise SystemExit(0)']);assert second.wait(timeout=4)==2
    assert state.read_bytes()==before


def test_cancel_before_start_cannot_launch_late_child(tmp_path):
    state=tmp_path/'late.json';marker=tmp_path/'must-not-exist'
    owned.stop_stage(state,grace=0)
    process=launch(state,[sys.executable,'-c',f'from pathlib import Path; Path({str(marker)!r}).touch()'])
    assert process.wait(timeout=4)==2 and not marker.exists()
    assert json.loads(state.read_text())['status']=='supervisor_error'


def test_supervisor_termination_stops_its_child(tmp_path):
    state=tmp_path/'signal.json';p=launch(state,[sys.executable,'-c','import time; time.sleep(60)'])
    try:
        record=wait_for(lambda: (d if (d:=json.loads(state.read_text()))['status']=='running' else None))
        p.send_signal(signal.SIGTERM);p.wait(timeout=8)
        assert owned.owned_processes(record['token'])==[]
        assert json.loads(state.read_text())['signal_requests']==[signal.SIGTERM]
    finally:
        owned.stop_stage(state,grace=.1)
        if p.poll() is None:p.kill();p.wait()


def test_pidfd_identity_is_rechecked_before_sending(monkeypatch):
    events=[]
    monkeypatch.setattr(owned,'owned_processes',lambda token:[{'pid':123,'start_ticks':1}])
    monkeypatch.setattr(owned,'pidfd_open',lambda pid:456)
    monkeypatch.setattr(owned,'proc_record',lambda pid,token:{'pid':pid,'start_ticks':2})
    monkeypatch.setattr(owned,'send_pidfd',lambda *args:events.append(args))
    monkeypatch.setattr(owned.os,'close',lambda fd:None)
    assert owned.signal_owned('token',signal.SIGKILL)==[] and not events


def test_idle_guard_reports_conflict_without_signalling_it():
    process=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)','benchmark_owned_process_fixture'])
    try:
        wait_for(lambda:owned.proc_record(process.pid))
        assert any(r['pid']==process.pid for r in owned.busy(['benchmark_owned_process_fixture']))
        assert process.poll() is None
    finally:
        process.terminate();process.wait()


def fake_docker(tmp_path):
    docker=tmp_path/'docker'
    docker.write_text('#!'+sys.executable+'\nimport os,sys\nassert sys.argv[1:3]==["exec","fixture"]\nassert sys.argv[3]=="python3"\nos.execv(sys.executable,[sys.executable,*sys.argv[4:]])\n')
    docker.chmod(0o755)
    return dict(os.environ,PATH=str(tmp_path)+os.pathsep+os.environ['PATH'])


def test_container_transport_runs_same_worker_and_preserves_exact_command(tmp_path):
    env=fake_docker(tmp_path);state=tmp_path/'container-stage.json';marker=tmp_path/'marker'
    literal='spaces; $(not a command) and quotes " remain arguments'
    command=[sys.executable,'-c',f'import sys;from pathlib import Path;Path({str(marker)!r}).write_text(sys.argv[1]);raise SystemExit(7)',literal]
    process=subprocess.run([sys.executable,str(SCRIPT),'--container','fixture','--state',str(state),
        '--container-state',str(state),'run','--',*command],env=env,capture_output=True,text=True)
    assert process.returncode==7 and marker.read_text()==literal
    assert json.loads(state.read_text())['command']==command


def test_container_supervisor_termination_requests_remote_owned_cleanup(tmp_path):
    env=fake_docker(tmp_path);state=tmp_path/'remote-signal.json'
    process=subprocess.Popen([sys.executable,str(SCRIPT),'--container','fixture','--state',str(state),
        '--container-state',str(state),'--grace','.1','run','--',sys.executable,'-c','import time;time.sleep(60)'],
        env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        record=wait_for(lambda: (d if (d:=json.loads(state.read_text()))['status']=='running' else None))
        process.terminate();process.wait(timeout=5)
        assert owned.owned_processes(record['token'])==[]
        assert json.loads(state.read_text())['status']=='exited'
    finally:
        owned.stop_stage(state,grace=.1)
        if process.poll() is None:process.kill();process.wait()


def test_domain_probe_detects_udp_port_and_rejects_unsafe_range():
    with pytest.raises(ValueError):owned.domain_free(102)
    for domain in range(80,100):
        if owned.domain_free(domain):break
    else:pytest.skip('no free domain for harmless UDP fixture')
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.bind(('127.0.0.1',7400+250*domain+17))
        assert not owned.domain_free(domain)
    assert owned.domain_free(domain)


def test_domain_shell_lock_excludes_other_attempt(tmp_path):
    script_dir=tmp_path/'scripts/run';script_dir.mkdir(parents=True)
    (script_dir/'_owned_process.py').symlink_to(SCRIPT)
    out=tmp_path/'result';out.mkdir()
    shell=SCRIPT.with_suffix('.sh')
    command=['bash','-c','source "$1"; owned_ros2_domain; echo ready; read -r release',
             'bash',str(shell)]
    env=dict(os.environ,WS=str(tmp_path),OUT_DIR=str(out))
    first=subprocess.Popen(command,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    try:
        assert first.stdout.readline().strip()=='ready'
        domain=(out/'ros_domain_id.txt').read_text().strip()
        other=subprocess.run(['bash','-c','source "$1"; owned_ros2_domain','bash',str(shell)],
            env=dict(env,VSLAM_ROS_DOMAIN_ID=domain),capture_output=True,text=True,timeout=5)
        assert other.returncode==2
        assert 'no unused, unlocked' in other.stderr
    finally:
        first.communicate('release\n',timeout=5)


def test_forced_shutdown_is_recorded(tmp_path):
    state=tmp_path/'stubborn.json';ready=tmp_path/'ready'
    p=launch(state,[sys.executable,'-c',
        'import signal,time;from pathlib import Path;'
        'signal.signal(signal.SIGINT,signal.SIG_IGN);signal.signal(signal.SIGTERM,signal.SIG_IGN);'
        f'Path({str(ready)!r}).touch();time.sleep(60)'])
    try:
        wait_for(ready.exists)
        owned.stop_stage(state,grace=.05);p.wait(timeout=4)
        events=[json.loads(line) for line in state.with_suffix('.stops.jsonl').read_text().splitlines()]
        assert any(e['signal']==9 for stop in events for e in stop['signals'])
        assert all(not stop['remaining'] for stop in events)
    finally:
        owned.stop_stage(state,grace=.1)
        if p.poll() is None:p.kill();p.wait()
