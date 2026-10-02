#!/usr/bin/env python3
"""Record current native/model/container assets without executing an estimator.

Docker inspect/cp also work on stopped containers. No container is created,
started, or executed here. Known build directories are hashed, not assumed to
match the source checkout; runtime dependency resolution still needs validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

from _capture_implementation import SOURCES, digest_file
from _capture_inputs import digest

CONTAINERS={'airslam':'air_slam','ov2slam':'ov2slam','voxel_svio':'voxel_svio',
            'cifasis_gnss_si':'cifasis_gnss_si','vins_fusion_gps':'vins_fusion'}


def container_tree(container,path):
    process=subprocess.Popen(['docker','cp','-L',f'{container}:{path}','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    entries=[]
    try:
        with tarfile.open(fileobj=process.stdout,mode='r|*') as archive:
            for member in archive:
                if member.isfile():
                    h=hashlib.sha256()
                    stream=archive.extractfile(member)
                    for chunk in iter(lambda:stream.read(2**20),b''):h.update(chunk)
                    entries.append(dict(path=member.name,size_bytes=member.size,sha256=h.hexdigest()))
                elif member.issym() or member.islnk():
                    entries.append(dict(path=member.name,link=member.linkname,requires_target_resolution=True))
        error=process.stderr.read();code=process.wait(timeout=60)
        if code:raise ValueError('cannot read container build directory: '+path)
    except BaseException:
        process.kill();process.wait();raise
    finally:
        process.stdout.close();process.stderr.close()
    return dict(path=path,files=sorted(entries,key=lambda x:x['path']))


def identity(repo,algorithm,*,tree_reader=container_tree,inspector=None):
    repo=Path(repo)
    if algorithm not in SOURCES:raise ValueError('unsupported runtime identity algorithm')
    files=[];missing=[];container=None
    def host(path):
        path=Path(path);p=path if path.is_absolute() else repo/path
        label=str(path)
        # External native paths use a stable public basename, not a home path.
        if path.is_absolute() and str(path).startswith(('/home/','/data/')):label=path.name
        if not p.is_file():missing.append('missing_runtime_asset:'+label);return
        before=p.stat();value=digest_file(p);after=p.stat()
        if (before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
            raise ValueError('runtime asset changed while hashing: '+label)
        files.append(dict(path=label,size_bytes=after.st_size,sha256=value))
    def inspect(args):
        if inspector:return inspector(args)
        return json.loads(subprocess.check_output(['docker',*args],timeout=30,stderr=subprocess.DEVNULL))[0]
    if algorithm=='orbslam3':
        for p in ('Examples/Stereo/stereo_euroc','Examples/Stereo-Inertial/stereo_inertial_euroc',
                  'Vocabulary/ORBvoc.txt','lib/libORB_SLAM3.so','Thirdparty/DBoW2/lib/libDBoW2.so','Thirdparty/g2o/lib/libg2o.so'):
            host('src/ORB_SLAM3/'+p)
        host('results/zed-preparation-20261002/orb-build/g2o-source/lib/libg2o.so')
        host('results/zed-preparation-20261002/orb-build/orb-shutdown/libORB_SLAM3.so')
    elif algorithm in ('okvis2','okvis2x'):
        for p in ('okvis_app_synchronous','small_voc.yml.gz'):host(f'src/{algorithm}/build/{p}')
        for p in sorted((repo/'src'/algorithm/'build').rglob('*.so*')):
            if p.is_file():host(p.relative_to(repo))
    elif algorithm=='basalt':
        # run_basalt.sh sources the installer environment before its own capture.
        # Resolve identically here so the campaign identity and the launch
        # preflight do not depend on the caller's PATH or LD_LIBRARY_PATH.
        environment=dict(os.environ)
        if (Path.home()/'.basalt/env').is_file():
            for key,folder in (('PATH','bin'),('LD_LIBRARY_PATH','lib')):
                local=str(Path.home()/'.local'/folder)
                parts=[x for x in environment.get(key,'').split(':') if x]
                if local not in parts:environment[key]=':'.join([local]+parts)
        binary=shutil.which('basalt_vio',path=environment.get('PATH'))
        host(binary or 'missing-basalt_vio')
        if binary:
            dependencies=subprocess.check_output(['ldd',binary],text=True,timeout=30,env=environment)
            libraries=[line.split()[2] for line in dependencies.splitlines()
                       if line.strip().startswith('libbasalt.so => /')]
            if len(libraries)!=1:missing.append('unresolved_basalt_shared_library')
            for library in libraries:host(library)
    elif algorithm=='dpvo':
        host('src/DPVO/dpvo.pth')
        for p in sorted((repo/'src/DPVO').rglob('*.so')):host(p.relative_to(repo))
    elif algorithm=='macvo':
        host('src/MAC-VO/Model/MACVO_FrontendCov.pth')
        for p in sorted((repo/'src/MAC-VO').rglob('*.so')):host(p.relative_to(repo))
    elif algorithm=='airslam':
        for p in ['superpoint_lightglue.onnx']+[f'superpoint_lightglue_{ds}.engine' for ds in ('euroc_mav','hortimulti','rosariov2','zed2i')]:
            host('src/airslam/output/'+p)
    if algorithm in ('openvins','openvins_gps'):
        info=inspect(['image','inspect','openvins:humble'])
        container=dict(kind='ephemeral_image',image_id=info['Id'],image='openvins:humble',
                       estimator_prefix='/colcon_ws/install',build_bytes_covered_by_immutable_image=True,
                       note='runner mounts /ws and optional sequence data, not /colcon_ws/install')
        if algorithm=='openvins':
            corrected=inspect(['image','inspect','openvins:humble-shutdown-20261001'])
            container['corrected_euroc_image']={'image':'openvins:humble-shutdown-20261001',
                                              'image_id':corrected['Id']}
    elif algorithm in CONTAINERS:
        name=CONTAINERS[algorithm];info=inspect(['inspect',name])
        mounts=[]
        for m in info.get('Mounts',[]):
            source=Path(m['Source'])
            try:source_label=source.relative_to(repo).as_posix()
            except ValueError:source_label='<external>/'+source.name
            mounts.append(dict(destination=m['Destination'],source=source_label,read_write=m.get('RW')))
        container=dict(kind='persistent_container',name=name,image_id=info['Image'],
                       mounts=sorted(mounts,key=lambda x:x['destination']),build_trees=[])
        paths=['/root/catkin_ws/devel/lib']
        if algorithm=='airslam':
            # Corrected EuRoC inertial cohort uses an isolated build; retain the
            # legacy tree identity as well for the other, unchanged modes.
            paths.append('/root/catkin_ws_rectified_20261001/devel/lib')
        if algorithm=='voxel_svio':
            paths.append('/root/catkin_ws_shutdown_20261002/devel/lib')
            paths.append('/root/vslam_voxel_audit_20261002_v2')
            paths.append('/root/vslam_voxel_audit_20261002_v3')
        if algorithm=='cifasis_gnss_si':paths = ['/root/catkin_ws/src/gnss-stereo-inertial-fusion/lib',
            '/root/catkin_ws/src/gnss-stereo-inertial-fusion/Examples/ROS/GNSS_SI/GNSS_Stereo_Inertial',
            '/root/catkin_ws/src/gnss-stereo-inertial-fusion/Vocabulary/ORBvoc.txt']
        for path in paths:
            try:container['build_trees'].append(tree_reader(name,path))
            except (ValueError,tarfile.TarError,OSError,subprocess.SubprocessError):missing.append('unreadable_container_build:'+name+':'+path)
    if algorithm in ('openvins_gps','rtabmap_gps'):
        for p in ('robot_localization/ekf_node','robot_localization/navsat_transform_node','tf2_ros/static_transform_publisher'):
            host('/opt/ros/humble/lib/'+p)
    if algorithm=='rtabmap_gps':
        for p in ('rtabmap_slam/rtabmap','rtabmap_odom/stereo_odometry','imu_filter_madgwick/imu_filter_madgwick_node'):
            host('/opt/ros/humble/lib/'+p)
        host(shutil.which('rtabmap-export') or '/opt/ros/humble/bin/rtabmap-export')
    value=dict(schema=1,algorithm=algorithm,files=files,container=container,missing=missing,
        native_binary_source_linkage_verified=False,loaded_dependency_closure_verified=False,
        limitations=['current known asset bytes only; not historical implementation evidence',
                     'ROS resolution, Python native extensions outside source, dynamically loaded dependencies and build linkage need execution/build evidence'])
    value['sha256']=digest(value);return value


def verify_identity(repo,value,*,check_live=True):
    if value.get('schema')!=1 or digest({k:v for k,v in value.items() if k!='sha256'})!=value.get('sha256'):
        raise ValueError('runtime asset manifest digest mismatch')
    if check_live and identity(repo,value['algorithm'])!=value:raise ValueError('runtime assets changed since capture')


def capture(repo,run):
    repo=Path(repo).resolve();run=Path(run).resolve();parts=run.relative_to(repo/'results').parts
    if len(parts)!=5:raise ValueError('unexpected physical attempt path')
    value=identity(repo,parts[3]);target=run/'provenance/runtime-assets.json'
    expected=os.environ.get('VSLAM_EXPECTED_RUNTIME_SHA256')
    if expected and value['sha256']!=expected:raise ValueError('runtime assets disagree with reviewed campaign')
    if value['missing']:raise ValueError('; '.join(value['missing']))
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return value


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',required=True,type=Path);ap.add_argument('--run',required=True,type=Path)
    args=ap.parse_args();value=capture(args.repo,args.run)
    print(json.dumps(dict(runtime_capture=True,sha256=value['sha256'])))


if __name__=='__main__':main()
