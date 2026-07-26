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
V2_ACTIVATION_PATH = SCENARIO_ROOT / 'phase08_v2_activation.yaml'
V2_TRAINING_PATH = SCENARIO_ROOT / 'phase08_v2_training.yaml'
V2_HOLDOUT_PATH = SCENARIO_ROOT / 'phase08_v2_holdout.yaml'
V2_VALIDATION_PATH = SCENARIO_ROOT / 'phase08_v2_validation.yaml'
V2_REPRODUCIBILITY_PATH = (
    SCENARIO_ROOT / 'phase08_v2_reproducibility.yaml'
)
V2_FROZEN_PATH = SCENARIO_ROOT / 'phase08_v2_frozen_parameters.yaml'
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
V2_CANDIDATES = (
    {
        'candidate_id': 'V2-C0',
        'launch_overrides': {
            'gaussian_fill_covariance_scale': 2.5,
            'gaussian_fill_amplitude_depth_scale': 1.5,
            'gaussian_fill_exit_sigma': 2.5,
            'stall_window_sec': 3.0,
            'minimum_radial_progress_m': 0.05,
        },
    },
    {
        'candidate_id': 'V2-C1',
        'launch_overrides': {
            'gaussian_fill_covariance_scale': 2.0,
            'gaussian_fill_amplitude_depth_scale': 1.2,
            'gaussian_fill_exit_sigma': 2.25,
            'stall_window_sec': 4.0,
            'minimum_radial_progress_m': 0.03,
        },
    },
    {
        'candidate_id': 'V2-C2',
        'launch_overrides': {
            'gaussian_fill_covariance_scale': 3.0,
            'gaussian_fill_amplitude_depth_scale': 1.8,
            'gaussian_fill_exit_sigma': 2.75,
            'stall_window_sec': 2.0,
            'minimum_radial_progress_m': 0.08,
        },
    },
)
V2_EXPECTED_COUNTS = {
    'activation': 10,
    'training_per_candidate': 10,
    'training_total': 30,
    'holdout': 20,
    'validation': 50,
    'unique': 70,
    'reproducibility': 10,
    'total': 120,
}
V2_EXPECTED_ALLOCATION = {
    'holdout': {
        'ordered_two_source': 7,
        'multi_close_overlap': 3,
        'wall_corner': 2,
        'noise_delay': 2,
        'saturation_safe_failure': 2,
        'lifecycle': 4,
    },
    'validation': {
        'ordered_two_source': 18,
        'multi_close_overlap': 6,
        'wall_corner': 6,
        'noise_delay': 6,
        'saturation_safe_failure': 6,
        'lifecycle': 8,
    },
    'reproducibility': {
        'ordered_two_source': 2,
        'multi_close_overlap': 2,
        'wall_corner': 1,
        'noise_delay': 1,
        'saturation_safe_failure': 1,
        'lifecycle': 3,
    },
}
V2_REPEAT_REFERENCES = {
    'repeat_ordered_01': 'h_ordered_01',
    'repeat_ordered_02': 'v_ordered_08',
    'repeat_multi_01': 'h_multi_01',
    'repeat_multi_02': 'v_multi_04',
    'repeat_wall_01': 'h_wall_01',
    'repeat_noise_01': 'v_noise_04',
    'repeat_saturation_01': 'v_saturation_03',
    'repeat_lifecycle_01': 'h_lifecycle_01',
    'repeat_lifecycle_02': 'v_lifecycle_04',
    'repeat_lifecycle_03': 'v_lifecycle_08',
}
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


def v2_allocation_bucket(family):
    """Map one scenario family to the amended six-family allocation."""
    if family == 'two_source':
        return 'ordered_two_source'
    if family in {'multi_source', 'close_minimum', 'separation_overlap'}:
        return 'multi_close_overlap'
    if family == 'boundary':
        return 'wall_corner'
    if family == 'noise_delay':
        return 'noise_delay'
    if family == 'starts_saturation':
        return 'saturation_safe_failure'
    if family in {'escape', 'fill_merge', 'recenter_resume'}:
        return 'lifecycle'
    raise ValueError(f'family is outside the v2 allocation: {family}')


def v2_suite_counts():
    """Validate the exact 120-run v2 arithmetic and family allocation."""
    suites = {
        'activation': V2_ACTIVATION_PATH,
        'training': V2_TRAINING_PATH,
        'holdout': V2_HOLDOUT_PATH,
        'validation': V2_VALIDATION_PATH,
        'reproducibility': V2_REPRODUCIBILITY_PATH,
    }
    expanded = {}
    unsupported = {}
    for stage, path in suites.items():
        expanded[stage], unsupported[stage] = expand_suite(load_suite(path))
    counts = {
        'activation': len(expanded['activation']),
        'training_per_candidate': len(expanded['training']),
        'training_total': (
            len(expanded['training']) * len(V2_CANDIDATES)
        ),
        'holdout': len(expanded['holdout']),
        'validation': len(expanded['validation']),
        'unique': len(expanded['holdout']) + len(expanded['validation']),
        'reproducibility': len(expanded['reproducibility']),
    }
    counts['total'] = (
        counts['activation']
        + counts['training_total']
        + counts['holdout']
        + counts['validation']
        + counts['reproducibility']
    )
    if counts != V2_EXPECTED_COUNTS:
        raise ValueError(f'Phase 08 v2 counts drifted: {counts}')
    if any(unsupported.values()):
        raise ValueError(f'Phase 08 v2 contains unsupported cases: {unsupported}')

    unique_case_ids = [
        run['case_id']
        for stage in ('holdout', 'validation')
        for run in expanded[stage]
    ]
    if len(set(unique_case_ids)) != V2_EXPECTED_COUNTS['unique']:
        raise ValueError('v2 holdout and validation case IDs must be unique')
    for stage in ('holdout', 'validation', 'reproducibility'):
        allocation = Counter(
            v2_allocation_bucket(run['family'])
            for run in expanded[stage]
        )
        if dict(allocation) != V2_EXPECTED_ALLOCATION[stage]:
            raise ValueError(
                f'Phase 08 v2 {stage} allocation drifted: {dict(allocation)}'
            )
    repeat_ids = {run['case_id'] for run in expanded['reproducibility']}
    if repeat_ids != set(V2_REPEAT_REFERENCES):
        raise ValueError('v2 reproducibility reference IDs drifted')
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


def candidate_metrics(
    candidate_id,
    records,
    expected_count=EXPECTED_COUNTS['training_per_candidate'],
):
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
            and record.get('classification', {}).get('passed')
            and analysis.get('analysis_status') == 'complete'
            and collision.get('status') == 'valid'
            and collision.get('value') is False
        )
        if not infrastructure:
            eligible = False
            reasons.append(record.get('run_id') or record.get('case_id'))
        outcomes = record.get('outcomes', {})
        if not (
            outcomes.get('required_state_sequence_passed', False)
            and outcomes.get('required_events_passed', False)
            and outcomes.get('forbidden_events_absent', False)
        ):
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
        'eligible': eligible and total == expected_count,
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


def evaluate_gate_set(records, functional_passed=True, family_mapper=None):
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
        family = (
            family_mapper(record['family'])
            if family_mapper is not None else record['family']
        )
        e2e_by_family[family].append(e2e)
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
        if record['family'] in {
            'escape', 'fill_merge', 'recenter_resume',
        }:
            outcomes = record.get('outcomes', {})
            coverage.append(
                outcomes.get('required_state_sequence_passed', False)
                and outcomes.get('required_events_passed', False)
                and outcomes.get('forbidden_events_absent', False)
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


def _v2_manifest_document(evidence_root):
    paths = {
        'activation': V2_ACTIVATION_PATH,
        'training': V2_TRAINING_PATH,
        'holdout': V2_HOLDOUT_PATH,
        'validation': V2_VALIDATION_PATH,
        'reproducibility': V2_REPRODUCIBILITY_PATH,
    }
    stages = {}
    for stage, path in paths.items():
        runs, unsupported = expand_suite(load_suite(path))
        if unsupported:
            raise ValueError(f'{stage} contains unsupported cases')
        stages[stage] = {
            'scenario_path': str(path.relative_to(REPOSITORY_ROOT)),
            'scenario_sha256': file_sha256(path),
            'runs': [
                {
                    'case_id': run['case_id'],
                    'case_key': run['case_key'],
                    'family': run['family'],
                    'seed': run['seed'],
                    'start': run['start'],
                    'sources': run['sources'],
                    'disturbances': run['disturbances'],
                    'validation': run['validation'],
                }
                for run in runs
            ],
        }
    return {
        'schema_version': 2,
        'workflow': 'phase08_staged_validation_v2',
        'evidence_root': str(Path(evidence_root).expanduser().resolve()),
        'historical_v1_evidence_excluded': True,
        'counts': v2_suite_counts(),
        'candidates': list(V2_CANDIDATES),
        'candidate_sha256': canonical_sha256(V2_CANDIDATES),
        'stage_order': [
            'activation',
            'sweep',
            'freeze_commit',
            'holdout',
            'validation',
            'reproducibility',
            'report',
        ],
        'stages': stages,
    }


def _ensure_v2_workflow(evidence_root):
    root = Path(evidence_root).expanduser().resolve()
    state_root = _state_root(root)
    state_root.mkdir(parents=True, exist_ok=True)
    legacy_markers = (
        'sweep_progress.json',
        'sweep.json',
        'freeze_pending.json',
        'frozen_snapshot.json',
        'pass_1.json',
        'pass_2.json',
        'pass_3.json',
    )
    marker = state_root / 'v2_workflow.json'
    if not marker.exists() and any(
        (state_root / name).exists() for name in legacy_markers
    ):
        raise RuntimeError('v1 and v2 evidence roots must not be mixed')

    current = _v2_manifest_document(root)
    immutable_sha = canonical_sha256(current)
    if marker.exists():
        stored = _load_json(marker)
        if stored.get('schema_version') != 2:
            raise RuntimeError('v2 workflow marker has the wrong schema')
        if stored.get('manifest_sha256') != immutable_sha:
            raise RuntimeError('sealed v2 scenario identities or hashes changed')
    else:
        stored = {
            'schema_version': 2,
            'manifest_sha256': immutable_sha,
            'manifest': current,
        }
        atomic_json(marker, stored)
        VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
        durable = VALIDATION_ROOT / 'phase_08_v2_run_manifest.json'
        if durable.exists() and _load_json(durable) != stored:
            raise RuntimeError('durable v2 manifest already has different content')
        atomic_json(durable, stored)
    return root, stored


def _v2_state(evidence_root, name):
    return _state_root(evidence_root) / f'v2_{name}.json'


def _v2_record_integrity(record):
    analysis = record.get('analysis') or {}
    collision = _metric(analysis, 'collision')
    outcomes = record.get('outcomes', {})
    return (
        record.get('recording_complete') is True
        and record.get('cleanup', {}).get('passed') is True
        and not record.get('record_process', {}).get('timed_out', False)
        and analysis.get('analysis_status') == 'complete'
        and collision.get('status') == 'valid'
        and collision.get('value') is False
        and record.get('classification', {}).get('passed') is True
        and outcomes.get('required_state_sequence_passed') is True
        and outcomes.get('required_events_passed') is True
        and outcomes.get('forbidden_events_absent') is True
    )


def _v2_failure(stage, reasons, evidence_root):
    result = {
        'schema_version': 2,
        'stage': stage,
        'passed': False,
        'level_c': True,
        'reasons': list(reasons),
        'evidence_root': str(Path(evidence_root).expanduser().resolve()),
        'later_stages_forbidden': True,
        'simulation_ready_tag_permitted': False,
    }
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    lines = [
        '# Phase 08 v2 Failure Report',
        '',
        f'Stopped after `{stage}`. No later empirical stage was authorized.',
        '',
        '## Observed reasons',
        '',
        *[f'- {reason}' for reason in reasons],
        '',
        '## Smallest justified next engineering phase',
        '',
        'Open a bounded Phase 08.1 diagnosis against the retained failed-stage '
        'bags and resolved scenarios. Do not retune, weaken gates, resume '
        'historical v1 evidence, begin physical Phase 09, or create the '
        'simulation-ready tag.',
        '',
        'No physical hardware was run.',
        '',
    ]
    (
        VALIDATION_ROOT / 'phase_08_v2_failure_report.md'
    ).write_text('\n'.join(lines), encoding='utf-8')
    atomic_json(_v2_state(evidence_root, 'failure'), result)
    return result


def _v2_require_pass(evidence_root, stage):
    path = _v2_state(evidence_root, stage)
    if not path.exists():
        raise RuntimeError(f'v2 {stage} must complete first')
    state = _load_json(path)
    if not state.get('passed'):
        raise RuntimeError(f'v2 {stage} failed; later stages are forbidden')
    return state


def run_v2_activation(operator, evidence_root):
    """Execute and evaluate the mandatory ten-run activation gate."""
    root, workflow = _ensure_v2_workflow(evidence_root)
    if _v2_state(root, 'sweep').exists():
        raise RuntimeError('activation cannot run after tuning has started')
    profile = {
        'profile_id': 'phase08-v2-activation-contract',
        'launch_overrides': {},
    }
    summary, records = _execute_stage(
        V2_ACTIVATION_PATH, profile, operator, root / 'activation',
    )
    integrity = [_v2_record_integrity(record) for record in records]
    fills = sum(
        int(_valid_value(record, 'fill_count') or 0) for record in records
    )
    attempts = sum(
        int(_valid_value(record, 'escape_attempt_count') or 0)
        for record in records
    )
    functional = _run_functional_tests()
    reasons = []
    if len(records) != V2_EXPECTED_COUNTS['activation']:
        reasons.append(f'activation run count is {len(records)}, expected 10')
    if not all(integrity):
        reasons.append(
            'one or more activation runs missed integrity or lifecycle coverage'
        )
    if fills <= 0:
        reasons.append('activation produced zero typed fills')
    if attempts <= 0:
        reasons.append('activation produced zero observed escape attempts')
    if not functional['passed']:
        reasons.append('retained functional suite failed')
    result = {
        'schema_version': 2,
        'stage': 'activation',
        'passed': not reasons,
        'workflow_manifest_sha256': workflow['manifest_sha256'],
        'run_count': len(records),
        'integrity_pass_count': sum(integrity),
        'fill_count': fills,
        'escape_attempt_count': attempts,
        'functional_tests': functional,
        'scenario_summary_path': summary.get('summary_path'),
        'records_path': str(root / 'activation/records.json'),
        'reasons': reasons,
    }
    atomic_json(_v2_state(root, 'activation'), result)
    if reasons:
        _v2_failure('activation', reasons, root)
    return result


def run_v2_sweep(operator, evidence_root):
    """Execute three candidates over the same ten selection-only cases."""
    root, workflow = _ensure_v2_workflow(evidence_root)
    activation = _v2_require_pass(root, 'activation')
    if _v2_state(root, 'holdout').exists():
        raise RuntimeError('tuning cannot run after holdout')
    progress_path = _v2_state(root, 'sweep_progress')
    progress = _load_json(progress_path) if progress_path.exists() else {
        'schema_version': 2,
        'stage': 'sweep',
        'workflow_manifest_sha256': workflow['manifest_sha256'],
        'activation_state_sha256': canonical_sha256(activation),
        'candidates': [],
    }
    completed = {
        item['candidate_id'] for item in progress['candidates']
    }
    for candidate in V2_CANDIDATES:
        candidate_id = candidate['candidate_id']
        if candidate_id in completed:
            continue
        profile = {
            'profile_id': f'phase08-v2-training-{candidate_id}',
            'launch_overrides': candidate['launch_overrides'],
        }
        summary, records = _execute_stage(
            V2_TRAINING_PATH,
            profile,
            operator,
            root / 'sweep' / candidate_id,
        )
        metrics = candidate_metrics(
            candidate_id,
            records,
            expected_count=V2_EXPECTED_COUNTS['training_per_candidate'],
        )
        progress['candidates'].append({
            'candidate_id': candidate_id,
            'launch_overrides': candidate['launch_overrides'],
            'scenario_summary_path': summary.get('summary_path'),
            'records_path': str(root / 'sweep' / candidate_id / 'records.json'),
            'metrics': metrics,
        })
        atomic_json(progress_path, progress)
        if summary.get('stopped_early_reason') == 'cleanup_failure':
            raise RuntimeError(f'{candidate_id} stopped on cleanup contamination')
    metrics = [item['metrics'] for item in progress['candidates']]
    winner = select_candidate(metrics)
    total_e2e = sum(
        item['end_to_end_success_rate'] * item['run_count']
        for item in metrics
    )
    total_attempts = sum(item['escape_attempt_count'] for item in metrics)
    reasons = []
    if len(progress['candidates']) != len(V2_CANDIDATES):
        reasons.append('not all three candidates completed')
    if winner is None:
        reasons.append('no candidate met the eligibility contract')
    if total_e2e <= 0:
        reasons.append('all candidates had zero end-to-end success')
    if total_attempts <= 0:
        reasons.append('all candidates had zero escape activation')
    result = {
        **progress,
        'passed': not reasons,
        'selected_candidate_id': (
            winner['candidate_id'] if winner is not None else None
        ),
        'selection_key': (
            list(selection_key(winner)) if winner is not None else None
        ),
        'reasons': reasons,
    }
    atomic_json(_v2_state(root, 'sweep'), result)
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    atomic_json(
        VALIDATION_ROOT / 'phase_08_v2_parameter_selection.json',
        result,
    )
    if reasons:
        _v2_failure('sweep', reasons, root)
    return result


def run_v2_freeze(evidence_root):
    """Generate the selected v2 parameter file pending a dedicated commit."""
    root, workflow = _ensure_v2_workflow(evidence_root)
    sweep = _v2_require_pass(root, 'sweep')
    if _v2_state(root, 'holdout').exists():
        raise RuntimeError('freeze cannot change after holdout')
    selected_id = sweep['selected_candidate_id']
    candidate = next(
        item for item in V2_CANDIDATES
        if item['candidate_id'] == selected_id
    )
    overrides = dict(candidate['launch_overrides'])
    document = {
        'schema_version': 2,
        'profile_id': 'robust_gaussian_v1_phase08_v2_frozen',
        'selected_candidate_id': selected_id,
        'selection_source': (
            'docs/codex/gesc_gaussian/validation/'
            'phase_08_v2_parameter_selection.json'
        ),
        'workflow_manifest_sha256': workflow['manifest_sha256'],
        'launch_overrides': overrides,
        'sha256': canonical_sha256(overrides),
    }
    atomic_yaml(V2_FROZEN_PATH, document)
    result = {
        'schema_version': 2,
        'stage': 'freeze_pending_commit',
        'passed': True,
        'frozen_profile': document,
        'frozen_file_sha256': file_sha256(V2_FROZEN_PATH),
        'repository_before_freeze_commit': repository_snapshot(),
    }
    atomic_json(_v2_state(root, 'freeze_pending'), result)
    return result


def _load_v2_frozen_profile():
    if not V2_FROZEN_PATH.exists():
        raise RuntimeError('v2 frozen parameter file is missing')
    document = yaml.safe_load(V2_FROZEN_PATH.read_text(encoding='utf-8'))
    if document.get('schema_version') != 2:
        raise RuntimeError('v2 frozen parameter schema is invalid')
    overrides = document.get('launch_overrides', {})
    if set(overrides) != set(FACTOR_NAMES):
        raise RuntimeError('v2 frozen profile does not contain five factors')
    if document.get('sha256') != canonical_sha256(overrides):
        raise RuntimeError('v2 frozen parameter hash does not match values')
    return {
        'profile_id': document['profile_id'],
        'launch_overrides': overrides,
    }, document


def _v2_repository_snapshot(require_clean=False):
    status = _git('status', '--porcelain')
    if require_clean and status:
        raise RuntimeError('the v2 frozen checkout must be clean')
    paths = [
        V2_ACTIVATION_PATH,
        V2_TRAINING_PATH,
        V2_HOLDOUT_PATH,
        V2_VALIDATION_PATH,
        V2_REPRODUCIBILITY_PATH,
        V2_FROZEN_PATH,
        Path(__file__),
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py',
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py',
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/'
        'gesc_gaussian_bag_analysis.py',
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py',
        REPOSITORY_ROOT
        / 'ros2_ws/src/ros_esc/ros_esc/supervisor_node/'
        'supervisor_node_script.py',
        REPOSITORY_ROOT
        / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml',
    ]
    return {
        'commit': _git('rev-parse', 'HEAD'),
        'tree': _git('rev-parse', 'HEAD^{tree}'),
        'clean': not bool(status),
        'input_hashes': {
            str(path.relative_to(REPOSITORY_ROOT)): file_sha256(path)
            for path in paths
        },
    }


def _v2_frozen_snapshot(evidence_root):
    root, workflow = _ensure_v2_workflow(evidence_root)
    _v2_require_pass(root, 'sweep')
    profile, frozen = _load_v2_frozen_profile()
    current = _v2_repository_snapshot(require_clean=True)
    path = _v2_state(root, 'freeze_snapshot')
    candidate = {
        'schema_version': 2,
        'workflow_manifest_sha256': workflow['manifest_sha256'],
        'repository': current,
        'frozen_profile': frozen,
        'frozen_file_sha256': file_sha256(V2_FROZEN_PATH),
    }
    if path.exists():
        stored = _load_json(path)
        if stored != candidate:
            raise RuntimeError(
                'code, scenarios, parameters, or freeze commit changed'
            )
    else:
        stored = candidate
        atomic_json(path, stored)
    return profile, stored


def _record_expected_failsafe(record):
    run_directory = record.get('run_directory')
    if not run_directory:
        return False
    resolved = yaml.safe_load(
        (Path(run_directory) / 'resolved_scenario.yaml').read_text(
            encoding='utf-8'
        )
    )
    expected = resolved['success']['controller']['expected_terminal_state']
    return str(expected).removeprefix('STATE_') == 'FAILSAFE'


def _v2_holdout_evaluation(records):
    integrity = [_v2_record_integrity(record) for record in records]
    successes = sum(
        _valid_value(record, 'controller_success') is True
        and _valid_value(
            record, 'simulation_ground_truth_success'
        ) is True
        for record in records
    )
    unexplained_failsafe = [
        record['run_id']
        for record in records
        if _valid_value(record, 'failsafe') is True
        and not _record_expected_failsafe(record)
    ]
    reasons = []
    if len(records) != V2_EXPECTED_COUNTS['holdout']:
        reasons.append(f'holdout run count is {len(records)}, expected 20')
    if not all(integrity):
        reasons.append('holdout integrity or lifecycle coverage was incomplete')
    if successes < 18:
        reasons.append(f'holdout end-to-end success was {successes}/20')
    if unexplained_failsafe:
        reasons.append('holdout contained unexplained failsafe outcomes')
    return {
        'passed': not reasons,
        'run_count': len(records),
        'integrity_pass_count': sum(integrity),
        'end_to_end_success_count': successes,
        'unexplained_failsafe_run_ids': unexplained_failsafe,
        'reasons': reasons,
    }


def run_v2_holdout(operator, evidence_root):
    """Execute the sealed holdout once from the committed clean freeze."""
    root, _ = _ensure_v2_workflow(evidence_root)
    profile, frozen = _v2_frozen_snapshot(root)
    if _v2_state(root, 'validation').exists():
        raise RuntimeError('holdout cannot run after validation')
    summary, records = _execute_stage(
        V2_HOLDOUT_PATH, profile, operator, root / 'holdout',
    )
    evaluation = _v2_holdout_evaluation(records)
    result = {
        'schema_version': 2,
        'stage': 'holdout',
        **evaluation,
        'frozen_snapshot': frozen,
        'scenario_summary_path': summary.get('summary_path'),
        'records_path': str(root / 'holdout/records.json'),
    }
    atomic_json(_v2_state(root, 'holdout'), result)
    if not result['passed']:
        _v2_failure('holdout', result['reasons'], root)
    return result


def wilson_interval(successes, total, confidence_z=1.959963984540054):
    """Return a two-sided Wilson score interval for one binomial rate."""
    if (
        isinstance(successes, bool)
        or isinstance(total, bool)
        or not isinstance(successes, int)
        or not isinstance(total, int)
        or total <= 0
        or successes < 0
        or successes > total
    ):
        raise ValueError('Wilson inputs require 0 <= successes <= total')
    rate = successes / total
    z2 = confidence_z ** 2
    denominator = 1.0 + z2 / total
    center = (rate + z2 / (2.0 * total)) / denominator
    radius = (
        confidence_z
        * math.sqrt(
            rate * (1.0 - rate) / total + z2 / (4.0 * total ** 2)
        )
        / denominator
    )
    return {
        'successes': successes,
        'total': total,
        'rate': rate,
        'lower': max(0.0, center - radius),
        'upper': min(1.0, center + radius),
        'confidence': 0.95,
        'method': 'two-sided Wilson score',
    }


def _v2_confidence_intervals(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[v2_allocation_bucket(record['family'])].append(record)

    def interval(items):
        successes = sum(
            _valid_value(record, 'controller_success') is True
            and _valid_value(
                record, 'simulation_ground_truth_success'
            ) is True
            for record in items
        )
        return wilson_interval(successes, len(items))

    return {
        'overall': interval(records),
        'by_family': {
            family: interval(items)
            for family, items in sorted(grouped.items())
        },
    }


def run_v2_validation(operator, evidence_root):
    """Execute 50 additional cases and evaluate the 70 unique denominator."""
    root, _ = _ensure_v2_workflow(evidence_root)
    holdout = _v2_require_pass(root, 'holdout')
    profile, frozen = _v2_frozen_snapshot(root)
    if holdout['frozen_snapshot'] != frozen:
        raise RuntimeError('holdout and validation freeze snapshots differ')
    if _v2_state(root, 'reproducibility').exists():
        raise RuntimeError('validation cannot run after reproducibility')
    summary, records = _execute_stage(
        V2_VALIDATION_PATH, profile, operator, root / 'validation',
    )
    holdout_records = _load_json(holdout['records_path'])
    unique_records = holdout_records + records
    functional = _load_json(
        _v2_state(root, 'activation')
    )['functional_tests']['passed']
    gates = evaluate_gate_set(
        unique_records,
        functional,
        family_mapper=v2_allocation_bucket,
    )
    reasons = []
    if len(records) != V2_EXPECTED_COUNTS['validation']:
        reasons.append(f'validation run count is {len(records)}, expected 50')
    if len(unique_records) != V2_EXPECTED_COUNTS['unique']:
        reasons.append('unique denominator does not contain 70 records')
    if not gates['passed']:
        reasons.append('one or more 70-run unique acceptance gates failed')
    result = {
        'schema_version': 2,
        'stage': 'validation',
        'passed': not reasons,
        'frozen_snapshot': frozen,
        'run_count': len(records),
        'unique_run_count': len(unique_records),
        'scenario_summary_path': summary.get('summary_path'),
        'records_path': str(root / 'validation/records.json'),
        'unique_gate_evaluation': gates,
        'confidence_intervals': _v2_confidence_intervals(unique_records),
        'reasons': reasons,
    }
    atomic_json(_v2_state(root, 'validation'), result)
    if reasons:
        _v2_failure('validation', reasons, root)
    return result


def _resolved_projection(record):
    resolved = yaml.safe_load(
        (Path(record['run_directory']) / 'resolved_scenario.yaml').read_text(
            encoding='utf-8'
        )
    )
    return {
        name: resolved[name]
        for name in (
            'profile',
            'start',
            'sources',
            'bounds_m',
            'room_center_m',
            'disturbances',
            'validation',
            'frozen_profile',
            'algorithm',
            'success',
            'seed',
        )
    }


def _numeric_reproducible(reference, repeat, absolute, relative=0.10):
    reference_value = _valid_value(reference, reference['metric_name'])
    repeat_value = _valid_value(repeat, repeat['metric_name'])
    if reference_value is None or repeat_value is None:
        reference_metric = _metric(
            reference.get('analysis') or {}, reference['metric_name']
        )
        repeat_metric = _metric(
            repeat.get('analysis') or {}, repeat['metric_name']
        )
        return reference_metric.get('status') == repeat_metric.get('status')
    tolerance = max(absolute, abs(float(reference_value)) * relative)
    return abs(float(repeat_value) - float(reference_value)) <= tolerance


def _final_goal_distance(record):
    distances = record.get('outcomes', {}).get('final_goal_distances_m', {})
    return min(distances.values()) if distances else None


def evaluate_reproducibility(repeats, unique_records):
    """Compare ten repeats to their predeclared unique-run references."""
    references = {record['case_id']: record for record in unique_records}
    results = []
    for repeat in repeats:
        reference_id = V2_REPEAT_REFERENCES.get(repeat['case_id'])
        reference = references.get(reference_id)
        reasons = []
        if reference is None:
            reasons.append('reference record is missing')
        else:
            if _resolved_projection(reference) != _resolved_projection(repeat):
                reasons.append('resolved scenario dimensions differ')
            for name in (
                'controller_success', 'timeout', 'failsafe', 'collision',
            ):
                reference_metric = _metric(
                    reference.get('analysis') or {}, name
                )
                repeat_metric = _metric(
                    repeat.get('analysis') or {}, name
                )
                if (
                    reference_metric.get('status'),
                    reference_metric.get('value'),
                ) != (
                    repeat_metric.get('status'),
                    repeat_metric.get('value'),
                ):
                    reasons.append(f'{name} categorical outcome differs')
            for name, absolute, relative in (
                ('escape_time', 2.0, 0.10),
                ('convergence_time', 2.0, 0.10),
                ('path_length', 0.25, 0.10),
                ('approximate_orbit_count', 0.25, 0.0),
            ):
                reference_with_name = {**reference, 'metric_name': name}
                repeat_with_name = {**repeat, 'metric_name': name}
                if not _numeric_reproducible(
                    reference_with_name,
                    repeat_with_name,
                    absolute,
                    relative,
                ):
                    reasons.append(f'{name} exceeded tolerance')
            reference_distance = _final_goal_distance(reference)
            repeat_distance = _final_goal_distance(repeat)
            if (
                reference_distance is None
                or repeat_distance is None
                or abs(repeat_distance - reference_distance) > 0.10
            ):
                reasons.append('final goal distance exceeded tolerance')
            for name in (
                'required_state_sequence_passed',
                'required_events_passed',
                'forbidden_events_absent',
            ):
                if (
                    reference.get('outcomes', {}).get(name)
                    != repeat.get('outcomes', {}).get(name)
                ):
                    reasons.append(f'{name} differs')
        results.append({
            'repeat_case_id': repeat['case_id'],
            'reference_case_id': reference_id,
            'passed': not reasons,
            'reasons': reasons,
        })
    return {
        'passed': (
            len(results) == V2_EXPECTED_COUNTS['reproducibility']
            and all(item['passed'] for item in results)
        ),
        'repeat_count': len(results),
        'results': results,
    }


def run_v2_reproducibility(operator, evidence_root):
    """Execute ten repeats after all 70 unique-case gates pass."""
    root, _ = _ensure_v2_workflow(evidence_root)
    validation = _v2_require_pass(root, 'validation')
    profile, frozen = _v2_frozen_snapshot(root)
    if validation['frozen_snapshot'] != frozen:
        raise RuntimeError('validation and reproducibility freezes differ')
    summary, repeats = _execute_stage(
        V2_REPRODUCIBILITY_PATH,
        profile,
        operator,
        root / 'reproducibility',
    )
    holdout = _load_json(_v2_state(root, 'holdout'))
    unique_records = (
        _load_json(holdout['records_path'])
        + _load_json(validation['records_path'])
    )
    evaluation = evaluate_reproducibility(repeats, unique_records)
    reasons = []
    if not evaluation['passed']:
        reasons.append('one or more reproducibility comparisons failed')
    result = {
        'schema_version': 2,
        'stage': 'reproducibility',
        'passed': not reasons,
        'frozen_snapshot': frozen,
        'scenario_summary_path': summary.get('summary_path'),
        'records_path': str(root / 'reproducibility/records.json'),
        'evaluation': evaluation,
        'reasons': reasons,
    }
    atomic_json(_v2_state(root, 'reproducibility'), result)
    if reasons:
        _v2_failure('reproducibility', reasons, root)
    return result


def run_v2_report(evidence_root):
    """Write final v2 gate JSON and Markdown from retained stage evidence."""
    root, workflow = _ensure_v2_workflow(evidence_root)
    activation = _v2_require_pass(root, 'activation')
    holdout = _v2_require_pass(root, 'holdout')
    validation = _v2_require_pass(root, 'validation')
    reproducibility = _v2_require_pass(root, 'reproducibility')
    unique = validation['unique_gate_evaluation']
    by_identifier = {gate['gate']: gate for gate in unique['gates']}
    gates = [
        _gate(
            '1_functional',
            activation['functional_tests']['passed'],
            activation['functional_tests']['passed'],
            'all retained functional tests pass',
        ),
        _gate(
            '2_activation',
            activation['passed'],
            f'{activation["integrity_pass_count"]}/10',
            'all ten activation proofs',
        ),
        _gate(
            '3_holdout',
            holdout['passed'],
            f'{holdout["end_to_end_success_count"]}/20',
            'at least 18/20 with complete valid evidence',
        ),
        *[
            {
                **by_identifier[source],
                'gate': target,
            }
            for source, target in (
                ('2_completeness', '4_completeness'),
                ('3_collision', '5_collision'),
                ('4_local_escape', '6_local_escape'),
                ('5_end_to_end', '7_end_to_end'),
                ('6_family_minimum', '8_family_minimum'),
                ('7_median_escape_time', '9_median_escape_time'),
                ('8_p95_escape_time', '10_p95_escape_time'),
                ('9_median_orbit_count', '11_median_orbit_count'),
                ('10_normal_termination', '12_normal_termination'),
                ('11_revisit_rate', '13_revisit_rate'),
            )
        ],
        _gate(
            '14_reproducibility',
            reproducibility['evaluation']['passed'],
            (
                f"{sum(item['passed'] for item in reproducibility['evaluation']['results'])}"
                '/10'
            ),
            'all ten categorical and numeric comparisons',
        ),
    ]
    overall = all(gate['passed'] for gate in gates)
    results = {
        'schema_version': 2,
        'simulation_ready': overall,
        'workflow_manifest_sha256': workflow['manifest_sha256'],
        'frozen_snapshot': validation['frozen_snapshot'],
        'unique_run_count': validation['unique_run_count'],
        'confidence_intervals': validation['confidence_intervals'],
        'gates': gates,
    }
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    atomic_json(VALIDATION_ROOT / 'phase_08_v2_gate_results.json', results)
    lines = [
        '# Phase 08 v2 Simulation Validation Report',
        '',
        f'Outcome: **{"PASS" if overall else "FAIL"}**.',
        '',
        f'Frozen commit: `{validation["frozen_snapshot"]["repository"]["commit"]}`.',
        '',
        'The acceptance denominator contains 70 unique cases. Ten '
        'reproducibility repeats are reported separately.',
        '',
        '## Gates',
        '',
    ]
    for gate in gates:
        lines.append(
            f'- `{gate["gate"]}`: '
            f'{"PASS" if gate["passed"] else "FAIL"}; '
            f'value `{gate["value"]}`; threshold `{gate["threshold"]}`.'
        )
    intervals = validation['confidence_intervals']
    lines.extend([
        '',
        '## 95% Wilson score intervals',
        '',
        (
            f'- Overall: {intervals["overall"]["rate"]:.4f} '
            f'[{intervals["overall"]["lower"]:.4f}, '
            f'{intervals["overall"]["upper"]:.4f}].'
        ),
    ])
    for family, interval in intervals['by_family'].items():
        lines.append(
            f'- `{family}`: {interval["rate"]:.4f} '
            f'[{interval["lower"]:.4f}, {interval["upper"]:.4f}].'
        )
    lines.extend(['', 'No physical hardware was run.', ''])
    (
        VALIDATION_ROOT / 'phase_08_v2_validation_report.md'
    ).write_text('\n'.join(lines), encoding='utf-8')
    if not overall:
        _v2_failure(
            'report',
            ['one or more final v2 acceptance gates failed'],
            root,
        )
    return results


def _is_v2_invocation(subcommand, evidence_root):
    if subcommand in {'activation', 'validation', 'reproducibility'}:
        return True
    state_root = _state_root(evidence_root)
    if (state_root / 'v2_workflow.json').exists():
        return True
    return not any(
        (state_root / name).exists()
        for name in (
            'sweep_progress.json',
            'sweep.json',
            'frozen_snapshot.json',
            'pass_1.json',
        )
    )


def _parser():
    parser = argparse.ArgumentParser(
        description='Execute and verify the frozen Phase 08 workflow.',
    )
    subparsers = parser.add_subparsers(dest='subcommand', required=True)
    for name in (
        'activation',
        'sweep',
        'holdout',
        'validation',
        'reproducibility',
        'report',
    ):
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
        if arguments.subcommand == 'full-pass':
            raise RuntimeError(
                'the Phase 08 v1 full-pass workflow is retired and '
                'cannot be resumed'
            )
        else:
            v2 = _is_v2_invocation(
                arguments.subcommand, arguments.evidence_root
            )
            if v2:
                if arguments.subcommand == 'activation':
                    result = run_v2_activation(
                        arguments.operator, arguments.evidence_root
                    )
                elif arguments.subcommand == 'sweep':
                    result = run_v2_sweep(
                        arguments.operator, arguments.evidence_root
                    )
                elif arguments.subcommand == 'freeze':
                    result = run_v2_freeze(arguments.evidence_root)
                elif arguments.subcommand == 'holdout':
                    result = run_v2_holdout(
                        arguments.operator, arguments.evidence_root
                    )
                elif arguments.subcommand == 'validation':
                    result = run_v2_validation(
                        arguments.operator, arguments.evidence_root
                    )
                elif arguments.subcommand == 'reproducibility':
                    result = run_v2_reproducibility(
                        arguments.operator, arguments.evidence_root
                    )
                else:
                    result = run_v2_report(arguments.evidence_root)
            elif arguments.subcommand in {'sweep', 'freeze', 'holdout'}:
                raise RuntimeError(
                    'the Phase 08 v1 execution workflow is retired and '
                    'cannot be resumed'
                )
            elif arguments.subcommand == 'report':
                result = run_report(arguments.evidence_root)
            else:
                raise RuntimeError(
                    f'{arguments.subcommand} is available only in v2'
                )
    except Exception as exc:
        print(
            f'validate_robustness: {type(exc).__name__}: {exc}',
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    if result.get('passed') is False:
        return 1
    if result.get('level_c_no_eligible_candidate'):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
