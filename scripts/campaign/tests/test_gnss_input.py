"""GNSS input/uncertainty tests without ROS or estimator processes."""
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/'scripts/run'))
from _gnss_input import read_gnss_csv,fix_uncertainty,prepare
spec=importlib.util.spec_from_file_location('gps_convert',REPO/'scripts/data/gps_to_okvis2x.py')
gps_convert=importlib.util.module_from_spec(spec);spec.loader.exec_module(gps_convert)


def test_status_zero_is_preserved_and_each_missing_variance_uses_fallback():
    covariance,status=fix_uncertainty((.04,None,.09),0,1.,4.,2)
    assert covariance==(.04,1.,.09)
    assert status==0
    assert fix_uncertainty((None,None,None),None,1.,4.,2)==((1.,1.,4.),2)
    with pytest.raises(ValueError,match='variances'):fix_uncertainty((.04,-1,.09),0)


def test_source_copy_and_label_are_bound_to_actual_input(tmp_path):
    source=tmp_path/'conventional.csv';source.write_text('t,lat,lon,alt\n1700000000.000000123,51,-2,100\n')
    output=tmp_path/'gnss_input.csv'
    with pytest.raises(ValueError,match='explicit GNSS_CSV'):
        prepare(source,output,'conventional_gps',False)
    record=prepare(source,output,'conventional_gps',True)
    assert record['first_timestamp_ns']==1700000000000000123
    assert output.read_bytes()==source.read_bytes()
    source.write_text('changed by a different experiment')
    assert read_gnss_csv(output)[0][1:4]==(51.,-2.,100.)
    assert json.loads(output.with_suffix('.json').read_text())['input_sha256']==record['input_sha256']
    with pytest.raises(ValueError,match='refusing replacement'):
        prepare(source,output,'conventional_gps',True)


def test_no_fix_rows_are_excluded_without_sanitizing_valid_fix_errors(tmp_path):
    source=tmp_path/'gps.csv'
    source.write_text('t,lat,lon,alt,status\n1,nan,nan,nan,-1\n2,51,-2,100,0\n')
    assert len(read_gnss_csv(source))==1
    source.write_text('t,lat,lon,alt,status\n1,nan,-2,100,0\n')
    with pytest.raises(ValueError,match='geodetic'):read_gnss_csv(source)


@pytest.mark.parametrize('bad',['nan','Infinity','1000000000000000000','bad'])
def test_invalid_timestamp_or_nanoseconds_are_rejected(tmp_path,bad):
    source=tmp_path/'gps.csv';source.write_text(f't,lat,lon,alt\n{bad},51,-2,100\n')
    with pytest.raises(ValueError,match='GNSS CSV row'):read_gnss_csv(source)


def test_out_of_order_inputs_are_not_silently_sorted(tmp_path):
    source=tmp_path/'gps.csv';source.write_text('t,lat,lon,alt\n2,51,-2,100\n1,51,-2,100\n')
    with pytest.raises(ValueError,match='increase'):read_gnss_csv(source)


def test_native_conversion_has_same_variance_policy_and_preserves_old_cache(tmp_path):
    source=tmp_path/'gps.csv'
    source.write_text('t,lat,lon,alt,cov_xx,cov_yy,cov_zz,status\n1.000000123,51,-2,100,0.04,,0.09,0\n2,nan,nan,nan,,,,-1\n')
    output=tmp_path/'attempt/mav0/gps0/data_raw.csv'
    assert gps_convert.convert(source,output)==1
    fields=output.read_text().splitlines()[1].split(',')
    assert fields[0]=='1000000123'
    assert abs(float(fields[4])-math.sqrt((.04+1.)/2))<5e-5
    assert float(fields[5])==.3
    old=output.read_bytes()
    with pytest.raises(FileExistsError):gps_convert.convert(source,output)
    assert output.read_bytes()==old


def test_shell_helper_maps_preserved_file_to_existing_container_mount(tmp_path):
    ws=tmp_path/'workspace';ws.mkdir();(ws/'scripts').symlink_to(REPO/'scripts',target_is_directory=True)
    seq=ws/'datasets/test/sequence';seq.mkdir(parents=True)
    (seq/'gps.csv').write_text('t,lat,lon,alt\n1,51,-2,100\n')
    output=ws/'results/gnss-vio/test/sequence/algo/run10001';output.mkdir(parents=True)
    command=['bash','-c','set -euo pipefail; WS="$1"; source "$WS/scripts/_paths.sh"; prepare_gnss_input "$2" "$3"; printf "%s\\n" "$GNSS_INPUT_CONT"','test',str(ws),str(output),str(seq)]
    result=subprocess.run(command,text=True,capture_output=True,check=True)
    assert result.stdout.splitlines()[-1]=='/results/gnss-vio/test/sequence/algo/run10001/gnss_input.csv'
    assert (output/'gnss_input.json').is_file()
