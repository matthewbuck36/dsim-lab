#!/usr/bin/env python3
"""Freeze the declared Q1 inputs and commands, with no ROS/Gazebo dispatch.

Run once from the sourced isolated V2 overlay after focused checks. Scientific
selection and recording remain owned by the existing analyzer and runner.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite
from q1_acquisition_layout import (ACQUISITION_ROOTS, SCIENCE_VERSION, Q2_SCIENCE_VERSION,
                                   Q2_CORRECTED_VERSION, Q2_VERSIONS,
                                   acquisition_root, acquisition_science_version,
                                   acquisition_expected_build, acquisition_scenario,
                                   acquisition_population, contract_output,
                                   require_unused_q2_acquisition,
                                   validate_acquisition_layout)
from q1_environment import installed_entry_points


ROOT = Path('/home/mattb/dsim-lab')
OUTPUT = Path('/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1')
SCENARIO = ROOT / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/q1_primary_shadow_v1.yaml'
VERSION = SCIENCE_VERSION


def receipt(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def build_acquisition_runs(suite, resolved, root, acquisition_version):
    """Freeze existing runner argv with only the acquisition identity/root varied."""
    science = acquisition_science_version(acquisition_version)
    scenario = acquisition_scenario(acquisition_version) if science in Q2_VERSIONS else SCENARIO
    prefix = 'q2_' if science in Q2_VERSIONS else 'q1_'
    runs = []
    for position, run in enumerate(resolved):
        partition, exposure = run['case_id'].removeprefix(prefix).split('_')
        run_id = runner.validate_run_id(f'{acquisition_version}-{partition}-{exposure}-{run["seed"]}')
        metadata = runner.build_metadata(run, 'mattb', science, suite['metadata']['operator_notes'], run_id=run_id)
        launch = runner.build_launch_command(run, gui=position == 0, run_id=run_id)
        metadata_path = root / 'preflight' / f'metadata_{run["seed"]}.yaml'
        record = runner.build_record_command(run, run_id, metadata_path, root / 'runs', suite['execution'], launch)
        command = ['ros2', 'run', 'ros_esc', 'run_scenario', str(scenario), '--operator', 'mattb',
                   '--case-id', run['case_id'], '--run-id', run_id,
                   '--runs-root', str(root / 'runs'),
                   '--summary-output', str(root / 'acquisition' / f'summary_{run["seed"]}.yaml')]
        if position == 0:
            command.append('--gui')
        runs.append({'run_id': run_id, 'case_id': run['case_id'], 'seed': run['seed'],
                     'partition': partition, 'exposure': exposure, 'visible': position == 0,
                     'resolved_scenario': run, 'metadata_preview': metadata,
                     'launch_argv': launch, 'record_argv_template': record,
                     'record_metadata_path_semantics': 'runner creates a temporary input file with the frozen preview content',
                     'runner_argv': command})
    return runs


def collect_source_paths(acquisition_version):
    """Shared read-only source set for equivalence preparation and final freeze."""
    acquisition_root(acquisition_version)
    names = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others',
                                     '--exclude-standard', '-z', 'ros2_ws/src',
                                     'extremum-seeking/src']).split(b'\0')
    sources = {ROOT / name.decode() for name in names if name and (ROOT / name.decode()).is_file()}
    docs = ROOT / 'docs/codex/gesc_gaussian/v2'
    sources.update({Path(__file__).resolve(), docs/'q1_plan.md', docs/'qualification_release_review.md'})
    sources.update(Path(__file__).resolve().parent.glob('*.py'))
    additions = {
        f'{VERSION}-recovery1': ('q1_acquisition_recovery_plan.md','validation/q1_acquisition_failure_v1.md'),
        f'{VERSION}-recovery2': ('q1_acquisition_recovery2_plan.md','q1_simulation_source_plan.md'),
        f'{VERSION}-recovery3': ('q1_acquisition_recovery3_plan.md','q1_event_attribution_plan.md'),
        f'{VERSION}-recovery4': ('q1_acquisition_recovery4_plan.md','q1_filter_expiry_recovery_plan.md'),
        Q2_SCIENCE_VERSION: ('q2_qualification_plan.md', 'q2_policy_runtime_plan.md',
                            'q2_policy_runtime_handoff.md', 'q2_snapshot_serialization_plan.md',
                            'q2_snapshot_structural_clone_plan.md'),
    }
    additions[Q2_CORRECTED_VERSION] = additions[Q2_SCIENCE_VERSION] + ('q2_acquisition_path_correction_plan.md',)
    sources.update(docs/name for name in additions.get(acquisition_version, ()))
    if acquisition_version == f'{VERSION}-recovery4':
        old = json.loads((acquisition_root(f'{VERSION}-recovery3')/'preflight/contract.json').read_text())
        sources.update(Path(ref['path']) for ref in old['source_files'])
    sources.update(Path(path) for path in (
        '/opt/ros/humble/lib/libgazebo_ros_diff_drive.so',
        '/opt/ros/humble/lib/gazebo_ros/spawn_entity.py',
        '/opt/ros/humble/share/gazebo_msgs/srv/SpawnEntity.srv'))
    return sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquisition-version', choices=tuple(ACQUISITION_ROOTS), default=VERSION)
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    output_root = acquisition_root(arguments.acquisition_version)
    science = acquisition_science_version(arguments.acquisition_version)
    scenario = acquisition_scenario(arguments.acquisition_version) if science in Q2_VERSIONS else SCENARIO
    path = contract_output(output_root, arguments.output)
    if science in Q2_VERSIONS:
        require_unused_q2_acquisition(path, version=science)
    branch = subprocess.check_output(['git', '-C', str(ROOT), 'branch', '--show-current'], text=True).strip()
    if branch != 'feature/gesc-gaussian-robustness-v2':
        raise ValueError('Q1 requires the V2 branch')
    suite = load_suite(scenario)
    resolved, unsupported = expand_suite(suite)
    if unsupported or [r['seed'] for r in resolved] != [row[0] for row in acquisition_population(arguments.acquisition_version)]:
        raise ValueError('Q1 fixed scenario population changed')
    geometry = Path('/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/geometry_1.json')
    geometry_recovery_path = Path('/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1_recovery1/labels.json')
    geometry_document = json.loads(geometry.read_text())
    recovery_document = json.loads(geometry_recovery_path.read_text())['numerical_geometry_recovery']
    geometry_files = {geometry, geometry_recovery_path, Path(recovery_document['recovery_manifest_path']),
                      Path(recovery_document['original_analyzer_snapshot_path'])}
    for basin in geometry_document['basins']:
        for item in basin['point_receipts']:
            if receipt(item['path'])['sha256'] != item['sha256']:
                raise ValueError('A frozen primary geometry point changed')
            geometry_files.add(Path(item['path']))
    sources = collect_source_paths(arguments.acquisition_version)
    acquisition_recovery = None
    if arguments.acquisition_version == f'{VERSION}-recovery1':
        amendment = ROOT / 'docs/codex/gesc_gaussian/v2/q1_acquisition_recovery_plan.md'
        closure = ROOT / 'docs/codex/gesc_gaussian/v2/validation/q1_acquisition_failure_v1.md'
        sources.update((amendment, closure))
        acquisition_recovery = {'amendment': receipt(amendment), 'closure': receipt(closure),
                    'prior_acquisition': receipt(OUTPUT / 'acquisition/acquisition.json')}
    elif arguments.acquisition_version == f'{VERSION}-recovery2':
        amendment = ROOT / 'docs/codex/gesc_gaussian/v2/q1_acquisition_recovery2_plan.md'
        correction = ROOT / 'docs/codex/gesc_gaussian/v2/q1_simulation_source_plan.md'
        sources.update((amendment, correction))
        prior_root = acquisition_root(f'{VERSION}-recovery1')
        acquisition_recovery = {
            'amendment': receipt(amendment), 'source_correction': receipt(correction),
            'closure': receipt(prior_root / 'acquisition_closed.json'),
            'prior_acquisition': receipt(prior_root / 'acquisition/acquisition.json'),
        }
    elif arguments.acquisition_version == f'{VERSION}-recovery3':
        amendment = ROOT / 'docs/codex/gesc_gaussian/v2/q1_acquisition_recovery3_plan.md'
        correction = ROOT / 'docs/codex/gesc_gaussian/v2/q1_event_attribution_plan.md'
        sources.update((amendment, correction))
        prior_root = acquisition_root(f'{VERSION}-recovery2')
        acquisition_recovery = {
            'amendment': receipt(amendment), 'source_correction': receipt(correction),
            'closure': receipt(prior_root / 'acquisition_closed.json'),
            'prior_acquisition': receipt(prior_root / 'acquisition/acquisition.json'),
        }
    elif arguments.acquisition_version == f'{VERSION}-recovery4':
        acquisition_recovery = {
            'amendment':receipt(ROOT/'docs/codex/gesc_gaussian/v2/q1_acquisition_recovery4_plan.md'),
            'source_correction':receipt(ROOT/'docs/codex/gesc_gaussian/v2/q1_filter_expiry_recovery_plan.md')}
    sources.update(Path(path) for path in (
        '/opt/ros/humble/lib/libgazebo_ros_diff_drive.so',
        '/opt/ros/humble/lib/gazebo_ros/spawn_entity.py',
        '/opt/ros/humble/share/gazebo_msgs/srv/SpawnEntity.srv',
    ))
    runs = build_acquisition_runs(suite, resolved, output_root, arguments.acquisition_version)
    imports = None
    if arguments.acquisition_version == f'{VERSION}-recovery4':
        prior_root = acquisition_root(f'{VERSION}-recovery3')
        prior_contract = prior_root/'preflight/contract.json'
        old = json.loads(prior_contract.read_text())
        runs[:2] = old['runs'][:2]
        imports = {'prior_contract':receipt(prior_contract),
            'prior_acquisition':receipt(prior_root/'acquisition/acquisition.json'),
            'prior_closure':receipt(prior_root/'acquisition_closed.json'),
            'input_files':[receipt(prior_root/'acquisition'/f'input_{seed}.json') for seed in (26090911,26090912)],
            'expiry_audit':receipt(prior_root/'diagnostics/discovery_expiry_audit_v1/result.json'),
            'source_equivalence':receipt(output_root/'preflight/source_equivalence.json')}
    contract = {
        'schema_version': 1, 'version': science, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'acquisition_version': arguments.acquisition_version, 'acquisition_root': str(output_root),
        'branch': branch, 'head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'status': 'FROZEN_INPUTS_ONLY', 'gazebo_dispatch_released': False,
        'scenario': receipt(scenario), 'source_files': [receipt(p) for p in sorted(sources)],
        'installed_entry_points': (installed_entry_points(expected_build=acquisition_expected_build(arguments.acquisition_version))
                                   if science in Q2_VERSIONS else installed_entry_points()),
        'geometry_receipts': [receipt(p) for p in sorted(geometry_files)],
        'label_geometry': receipt(geometry), 'geometry_recovery': receipt(geometry_recovery_path),
        'coordinate_preflight': receipt(ROOT / 'docs/codex/gesc_gaussian/v2/validation/q1_coordinate_preflight.md'),
        'execution': {**suite['execution'], 'runs_root': str(output_root / 'runs'),
                      'outer_acquisition_ceiling_sec': 600. if imports else 1200.,
                      'recorder_process_ceiling_sec': 240., 'escalation_allowance_sec': 15.,
                      'ros_domain_id': 191},
        'detector': {'window_seconds': 6., 'epsilon_m': .30, 'radius_grid_m': [.25, .5, .75],
                     'candidate_epsilon_grid_m': [.05, .10, .15], 'positive_support_sec': 42.,
                     'verification_sec': 12., 'label_job_timeout_sec': 600},
        'reference': {'target_offsets_sec': list(range(10, 121, 10)), 'anchor_window_sec': .05,
                      'minimum_confirmation_informative_anchors_per_run': 6,
                      'maximum_median_error_deg': 30, 'maximum_p90_error_deg': 60,
                      'minimum_usable_averaging_availability': .8,
                      'output_magnitude_floor': 1e-6, 'job_timeout_sec': 300},
        'spawn_check': {'selected_pose_topic': '/odom', 'frame_id': 'odom',
                        'maximum_position_error_m': .02, 'maximum_yaw_error_rad': .05,
                        'sample': 'first finite selected pose before recording readiness; no fitted transform'},
        'runs': runs,
    }
    if science in Q2_VERSIONS:
        from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
        additions = analysis.q2_contract_fields(science)
        if (additions['version'] != science
                or additions['expected_build'] != str(acquisition_expected_build(arguments.acquisition_version))
                or receipt(additions['runtime_source_checkpoint']['path']) != additions['runtime_source_checkpoint']
                or [seed for seeds in analysis.qualification_partition_seeds(science).values() for seed in seeds]
                   != [run['seed'] for run in runs]):
            raise ValueError('Q2 acquisition profile and analytical contract disagree')
        if science == Q2_CORRECTED_VERSION:
            for name in ('prior_acquisition_closure', 'acquisition_path_correction_checkpoint'):
                if receipt(additions[name]['path']) != additions[name]:
                    raise ValueError('Q2 path correction closure/checkpoint changed')
        contract.update(additions)
    if acquisition_recovery is not None:
        contract['recovery'] = acquisition_recovery
    if imports is not None:
        contract['imports'] = imports
    validate_acquisition_layout(contract, path)
    # Enforce the public analytical/geometry contract before saving a dispatchable artifact.
    from ros_esc.plotting_scripts import q1_study
    for run in runs:
        q1_study.verify_q1_geometry(contract, run['resolved_scenario'])
    if science in Q2_VERSIONS:
        require_unused_q2_acquisition(path, version=science)
    output = path.parent
    output.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(contract, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'contract': receipt(path), 'runs': len(runs), 'source_files': len(sources),
                      'geometry_receipts': len(geometry_files), 'gazebo_dispatched': False}))


if __name__ == '__main__':
    main()
