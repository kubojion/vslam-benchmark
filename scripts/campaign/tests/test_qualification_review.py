import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qualification_review import review_saved


def review(meta=None, value=None, findings=None, exists=True):
    return review_saved('vo/euroc_mav/MH_01_easy/macvo/run1', meta or {
        'process': {'exit_code': 0}, 'provenance': {'workspace': {'commit': 'old', 'dirty': True}}},
        value or {'run_status': 'ok', 'coverage': {'coverage_gap_pct': 100}}, findings or [],
        [{'verified': True}], exists=exists)


def test_full_clean_export_is_not_a_certificate_and_a_gap_does_not_request_rerun():
    decision = review()
    assert decision['status'] == 'blocked' and not decision['reuse_qualified']
    assert 'historical_dirty_runner_tree_recorded_only_as_nonreconstructable_digest' in decision['blockers']
    assert decision['rerun_decision'].startswith('not_requested')
    assert 'configuration_and_claim_qualification_pending' not in decision['blockers']


def test_confirmed_defect_and_missing_slot_are_different_from_retained_failure():
    assert review(findings=[{'code': 'confirmed_calibration_defect'}])['status'] == 'rerun_required'
    assert review(exists=False)['status'] == 'not_executed'
    value = {'run_status': 'scale_collapse', 'coverage': {'coverage_gap_pct': 80}}
    before = copy.deepcopy(value)
    decision = review(value=value)
    assert value == before
    assert decision['status'] == 'blocked' and decision['rerun_decision'].startswith('not_requested')
    assert 'retain_observed_scale_collapse_in_attempt_denominator' in decision['claim_limits']
    assert 'export_coverage_below_95_percent_no_clean_success_tick' in decision['claim_limits']


def test_review_without_machine_gaps_still_requires_an_explicit_claim_decision():
    decision = review(meta={'process': {'exit_code': 0}, 'provenance': {
        'workspace': {'commit': 'known', 'dirty': False}}})
    assert decision['blockers'] == ['explicit_configuration_input_and_claim_review_not_recorded']


def test_openvins_immutable_image_is_not_labelled_a_mutable_container_binary():
    decision=review_saved('vio/euroc_mav/MH_01_easy/openvins/run1',
        {'process':{'exit_code':0},'provenance':{'workspace':{'commit':'known'},'container':{'image_id':'sha256:known'}}},
        {'run_status':'ok','coverage':{'coverage_gap_pct':100}},[],[{'verified':True}],exists=True)
    assert 'historical_mutable_container_native_executable_not_identified' not in decision['blockers']
    assert 'historical_container_runtime_resolution_and_build_source_linkage_unverified' in decision['blockers']
