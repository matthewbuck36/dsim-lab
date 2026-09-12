"""Pure retained-development composition; no receipt I/O, bags or metric replay."""
from copy import deepcopy

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from test_m4_v12_science import integrated_rows
from test_m4_workflow import workflow


ROW_CHECKS = (
    'acquisition_complete', 'position_labels_complete',
    'confirmation_attribution_complete', 'selected_authority_complete',
    'error_attribution_complete', 'arrival_measurement_complete',
    'path_length_complete', 'motion_measurement_complete', 'direction_inputs_complete',
)
TOP_CHECKS = ('four_arm_analysis_complete', 'both_reference_products_complete')


def fixture():
    rows = integrated_rows('m4-pilot-v13')[:4]
    for row in rows:
        row.update(arrival_binding_method=metrics.RECORDED_ARRIVAL_BINDING,
            scientific_analysis_checks=dict.fromkeys(ROW_CHECKS, True),
            labels={'path': 'immutable-original-label-'+str(row['slot']), 'sha256': str(row['slot'])*64})
    # A's complete measured failure must survive, although the novel arms pass.
    rows[0].update(behavior_passed=False, arrival_passed=False, time_to_arrival_sec=None,
                   combined_sequence_passed=False)
    rows[0]['combined_sequence_components'].update(local_recovery_stage_passed=False,
        post_recovery_global_proximity_passed=False)
    selected = {slot: deepcopy(rows[slot-1]['mandatory_stop_evidence']) for slot in (3, 4)}
    for slot, motion in selected.items():
        motion.update(mandatory_stopped_acquisitions=0,
            command_pairing_scope='full_publication_order_v1',
            command_pairing_admitted_pair_count=6840 if slot == 3 else 7398,
            command_pairing_excluded_boundary_pairs=[] if slot == 3 else [
                {'index': 311, 'zero': True, 'command_in_readiness': False,
                 'diagnostic_in_readiness': True}])
    rows[3].update(mandatory_stopped_acquisitions=None, scientific_analysis_complete=False)
    rows[3]['mandatory_stop_evidence'].update(status='EVIDENCE_UNAVAILABLE',
        analysis_complete=False, command_pairing_complete=False,
        command_pairing_scope='recorded_readiness_interval_v1')
    rows[3]['scientific_analysis_checks']['motion_measurement_complete'] = False
    source = dict(version=metrics.VERSION, **metrics.experiment_fields('m4-pilot-v13'),
        block=0, complete=True, integrity_passed=True, scientific_analysis_complete=False,
        scientific_analysis_checks=dict(four_arm_analysis_complete=False,
                                       both_reference_products_complete=True),
        runs=rows, references=[{'path': 'original-reference-3', 'sha256': '3'*64},
                              {'path': 'original-reference-4', 'sha256': '4'*64}],
        contract={'path': 'original-v13-contract', 'sha256': 'a'*64})
    return source, selected


def expected_view(source, selected):
    expected = deepcopy(source)
    for slot in (3, 4):
        row = expected['runs'][slot-1]
        row['mandatory_stop_evidence'] = deepcopy(selected[slot])
        row['mandatory_stopped_acquisitions'] = selected[slot]['mandatory_stopped_acquisitions']
        row['scientific_analysis_checks']['motion_measurement_complete'] = selected[slot]['analysis_complete']
        row['scientific_analysis_complete'] = all(row['scientific_analysis_checks'].values())
    expected['scientific_analysis_checks']['four_arm_analysis_complete'] = all(
        row['scientific_analysis_complete'] and all(row['scientific_analysis_checks'].values())
        for row in expected['runs'])
    expected['scientific_analysis_complete'] = all(expected['scientific_analysis_checks'].values())
    return expected


def test_exact_composition_changes_only_allowed_motion_fields_and_conjunctions():
    source, selected = fixture(); old = deepcopy(source); old_selected = deepcopy(selected)
    actual = workflow._compose_v14_development(source, selected)
    assert actual == expected_view(old, old_selected)
    assert source == old and selected == old_selected
    assert actual['scientific_analysis_complete'] is True
    assert actual['runs'][:2] == old['runs'][:2]
    assert actual['runs'][0]['behavior_passed'] is False
    assert actual['runs'][0]['arrival_passed'] is False
    assert actual['runs'][0]['combined_sequence_passed'] is False
    assert actual['experiment_version'] == 'm4-pilot-v13'
    assert actual['method_version'] == 'recurrent_trapping_integrated_arrival_v13'
    # Independent C control: every pre-existing common motion field is preserved.
    for key, value in old['runs'][2]['mandatory_stop_evidence'].items():
        assert actual['runs'][2]['mandatory_stop_evidence'][key] == value
    actual['runs'][3]['mandatory_stop_evidence']['command_pairing_excluded_boundary_pairs'][0]['zero'] = False
    actual['runs'][2]['direction_rows'][0]['actual_error_deg'] = 90.
    assert source == old and selected == old_selected


@pytest.mark.parametrize('check', [name for name in ROW_CHECKS if name != 'motion_measurement_complete'])
def test_successful_selected_motion_cannot_erase_an_independent_failed_check(check):
    source, selected = fixture()
    source['runs'][3]['scientific_analysis_checks'][check] = False
    actual = workflow._compose_v14_development(source, selected)
    assert actual == expected_view(source, selected)
    assert actual['runs'][3]['scientific_analysis_checks']['motion_measurement_complete'] is True
    assert actual['runs'][3]['scientific_analysis_checks'][check] is False
    assert actual['runs'][3]['scientific_analysis_complete'] is False
    assert actual['scientific_analysis_complete'] is False


def test_failed_stationary_arm_measurement_is_preserved_in_top_completeness():
    source, selected = fixture()
    source['runs'][0]['scientific_analysis_checks']['error_attribution_complete'] = False
    source['runs'][0]['scientific_analysis_complete'] = False
    original_a = deepcopy(source['runs'][0])
    actual = workflow._compose_v14_development(source, selected)
    assert actual['runs'][0] == original_a
    assert actual['runs'][3]['scientific_analysis_complete'] is True
    assert not actual['scientific_analysis_checks']['four_arm_analysis_complete']
    assert not actual['scientific_analysis_complete']


def test_unavailable_selected_motion_stays_unavailable_without_fabricated_zero():
    source, selected = fixture()
    selected[4].update(status='EVIDENCE_UNAVAILABLE', analysis_complete=False,
        command_pairing_complete=False, mandatory_stopped_acquisitions=None)
    actual = workflow._compose_v14_development(source, selected)
    assert actual == expected_view(source, selected)
    assert actual['runs'][3]['mandatory_stopped_acquisitions'] is None
    assert actual['runs'][3]['scientific_analysis_complete'] is False
    assert actual['scientific_analysis_complete'] is False
    assert metrics.integrated_method_run_checks(actual['runs'][3])['status'] == 'EVIDENCE_UNAVAILABLE'


def test_false_reference_completeness_cannot_be_repaired_by_motion():
    source, selected = fixture()
    source['scientific_analysis_checks']['both_reference_products_complete'] = False
    actual = workflow._compose_v14_development(source, selected)
    assert actual['scientific_analysis_checks']['four_arm_analysis_complete'] is True
    assert actual['scientific_analysis_checks']['both_reference_products_complete'] is False
    assert actual['scientific_analysis_complete'] is False



def test_complete_measured_stop_stays_a_failed_package_not_an_unavailable_measurement():
    source, selected = fixture()
    selected[4].update(status='OBSERVED_STATIONARY_INTERVAL',
                       mandatory_stopped_acquisitions=None)
    actual = workflow._compose_v14_development(source, selected)
    assert actual['scientific_analysis_complete'] is True
    check = metrics.integrated_method_run_checks(actual['runs'][3])
    assert check['continuous_acquisition_passed'] is False
    assert check['status'] == 'FAIL'


def test_boolean_stopped_count_cannot_masquerade_as_integer_zero_at_package_gate():
    source, selected = fixture()
    selected[4]['mandatory_stopped_acquisitions'] = False
    actual = workflow._compose_v14_development(source, selected)
    assert actual['runs'][3]['mandatory_stopped_acquisitions'] is False
    check = metrics.integrated_method_run_checks(actual['runs'][3])
    assert check['continuous_acquisition_passed'] is None
    assert check['status'] == 'EVIDENCE_UNAVAILABLE'


@pytest.mark.parametrize('fault', ['missing_row', 'duplicate_slot', 'outside_slot',
    'missing_motion', 'extra_motion', 'string_motion_key'])
def test_composition_requires_exact_four_source_slots_and_two_motion_slots(fault):
    source, selected = fixture()
    if fault == 'missing_row': source['runs'].pop()
    elif fault == 'duplicate_slot': source['runs'][3]['slot'] = 3
    elif fault == 'outside_slot': source['runs'][0]['slot'] = 5
    elif fault == 'missing_motion': selected.pop(3)
    elif fault == 'extra_motion': selected[2] = deepcopy(selected[3])
    else: selected['3'] = selected.pop(3)
    before = deepcopy(source); old_selected = deepcopy(selected)
    with pytest.raises(ValueError):
        workflow._compose_v14_development(source, selected)
    assert source == before and selected == old_selected


@pytest.mark.parametrize('fault', ['missing_row_check', 'extra_row_check', 'nonbool_row_check',
    'missing_top_check', 'extra_top_check', 'nonbool_top_check', 'nonbool_motion_complete'])
def test_malformed_named_checks_do_not_receive_a_composed_pass(fault):
    source, selected = fixture()
    if fault == 'missing_row_check': source['runs'][2]['scientific_analysis_checks'].pop('path_length_complete')
    elif fault == 'extra_row_check': source['runs'][2]['scientific_analysis_checks']['custom_pass'] = True
    elif fault == 'nonbool_row_check': source['runs'][2]['scientific_analysis_checks']['path_length_complete'] = 1
    elif fault == 'missing_top_check': source['scientific_analysis_checks'].pop(TOP_CHECKS[1])
    elif fault == 'extra_top_check': source['scientific_analysis_checks']['custom_pass'] = True
    elif fault == 'nonbool_top_check': source['scientific_analysis_checks'][TOP_CHECKS[1]] = 1
    else: selected[4]['analysis_complete'] = 1
    with pytest.raises(ValueError):
        workflow._compose_v14_development(source, selected)
