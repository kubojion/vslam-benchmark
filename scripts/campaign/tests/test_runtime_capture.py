from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'run'))
from _capture_runtime import identity,verify_identity


def test_model_changed_and_missing_asset_are_explicit(tmp_path):
    model=tmp_path/'src/MAC-VO/Model/MACVO_FrontendCov.pth';model.parent.mkdir(parents=True);model.write_bytes(b'weights')
    value=identity(tmp_path,'macvo')
    assert not value['missing']
    assert value['native_binary_source_linkage_verified'] is False
    verify_identity(tmp_path,value)
    model.write_bytes(b'new weights')
    with pytest.raises(ValueError,match='changed'):verify_identity(tmp_path,value)
    model.unlink();assert identity(tmp_path,'macvo')['missing']


def test_container_capture_records_writable_build_not_just_image(tmp_path):
    calls=[]
    def read(name,path):
        calls.append((name,path));return dict(path=path,files=[dict(path='node',sha256='a'*64,size_bytes=1)])
    def inspect(args):return {'Image':'sha256:image','Mounts':[]}
    value=identity(tmp_path,'ov2slam',tree_reader=read,inspector=inspect)
    assert calls==[('ov2slam','/root/catkin_ws/devel/lib')]
    assert value['container']['build_trees'][0]['files'][0]['sha256']=='a'*64
    assert value['loaded_dependency_closure_verified'] is False
    # CIFASIS uses its explicit ROS example build, not an absent catkin devel dir.
    calls.clear();value=identity(tmp_path,'cifasis_gnss_si',tree_reader=read,inspector=inspect)
    assert all(path!='/root/catkin_ws/devel/lib' for name,path in calls)
    assert any(path.endswith('Vocabulary/ORBvoc.txt') for name,path in calls)


def test_ephemeral_openvins_image_covers_unmounted_install_prefix(tmp_path):
    value=identity(tmp_path,'openvins',inspector=lambda args:{'Id':'sha256:image'})
    assert value['container']['estimator_prefix']=='/colcon_ws/install'
    assert value['container']['build_bytes_covered_by_immutable_image'] is True
    assert not value['native_binary_source_linkage_verified']


def test_basalt_identity_matches_runner_environment_regardless_of_caller(tmp_path,monkeypatch):
    home=tmp_path/'home';(home/'.basalt').mkdir(parents=True);(home/'.basalt/env').write_text('')
    binary=home/'.local/bin/basalt_vio';binary.parent.mkdir(parents=True);binary.write_bytes(b'elf');binary.chmod(0o755)
    library=home/'.local/lib/libbasalt.so';library.parent.mkdir(parents=True);library.write_bytes(b'so')
    import _capture_runtime
    monkeypatch.setattr(_capture_runtime.Path,'home',classmethod(lambda cls:home))
    def ldd(command,**options):
        resolved=str(library.parent) in options['env'].get('LD_LIBRARY_PATH','').split(':')
        return 'libbasalt.so => '+(str(library)+' (0x0)' if resolved else 'not found')+'\n'
    monkeypatch.setattr(_capture_runtime.subprocess,'check_output',ldd)
    values=[]
    for path,libraries in (('/usr/bin',None),(str(binary.parent)+':/usr/bin',str(library.parent))):
        monkeypatch.setenv('PATH',path)
        if libraries:monkeypatch.setenv('LD_LIBRARY_PATH',libraries)
        else:monkeypatch.delenv('LD_LIBRARY_PATH',raising=False)
        values.append(identity(tmp_path,'basalt'))
    assert values[0]==values[1] and not values[0]['missing']
    assert [f['path'] for f in values[0]['files']]==[str(binary),str(library)]
