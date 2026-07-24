#!/usr/bin/env python3

"""Execute the frozen Phase 08 robustness-validation workflow."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

import numpy as np

from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import analyze_run

import yaml

from .run_scenario import execute_suite
from .scenario_schema import expand_suite, load_suite


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
SCENARIO_ROOT = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios'
)
VALIDATION_ROOT = REPOSITORY_ROOT / 'docs/codex/gesc_gaussian/validation'
CANDIDATES_PATH = SCENARIO_ROOT / 'phase08_parameter_candidates.yaml'
TRAINING_PATH = SCENARIO_ROOT / 'phase08_training.yaml'
HOLDOUT_PATH = SCENARIO_ROOT / 'phase08_holdout.yaml'
FULL_MATRIX_PATH = SCENARIO_ROOT / 'phase08_full_matrix.yaml'
FROZEN_PATH = SCENARIO_ROOT / 'phase08_frozen_parameters.yaml'
DIAGNOSTIC_CASES = {
    'diagnostic_recorded_smoke',
    'diagnostic_legacy_ordered_levels',
    'diagnostic_gaussian_ablation',
    'diagnostic_affine_ablation',
    'diagnostic_recenter_ablation',
}
EXPECTED_COUNTS = {
    'training_per_candidate': 9,
    'training_total': 81,
    'holdout': 12,
    'full': 519,
    'required': 483,
}
FACTOR_NAMES = (
    'gaussian_fill_covariance_scale',
    'gaussian_fill_amplitude_depth_scale',
    'gaussian_fill_exit_sigma',
    'stall_window_sec',
    'minimum_radial_progress_m',
)
FUNCTIONAL_TESTS = (
    'test_simulation_disturbances.py',
    'test_phase08_validation.py',
    'test_bag_analysis.py',
    'test_bag_analysis_integration.py',
    'test_scenario_schema.py',
    'test_scenario_runner.py',
    'test_experiment_recording.py',
    'test_recording_integration.py',
    'test_state_machine.py',
    'test_supervisor_integration.py',
    'test_observability_contract.py',
    'test_legacy_behavior.py',
    'test_robust_gaussian_algorithm.py',
    'test_escape_recenter.py',
)


def _sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def file_sha256(path):
    """Return the SHA-256 of one file."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value):
    """Hash a JSON-compatible value with deterministic serialization."""
    payload = json.dumps(
        value, sort_keys=True, separators=(',', ':'), allow_nan=False,
    ).encode('utf-8')
    return _sha256_bytes(payload)


def atomic_json(path, value):
    """Atomically write JSON without accepting NaN values."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.tmp-{os.getpid()}')
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
        encoding='utf-8',
    )
    os.replace(temporary, path)


def atomic_yaml(path, value):
    """Atomically write one YAML document."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.tmp-{os.getpid()}')
    temporary.write_text(
        yaml.safe_dump(value, sort_keys=False),
        encoding='utf-8',
    )
    os.replace(temporary, path)


def load_candidates(path=CANDIDATES_PATH):
    """Strictly load the declared nine-candidate grid."""
    document = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if set(document) != {
        'schema_version', 'candidate_set_id', 'selection_order', 'candidates'
    }:
        raise ValueError('candidate document has unknown or missing keys')
    if document['schema_version'] != 1:
        raise ValueError('candidate schema_version must equal 1')
    candidates = document['candidates']
    if not isinstance(candidates, list) or len(candidates) != 9:
        raise ValueError('exactly nine candidates are required')
    expected_ids = [f'C{index}' for index in range(9)]
    if [item.get('candidate_id') for item in candidates] != expected_ids:
        raise ValueError('candidate IDs must be ordered C0 through C8')
    for item in candidates:
        if set(item) != {'candidate_id', 'launch_overrides'}:
            raise ValueError('candidate has unknown or missing keys')
        if set(item['launch_overrides']) != set(FACTOR_NAMES):
            raise ValueError('candidate must define exactly five factors')
        for name, value in item['launch_overrides'].items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f'{item["candidate_id"]}.{name} is not numeric')
            if not math.isfinite(float(value)):
                raise ValueError(f'{item["candidate_id"]}.{name} is not finite')
    return document


def suite_counts():
    """Return the audited expansion counts for every Phase 08 suite."""
    training, training_unsupported = expand_suite(load_suite(TRAINING_PATH))
    holdout, holdout_unsupported = expand_suite(load_suite(HOLDOUT_PATH))
    full, full_unsupported = expand_suite(load_suite(FULL_MATRIX_PATH))
    required = [
        run for run in full if run['case_id'] not in DIAGNOSTIC_CASES
    ]
    return {
        'training_per_candidate': len(training),
        'training_total': len(training) * len(load_candidates()['candidates']),
        'holdout': len(holdout),
        'full': len(full),
        'required': len(required),
        'unsupported': (
            len(training_unsupported)
            + len(holdout_unsupported)
            + len(full_unsupported)
        ),
    }


def validate_suite_counts():
    """Refuse execution if the checked-in matrix arithmetic drifts."""
    counts = suite_counts()
    expected = {**EXPECTED_COUNTS, 'unsupported': 0}
    if counts != expected:
        raise ValueError(f'Phase 08 suite counts drifted: {counts} != {expected}')
    return counts


def _git(*arguments):
    return subprocess.run(
        ['git', *arguments],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def repository_snapshot(require_clean=False):
    """Capture the commit/tree and immutable input hashes."""
    status = _git('status', '--porcelain')
    if require_clean and status:
        raise RuntimeError('the frozen checkout must be clean')
    paths = [
        CANDIDATES_PATH,
        TRAINING_PATH,
        HOLDOUT_PATH,
        FULL_MATRIX_PATH,
        REPOSITORY_ROOT
        / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml',
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py',
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/'
        'gesc_gaussian_bag_analysis.py',
    ]
    if FROZEN_PATH.exists():
        paths.append(FROZEN_PATH)
    return {
        'commit': _git('rev-parse', 'HEAD'),
        'tree': _git('rev-parse', 'HEAD^{tree}'),
        'clean': not bool(status),
        'input_hashes': {
            str(path.relative_to(REPOSITORY_ROOT)): file_sha256(path)
            for path in paths
        },
    }


def _state_root(evidence_root):
    return Path(evidence_root).expanduser().resolve() / 'workflow_state'


def _load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _materialize_suite(source_path, profile, destination):
    document = yaml.safe_load(Path(source_path).read_text(encoding='utf-8'))
    overrides = dict(profile['launch_overrides'])
    document['frozen_profile'] = {
        'profile_id': profile['profile_id'],
        'launch_overrides': overrides,
        'sha256': canonical_sha256(overrides),
    }
    destination = Path(destination)
    destination.write_text(
        yaml.safe_dump(document, sort_keys=False),
        encoding='utf-8',
    )
    return destination


def _metric(summary, name):
    return summary.get('metrics', {}).get(name, {
        'value': None,
        'status': 'unavailable',
        'reason': 'metric absent',
    })


def _analyze_scenario_summary(summary):
    records = []
    for run in summary['runs']:
        run_directory = run.get('run_directory')
        analysis = None
        error = None
        if run_directory:
            output = Path(run_directory) / 'analysis' / 'phase08'
            try:
                if output.exists():
                    analysis = _load_json(output / 'summary_metrics.json')
                else:
                    analysis = analyze_run(
                        run_directory, output_directory=output,
                    )
            except Exception as exc:
                error = f'{type(exc).__name__}: {exc}'
        records.append({
            'run_id': run.get('run_id'),
            'run_directory': run_directory,
            'case_id': run.get('case_id'),
            'family': None,
            'profile': run.get('profile'),
            'recording_complete': run.get('recording_complete', False),
            'cleanup': run.get('cleanup', {}),
            'classification': run.get('classification', {}),
            'record_process': run.get('record_process', {}),
            'outcomes': run.get('outcomes', {}),
            'analysis_error': error,
            'analysis': analysis,
        })
        if run_directory:
            resolved = yaml.safe_load(
                (Path(run_directory) / 'resolved_scenario.yaml').read_text(
                    encoding='utf-8'
                )
            )
            records[-1]['family'] = resolved['family']
            records[-1]['case_key'] = resolved['case_key']
    return records


def _execute_stage(source_path, profile, operator, stage_root):
    stage_root = Path(stage_root)
    stage_root.mkdir(parents=True, exist_ok=True)
    summary_path = stage_root / 'scenario_summary.yaml'
    if summary_path.exists():
        summary = yaml.safe_load(summary_path.read_text(encoding='utf-8'))
    else:
        with tempfile.TemporaryDirectory(prefix='phase08_suite_') as directory:
            materialized = _materialize_suite(
                source_path, profile, Path(directory) / Path(source_path).name,
            )
            summary = execute_suite(
                materialized,
                operator,
                runs_root=stage_root / 'runs',
                summary_output=summary_path,
            )
    records_path = stage_root / 'records.json'
    if records_path.exists():
        records = _load_json(records_path)
    else:
        records = _analyze_scenario_summary(summary)
        atomic_json(records_path, records)
    return summary, records


def _valid_value(record, name):
    item = _metric(record.get('analysis') or {}, name)
    return item['value'] if item.get('status') == 'valid' else None


def _percentile(values, percentile):
    if not values:
        return None
    return float(np.percentile(np.asarray(values, dtype=float), percentile))


def candidate_metrics(candidate_id, records):
    """Calculate the declared lexicographic training metrics."""
    eligible = True
    reasons = []
    family_totals = Counter()
    family_successes = Counter()
    e2e = 0
    escape_attempts = 0
    escape_successes = 0
    escape_times = []
    orbits = []
    revisits = []
    convergence = []
    paths = []
    for record in records:
        analysis = record.get('analysis') or {}
        collision = _metric(analysis, 'collision')
        infrastructure = (
            record.get('recording_complete')
            and record.get('cleanup', {}).get('passed')
            and not record.get('record_process', {}).get('timed_out')
            and analysis.get('analysis_status') == 'complete'
            and collision.get('status') == 'valid'
            and collision.get('value') is False
        )
        if not infrastructure:
            eligible = False
            reasons.append(record.get('run_id') or record.get('case_id'))
        controller = _valid_value(record, 'controller_success')
        ground = _valid_value(record, 'simulation_ground_truth_success')
        success = controller is True and ground is True
        family_totals[record['family']] += 1
        family_successes[record['family']] += int(success)
        e2e += int(success)
        escape_attempts += int(_valid_value(record, 'escape_attempt_count') or 0)
        escape_successes += int(_valid_value(record, 'escape_success_count') or 0)
        for name, destination in (
            ('escape_time', escape_times),
            ('approximate_orbit_count', orbits),
            ('revisit_count', revisits),
            ('convergence_time', convergence),
            ('path_length', paths),
        ):
            value = _valid_value(record, name)
            if isinstance(value, (int, float)):
                destination.append(float(value))
    total = len(records)
    family_rates = {
        family: family_successes[family] / count
        for family, count in sorted(family_totals.items())
    }
    return {
        'candidate_id': candidate_id,
        'eligible': eligible and total == EXPECTED_COUNTS['training_per_candidate'],
        'ineligible_run_ids': sorted(set(reasons)),
        'run_count': total,
        'end_to_end_success_rate': e2e / total if total else 0.0,
        'local_escape_success_rate': (
            escape_successes / escape_attempts if escape_attempts else 0.0
        ),
        'escape_attempt_count': escape_attempts,
        'minimum_family_goal_success_rate': (
            min(family_rates.values()) if family_rates else 0.0
        ),
        'family_goal_success_rates': family_rates,
        'escape_time_p95_sec': _percentile(escape_times, 95),
        'escape_time_median_sec': (
            statistics.median(escape_times) if escape_times else None
        ),
        'orbit_count_median': statistics.median(orbits) if orbits else None,
        'revisit_rate': (
            sum(value > 0 for value in revisits) / len(revisits)
            if revisits else 0.0
        ),
        'convergence_time_median_sec': (
            statistics.median(convergence) if convergence else None
        ),
        'path_length_median_m': (
            statistics.median(paths) if paths else None
        ),
    }


def _ascending(value):
    return float('inf') if value is None else float(value)


def selection_key(metrics):
    """Return the authoritative lexicographic selection key."""
    return (
        -metrics['end_to_end_success_rate'],
        -metrics['local_escape_success_rate'],
        -metrics['minimum_family_goal_success_rate'],
        _ascending(metrics['escape_time_p95_sec']),
        _ascending(metrics['escape_time_median_sec']),
        _ascending(metrics['orbit_count_median']),
        _ascending(metrics['revisit_rate']),
        _ascending(metrics['convergence_time_median_sec']),
        _ascending(metrics['path_length_median_m']),
        metrics['candidate_id'],
    )


def select_candidate(metrics):
    """Select one eligible candidate, or return no winner."""
    eligible = [item for item in metrics if item['eligible']]
    return min(eligible, key=selection_key) if eligible else None


def _run_functional_tests():
    test_root = REPOSITORY_ROOT / 'ros2_ws/src/ros_esc/test'
    command = [
        sys.executable, '-m', 'pytest', '-q', '-rs',
        *[str(test_root / name) for name in FUNCTIONAL_TESTS],
    ]
    result = subprocess.run(
        command,
        cwd=REPOSITORY_ROOT / 'ros2_ws',
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        'command': command,
        'return_code': result.returncode,
        'passed': result.returncode == 0,
        'output_tail': result.stdout[-12000:],
    }


def run_sweep(operator, evidence_root):
    """Run or resume all nine candidates over the fixed training subset."""
    counts = validate_suite_counts()
    candidates = load_candidates()
    state_root = _state_root(evidence_root)
    state_root.mkdir(parents=True, exist_ok=True)
    progress_path = state_root / 'sweep_progress.json'
    progress = _load_json(progress_path) if progress_path.exists() else {
        'schema_version': 1,
        'stage': 'sweep',
        'counts': counts,
        'repository': repository_snapshot(),
        'functional_tests': _run_functional_tests(),
        'candidates': [],
    }
    completed = {
        item['candidate_id'] for item in progress['candidates']
    }
    for candidate in candidates['candidates']:
        candidate_id = candidate['candidate_id']
        if candidate_id in completed:
            continue
        profile = {
            'profile_id': f'phase08-training-{candidate_id}',
            'launch_overrides': candidate['launch_overrides'],
        }
        summary, records = _execute_stage(
            TRAINING_PATH,
            profile,
            operator,
            Path(evidence_root) / 'sweep' / candidate_id,
        )
        item = {
            'candidate_id': candidate_id,
            'launch_overrides': candidate['launch_overrides'],
            'scenario_summary_path': summary.get('summary_path'),
            'metrics': candidate_metrics(candidate_id, records),
        }
        progress['candidates'].append(item)
        atomic_json(progress_path, progress)
        if summary.get('stopped_early_reason') == 'cleanup_failure':
            raise RuntimeError(f'{candidate_id} stopped on cleanup contamination')
    metrics = [item['metrics'] for item in progress['candidates']]
    winner = select_candidate(metrics)
    result = {
        **progress,
        'completed': len(progress['candidates']) == 9,
        'selected_candidate_id': (
            winner['candidate_id'] if winner is not None else None
        ),
        'level_c_no_eligible_candidate': winner is None,
    }
    atomic_json(state_root / 'sweep.json', result)
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    atomic_json(
        VALIDATION_ROOT / 'phase_08_parameter_selection.json',
        result,
    )
    return result


def run_freeze(evidence_root):
    """Write the selected profile without changing any launch default."""
    sweep_path = _state_root(evidence_root) / 'sweep.json'
    if not sweep_path.exists():
        raise RuntimeError('sweep must complete before freeze')
    sweep = _load_json(sweep_path)
    selected_id = sweep.get('selected_candidate_id')
    if not selected_id:
        raise RuntimeError('no eligible training candidate; freeze is forbidden')
    candidate = next(
        item for item in load_candidates()['candidates']
        if item['candidate_id'] == selected_id
    )
    overrides = candidate['launch_overrides']
    document = {
        'schema_version': 1,
        'profile_id': 'robust_gaussian_v1_phase08_frozen',
        'selected_candidate_id': selected_id,
        'selection_source': str(
            (VALIDATION_ROOT / 'phase_08_parameter_selection.json').relative_to(
                REPOSITORY_ROOT
            )
        ),
        'launch_overrides': overrides,
        'sha256': canonical_sha256(overrides),
    }
    atomic_yaml(FROZEN_PATH, document)
    state = {
        'schema_version': 1,
        'stage': 'freeze_pending_commit',
        'frozen_profile': document,
        'repository_before_freeze_commit': repository_snapshot(),
    }
    atomic_json(_state_root(evidence_root) / 'freeze_pending.json', state)
    return state


def _load_frozen_profile():
    if not FROZEN_PATH.exists():
        raise RuntimeError('frozen parameter file is missing')
    document = yaml.safe_load(FROZEN_PATH.read_text(encoding='utf-8'))
    if document.get('sha256') != canonical_sha256(
        document.get('launch_overrides', {})
    ):
        raise RuntimeError('frozen parameter hash does not match its values')
    return {
        'profile_id': document['profile_id'],
        'launch_overrides': document['launch_overrides'],
    }, document


def _frozen_snapshot(evidence_root):
    state_path = _state_root(evidence_root) / 'frozen_snapshot.json'
    current = repository_snapshot(require_clean=True)
    profile, document = _load_frozen_profile()
    if state_path.exists():
        stored = _load_json(state_path)
        if stored['repository'] != current:
            raise RuntimeError('code, scenarios, parameters, or freeze commit changed')
    else:
        stored = {
            'schema_version': 1,
            'repository': current,
            'frozen_profile': document,
        }
        atomic_json(state_path, stored)
    return profile, stored


def run_holdout(operator, evidence_root):
    """Execute the holdout once after a clean committed freeze."""
    validate_suite_counts()
    profile, frozen = _frozen_snapshot(evidence_root)
    summary, records = _execute_stage(
        HOLDOUT_PATH, profile, operator, Path(evidence_root) / 'holdout',
    )
    result = {
        'schema_version': 1,
        'stage': 'holdout',
        'frozen_snapshot': frozen,
        'run_count': len(records),
        'scenario_summary_path': summary.get('summary_path'),
        'records_path': str(
            Path(evidence_root).expanduser().resolve()
            / 'holdout/records.json'
        ),
        'stopped_early_reason': summary.get('stopped_early_reason'),
    }
    atomic_json(_state_root(evidence_root) / 'holdout.json', result)
    return result


def run_full_pass(pass_index, operator, evidence_root):
    """Execute one unchanged 519-run pass."""
    if pass_index not in (1, 2, 3):
        raise ValueError('pass index must be 1, 2, or 3')
    holdout_path = _state_root(evidence_root) / 'holdout.json'
    if not holdout_path.exists():
        raise RuntimeError('holdout must run before the full matrix')
    for prior in range(1, pass_index):
        if not (_state_root(evidence_root) / f'pass_{prior}.json').exists():
            raise RuntimeError(f'full pass {prior} must run first')
    profile, frozen = _frozen_snapshot(evidence_root)
    summary, records = _execute_stage(
        FULL_MATRIX_PATH,
        profile,
        operator,
        Path(evidence_root) / f'full_pass_{pass_index}',
    )
    result = {
        'schema_version': 1,
        'stage': 'full_pass',
        'pass_index': pass_index,
        'frozen_snapshot': frozen,
        'run_count': len(records),
        'scenario_summary_path': summary.get('summary_path'),
        'records_path': str(
            Path(evidence_root).expanduser().resolve()
            / f'full_pass_{pass_index}/records.json'
        ),
        'stopped_early_reason': summary.get('stopped_early_reason'),
    }
    atomic_json(_state_root(evidence_root) / f'pass_{pass_index}.json', result)
    return result


def _gate(identifier, passed, value, threshold, reason=None):
    return {
        'gate': identifier,
        'passed': bool(passed),
        'value': value,
        'threshold': threshold,
        'reason': reason,
    }


def evaluate_gate_set(records, functional_passed=True):
    """Calculate all behavioral gates for one pass or a pooled set."""
    required = [
        record for record in records
        if record['case_id'] not in DIAGNOSTIC_CASES
    ]
    complete = [
        record for record in required
        if (
            record.get('recording_complete')
            and (record.get('analysis') or {}).get('analysis_status') == 'complete'
        )
    ]
    collision_ok = [
        record for record in required
        if (
            _metric(record.get('analysis') or {}, 'collision').get('status')
            == 'valid'
            and _metric(
                record.get('analysis') or {}, 'collision'
            ).get('value') is False
        )
    ]
    attempts = sum(
        int(_valid_value(record, 'escape_attempt_count') or 0)
        for record in required
    )
    successes = sum(
        int(_valid_value(record, 'escape_success_count') or 0)
        for record in required
    )
    e2e_by_family = defaultdict(list)
    escape_times = []
    orbits = []
    successful_fill_revisit = []
    normal = []
    coverage = []
    for record in required:
        e2e = (
            _valid_value(record, 'controller_success') is True
            and _valid_value(record, 'simulation_ground_truth_success') is True
        )
        e2e_by_family[record['family']].append(e2e)
        for name, target in (
            ('escape_time', escape_times),
            ('approximate_orbit_count', orbits),
        ):
            value = _valid_value(record, name)
            if isinstance(value, (int, float)):
                target.append(float(value))
        if e2e and (_valid_value(record, 'fill_count') or 0) > 0:
            revisit = _valid_value(record, 'revisit_count')
            if isinstance(revisit, (int, float)):
                successful_fill_revisit.append(float(revisit))
        terminal = _metric(record.get('analysis') or {}, 'terminal_state')
        timeout = _valid_value(record, 'timeout')
        normal.append(
            not record.get('record_process', {}).get('timed_out')
            and record.get('cleanup', {}).get('passed')
            and terminal.get('status') == 'valid'
            and timeout in (False, True)
        )
        if record['case_id'] in {
            'robust_pure_escape', 'robust_assisted_escape',
            'robust_fill_merge', 'robust_recenter',
        }:
            outcomes = record.get('outcomes', {})
            coverage.append(
                outcomes.get('required_state_sequence_passed', False)
                and outcomes.get('required_events_passed', False)
            )
    e2e_total = sum(sum(values) for values in e2e_by_family.values())
    family_rates = {
        family: sum(values) / len(values)
        for family, values in sorted(e2e_by_family.items())
    }
    escape_rate = successes / attempts if attempts else None
    e2e_rate = e2e_total / len(required) if required else None
    median_escape = statistics.median(escape_times) if escape_times else None
    p95_escape = _percentile(escape_times, 95)
    median_orbits = statistics.median(orbits) if orbits else None
    revisit_rate = (
        sum(value > 0 for value in successful_fill_revisit)
        / len(successful_fill_revisit)
        if successful_fill_revisit else None
    )
    gates = [
        _gate('1_functional', functional_passed, functional_passed, 'all pass'),
        _gate(
            '2_completeness',
            len(complete) == len(required) and bool(required),
            f'{len(complete)}/{len(required)}',
            'all required runs',
        ),
        _gate(
            '3_collision',
            len(collision_ok) == len(required) and bool(required),
            f'{len(collision_ok)}/{len(required)}',
            'valid and zero collisions',
        ),
        _gate(
            '4_local_escape',
            escape_rate is not None
            and escape_rate >= 0.95
            and all(coverage),
            escape_rate,
            '>= 0.95 and designated coverage',
            None if attempts else 'no valid escape attempts',
        ),
        _gate('5_end_to_end', e2e_rate is not None and e2e_rate >= 0.90,
              e2e_rate, '>= 0.90'),
        _gate(
            '6_family_minimum',
            bool(family_rates) and min(family_rates.values()) >= 0.80,
            family_rates,
            'every family >= 0.80',
        ),
        _gate('7_median_escape_time',
              median_escape is not None and median_escape <= 20.0,
              median_escape, '<= 20 s'),
        _gate('8_p95_escape_time',
              p95_escape is not None and p95_escape <= 45.0,
              p95_escape, '<= 45 s'),
        _gate('9_median_orbit_count',
              median_orbits is not None and median_orbits <= 1.5,
              median_orbits, '<= 1.5'),
        _gate('10_normal_termination',
              len(normal) == len(required) and all(normal),
              f'{sum(normal)}/{len(required)}', 'all required runs'),
        _gate('11_revisit_rate',
              revisit_rate is not None and revisit_rate < 0.05,
              revisit_rate, '< 0.05',
              None if successful_fill_revisit
              else 'no valid successful goal runs with fills'),
    ]
    return {
        'required_run_count': len(required),
        'diagnostic_run_count': len(records) - len(required),
        'escape_attempt_count': attempts,
        'escape_success_count': successes,
        'family_goal_success_rates': family_rates,
        'gates': gates,
        'passed': all(gate['passed'] for gate in gates),
    }


def run_report(evidence_root):
    """Generate machine-readable and Markdown acceptance evidence."""
    state_root = _state_root(evidence_root)
    pass_states = []
    pass_records = []
    for index in (1, 2, 3):
        state_path = state_root / f'pass_{index}.json'
        if not state_path.exists():
            raise RuntimeError(f'full pass {index} has not completed')
        state = _load_json(state_path)
        pass_states.append(state)
        pass_records.append(_load_json(state['records_path']))
    sweep = _load_json(state_root / 'sweep.json')
    functional_passed = sweep['functional_tests']['passed']
    per_pass = [
        evaluate_gate_set(records, functional_passed)
        for records in pass_records
    ]
    pooled = evaluate_gate_set(
        [record for records in pass_records for record in records],
        functional_passed,
    )
    same_freeze = all(
        state['frozen_snapshot'] == pass_states[0]['frozen_snapshot']
        for state in pass_states[1:]
    )
    pass_counts = [state['run_count'] for state in pass_states]
    gate12 = _gate(
        '12_three_unchanged_passes',
        same_freeze
        and pass_counts == [EXPECTED_COUNTS['full']] * 3
        and all(item['passed'] for item in per_pass),
        {'same_freeze': same_freeze, 'run_counts': pass_counts},
        'three passing 519-run passes with identical frozen snapshot',
    )
    overall = all(item['passed'] for item in per_pass) and gate12['passed']
    results = {
        'schema_version': 1,
        'simulation_ready': overall,
        'per_pass': {
            str(index): result
            for index, result in enumerate(per_pass, start=1)
        },
        'pooled': pooled,
        'gate_12': gate12,
    }
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    atomic_json(VALIDATION_ROOT / 'phase_08_gate_results.json', results)
    manifest = {
        'schema_version': 1,
        'evidence_root': str(Path(evidence_root).expanduser().resolve()),
        'frozen_snapshot': pass_states[0]['frozen_snapshot'],
        'stages': {
            'sweep': str(state_root / 'sweep.json'),
            'holdout': str(state_root / 'holdout.json'),
            'passes': [
                str(state_root / f'pass_{index}.json')
                for index in (1, 2, 3)
            ],
        },
        'counts': {
            'training': EXPECTED_COUNTS['training_total'],
            'holdout': EXPECTED_COUNTS['holdout'],
            'full_passes': sum(pass_counts),
        },
    }
    atomic_json(VALIDATION_ROOT / 'phase_08_run_manifest.json', manifest)
    lines = [
        '# Phase 08 Simulation Validation Report',
        '',
        f'Outcome: **{"PASS" if overall else "FAIL"}**.',
        '',
        f'Frozen commit: `{pass_states[0]["frozen_snapshot"]["repository"]["commit"]}`.',
        '',
    ]
    for index, result in enumerate(per_pass, start=1):
        lines.extend([
            f'## Pass {index}',
            '',
            f'Required runs: {result["required_run_count"]}; '
            f'diagnostics: {result["diagnostic_run_count"]}.',
            '',
        ])
        for gate in result['gates']:
            lines.append(
                f'- `{gate["gate"]}`: '
                f'{"PASS" if gate["passed"] else "FAIL"}; '
                f'value `{gate["value"]}`; threshold `{gate["threshold"]}`.'
            )
        lines.append('')
    lines.extend([
        '## Freeze consistency',
        '',
        f'- `12_three_unchanged_passes`: '
        f'{"PASS" if gate12["passed"] else "FAIL"}.',
        '',
        'No physical hardware was run.',
        '',
    ])
    report_path = VALIDATION_ROOT / 'phase_08_validation_report.md'
    report_path.write_text('\n'.join(lines), encoding='utf-8')
    if not overall:
        failure = [
            '# Phase 08 Failure Report',
            '',
            'The frozen matrix missed one or more acceptance gates. '
            'No simulation-ready tag is permitted.',
            '',
            '## Smallest justified next engineering phase',
            '',
            'Create a bounded Phase 08.1 diagnosis phase using only the '
            'retained failed-family evidence. Do not retune or reinterpret '
            'the frozen Phase 08 matrix, and do not begin physical Phase 09.',
            '',
        ]
        (VALIDATION_ROOT / 'phase_08_failure_report.md').write_text(
            '\n'.join(failure), encoding='utf-8'
        )
    return results


def _parser():
    parser = argparse.ArgumentParser(
        description='Execute and verify the frozen Phase 08 workflow.',
    )
    subparsers = parser.add_subparsers(dest='subcommand', required=True)
    for name in ('sweep', 'holdout', 'report'):
        subparser = subparsers.add_parser(name)
        subparser.add_argument('--operator', required=True)
        subparser.add_argument('--evidence-root', required=True)
    freeze = subparsers.add_parser('freeze')
    freeze.add_argument('--operator', required=True)
    freeze.add_argument('--evidence-root', required=True)
    full = subparsers.add_parser('full-pass')
    full.add_argument('--pass-index', type=int, required=True)
    full.add_argument('--operator', required=True)
    full.add_argument('--evidence-root', required=True)
    return parser


def main(argv=None):
    """CLI entry point."""
    arguments = _parser().parse_args(argv)
    try:
        if arguments.subcommand == 'sweep':
            result = run_sweep(arguments.operator, arguments.evidence_root)
        elif arguments.subcommand == 'freeze':
            result = run_freeze(arguments.evidence_root)
        elif arguments.subcommand == 'holdout':
            result = run_holdout(
                arguments.operator, arguments.evidence_root,
            )
        elif arguments.subcommand == 'full-pass':
            result = run_full_pass(
                arguments.pass_index,
                arguments.operator,
                arguments.evidence_root,
            )
        else:
            result = run_report(arguments.evidence_root)
    except Exception as exc:
        print(
            f'validate_robustness: {type(exc).__name__}: {exc}',
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    if (
        arguments.subcommand == 'sweep'
        and result.get('level_c_no_eligible_candidate')
    ):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
