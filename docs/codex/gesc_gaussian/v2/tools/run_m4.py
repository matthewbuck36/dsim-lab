#!/usr/bin/env python3
"""Dispatch fixed M4 slots through the existing runner and frozen science hooks.

This owns orchestration receipts only. The ROS graph, recording, cleanup,
topology, numerical references and scientific metrics retain existing owners.
"""

import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import time

import yaml

from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.m4_scenario import (
    DEFAULT_EXPERIMENT_VERSION, expected_slots, experiment_identity, validate_experiment_contract,
    experiment_execution_budgets, is_retained_development_experiment_version,
)


def receipt(path):
    path = Path(path).resolve()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return {'path': str(path), 'sha256': digest.hexdigest()}


def runner_command(contract, planned):
    """Canonical one-case command; its transient absolute end is appended later."""
    command = ['ros2', 'run', 'ros_esc', 'run_scenario', contract['scenario']['path'],
        '--operator', 'mattb', '--case-id', planned['case_id'], '--run-id', planned['run_id'],
        '--runs-root', contract['execution']['runs_root'],
        '--summary-output', planned['summary_path'], '--strict-cleanup']
    if contract['version'] != DEFAULT_EXPERIMENT_VERSION:
        command += ['--process-ownership-mode', experiment_identity(contract['version'])['process_ownership_mode']]
    if planned['visible']:
        command.append('--gui')
    return command


def validate_process_ownership(contract, process_result):
    """Consume the selected owner's proof without reinterpreting old receipts."""
    if contract['version'] == DEFAULT_EXPERIMENT_VERSION:
        return
    mode = experiment_identity(contract['version'])['process_ownership_mode']
    ownership = process_result.get('process_ownership', {})
    proof = ownership.get('kernel_proof', {})
    if (ownership.get('mode') != mode or ownership.get('inspection_complete') is not True
            or any(proof.get(key) is not True for key in ('complete', 'baseline_echild',
                'subreaper_verified', 'root_reaped', 'final_echild', 'scope_exclusive',
                'sigchld_valid', 'state_restored'))):
        raise ValueError('M4 v2 selected subreaper ownership proof is incomplete')
    if (mode == 'subreaper_group_v3' and ownership.get('signal_strategy') !=
            'initial_unreaped_root_group_sigint_then_adopted_pidfd'):
        raise ValueError('M4 v3 selected graceful signal strategy is absent or changed')


def validate_contract(contract):
    """Reject changed populations, routing, budgets and existing reserved IDs."""
    validate_experiment_contract(contract)
    root = Path(contract['root']).resolve()
    execution = contract['execution']
    budgets = experiment_execution_budgets(contract['version'])
    for key in ('suite_timeout_sec', 'case_timeout_sec', 'cleanup_reserve_sec',
                'science_budget_sec', 'recording_sec', 'shutdown_grace_sec'):
        expected = budgets[key]
        if isinstance(execution.get(key), bool) or execution.get(key) != expected:
            raise ValueError('M4 execution budget differs: ' + key)
    if Path(execution['runs_root']).resolve() != root / 'runs':
        raise ValueError('M4 runs root differs from exclusive contract root')
    science = contract['science']
    if any(isinstance(science.get(key), bool) or not isinstance(science.get(key), (int, float))
           or not math.isfinite(science[key]) or science[key] <= 0
           for key in ('labels_sec', 'references_sec', 'summary_sec', 'freeze_report_sec')):
        raise ValueError('M4 scientific caps must be finite positive seconds')
    if 4*(science['labels_sec']+2*science['references_sec']+science['summary_sec']) + science['freeze_report_sec'] != budgets['science_budget_sec']:
        raise ValueError('M4 scientific caps differ from the total reserved budget')
    plans = contract.get('runs', [])
    if len(plans) != 16:
        raise ValueError('M4 requires exactly sixteen fixed slots')
    ids = set()
    for expected, actual in zip(expected_slots(contract['version']), plans):
        if any(actual.get(key) != value for key, value in expected.items()):
            raise ValueError('M4 slot population/order differs')
        run_id = runner.validate_run_id(actual['run_id'])
        if run_id in ids:
            raise ValueError('M4 run identity repeated')
        ids.add(run_id)
        # The scenario owner has already authenticated these complete original
        # V13 plans, including their original summary and runner command paths.
        if is_retained_development_experiment_version(contract['version']) and actual['slot'] <= 4:
            continue
        summary = root / 'acquisition' / f'summary_{actual["slot"]}.yaml'
        if Path(actual['summary_path']).resolve() != summary:
            raise ValueError('M4 summary path differs from reserved slot')
        if actual['runner_argv'] != runner_command(contract, actual):
            raise ValueError('M4 command differs from canonical existing runner')
    return root


def _read_yaml(path):
    with Path(path).open() as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError('expected a retained YAML mapping: ' + str(path))
    return value


def validate_launch_binding(planned, result, directory):
    """Bind every actual argument; only witnessed noisy JSON relocation is allowed."""
    actual, expected = result.get('launch_argv'), planned.get('launch_argv')
    if any(not isinstance(argv, list) or not argv
           or any(not isinstance(value, str) for value in argv)
           for argv in (actual, expected)):
        raise ValueError('M4 actual/frozen launch command is absent or invalid')
    if actual == expected:
        return
    prefix = 'cost_function_config_filepath:='
    actual_cost = [index for index, value in enumerate(actual) if value.startswith(prefix)]
    expected_cost = [index for index, value in enumerate(expected) if value.startswith(prefix)]
    if (planned['condition'] != 'noise' or len(actual) != len(expected)
            or len(actual_cost) != 1 or actual_cost != expected_cost):
        raise ValueError('M4 actual launch differs from frozen command')
    index = actual_cost[0]
    if any(value != expected[position] for position, value in enumerate(actual)
           if position != index):
        raise ValueError('M4 actual launch differs from frozen command')
    frozen = planned.get('expected_cost_configuration')
    witness = result.get('captured_cost_configuration')
    captured = Path(directory) / 'resolved_cost_function.json'
    if (not isinstance(frozen, dict) or set(frozen) != {'path', 'sha256'}
            or not isinstance(witness, dict) or set(witness) != {'argv_path', 'path', 'sha256'}
            or expected[index] != prefix + frozen['path']
            or actual[index] != prefix + witness['argv_path']
            or not Path(witness['argv_path']).is_absolute()
            or witness['path'] != str(captured) or captured.is_symlink()
            or witness['sha256'] != frozen['sha256']
            or receipt(frozen['path']) != frozen
            or receipt(captured) != {'path': witness['path'], 'sha256': witness['sha256']}):
        raise ValueError('M4 noisy launch relocation lacks exact captured/frozen cost witness')


def validate_case_result(contract, planned, process_result):
    """Separate integrity/safety from complete safe behavioral failures."""
    if (process_result.get('timed_out') or process_result.get('return_code') not in (0, 1)
            or process_result.get('deadline_audit', {}).get('deadline_exhausted')):
        raise ValueError('M4 outer child timeout or infrastructure exit')
    summary = _read_yaml(planned['summary_path'])
    if (summary.get('resolved_run_count') != 1 or summary.get('dry_run') is not False
            or summary.get('selected_case_ids') != [planned['case_id']]
            or len(summary.get('runs', [])) != 1
            or Path(summary.get('source_path', '')).resolve() != Path(contract['scenario']['path']).resolve()):
        raise ValueError('M4 child summary differs from its exact one-case request')
    result = summary['runs'][0]
    for key in ('run_id', 'case_id', 'seed'):
        if result.get(key) != planned[key]:
            raise ValueError('M4 child result identity differs: ' + key)
    if result.get('case_key') != planned['resolved_scenario']['case_key']:
        raise ValueError('M4 child scenario key differs')
    directory = Path(result.get('run_directory') or '').resolve()
    root = Path(contract['execution']['runs_root']).resolve()
    if (directory.parent.parent != root or directory.name != planned['run_id']
            or runner.find_run_directory(root, planned['run_id']).resolve() != directory):
        raise ValueError('M4 child run directory differs from exact reserved dated path')
    metadata = _read_yaml(directory / 'metadata.yaml')
    completeness = json.loads((directory / 'completeness.json').read_text())
    recording = metadata.get('recording', {})
    if (result.get('recording_complete') is not True or completeness.get('passed') is not True
            or result.get('classification', {}).get('infrastructure_status') != 'completed'
            or recording.get('status') != 'finalized'
            or recording.get('infrastructure_status') != 'completed'
            or any(recording.get(key) is not True for key in ('complete', 'final_zero_observed',
                'target_clean_shutdown', 'bag_clean_shutdown', 'completeness_passed', 'readiness_ever_true'))
            or any(recording.get(key) for key in ('run_error', 'cleanup_errors',
                'pre_ready_nonzero_topics', 'pre_ready_lifecycle_violations', 'failure_stage'))):
        raise ValueError('M4 recording or final-zero integrity failed')
    outcomes = result.get('outcomes', {})
    states, events = outcomes.get('observed_state_sequence'), outcomes.get('observed_events')
    if (not isinstance(states, list) or not states or not isinstance(events, list)
            or 'FAILSAFE' in states or 'RECENTER' in states or 'FAILSAFE' in events):
        raise ValueError('M4 safety state/event evidence is absent or failed')
    cleanup = result.get('cleanup', {})
    inner = result.get('record_process', {})
    if (cleanup.get('passed') is not True or cleanup.get('strict') is not True
            or cleanup.get('inspection_errors')
            or inner.get('timed_out') or inner.get('return_code') not in (0, 1)
            or not isinstance(inner.get('session_id'), int)
            or inner.get('process_ownership', {}).get('inspection_complete') is not True):
        raise ValueError('M4 strict inner recorder/owned-session cleanup failed')
    validate_process_ownership(contract, inner)
    if (_read_yaml(directory / 'resolved_scenario.yaml') != planned['resolved_scenario']
            or result.get('launch_argv') != metadata.get('target_argv')
            or _read_yaml(directory / 'scenario_result.yaml') != result):
        raise ValueError('M4 actual launch/scenario/summary witnesses disagree')
    validate_launch_binding(planned, result, directory)
    return result, directory


def _save_case(path, row):
    atomic_exclusive_json(path, row)
    return {**row, 'receipt': receipt(path)}


def _validate_retained_rows(contract, rows, block):
    """Check callback receipts without relabelling the original acquisitions."""
    if not isinstance(rows, list) or len(rows) != 4:
        raise ValueError('M4 retained development requires four original acquisitions')
    if (not isinstance(block, dict) or block.get('block') != 0
            or block.get('complete') is not True or block.get('integrity_passed') is not True):
        raise ValueError('M4 retained development cached block is incomplete')
    reference = block.get('receipt', {})
    if receipt(reference['path']) != reference:
        raise ValueError('M4 retained development block receipt changed')
    if json.loads(Path(reference['path']).read_text()) != {k: v for k, v in block.items() if k != 'receipt'}:
        raise ValueError('M4 retained development block differs from its receipt')
    for planned, row in zip(contract['runs'][:4], rows):
        if (not isinstance(row, dict) or row.get('status') != 'COMPLETE'
                or row.get('integrity_passed') is not True
                or any(row.get(key) != planned[key] for key in (
                    'slot', 'block', 'run_id', 'case_id', 'seed', 'arm', 'partition',
                    'geometry', 'condition', 'visible', 'experiment_version'))):
            raise ValueError('M4 retained development acquisition identity or integrity differs')
        source = row.get('receipt', {})
        if receipt(source['path']) != source:
            raise ValueError('M4 retained development acquisition receipt changed')
        if json.loads(Path(source['path']).read_text()) != {k: v for k, v in row.items() if k != 'receipt'}:
            raise ValueError('M4 retained development row differs from original acquisition')
    if block.get('cases') != [row['receipt'] for row in rows]:
        raise ValueError('M4 retained development block acquisition receipts differ')


def dispatch(contract_path, *, verify_frozen, analyze_block, release_holdouts, finalize,
             bind_recorded=None, retained_development=None):
    """Run once, retain every outcome, and never replace an attempted slot."""
    contract_path = Path(contract_path).resolve()
    contract = json.loads(contract_path.read_text())
    root = validate_contract(contract)
    if Path(contract.get('contract_path', '')).resolve() != contract_path:
        raise ValueError('M4 contract self-path differs')
    if os.environ.get('ROS_DOMAIN_ID') != str(contract['execution']['ros_domain_id']):
        raise ValueError('M4 ROS domain differs from frozen graph')
    verify_frozen(contract)
    ownership = ({'process_ownership_mode': experiment_identity(contract['version'])['process_ownership_mode']}
                 if contract['version'] != DEFAULT_EXPERIMENT_VERSION else {})
    output = root / 'acquisition'
    output.mkdir(parents=True, exist_ok=False)
    if any((root/'runs').glob('*/*')):
        raise ValueError('M4 exclusive runs root already contains acquisitions')
    contract_ref = receipt(contract_path)
    started = time.monotonic()
    suite_budget = contract['execution']['suite_timeout_sec']
    suite_end = started + suite_budget
    atomic_exclusive_json(output/'started.json', dict(status='INCOMPLETE', contract=contract_ref,
        started_monotonic=started, suite_deadline=suite_end))
    rows, block_results, release, failure = [], [], None, None
    retained = is_retained_development_experiment_version(contract['version'])
    retained_references = []
    remaining_science = contract['execution']['science_budget_sec']
    try:
        if retained:
            if not callable(retained_development):
                raise ValueError('M4 V14 requires authenticated retained development')
            original_rows, cached_block = retained_development(contract, suite_end)
            _validate_retained_rows(contract, original_rows, cached_block)
            if time.monotonic() >= suite_end:
                raise TimeoutError('M4 retained development exceeded suite deadline')
            verify_frozen(contract)
            if receipt(contract_path) != contract_ref:
                raise ValueError('M4 frozen contract bytes changed')
            rows = deepcopy(original_rows)
            block_results.append(deepcopy(cached_block))
            for row in rows:
                reference_path = output/f'slot_{row["slot"]}.json'
                atomic_exclusive_json(reference_path, dict(
                    experiment_version=contract['version'], comparison_slot=row['slot'],
                    acquisition_origin='retained_v13', source_row=deepcopy(row),
                    source_acquisition=deepcopy(row['receipt']),
                    reuse_receipt=deepcopy(cached_block['receipt'])))
                retained_references.append(receipt(reference_path))
            science = contract['science']
            remaining_science -= science['labels_sec']+2*science['references_sec']+science['summary_sec']
            release = release_holdouts(contract, rows[:4], cached_block, suite_end)
            if not isinstance(release, dict) or release.get('status') != 'RELEASED':
                raise ValueError('M4 holdout release was not issued')
        first_fresh = 4 if retained else 0
        for index, planned in enumerate(contract['runs'][first_fresh:], start=first_fresh):
            case_start = started if index == 0 else time.monotonic()
            case_end = case_start + 900.
            # Compare elapsed time with an exact reserved allowance. Subtracting
            # separately rounded absolute deadlines can reject the first fit.
            if case_start - started > suite_budget - ((16-index)*900. + remaining_science):
                raise TimeoutError('M4 remaining case/science envelopes do not fit suite deadline')
            if index >= 4 and release is None:
                raise ValueError('M4 holdout seal has no one-time development release')
            verify_frozen(contract)
            if receipt(contract_path) != contract_ref:
                raise ValueError('M4 frozen contract bytes changed')
            if Path(planned['summary_path']).exists() or list((root/'runs').glob('*/'+planned['run_id'])):
                raise ValueError('M4 reserved slot already has a summary or run')
            row = {key: deepcopy(value) for key, value in planned.items()
                   if key in ('slot', 'block', 'run_id', 'case_id', 'seed', 'arm', 'partition',
                              'geometry', 'condition', 'visible', 'experiment_version')}
            row.update(status='INCOMPLETE', integrity_passed=False,
                       dispatch_attempted=False, started_monotonic=case_start, case_deadline=case_end)
            outer = None
            try:
                # Establish shared discovery outside the subsequently owned
                # child tree; the existing inner helper then reuses it.
                runner.ensure_ros_daemon()
                baseline = runner.ros_graph_nodes(strict=True, absolute_deadline=case_end-30.)
                command = [*planned['runner_argv'], '--cleanup-deadline', str(case_end-30.)]
                row['dispatch_attempted'] = True
                outer = runner.run_record_process(command, 900., 45.,
                    absolute_deadline=case_end-30., strict_process_tracking=True, **ownership)
                stdout = outer.pop('stdout')
                with (output/f'runner_{planned["slot"]}.log').open('x') as stream:
                    stream.write(stdout)
                row['outer_process'] = outer
                outer_cleanup = runner.cleanup_evidence(baseline, outer['session_id'],
                    settle_sec=30., strict=True, absolute_deadline=case_end,
                    process_ownership=outer.get('process_ownership'), **ownership)
                row['outer_cleanup'] = outer_cleanup
                validate_process_ownership(contract, outer)
                if outer_cleanup.get('passed') is not True:
                    raise ValueError('M4 outer observed process/session cleanup failed')
                result, directory = validate_case_result(contract, planned, outer)
                inner = result['record_process']
                inner_cleanup = runner.cleanup_evidence(baseline, inner['session_id'],
                    settle_sec=max(0., case_end-time.monotonic()), strict=True,
                    absolute_deadline=case_end, process_ownership=inner['process_ownership'], **ownership)
                row['independent_inner_cleanup'] = inner_cleanup
                if inner_cleanup.get('passed') is not True:
                    raise ValueError('M4 independently inspected inner session cleanup failed')
                verify_frozen(contract)
                if bind_recorded is None:
                    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import m4_recorded_binding
                    binding = m4_recorded_binding(directory, source_files=contract['source_files'],
                        expected_cost_configuration=(planned.get('expected_cost_configuration')
                            if planned['condition'] == 'noise' else None))
                else:
                    binding = bind_recorded(directory, source_files=contract['source_files'],
                        expected_cost_configuration=(planned.get('expected_cost_configuration')
                            if planned['condition'] == 'noise' else None))
                files = [directory/name for name in ('metadata.yaml', 'resolved_topics.yaml',
                    'resolved_scenario.yaml', 'resolved_parameters.yaml', 'scenario_result.yaml',
                    'completeness.json', 'bag/metadata.yaml')]
                files.extend(sorted((directory/'bag').glob('*.db3')))
                row.update(status='COMPLETE', integrity_passed=True, runner_result=result,
                    behavior_passed=result['classification']['passed'], run_directory=str(directory),
                    binding=binding, input_files=[receipt(path) for path in files])
                if time.monotonic() > case_end:
                    raise TimeoutError('M4 case inclusive deadline exceeded during evidence checks')
            except (Exception, KeyboardInterrupt) as error:
                row.update(status='INCOMPLETE', integrity_passed=False,
                           failure=f'{type(error).__name__}: {error}')
                if hasattr(error, 'execution_deadline_audit'):
                    row['execution_deadline_audit'] = error.execution_deadline_audit
                raise
            finally:
                row['completed_monotonic'] = time.monotonic()
                rows.append(_save_case(output/f'slot_{planned["slot"]}.json', row))
            if (index+1) % 4 == 0:
                block = index // 4
                result = analyze_block(contract, block, rows[-4:], suite_end)
                block_results.append(result)
                science = contract['science']
                remaining_science -= science['labels_sec']+2*science['references_sec']+science['summary_sec']
                if result.get('complete') is not True or result.get('integrity_passed') is not True:
                    raise ValueError('M4 block analysis outcome ledger integrity failed')
                verify_frozen(contract)
                if block == 0:
                    release = release_holdouts(contract, rows[:4], result, suite_end)
                    if not isinstance(release, dict) or release.get('status') != 'RELEASED':
                        raise ValueError('M4 holdout release was not issued')
    except (Exception, KeyboardInterrupt) as error:
        failure = f'{type(error).__name__}: {error}'
    for planned in contract['runs'][len(rows):]:
        row = {key: deepcopy(value) for key, value in planned.items()
               if key in ('slot', 'block', 'run_id', 'case_id', 'seed', 'arm', 'partition',
                          'geometry', 'condition', 'visible', 'experiment_version')}
        row.update(status=('RETAINED_UNAVAILABLE' if retained and planned['slot'] <= 4
                           else 'UNSTARTED'), integrity_passed=False, reason=failure)
        rows.append(_save_case(output/f'slot_{planned["slot"]}.json', row))
    final = None
    try:
        if time.monotonic() >= suite_end:
            raise TimeoutError('M4 suite deadline exhausted before final receipt')
        final = finalize(contract, rows, suite_end)
    except (Exception, KeyboardInterrupt) as error:
        failure = failure or f'{type(error).__name__}: {error}'
    result = dict(status='COMPLETE' if failure is None else 'INCOMPLETE', failure=failure,
        contract=contract_ref, slots=rows, analysis_blocks=block_results,
        holdout_release=release, final=final, suite_deadline=suite_end,
        elapsed_wall_sec=time.monotonic()-started, replacements_dispatched=False)
    if retained:
        result['retained_development_references'] = retained_references
    if result['elapsed_wall_sec'] > contract['execution']['suite_timeout_sec']:
        result.update(status='INCOMPLETE', failure='M4 inclusive suite deadline exceeded')
    atomic_exclusive_json(output/'acquisition.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', type=Path, required=True)
    arguments = parser.parse_args()
    from m4_workflow import (
        verify_dispatch_release, verify_frozen, analyze_block, release_holdouts, finalize,
    )
    import m4_workflow as workflow
    verify_dispatch_release(arguments.contract)
    result = dispatch(arguments.contract, verify_frozen=verify_frozen,
        analyze_block=analyze_block, release_holdouts=release_holdouts, finalize=finalize,
        retained_development=getattr(workflow, 'load_retained_development', None))
    print(json.dumps({key: result[key] for key in ('status', 'failure', 'elapsed_wall_sec')}))
    return 0 if result['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
