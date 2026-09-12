"""Q2 admission uses the real recorder's dated layout before input reads.

The inherited recorder fixture executes record_run.run with simulated process,
ROS, executor and clock owners. It starts no process or node. Recorded inputs
below are temporary synthetic receipts, never real bags.
"""

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ros_esc.experiment_recording import record_run as recorder
from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.scenario_runner.run_scenario import find_run_directory
from test_experiment_recording import (
    test_run_rechecks_operational_epoch_after_parameter_capture as run_recorder_case,
)
from test_q2_qualification_contract import q2_study  # noqa: F401


def move_run(run, destination):
    """Move synthetic content, preserving the exact receipt bytes and hashes."""
    old = Path(run['run_directory'])
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    old.rename(destination)
    run['run_directory'] = str(destination)
    for receipt in run['input_files']:
        receipt['path'] = str(destination/Path(receipt['path']).relative_to(old))


@pytest.mark.parametrize('q2_study', ['q2-primary-shadow-v1', 'q2-primary-shadow-v2'], indirect=True)
@pytest.mark.parametrize('created_at', [
    datetime(2026, 9, 9, 23, 59, 59, tzinfo=timezone.utc),
    datetime(2026, 9, 10, 0, 0, 1, tzinfo=timezone.utc),
])
def test_actual_recorder_created_bucket_is_admitted_across_utc_rollover(
        q2_study, monkeypatch, tmp_path, created_at):
    runs_root = tmp_path/'actual_recorder_runs'
    # Run the unchanged recorder directory owner, not a mirrored path formula.
    # Restore its mocked shared clock/ROS functions before analyzer admission.
    with monkeypatch.context() as recorder_patches:
        recorder_patches.setattr(recorder, '_utc_now', lambda: created_at)
        run_recorder_case(recorder_patches, runs_root)
    actual = find_run_directory(runs_root, 'm4-two-barrier-test')
    assert actual.parent.name == created_at.date().isoformat()
    assert (actual/'metadata.yaml').is_file()
    run = deepcopy(q2_study['runs'][0])
    move_run(run, actual.parent/run['run_id'])
    contract = deepcopy(q2_study['contract'])
    contract['execution']['runs_root'] = str(runs_root)
    # A suffix-decoy in another day is not a duplicate of the exact ID.
    (runs_root/'2026-09-11'/(run['run_id']+'-decoy')).mkdir(parents=True)
    assert find_run_directory(runs_root, run['run_id']) == Path(run['run_directory'])
    analysis._q1_verify_run(run, contract)


@pytest.mark.parametrize('q2_study', ['q2-primary-shadow-v1', 'q2-primary-shadow-v2'], indirect=True)
@pytest.mark.parametrize('change', [
    'duplicate_exact_id', 'missing_directory', 'direct_layout', 'invalid_date',
    'noncanonical_date', 'nested_bucket', 'wrong_id', 'outside_root',
    'symlink_outside_root', 'sealed_confirmation_redirect',
    'wrong_seed', 'wrong_partition', 'wrong_exposure',
])
def test_bad_layout_or_reserved_identity_fails_before_input_reads(
        q2_study, monkeypatch, tmp_path, change):
    run = deepcopy(q2_study['runs'][0])
    directory = Path(run['run_directory'])
    root = Path(q2_study['contract']['execution']['runs_root'])
    if change == 'duplicate_exact_id':
        (root/'2026-09-10'/run['run_id']).mkdir(parents=True)
    elif change == 'missing_directory':
        directory.rename(directory.with_name(run['run_id']+'-removed'))
    elif change == 'direct_layout':
        move_run(run, root/run['run_id'])
    elif change == 'invalid_date':
        move_run(run, root/'2026-02-30'/run['run_id'])
    elif change == 'noncanonical_date':
        move_run(run, root/'20260909'/run['run_id'])
    elif change == 'nested_bucket':
        move_run(run, root/'nested'/'2026-09-09'/run['run_id'])
    elif change == 'wrong_id':
        run['run_directory'] = str(directory.with_name(run['run_id']+'-other'))
        Path(run['run_directory']).mkdir()
    elif change == 'outside_root':
        move_run(run, tmp_path/'outside'/'2026-09-09'/run['run_id'])
    elif change == 'symlink_outside_root':
        move_run(run, tmp_path/'outside'/'2026-09-09'/run['run_id'])
        directory.symlink_to(run['run_directory'], target_is_directory=True)
        run['run_directory'] = str(directory)
    elif change == 'sealed_confirmation_redirect':
        sealed = next(item for item in q2_study['runs'] if item['partition'] == 'confirmation')
        directory.rename(directory.with_name(run['run_id']+'-removed'))
        directory.symlink_to(sealed['run_directory'], target_is_directory=True)
    elif change == 'wrong_seed':
        run['seed'] = q2_study['runs'][2]['seed']
    elif change == 'wrong_partition':
        run['partition'] = 'confirmation'
    else:
        run['exposure'] = 'approach'
    def forbidden(*args, **kwargs):
        pytest.fail('layout and reserved-identity rejection must precede any input receipt or YAML read')
    monkeypatch.setattr(analysis, '_q1_verify_files', forbidden)
    monkeypatch.setattr(analysis, '_v2_file_hash', forbidden)
    monkeypatch.setattr(analysis, 'load_yaml', forbidden)
    monkeypatch.setattr(analysis, 'read_run_bag', forbidden)
    with pytest.raises(ValueError):
        analysis._q1_verify_run(run, q2_study['contract'])
    assert q2_study['reads'] == []
