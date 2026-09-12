#!/usr/bin/env python3
"""Execute the four frozen Q1 cases through the existing serial runner.

No numerical model, detector nomination or confirmation outcome is evaluated.
Invoke with the fixed outer interrupt/kill ceiling in the dispatch receipt.
"""
import argparse
import hashlib
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from ros_esc.scenario_runner.run_scenario import execute_suite
from q1_environment import verify_environment
from q1_acquisition_layout import (Q2_VERSIONS, acquisition_expected_build,
                                   require_unused_q2_acquisition,
                                   imported_inputs, validate_acquisition_layout)


def receipt(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def verify_acquisition_environment(contract, release):
    if contract['version'] in Q2_VERSIONS:
        verify_environment(contract, release,
                           expected_build=acquisition_expected_build(contract['acquisition_version']))
    else:
        verify_environment(contract, release)


def spawn_receipt(directory, planned, contract):
    topics = analysis.load_yaml(directory / 'resolved_topics.yaml')['topics']
    selected = contract['spawn_check']['selected_pose_topic']
    alias = next(item['alias'] for item in topics if item['topic'] == selected)
    bag = analysis.read_run_bag(directory, aliases=(alias,))
    if bag.readiness_start_ns is None:
        raise ValueError('Q1 spawn check has no recorded readiness boundary')
    first = None
    for record in bag.records_by_topic[selected]:
        if record.bag_timestamp_ns >= bag.readiness_start_ns:
            break
        pose = record.message.pose.pose
        values = [pose.position.x, pose.position.y, pose.orientation.x,
                  pose.orientation.y, pose.orientation.z, pose.orientation.w]
        if all(math.isfinite(value) for value in values):
            first = record
            break
    if first is None:
        raise ValueError('Q1 spawn check lacks a finite pre-ready selected pose')
    pose = first.message.pose.pose
    yaw = analysis._v2_direction_yaw(pose.orientation)
    start = planned['resolved_scenario']['start']
    position_error = math.hypot(pose.position.x-start['x_m'], pose.position.y-start['y_m'])
    yaw_error = abs(math.remainder(yaw-start['yaw_rad'], math.tau))
    passed = (first.message.header.frame_id == contract['spawn_check']['frame_id']
              and position_error <= contract['spawn_check']['maximum_position_error_m']
              and yaw_error <= contract['spawn_check']['maximum_yaw_error_rad'])
    return {'passed': passed, 'bag_timestamp_ns': first.bag_timestamp_ns,
            'source_stamp_ns': first.ros_timestamp_ns, 'frame_id': first.message.header.frame_id,
            'actual_xy': [pose.position.x, pose.position.y], 'actual_yaw_rad': yaw,
            'requested_start': start, 'position_error_m': position_error, 'yaw_error_rad': yaw_error,
            'readiness_start_bag_ns': bag.readiness_start_ns, 'offset_fitted': False}


def main():
    entry_started = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', required=True, type=Path)
    arguments = parser.parse_args()
    contract_ref = receipt(arguments.contract)
    raw_contract = json.loads(arguments.contract.read_text())
    root = validate_acquisition_layout(raw_contract, arguments.contract)
    if raw_contract['version'] in Q2_VERSIONS:
        require_unused_q2_acquisition(arguments.contract, version=raw_contract['version'],
                                      allow_reserved_contract=True)
    contract = analysis._q1_contract(contract_ref)
    if os.environ.get('ROS_DOMAIN_ID') != str(contract['execution']['ros_domain_id']):
        raise ValueError('Q1 inherited ROS_DOMAIN_ID differs from the frozen acquisition graph')
    release = json.loads((root / 'preflight/dispatch_release.json').read_text())
    if release.get('contract') != contract_ref or release.get('status') != 'RELEASED':
        raise ValueError('Q1 exact contract has no source/preflight dispatch release')
    verify_acquisition_environment(contract, release)
    imports = imported_inputs(contract)
    output = root / 'acquisition'
    output.mkdir(parents=True, exist_ok=False)
    started = entry_started if imports else time.monotonic()
    ceiling = contract['execution'].get('outer_acquisition_ceiling_sec', 1200.)
    common = {'schema_version': 1, 'version': contract['version'], 'contract': contract_ref,
              'acquisition_version': contract.get('acquisition_version', contract['version']),
              'acquisition_root': str(root),
              'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'dispatch_release': receipt(root / 'preflight/dispatch_release.json')}
    if imports:
        common['imports'] = contract['imports']
    atomic_exclusive_json(output / 'started.json', {**common, 'status': 'INCOMPLETE'})
    runs, completed, failure = list(imports), [], None
    dispatched = 0
    try:
        for planned in contract['runs'][len(imports):]:
            # Preserve one process cap plus interrupt cleanup within the fixed suite ceiling.
            if time.monotonic()-started > ceiling-240-60:
                raise TimeoutError('Q1 remaining outer budget cannot fit another bounded case')
            analysis._q1_contract(contract_ref)
            verify_acquisition_environment(contract, release)
            if imports and imported_inputs(contract) != imports:
                raise ValueError('Q1 accepted imported inputs changed before dispatch')
            if time.monotonic()-started > ceiling-240-60:
                raise TimeoutError('Q1 remaining outer budget cannot fit another bounded case')
            dispatched += 1
            summary = execute_suite(
                contract['scenario']['path'], operator='mattb', case_ids=[planned['case_id']],
                runs_root=contract['execution']['runs_root'],
                summary_output=str(output / f'summary_{planned["seed"]}.yaml'),
                gui=planned['visible'], run_id=planned['run_id'])
            if len(summary['runs']) != 1:
                raise ValueError('Q1 runner did not return exactly one fixed case')
            result = summary['runs'][0]
            completed.append({'run_id': planned['run_id'], 'seed': planned['seed'],
                              'runner_result': result})
            if result['run_id'] != planned['run_id'] or not result['classification']['passed']:
                raise ValueError('Q1 acquisition/safety/cleanup gate failed; stop dispatch')
            directory = Path(result['run_directory']).resolve()
            if not directory.is_relative_to(root / 'runs') or directory.name != planned['run_id']:
                raise ValueError('Q1 returned run directory differs from its reserved acquisition root/identity')
            metadata = analysis.load_yaml(directory / 'metadata.yaml')
            if (metadata.get('target_argv') != planned['launch_argv']
                    or analysis.load_yaml(directory / 'resolved_scenario.yaml') != planned['resolved_scenario']):
                raise ValueError('Q1 recorded launch/scenario differs from the fixed planned case')
            duration = metadata.get('recording', {}).get('simulation_duration', {})
            if (not duration.get('completed') or duration.get('requested_sec') != 125.
                    or metadata['recording'].get('completion_reason') != 'simulation_duration_elapsed'):
                raise ValueError('Q1 lacks complete readiness-based simulated exposure')
            # These are acquisition/configuration checks; sealed scientific outcomes are untouched.
            pose = spawn_receipt(directory, planned, contract)
            atomic_exclusive_json(output / f'spawn_{planned["seed"]}.json', pose)
            if not pose['passed']:
                raise ValueError('Q1 world-coordinate input check failed')
            binding = analysis.q1_recorded_binding(directory, source_files=contract['source_files'])
            inputs = [directory / name for name in ('metadata.yaml', 'resolved_topics.yaml',
                      'resolved_scenario.yaml', 'resolved_parameters.yaml', 'bag/metadata.yaml',
                      'completeness.json', 'scenario_result.yaml')]
            inputs += sorted((directory / 'bag').glob('*.db3'))
            run = {key: planned[key] for key in ('run_id', 'seed', 'partition', 'exposure')}
            run.update(run_directory=str(directory), input_files=[receipt(p) for p in inputs],
                       binding=binding, model_configuration=binding['selected_configurations']['cost_function_config_filepath'],
                       spawn_check=receipt(output / f'spawn_{planned["seed"]}.json'))
            analysis._q1_verify_run(run, contract)
            atomic_exclusive_json(output / f'input_{planned["seed"]}.json', run)
            runs.append(run)
        if imports and imported_inputs(contract) != imports:
            raise ValueError('Q1 accepted imported inputs changed during continuation')
    except (Exception, KeyboardInterrupt) as exc:
        failure = f'{type(exc).__name__}: {exc}'
    result = {**common, 'status': 'COMPLETE' if len(runs) == 4 and failure is None else 'INCOMPLETE',
              'elapsed_wall_sec': time.monotonic()-started, 'failure': failure,
              'completed_runner_results': completed, 'verified_input_runs': runs,
              'imported_inputs': len(imports), 'newly_dispatched': dispatched,
              'scientific_confirmation_opened': False, 'replacement_runs_dispatched': False}
    atomic_exclusive_json(output / 'acquisition.json', result)
    if result['status'] == 'COMPLETE':
        atomic_exclusive_json(root / 'study_manifest.json', {**common, 'runs': runs})
    print(json.dumps({'status': result['status'], 'verified_runs': len(runs), 'failure': failure,
                      'elapsed_wall_sec': result['elapsed_wall_sec']}), flush=True)
    return 0 if result['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
