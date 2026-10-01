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
