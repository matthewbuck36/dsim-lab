#!/usr/bin/env python3

"""Execute the frozen Phase 08 robustness-validation workflow."""

import argparse
import base64
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import secrets
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile

import numpy as np

from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import analyze_run

import yaml

from . import scenario_schema
from .aggregate_field_truth import (
    attach_local_branch_qualifications,
    derive_aggregate_field_truth,
    validate_aggregate_field_truth,
)
from .run_scenario import build_launch_command, execute_suite
from .scenario_schema import (
    ACCEPTANCE_FAMILIES,
    deterministic_case_key,
    expand_suite,
    load_suite,
)


def _discover_repository_root():
    configured = os.environ.get('DSIM_LAB_REPOSITORY_ROOT')
    starts = [
        Path(configured).expanduser() if configured else None,
        Path.cwd(),
        Path(__file__).resolve(),
    ]
    checked = set()
    for start in starts:
        if start is None:
            continue
        base = start if start.is_dir() else start.parent
        for candidate in (base, *base.parents):
            resolved = candidate.resolve()
            if resolved in checked:
                continue
            checked.add(resolved)
            if (
                (resolved / 'AGENTS.md').is_file()
                and (
                    resolved
                    / 'ros2_ws/src/ros_esc/package.xml'
                ).is_file()
            ):
                return resolved
    return None


def _installed_package_share():
    try:
        from ament_index_python.packages import get_package_share_directory

        return Path(get_package_share_directory('ros_esc')).resolve()
    except (ImportError, LookupError):
        return None


DISCOVERED_REPOSITORY_ROOT = _discover_repository_root()
PACKAGE_SHARE_ROOT = _installed_package_share()
REPOSITORY_ROOT = (
    DISCOVERED_REPOSITORY_ROOT
    if DISCOVERED_REPOSITORY_ROOT is not None
    else Path.cwd().resolve()
)
SOURCE_SCENARIO_ROOT = (
    REPOSITORY_ROOT
    / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios'
)
PACKAGE_SCENARIO_ROOT = (
    PACKAGE_SHARE_ROOT / 'scenario_runner/scenarios'
    if PACKAGE_SHARE_ROOT is not None else None
)
SCENARIO_ROOT = (
    SOURCE_SCENARIO_ROOT
    if SOURCE_SCENARIO_ROOT.is_dir()
    else PACKAGE_SCENARIO_ROOT
)
if SCENARIO_ROOT is None:
    SCENARIO_ROOT = SOURCE_SCENARIO_ROOT
VALIDATION_ROOT = (
    REPOSITORY_ROOT / 'docs/codex/gesc_gaussian/validation'
)
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
V3_ACTIVATION_PATH = SCENARIO_ROOT / 'phase08_v3_activation.yaml'
V3_DEVELOPMENT_PATH = SCENARIO_ROOT / 'phase08_v3_development.yaml'
V3_CANDIDATES_PATH = SCENARIO_ROOT / 'phase08_v3_candidates.yaml'
V3_FROZEN_PATH = SCENARIO_ROOT / 'phase08_v3_frozen_parameters.yaml'
V3_PRECOMMITTED_SUITE_PATH = (
    SCENARIO_ROOT / 'phase08_v3_acceptance_suite.json'
)
V3_COMMITMENT_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_suite_commitment.json'
)
V3_SELECTION_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_parameter_selection.json'
)
V3_FREEZE_PATH = VALIDATION_ROOT / 'phase_08_v3_freeze_state.json'
V3_CONTRACT_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_acceptance_contract.json'
)
V3_GATE_RESULTS_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_gate_results.json'
)
V3_MANIFEST_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_run_manifest.json'
)
V3_REPORT_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_validation_report.md'
)
V3_FAILURE_PATH = (
    VALIDATION_ROOT / 'phase_08_v3_failure_report.md'
)
V3_CONTACT_CORRECTION_PATH = (
    VALIDATION_ROOT / 'phase_08_v3a_contact_probe_contamination.json'
)
V3_HARD_STOP_CORRECTION_PATH = (
    VALIDATION_ROOT
    / 'phase_08_v3b_diagnostic_completion.json'
)
V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT = (
    (
        'ros2_ws/src/ros_esc/ros_esc/scenario_runner/'
        'phase08_validation.py'
    ),
    (
        'ros2_ws/src/ros_esc/ros_esc/scenario_runner/'
        'run_scenario.py'
    ),
    'ros2_ws/src/ros_esc/test/test_phase08_validation.py',
    'ros2_ws/src/ros_esc/test/test_scenario_runner.py',
)
EMPIRICAL_SUBCOMMANDS = {
    'activation',
    'sweep',
    'holdout',
    'validation',
    'reproducibility',
    'v3-activation',
    'v3-development',
    'v3-holdout',
    'v3-validation',
    'v3-reproducibility',
}
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
V3_EXPECTED_COUNTS = {
    'activation': 10,
    'development_per_candidate': 10,
    'development_total': 30,
    'holdout': 20,
    'validation': 50,
    'unique': 70,
    'reproducibility': 10,
    'acceptance_total': 80,
    'declared_total': 120,
}
V3_FAMILY_ALLOCATION = {
    'ordered_two_source': {
        'holdout': 7,
        'validation': 18,
        'unique': 25,
        'reproducibility': 2,
        'escape_attempt': 8,
    },
    'multi_close_overlap': {
        'holdout': 3,
        'validation': 6,
        'unique': 9,
        'reproducibility': 2,
        'escape_attempt': 6,
    },
    'wall_corner': {
        'holdout': 2,
        'validation': 6,
        'unique': 8,
        'reproducibility': 1,
        'escape_attempt': 5,
    },
    'noise_delay': {
        'holdout': 2,
        'validation': 6,
        'unique': 8,
        'reproducibility': 1,
        'escape_attempt': 5,
    },
    'constraint_recovery': {
        'holdout': 2,
        'validation': 6,
        'unique': 8,
        'reproducibility': 1,
        'escape_attempt': 3,
    },
    'lifecycle': {
        'holdout': 4,
        'validation': 8,
        'unique': 12,
        'reproducibility': 3,
        'escape_attempt': 12,
    },
}
V3_FAMILY_FLOORS = {
    'ordered_two_source': 20,
    'multi_close_overlap': 8,
    'wall_corner': 7,
    'noise_delay': 7,
    'constraint_recovery': 7,
    'lifecycle': 10,
}
V3_HOLDOUT_FLOORS = {
    'ordered_two_source': 6,
    'multi_close_overlap': 3,
    'wall_corner': 2,
    'noise_delay': 2,
    'constraint_recovery': 2,
    'lifecycle': 4,
}
V3_REVISIT_COUNTS = {
    'ordered_two_source': 4,
    'multi_close_overlap': 4,
    'wall_corner': 3,
    'noise_delay': 3,
    'constraint_recovery': 2,
    'lifecycle': 8,
}
V3_ORDERED_ESCAPE_INDEXES = {
    3,
    4,
    8,
    9,
    15,
    16,
    20,
    21,
}
V3_REPLACEMENT_CAPS = {
    'activation': 1,
    'development': 3,
    'holdout': 1,
    'validation': 2,
    'reproducibility': 1,
    'total': 8,
}
V3_CANDIDATES = (
    {
        'candidate_id': 'V3-C0',
        'launch_overrides': {
            'gaussian_fill_covariance_scale': 2.5,
            'gaussian_fill_amplitude_depth_scale': 1.5,
            'gaussian_fill_exit_sigma': 2.5,
            'stall_window_sec': 3.0,
            'minimum_radial_progress_m': 0.05,
        },
    },
    {
        'candidate_id': 'V3-C1',
        'launch_overrides': {
            'gaussian_fill_covariance_scale': 2.0,
            'gaussian_fill_amplitude_depth_scale': 1.2,
            'gaussian_fill_exit_sigma': 2.25,
            'stall_window_sec': 4.0,
            'minimum_radial_progress_m': 0.03,
        },
    },
    {
        'candidate_id': 'V3-C2',
        'launch_overrides': {
            'gaussian_fill_covariance_scale': 3.0,
            'gaussian_fill_amplitude_depth_scale': 1.8,
            'gaussian_fill_exit_sigma': 2.75,
            'stall_window_sec': 2.0,
            'minimum_radial_progress_m': 0.08,
        },
    },
)
V3_COMMON_OVERRIDES = {
    'goal_score_threshold': 0.95,
    'goal_score_rotation_period_sec': 3.0,
    'goal_score_required_rotations': 2,
    'goal_hold_sec': 3.0,
    'undesired_score_hold_sec': 3.0,
    'verification_max_sec': 12.0,
    'fill_design_timeout_sec': 5.0,
    'escape_max_sec': 20.0,
    'escape_exit_hold_sec': 1.0,
    'recenter_max_sec': 30.0,
    'recenter_tolerance_m': 0.25,
    'recenter_hold_sec': 1.0,
    'direction_lookahead_m': 0.5,
    'direction_candidate_step_rad': math.pi / 4.0,
    'wall_margin_m': 0.35,
    'fill_avoidance_margin_m': 0.10,
    'approach_history_window_sec': 0.50,
}
FUNCTIONAL_TESTS = (
    'test_aggregate_field_truth.py',
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


def _utc_now():
    return datetime.now(timezone.utc)


def _utc_text(value):
    return value.isoformat().replace('+00:00', 'Z')


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


def _v3_directory_manifest(directory):
    """Hash every regular file below one retained evidence directory."""
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError(f'v3 retained directory is missing: {root}')
    input_hashes = {
        str(path.relative_to(root)): file_sha256(path)
        for path in sorted(root.rglob('*'))
        if path.is_file()
    }
    if not input_hashes:
        raise RuntimeError(f'v3 retained directory is empty: {root}')
    return {
        'root': str(root),
        'file_count': len(input_hashes),
        'input_hashes': input_hashes,
        'manifest_sha256': canonical_sha256(input_hashes),
    }


def _v3_verify_directory_manifest(manifest):
    """Recompute and compare a retained evidence-directory manifest."""
    if not isinstance(manifest, dict):
        raise RuntimeError('v3 retained directory manifest is malformed')
    input_hashes = manifest.get('input_hashes')
    if (
        not isinstance(input_hashes, dict)
        or manifest.get('file_count') != len(input_hashes)
        or manifest.get('manifest_sha256')
        != canonical_sha256(input_hashes)
    ):
        raise RuntimeError('v3 retained directory manifest hash drifted')
    observed = _v3_directory_manifest(manifest.get('root', ''))
    if observed != manifest:
        raise RuntimeError('v3 retained directory contents drifted')
    return observed


def omission_sha256(value, field):
    """Hash a mapping after omitting its self-identifying hash field."""
    payload = dict(value)
    payload.pop(field, None)
    return canonical_sha256(payload)


def require_omission_sha256(value, field, description):
    """Reject a self-identifying document whose omission hash drifted."""
    label = field.replace('_sha256', ' hash')
    recorded = value.get(field)
    if not isinstance(recorded, str) or not re.fullmatch(
        '[0-9a-f]{64}', recorded
    ):
        raise RuntimeError(
            f'{description} {label} is missing or malformed'
        )
    if omission_sha256(value, field) != recorded:
        raise RuntimeError(f'{description} {label} drifted')
    return recorded


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


def canonical_json_bytes(value):
    """Serialize one finite JSON document with the v3 envelope contract."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False,
        allow_nan=False,
    ).encode('utf-8')


def atomic_bytes(path, value, mode=None):
    """Atomically replace one byte artifact in its destination directory."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f'.{path.name}.tmp-{os.getpid()}')
    try:
        with temporary.open('xb') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def create_or_verify_bytes(path, value, mode=0o644):
    """Create one immutable artifact or verify its existing exact bytes."""
    path = Path(path)
    if path.exists():
        if path.read_bytes() != value:
            raise RuntimeError(f'create-once artifact drifted: {path}')
        return
    atomic_bytes(path, value, mode=mode)


def create_or_verify_json(path, value, mode=0o644):
    """Create or verify one immutable, pretty-printed JSON artifact."""
    payload = (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + '\n'
    ).encode('utf-8')
    create_or_verify_bytes(path, payload, mode=mode)


def create_or_verify_yaml(path, value, mode=0o644):
    """Create or verify one immutable YAML artifact."""
    payload = yaml.safe_dump(
        value,
        sort_keys=False,
    ).encode('utf-8')
    create_or_verify_bytes(path, payload, mode=mode)


def _v3_replacement_eligible(evidence):
    """Require every pre-readiness fact before replacing one invalid attempt."""
    required = {
        'classification': 'infrastructure_invalid',
        'readiness_ever_true': False,
        'nonzero_command_observed': False,
        'non_search_lifecycle_observed': False,
        'active_fill_or_escape_observed': False,
        'external_startup_cause': True,
        'cleanup_passed': True,
        'classification_recorded': True,
    }
    return (
        isinstance(evidence, dict)
        and all(evidence.get(name) == value for name, value in required.items())
    )


def _v3_authorize_replacement(
    stage,
    slot_id,
    evidence,
    replacement_state,
    candidate_id=None,
):
    """Enforce identical-slot, per-stage, per-candidate, and total caps."""
    if stage not in V3_REPLACEMENT_CAPS or stage == 'total':
        raise ValueError(f'unknown replacement stage: {stage}')
    if not _v3_replacement_eligible(evidence):
        raise RuntimeError('attempt is not infrastructure-replaceable')
    state = {
        'total': int(replacement_state.get('total', 0)),
        'by_stage': dict(replacement_state.get('by_stage', {})),
        'slots': list(replacement_state.get('slots', [])),
        'development_candidates': list(
            replacement_state.get('development_candidates', [])
        ),
        'attempt_links': list(
            replacement_state.get('attempt_links', [])
        ),
    }
    if slot_id in state['slots']:
        raise RuntimeError('one slot cannot receive a second replacement')
    if state['total'] >= V3_REPLACEMENT_CAPS['total']:
        raise RuntimeError('v3 total replacement cap is exhausted')
    stage_count = int(state['by_stage'].get(stage, 0))
    if stage_count >= V3_REPLACEMENT_CAPS[stage]:
        raise RuntimeError(f'{stage} replacement cap is exhausted')
    if stage == 'development':
        if not candidate_id:
            raise ValueError(
                'development replacement requires candidate_id'
            )
        if candidate_id in state['development_candidates']:
            raise RuntimeError(
                'development allows at most one replacement per candidate'
            )
        state['development_candidates'].append(candidate_id)
    state['total'] += 1
    state['by_stage'][stage] = stage_count + 1
    state['slots'].append(slot_id)
    return state


def load_v3_candidates(path=V3_CANDIDATES_PATH):
    """Load exactly the three declared v3 five-factor bundles."""
    document = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if set(document) != {
        'schema_version',
        'candidate_set_id',
        'selection_order',
        'candidates',
    }:
        raise ValueError('v3 candidate document has unknown or missing keys')
    if document['schema_version'] != 1:
        raise ValueError('v3 candidate schema_version must equal 1')
    if document['selection_order'] != [
        'end_to_end_success_count',
        'behavior_contract_pass_count',
        'local_escape_success_rate',
        'minimum_family_success_rate',
        'escape_time_p95_sec',
        'escape_time_median_sec',
        'median_orbit_count',
        'revisit_rate',
        'median_convergence_time_sec',
        'median_path_length_m',
        'candidate_id',
    ]:
        raise ValueError('v3 candidate selection order drifted')
    if document['candidates'] != list(V3_CANDIDATES):
        raise ValueError('v3 candidate bundles drifted')
    return document


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
    """Bind a profile while preserving declared v4 branch-only overrides."""
    document = yaml.safe_load(Path(source_path).read_text(encoding='utf-8'))
    overrides = dict(profile['launch_overrides'])
    if document.get('schema_version') == 4:
        case_override_names = {
            name
            for case in document.get('cases', [])
            for name in (
                case.get('algorithm', {}).get('launch_overrides', {})
            )
        }
        case_bound_names = set(overrides) & case_override_names
        if case_bound_names:
            for case in document['cases']:
                algorithm = case.setdefault('algorithm', {})
                case_overrides = algorithm.setdefault(
                    'launch_overrides', {}
                )
                for name in sorted(case_bound_names):
                    case_overrides.setdefault(name, overrides[name])
            overrides = {
                name: value
                for name, value in overrides.items()
                if name not in case_bound_names
            }
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
            run_path = Path(run_directory)
            resolved_path = run_path / 'resolved_scenario.yaml'
            resolved = yaml.safe_load(
                resolved_path.read_text(encoding='utf-8')
            )
            records[-1]['family'] = resolved['family']
            records[-1]['case_key'] = resolved['case_key']
            records[-1]['resolved_scenario_sha256'] = file_sha256(
                resolved_path
            )
            if resolved.get('schema_version', 1) >= 4:
                records[-1]['acceptance_family'] = resolved[
                    'acceptance_family'
                ]
                records[-1]['acceptance_partition'] = resolved[
                    'acceptance_partition'
                ]
                records[-1]['repeat_reference'] = resolved[
                    'repeat_reference'
                ]
                records[-1]['metric_applicability'] = resolved[
                    'metric_applicability'
                ]
                records[-1]['disturbances'] = resolved['disturbances']
                records[-1]['success_contract'] = resolved['success']
                analysis_path = (
                    run_path / 'analysis/phase08/summary_metrics.json'
                )
                completeness_path = (
                    run_path
                    / 'analysis/phase08/analysis_completeness.json'
                )
                if analysis_path.is_file():
                    records[-1]['analysis_summary_sha256'] = file_sha256(
                        analysis_path
                    )
                if completeness_path.is_file():
                    records[-1]['analysis_completeness_sha256'] = (
                        file_sha256(completeness_path)
                    )
                    records[-1]['analysis_completeness'] = _load_json(
                        completeness_path
                    )
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


def _v3_materialize_profile_suite(source_path, profile, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix='phase08_v3_materialize_'
    ) as directory:
        temporary = _materialize_suite(
            source_path,
            profile,
            Path(directory) / destination.name,
        )
        payload = temporary.read_bytes()
    if destination.exists():
        if destination.read_bytes() != payload:
            raise RuntimeError(
                f'v3 materialized suite drifted: {destination}'
            )
    else:
        atomic_bytes(destination, payload, mode=0o400)
    return destination


def _v3_progress_path(stage_root):
    return Path(stage_root) / 'progress.json'


def _v3_write_progress(stage_root, document):
    value = dict(document)
    value['progress_sha256'] = omission_sha256(
        value, 'progress_sha256'
    )
    atomic_json(_v3_progress_path(stage_root), value)
    return value


def _v3_load_progress(stage_root):
    path = _v3_progress_path(stage_root)
    if not path.is_file():
        return None
    value = _load_json(path)
    require_omission_sha256(
        value, 'progress_sha256', f'{stage_root} progress'
    )
    return value


def _v3_replacement_state_path(evidence_root):
    return _state_root(evidence_root) / 'v3_replacements.json'


def _v3_load_replacement_state(evidence_root):
    path = _v3_replacement_state_path(evidence_root)
    if not path.is_file():
        return {
            'total': 0,
            'by_stage': {},
            'slots': [],
            'development_candidates': [],
            'attempt_links': [],
        }
    state = _load_json(path)
    require_omission_sha256(
        state, 'replacement_state_sha256', 'v3 replacement state'
    )
    return {
        key: value for key, value in state.items()
        if key != 'replacement_state_sha256'
    }


def _v3_store_replacement_state(evidence_root, state):
    value = dict(state)
    value['replacement_state_sha256'] = omission_sha256(
        value, 'replacement_state_sha256'
    )
    atomic_json(_v3_replacement_state_path(evidence_root), value)
    return value


def _v3_authorize_or_resume_replacement(
    evidence_root,
    stage,
    slot_id,
    evidence,
    replacement_state,
    invalid_record_path,
    replacement_attempt_index,
    *,
    candidate_id=None,
):
    """Persist one replacement authorization or resume that exact decision."""
    invalid_record = _load_json(invalid_record_path)
    derived_evidence = _v3_replacement_evidence(invalid_record)
    if derived_evidence != evidence:
        raise RuntimeError(
            'replacement evidence differs from retained source artifacts'
        )
    expected_link = {
        'slot_id': slot_id,
        'invalid_attempt_record': str(invalid_record_path),
        'proof_artifacts': _v3_replacement_proof_artifacts(
            invalid_record,
            invalid_record_path,
        ),
        'replacement_attempt_index': replacement_attempt_index,
        'evidence': evidence,
    }
    matching_links = [
        link for link in replacement_state.get('attempt_links', [])
        if link.get('slot_id') == slot_id
    ]
    if matching_links:
        if (
            len(matching_links) != 1
            or matching_links[0] != expected_link
            or slot_id not in replacement_state.get('slots', [])
        ):
            raise RuntimeError(
                'persisted replacement authorization drifted'
            )
        return replacement_state
    updated = _v3_authorize_replacement(
        stage,
        slot_id,
        evidence,
        replacement_state,
        candidate_id=candidate_id,
    )
    updated.setdefault('attempt_links', []).append(expected_link)
    _v3_store_replacement_state(evidence_root, updated)
    return updated


def _v3_replacement_evidence(record):
    run_directory = record.get('run_directory')
    metadata = {}
    completeness = {}
    if run_directory:
        run_path = Path(run_directory)
        metadata_path = run_path / 'metadata.yaml'
        completeness_path = run_path / 'completeness.json'
        if metadata_path.is_file():
            metadata = yaml.safe_load(
                metadata_path.read_text(encoding='utf-8')
            ) or {}
        if completeness_path.is_file():
            completeness = _load_json(completeness_path)
    recording = metadata.get('recording', {})
    checks = completeness.get('checks', {})
    motion = checks.get('no_motion_before_readiness', {})
    lifecycle = checks.get('clean_lifecycle_before_readiness', {})
    failure_stage = recording.get('failure_stage')
    external_startup = (
        failure_stage in {
            'initialization',
            'graph_preflight',
            'operational_readiness',
            'parameter_capture',
            'final_operational_readiness',
        }
        and recording.get('infrastructure_status') != 'runtime_failed'
    )
    return {
        'classification': record.get('classification', {}).get('status'),
        'readiness_ever_true': recording.get('readiness_ever_true'),
        'nonzero_command_observed': not (
            motion.get('passed') is True
            and not recording.get('pre_ready_nonzero_topics', {})
        ),
        'non_search_lifecycle_observed': not (
            lifecycle.get('passed') is True
            and not recording.get('pre_ready_lifecycle_violations', [])
        ),
        'active_fill_or_escape_observed': bool(
            recording.get('pre_ready_lifecycle_violations', [])
        ),
        'external_startup_cause': external_startup,
        'cleanup_passed': (
            record.get('cleanup', {}).get('passed') is True
        ),
        'classification_recorded': bool(record.get('classification')),
        'failure_stage': failure_stage,
        'run_error': recording.get('run_error'),
    }


def _v3_replacement_proof_artifacts(record, invalid_record_path):
    """Bind replacement authorization to its raw retained proof inputs."""
    run_directory = record.get('run_directory')
    if not run_directory:
        raise RuntimeError(
            'replacement record lacks a retained run directory'
        )
    paths = {
        'invalid_attempt_record': Path(invalid_record_path),
        'metadata': Path(run_directory) / 'metadata.yaml',
        'completeness': Path(run_directory) / 'completeness.json',
    }
    missing = [
        str(path)
        for path in paths.values()
        if not path.is_file()
    ]
    if missing:
        raise RuntimeError(
            'replacement proof artifact is missing: '
            + ', '.join(missing)
        )
    return {
        name: {
            'path': str(path),
            'sha256': file_sha256(path),
        }
        for name, path in paths.items()
    }


def _v3_pure_applicability_behavior_miss(record, integrity):
    """Recognize an analyzed behavior miss without weakening integrity."""
    expected_integrity_reasons = {
        'analysis is not complete',
        'metric applicability integrity failed',
        'analysis completeness status is not complete',
    }
    if (
        integrity.get('passed') is not False
        or set(integrity.get('reasons', []))
        != expected_integrity_reasons
        or len(integrity.get('reasons', []))
        != len(expected_integrity_reasons)
    ):
        return False
    classification = record.get('classification', {})
    predicate_results = classification.get('predicate_results', {})
    if not isinstance(predicate_results, dict):
        return False
    infrastructure_predicates = {
        'recording_complete',
        'cleanup_complete',
        'collision_expectation',
    }
    behavior_predicates = {
        'controller_goal',
        'ground_truth_goal',
        'expected_terminal_state',
        'required_state_path',
        'required_state_sequence',
        'required_event_sequence',
        'required_events',
        'no_forbidden_states',
        'no_forbidden_events',
        'minimum_saturation_samples',
    }
    false_predicates = {
        name
        for name, passed in predicate_results.items()
        if passed is False
    }
    if (
        classification.get('status') != 'failed'
        or classification.get('passed') is not False
        or classification.get('infrastructure_status') != 'completed'
        or not false_predicates
        or not false_predicates <= behavior_predicates
        or any(
            predicate_results.get(name) is False
            for name in infrastructure_predicates
        )
    ):
        return False

    analysis = record.get('analysis')
    completeness = record.get('analysis_completeness')
    applicability = record.get('metric_applicability')
    if (
        not isinstance(analysis, dict)
        or not isinstance(completeness, dict)
        or not isinstance(applicability, dict)
        or analysis.get('analysis_status') != 'partial'
        or completeness.get('status') != 'partial'
        or analysis.get('metric_applicability') != applicability
        or record.get('analysis_error')
        or record.get('recording_complete') is not True
        or record.get('cleanup', {}).get('passed') is not True
        or record.get('record_process', {}).get('timed_out')
    ):
        return False
    applicability_integrity = analysis.get('applicability_integrity', {})
    applicability_reasons = applicability_integrity.get('reasons')
    if (
        applicability_integrity.get('passed') is not False
        or applicability_reasons != [
            'escape occurred in a case declared not applicable',
        ]
    ):
        return False

    critical_inputs = completeness.get('critical_inputs')
    fresh_phase05 = completeness.get('fresh_phase05_validation', {})
    if (
        completeness.get('stored_phase05_passed') is not True
        or fresh_phase05.get('passed') is not True
        or critical_inputs != {
            'control': True,
            'cost': True,
            'pose': True,
            'readiness': True,
        }
        or completeness.get('recording_failures') != []
        or completeness.get('analysis_failures') != []
    ):
        return False
    metrics = analysis.get('metrics')
    metric_validity = completeness.get('metric_validity')
    if (
        not isinstance(metrics, dict)
        or not isinstance(metric_validity, dict)
        or metric_validity != {
            name: metric.get('status')
            for name, metric in metrics.items()
        }
        or any(
            status in {'invalid', 'unavailable'}
            for status in metric_validity.values()
        )
        or completeness.get('run_id') != record.get('run_id')
        or analysis.get('run_id') != record.get('run_id')
    ):
        return False
    run_directory = Path(record.get('run_directory', '')).resolve()
    artifact_paths = {
        'resolved_scenario_sha256': (
            run_directory / 'resolved_scenario.yaml'
        ),
        'analysis_summary_sha256': (
            run_directory / 'analysis/phase08/summary_metrics.json'
        ),
        'analysis_completeness_sha256': (
            run_directory
            / 'analysis/phase08/analysis_completeness.json'
        ),
    }
    if any(
        not path.is_file()
        or record.get(field) != file_sha256(path)
        for field, path in artifact_paths.items()
    ):
        return False
    if (
        _load_json(artifact_paths['analysis_summary_sha256']) != analysis
        or _load_json(
            artifact_paths['analysis_completeness_sha256']
        ) != completeness
    ):
        return False
    return True


def _v3_hard_stop_reason(
    record,
    *,
    allow_pure_applicability_miss=False,
):
    classification = record.get('classification', {})
    infrastructure = classification.get('infrastructure_status')
    if record.get('cleanup', {}).get('passed') is not True:
        return 'cleanup contamination'
    if record.get('record_process', {}).get('timed_out'):
        return 'outer wall timeout'
    if infrastructure not in {'completed', 'infrastructure_invalid'}:
        return f'infrastructure status {infrastructure}'
    analysis = record.get('analysis') or {}
    collision = analysis.get('metrics', {}).get('collision', {})
    if collision.get('status') != 'valid':
        return 'collision evidence unavailable'
    if collision.get('value') is True:
        return 'non-ground collision'
    if record.get('recording_complete') is not True and (
        infrastructure != 'infrastructure_invalid'
    ):
        return 'recording evidence invalid after readiness'
    integrity = _v3_record_integrity(
        record,
        require_terminal_outcomes=False,
    )
    if not integrity['passed']:
        if (
            allow_pure_applicability_miss
            and _v3_pure_applicability_behavior_miss(record, integrity)
        ):
            return None
        return f"evidence integrity: {integrity['reasons'][0]}"
    return None


def _v3_directory_size(path):
    total = 0
    for child in Path(path).rglob('*'):
        if child.is_file():
            total += child.stat().st_size
    return total


def _v3_progress_roots(evidence_root):
    root = Path(evidence_root)
    paths = [root / 'activation']
    paths.extend(
        root / 'development' / candidate['candidate_id']
        for candidate in V3_CANDIDATES
    )
    paths.extend(
        root / stage
        for stage in ('holdout', 'validation', 'reproducibility')
    )
    return paths


def _v3_remaining_declared_slots(evidence_root):
    completed = 0
    for stage_root in _v3_progress_roots(evidence_root):
        progress = _v3_load_progress(stage_root)
        if progress is not None:
            completed += len(progress.get('final_record_paths', {}))
    if completed > V3_EXPECTED_COUNTS['declared_total']:
        raise RuntimeError('v3 completed-slot count exceeds the Plan')
    return V3_EXPECTED_COUNTS['declared_total'] - completed


def _v3_required_free_bytes(evidence_root, remaining_slots):
    attempt_sizes = [
        _v3_directory_size(path)
        for path in Path(evidence_root).glob('**/attempts/*/*')
        if path.is_dir()
    ]
    observed_unit = (
        2 * _percentile(attempt_sizes, 95)
        if attempt_sizes else 0
    )
    per_slot = max(512 * 1024 ** 2, observed_unit)
    return int(25 * 1024 ** 3 + per_slot * remaining_slots)


def _v3_stage_summary(
    suite,
    stage,
    progress,
    attempt_summaries,
    summary_path,
):
    runs = [
        run
        for summary in attempt_summaries
        for run in summary.get('runs', [])
    ]
    summary = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'stage': stage,
        'suite_id': suite['suite_id'],
        'source_path': suite['source_path'],
        'serial_execution': True,
        'declared_slot_count': len(progress['slot_ids']),
        'completed_slot_count': len(progress['final_record_paths']),
        'attempted_slot_count': (
            len(progress['final_record_paths'])
            + len(progress.get(
                'ambiguous_interrupted_dispatch_case_ids',
                [],
            ))
        ),
        'ambiguous_interrupted_dispatch_case_ids': list(
            progress.get(
                'ambiguous_interrupted_dispatch_case_ids',
                [],
            )
        ),
        'carried_record_count': progress.get('carried_count', 0),
        'new_execution_count': progress.get(
            'newly_executed_count',
            len(progress['final_record_paths']),
        ),
        'carried_count': progress.get('carried_count', 0),
        'newly_executed_count': progress.get(
            'newly_executed_count',
            len(progress['final_record_paths']),
        ),
        'carried_records': list(
            progress.get('carried_records', [])
        ),
        'stopped_early_reason': progress.get('stopped_early_reason'),
        'attempt_count': len(progress['attempts']),
        'runs': runs,
        'summary_path': str(summary_path),
    }
    atomic_yaml(summary_path, summary)
    return summary


def _v3_verify_carried_record_bindings(carried_records, stage):
    """Rehash carried records and their retained run directories."""
    for item in carried_records:
        case_id = item.get('case_id')
        path = Path(item.get('record_path', '')).resolve()
        expected_sha256 = item.get('record_sha256')
        manifest = item.get('run_directory_manifest')
        if (
            not path.is_file()
            or re.fullmatch(
                r'[0-9a-f]{64}',
                str(expected_sha256),
            ) is None
            or file_sha256(path) != expected_sha256
        ):
            raise RuntimeError(
                f'v3 {stage} carried record binding failed: {case_id}'
            )
        record = _load_json(path)
        if (
            record.get('case_id') != case_id
            or not isinstance(manifest, dict)
            or Path(record.get('run_directory', '')).resolve()
            != Path(manifest.get('root', '')).resolve()
        ):
            raise RuntimeError(
                f'v3 {stage} carried record binding failed: {case_id}'
            )
        try:
            _v3_verify_directory_manifest(manifest)
        except RuntimeError as exc:
            raise RuntimeError(
                f'v3 {stage} carried record binding failed: {case_id}'
            ) from exc


def _v3_execute_serial_slots(
    suite_path,
    operator,
    evidence_root,
    stage_root,
    stage,
    *,
    candidate_id=None,
    stop_decider=None,
    runtime_snapshot=None,
    carried_records=None,
    required_execution_case_ids=None,
    allow_pure_applicability_miss=False,
):
    """Execute one declared case at a time with bounded replacements."""
    evidence_root = Path(evidence_root).expanduser().resolve()
    stage_root = Path(stage_root)
    if allow_pure_applicability_miss and stage != 'activation':
        raise RuntimeError(
            'pure applicability continuation is V3C activation-only'
        )
    stage_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    stage_root.chmod(0o700)
    if _git('status', '--porcelain'):
        raise RuntimeError(
            f'v3 {stage} empirical dispatch requires a clean worktree'
        )
    if runtime_snapshot is not None:
        _v3_verify_repository_snapshot(runtime_snapshot)
    active_processes = _v3_active_processes()
    if active_processes:
        raise RuntimeError(
            f'v3 {stage} pre-dispatch process set is not clean: '
            f'{active_processes}'
        )
    suite = load_suite(suite_path)
    runs, unsupported = expand_suite(suite)
    if unsupported:
        raise RuntimeError(f'v3 {stage} suite contains unsupported cases')
    slot_ids = []
    for run in runs:
        case_id = run['case_id']
        if case_id not in slot_ids:
            slot_ids.append(case_id)
    if len(slot_ids) != len(runs):
        raise RuntimeError(
            f'v3 {stage} slots must resolve to exactly one run each'
        )
    carried_by_case = {}
    for item in list(carried_records or []):
        if not isinstance(item, dict):
            raise RuntimeError(f'v3 {stage} carried record is malformed')
        case_id = item.get('case_id')
        path = Path(item.get('record_path', '')).resolve()
        expected_sha256 = item.get('record_sha256')
        if (
            case_id not in slot_ids
            or case_id in carried_by_case
            or not path.is_file()
            or re.fullmatch(
                r'[0-9a-f]{64}',
                str(expected_sha256),
            ) is None
            or file_sha256(path) != expected_sha256
            or _load_json(path).get('case_id') != case_id
        ):
            raise RuntimeError(
                f'v3 {stage} carried record binding failed: {case_id}'
            )
        carried_by_case[case_id] = {
            **item,
            'record_path': str(path),
        }
    normalized_carried = [
        carried_by_case[case_id]
        for case_id in slot_ids
        if case_id in carried_by_case
    ]
    _v3_verify_carried_record_bindings(normalized_carried, stage)
    execution_case_ids = [
        case_id for case_id in slot_ids
        if case_id not in carried_by_case
    ]
    normalized_required_execution_case_ids = (
        list(required_execution_case_ids)
        if required_execution_case_ids is not None else None
    )
    if (
        normalized_required_execution_case_ids is not None
        and execution_case_ids
        != normalized_required_execution_case_ids
    ):
        raise RuntimeError(
            f'v3 {stage} execution case IDs/order drifted'
        )
    suite_sha256 = file_sha256(suite_path)
    progress = _v3_load_progress(stage_root)
    if progress is None:
        progress = _v3_write_progress(stage_root, {
            'schema_version': 1,
            'experiment_version': 'phase08-v3',
            'stage': stage,
            'candidate_id': candidate_id,
            'suite_path': str(Path(suite_path).resolve()),
            'suite_sha256': suite_sha256,
            'slot_ids': slot_ids,
            'attempts': [],
            'carried_records': normalized_carried,
            'carried_count': len(normalized_carried),
            'newly_executed_count': 0,
            'carried_record_count': len(normalized_carried),
            'new_execution_count': 0,
            'required_execution_case_ids': (
                normalized_required_execution_case_ids
            ),
            'ambiguous_interrupted_dispatch_case_ids': [],
            'final_record_paths': {
                item['case_id']: item['record_path']
                for item in normalized_carried
            },
            'stopped_early_reason': None,
        })
    elif (
        progress.get('suite_path') != str(Path(suite_path).resolve())
        or progress.get('suite_sha256') != suite_sha256
        or progress.get('slot_ids') != slot_ids
        or progress.get('candidate_id') != candidate_id
        or progress.get('carried_records', []) != normalized_carried
        or progress.get('carried_count', 0) != len(normalized_carried)
        or progress.get('required_execution_case_ids')
        != normalized_required_execution_case_ids
    ):
        raise RuntimeError(f'v3 {stage} progress input drifted')
    for item in normalized_carried:
        if (
            progress.get('final_record_paths', {}).get(item['case_id'])
            != item['record_path']
            or file_sha256(item['record_path'])
            != item['record_sha256']
            or any(
                attempt.get('case_id') == item['case_id']
                for attempt in progress.get('attempts', [])
            )
        ):
            raise RuntimeError(
                f'v3 {stage} carried record progress drifted'
            )
    replacement_state = _v3_load_replacement_state(evidence_root)
    attempt_summaries = []
    final_records = []
    for slot_index, case_id in enumerate(slot_ids):
        if progress.get('stopped_early_reason'):
            break
        final_path_text = progress['final_record_paths'].get(case_id)
        if final_path_text:
            if case_id in carried_by_case:
                _v3_verify_carried_record_bindings(
                    normalized_carried,
                    stage,
                )
            final_records.append(_load_json(final_path_text))
            continue
        slot_identifier = (
            f'{stage}.{candidate_id}.{case_id}'
            if candidate_id else f'{stage}.{case_id}'
        )
        while True:
            _v3_verify_carried_record_bindings(
                normalized_carried,
                stage,
            )
            if (
                not Path(suite_path).is_file()
                or file_sha256(suite_path)
                != progress['suite_sha256']
            ):
                raise RuntimeError(
                    f'v3 {stage} suite drifted before dispatch'
                )
            if runtime_snapshot is not None:
                _v3_verify_repository_snapshot(runtime_snapshot)
            slot_attempts = [
                item for item in progress['attempts']
                if item.get('slot_id') == slot_identifier
            ]
            pending_attempts = [
                item for item in slot_attempts
                if item.get('outcome') == 'dispatch_intent'
            ]
            if len(pending_attempts) > 1:
                raise RuntimeError(
                    f'v3 {stage} has multiple pending dispatch intents'
                )
            if pending_attempts:
                attempt_entry = pending_attempts[0]
                attempt_index = attempt_entry['attempt_index'] - 1
                summary_path = Path(
                    attempt_entry['expected_summary_path']
                )
                record_path = Path(
                    attempt_entry['expected_record_path']
                )
                error_path = Path(
                    attempt_entry['expected_error_path']
                )
                attempt_root = summary_path.parent
                if not summary_path.is_file():
                    ambiguous_case_ids = progress.setdefault(
                        'ambiguous_interrupted_dispatch_case_ids',
                        [],
                    )
                    if case_id not in ambiguous_case_ids:
                        ambiguous_case_ids.append(case_id)
                    progress['stopped_early_reason'] = (
                        f'{slot_identifier}: ambiguous interrupted '
                        'dispatch intent without a complete summary'
                    )
                    _v3_write_progress(stage_root, progress)
                    break
            else:
                attempt_index = len(slot_attempts)
                remaining_slots = _v3_remaining_declared_slots(
                    evidence_root
                )
                free_bytes = shutil.disk_usage(stage_root).free
                required_bytes = _v3_required_free_bytes(
                    evidence_root, remaining_slots
                )
                if free_bytes < required_bytes:
                    progress['stopped_early_reason'] = (
                        f'{slot_identifier}: disk forecast failed '
                        f'({free_bytes} < {required_bytes})'
                    )
                    _v3_write_progress(stage_root, progress)
                    break
                attempt_root = (
                    stage_root
                    / 'attempts'
                    / f'{slot_index + 1:03d}_{case_id}'
                    / f'attempt_{attempt_index + 1:02d}'
                )
                attempt_root.mkdir(
                    parents=True,
                    exist_ok=True,
                    mode=0o700,
                )
                summary_path = (
                    attempt_root / 'scenario_summary.yaml'
                )
                record_path = attempt_root / 'record.json'
                error_path = attempt_root / 'execution_error.json'
                attempt_entry = {
                    'slot_id': slot_identifier,
                    'case_id': case_id,
                    'attempt_index': attempt_index + 1,
                    'summary_path': None,
                    'expected_summary_path': str(summary_path),
                    'summary_sha256': None,
                    'record_path': None,
                    'expected_record_path': str(record_path),
                    'record_sha256': None,
                    'error_path': None,
                    'expected_error_path': str(error_path),
                    'error_sha256': None,
                    'outcome': 'dispatch_intent',
                }
                progress['attempts'].append(attempt_entry)
                _v3_write_progress(stage_root, progress)
            try:
                if summary_path.is_file():
                    attempt_summary = yaml.safe_load(
                        summary_path.read_text(encoding='utf-8')
                    )
                else:
                    attempt_summary = execute_suite(
                        suite_path,
                        operator,
                        case_ids=[case_id],
                        runs_root=attempt_root / 'runs',
                        summary_output=summary_path,
                    )
                attempt_summaries.append(attempt_summary)
                if record_path.is_file():
                    record = _load_json(record_path)
                else:
                    records = _analyze_scenario_summary(attempt_summary)
                    if len(records) != 1:
                        raise RuntimeError(
                            'one v3 slot did not produce one record'
                        )
                    record = records[0]
                    atomic_json(record_path, record)
                if record.get('case_id') != case_id:
                    raise RuntimeError(
                        f'v3 {stage} analyzed record belongs to '
                        f'{record.get("case_id")}, not {case_id}'
                    )
            except Exception as exc:
                failure = {
                    'schema_version': 1,
                    'slot_id': slot_identifier,
                    'attempt_index': attempt_index + 1,
                    'error': f'{type(exc).__name__}: {exc}',
                }
                atomic_json(error_path, failure)
                attempt_entry.update({
                    'summary_path': (
                        str(summary_path)
                        if summary_path.is_file() else None
                    ),
                    'summary_sha256': (
                        file_sha256(summary_path)
                        if summary_path.is_file() else None
                    ),
                    'record_path': None,
                    'error_path': str(error_path),
                    'error_sha256': file_sha256(error_path),
                    'outcome': 'execution_error',
                })
                progress['stopped_early_reason'] = (
                    f'{slot_identifier}: execution error'
                )
                _v3_write_progress(stage_root, progress)
                break
            attempt_entry.update({
                'summary_path': str(summary_path),
                'summary_sha256': file_sha256(summary_path),
                'record_path': str(record_path),
                'record_sha256': file_sha256(record_path),
                'outcome': record.get('classification', {}).get('status'),
            })
            if record.get('classification', {}).get(
                'status'
            ) == 'infrastructure_invalid':
                evidence = _v3_replacement_evidence(record)
                surviving_processes = _v3_active_processes()
                if surviving_processes:
                    evidence['cleanup_passed'] = False
                    evidence['surviving_processes'] = (
                        surviving_processes
                    )
                try:
                    replacement_state = (
                        _v3_authorize_or_resume_replacement(
                            evidence_root,
                            stage,
                            slot_identifier,
                            evidence,
                            replacement_state,
                            record_path,
                            attempt_index + 2,
                            candidate_id=candidate_id,
                        )
                    )
                except RuntimeError as exc:
                    progress['stopped_early_reason'] = (
                        f'{slot_identifier}: {exc}'
                    )
                    _v3_write_progress(stage_root, progress)
                    break
                _v3_write_progress(stage_root, progress)
                continue
            hard_stop = _v3_hard_stop_reason(
                record,
                allow_pure_applicability_miss=(
                    allow_pure_applicability_miss
                ),
            )
            surviving_processes = _v3_active_processes()
            if surviving_processes:
                hard_stop = (
                    'post-attempt process contamination: '
                    f'{surviving_processes}'
                )
            progress['final_record_paths'][case_id] = str(record_path)
            final_records.append(record)
            if hard_stop:
                progress['stopped_early_reason'] = (
                    f'{slot_identifier}: {hard_stop}'
                )
            _v3_write_progress(stage_root, progress)
            break
        if progress.get('stopped_early_reason'):
            break
        if stop_decider is not None:
            reason = stop_decider(
                list(final_records),
                slot_ids[slot_index + 1:],
            )
            if reason:
                progress['stopped_early_reason'] = reason
                _v3_write_progress(stage_root, progress)
                break
    summary_path = stage_root / 'scenario_summary.yaml'
    _v3_verify_carried_record_bindings(normalized_carried, stage)
    final_records = [
        _load_json(progress['final_record_paths'][case_id])
        for case_id in slot_ids
        if case_id in progress['final_record_paths']
    ]
    ambiguous_case_ids = [
        case_id for case_id in slot_ids
        if case_id not in progress['final_record_paths']
        and any(
            attempt.get('case_id') == case_id
            and attempt.get('outcome') == 'dispatch_intent'
            for attempt in progress.get('attempts', [])
        )
    ]
    progress['ambiguous_interrupted_dispatch_case_ids'] = (
        ambiguous_case_ids
    )
    progress['not_run_slot_ids'] = [
        case_id for case_id in slot_ids
        if case_id not in progress['final_record_paths']
        and case_id not in ambiguous_case_ids
    ]
    progress['carried_count'] = len(normalized_carried)
    progress['newly_executed_count'] = (
        len(progress['final_record_paths'])
        - len(normalized_carried)
    )
    progress['carried_record_count'] = progress['carried_count']
    progress['new_execution_count'] = progress[
        'newly_executed_count'
    ]
    progress = _v3_write_progress(stage_root, progress)
    attempt_summaries = [
        yaml.safe_load(Path(path_text).read_text(encoding='utf-8'))
        for path_text in dict.fromkeys(
            attempt.get('summary_path')
            for attempt in progress['attempts']
            if attempt.get('summary_path')
        )
    ]
    summary = _v3_stage_summary(
        suite,
        stage,
        progress,
        attempt_summaries,
        summary_path,
    )
    records_path = stage_root / 'records.json'
    aggregate_records = []
    for case_id in slot_ids:
        if case_id not in progress['final_record_paths']:
            continue
        if case_id in carried_by_case:
            aggregate_records.append({
                'schema_version': 1,
                'case_id': case_id,
                'disposition': (
                    'carried_immutable_behavioral_failure'
                ),
                'carried_record': dict(carried_by_case[case_id]),
            })
        else:
            aggregate_records.append(
                _load_json(progress['final_record_paths'][case_id])
            )
    atomic_json(records_path, aggregate_records)
    attempts_path = stage_root / 'attempt_records.json'
    attempt_records = [
        _load_json(item['record_path'])
        for item in progress['attempts']
        if item.get('record_path')
    ]
    atomic_json(attempts_path, attempt_records)
    return summary, final_records, progress


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
    try:
        result = subprocess.run(
            command,
            cwd=REPOSITORY_ROOT / 'ros2_ws',
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=300.0,
        )
    except subprocess.TimeoutExpired as exc:
        output = (
            exc.stdout.decode('utf-8', errors='replace')
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or '')
        )
        return {
            'command': command,
            'return_code': 124,
            'passed': False,
            'output_tail': output[-12000:],
            'timed_out': True,
        }
    return {
        'command': command,
        'return_code': result.returncode,
        'passed': result.returncode == 0,
        'output_tail': result.stdout[-12000:],
        'timed_out': False,
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


def _not_run_gate(identifier, threshold, stopped_stage):
    return {
        **_gate(
            identifier,
            False,
            'not_run',
            threshold,
            f'not run after the {stopped_stage} early-stop gate failed',
        ),
        'status': 'not_run',
    }


def _run_v2_partial_report(root, workflow, failure):
    """Write a non-acceptance report without inventing unexecuted evidence."""
    activation = _load_json(_v2_state(root, 'activation'))
    holdout_path = _v2_state(root, 'holdout')
    validation_path = _v2_state(root, 'validation')
    reproducibility_path = _v2_state(root, 'reproducibility')
    holdout = _load_json(holdout_path) if holdout_path.exists() else None
    validation = (
        _load_json(validation_path) if validation_path.exists() else None
    )
    reproducibility = (
        _load_json(reproducibility_path)
        if reproducibility_path.exists()
        else None
    )
    gates = [
        {
            **_gate(
                '1_functional',
                activation['functional_tests']['passed'],
                activation['functional_tests']['passed'],
                'all retained functional tests pass',
            ),
            'status': 'evaluated',
        },
        {
            **_gate(
                '2_activation',
                activation['passed'],
                f'{activation["integrity_pass_count"]}/10',
                'all ten activation proofs',
                '; '.join(activation.get('reasons', [])) or None,
            ),
            'status': 'evaluated',
        },
    ]
    if holdout is None:
        gates.append(_not_run_gate(
            '3_holdout',
            'at least 18/20 with complete valid evidence',
            failure['stage'],
        ))
    else:
        gates.append({
            **_gate(
                '3_holdout',
                holdout['passed'],
                f'{holdout["end_to_end_success_count"]}/20',
                'at least 18/20 with complete valid evidence',
                '; '.join(holdout.get('reasons', [])) or None,
            ),
            'status': 'evaluated',
        })
    unique_gate_map = (
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
    deferred_unique = (
        ('4_completeness', '70/70 complete unique runs'),
        ('5_collision', 'zero collisions with valid evidence'),
        ('6_local_escape', 'all declared local-minimum escapes succeed'),
        ('7_end_to_end', 'at least 63/70 end-to-end successes'),
        ('8_family_minimum', 'every family success rate is at least 0.80'),
        ('9_median_escape_time', 'median escape time is at most 20 s'),
        ('10_p95_escape_time', 'p95 escape time is at most 35 s'),
        ('11_median_orbit_count', 'median orbit count is at most 2'),
        ('12_normal_termination', 'no unexplained timeout or failsafe'),
        ('13_revisit_rate', 'revisit rate is at most 0.10'),
    )
    if validation is None:
        gates.extend(
            _not_run_gate(identifier, threshold, failure['stage'])
            for identifier, threshold in deferred_unique
        )
    else:
        by_identifier = {
            gate['gate']: gate
            for gate in validation['unique_gate_evaluation']['gates']
        }
        gates.extend({
            **by_identifier[source],
            'gate': target,
            'status': 'evaluated',
        } for source, target in unique_gate_map)
    if reproducibility is None:
        gates.append(_not_run_gate(
            '14_reproducibility',
            'all ten categorical and numeric comparisons',
            failure['stage'],
        ))
    else:
        evaluation = reproducibility['evaluation']
        gates.append({
            **_gate(
                '14_reproducibility',
                evaluation['passed'],
                f"{sum(item['passed'] for item in evaluation['results'])}/10",
                'all ten categorical and numeric comparisons',
                '; '.join(reproducibility.get('reasons', [])) or None,
            ),
            'status': 'evaluated',
        })
    sweep_progress_path = _v2_state(root, 'sweep_progress')
    sweep_progress = (
        _load_json(sweep_progress_path)
        if sweep_progress_path.exists()
        else {'candidates': []}
    )
    executed_run_count = activation['run_count'] + sum(
        item['metrics']['run_count']
        for item in sweep_progress.get('candidates', [])
    )
    if holdout is not None:
        executed_run_count += holdout['run_count']
    if validation is not None:
        executed_run_count += validation['run_count']
    if reproducibility is not None:
        executed_run_count += reproducibility['evaluation']['repeat_count']
    confidence_intervals = (
        validation['confidence_intervals']
        if validation is not None
        else {
            'status': 'not_applicable',
            'reason': (
                'the 70-run acceptance denominator was not executed after '
                f'the {failure["stage"]} early-stop gate failed'
            ),
        }
    )
    frozen_snapshot = None
    for state in (validation, holdout):
        if state is not None:
            frozen_snapshot = state.get('frozen_snapshot')
            if frozen_snapshot is not None:
                break
    results = {
        'schema_version': 2,
        'simulation_ready': False,
        'outcome': 'failed_early',
        'stopped_stage': failure['stage'],
        'workflow_manifest_sha256': workflow['manifest_sha256'],
        'frozen_snapshot': frozen_snapshot,
        'executed_run_count': executed_run_count,
        'unique_run_count': (
            validation['unique_run_count'] if validation is not None else 0
        ),
        'confidence_intervals': confidence_intervals,
        'gates': gates,
    }
    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    atomic_json(VALIDATION_ROOT / 'phase_08_v2_gate_results.json', results)
    lines = [
        '# Phase 08 v2 Simulation Validation Report',
        '',
        'Outcome: **FAIL (EARLY STOP)**.',
        '',
        f'Stopped after `{failure["stage"]}`. No later empirical stage was '
        'authorized.',
        '',
        f'Executed declared runs: `{executed_run_count}`.',
        '',
        '## Gates',
        '',
    ]
    if frozen_snapshot is None:
        lines[8:8] = [
            'No v2 parameter profile was selected or frozen.',
            '',
        ]
    else:
        lines[8:8] = [
            'A frozen v2 profile existed before the failed stage; its snapshot '
            'is retained in the gate JSON.',
            '',
        ]
    for gate in gates:
        if gate['status'] == 'not_run':
            lines.append(
                f'- `{gate["gate"]}`: NOT RUN; threshold '
                f'`{gate["threshold"]}`.'
            )
        else:
            lines.append(
                f'- `{gate["gate"]}`: '
                f'{"PASS" if gate["passed"] else "FAIL"}; '
                f'value `{gate["value"]}`; threshold `{gate["threshold"]}`.'
            )
    lines.extend(['', '## 95% Wilson score intervals', ''])
    if validation is None:
        lines.append(
            'Not applicable: the 70-run acceptance denominator was not '
            'executed.'
        )
    else:
        intervals = validation['confidence_intervals']
        lines.append(
            f'- Overall: {intervals["overall"]["rate"]:.4f} '
            f'[{intervals["overall"]["lower"]:.4f}, '
            f'{intervals["overall"]["upper"]:.4f}].'
        )
        for family, interval in intervals['by_family'].items():
            lines.append(
                f'- `{family}`: {interval["rate"]:.4f} '
                f'[{interval["lower"]:.4f}, {interval["upper"]:.4f}].'
            )
    lines.extend([
        '',
        f'Retained evidence root: `{root}`.',
        '',
        'No physical hardware was run.',
        '',
    ])
    (
        VALIDATION_ROOT / 'phase_08_v2_validation_report.md'
    ).write_text('\n'.join(lines), encoding='utf-8')
    return results


def run_v2_report(evidence_root):
    """Write final v2 gate JSON and Markdown from retained stage evidence."""
    root, workflow = _ensure_v2_workflow(evidence_root)
    failure_path = _v2_state(root, 'failure')
    if failure_path.exists():
        return _run_v2_partial_report(
            root,
            workflow,
            _load_json(failure_path),
        )
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


def _v3_rotate(point, quarter_turns):
    x_value, y_value = point
    for unused in range(quarter_turns % 4):
        del unused
        x_value, y_value = -y_value, x_value
    return round(x_value, 6), round(y_value, 6)


def _v3_source(
    identifier,
    point,
    intensity,
    role,
    quarter_turns,
):
    x_value, y_value = _v3_rotate(point, quarter_turns)
    return {
        'id': identifier,
        'x_m': x_value,
        'y_m': y_value,
        'relative_lumen_input': float(intensity),
        'evaluation_role': role,
    }


def _v3_case_success(
    case_id,
    escape,
    revisit,
    saturation,
    merge=False,
    assist=False,
):
    if escape:
        path = [
            'SEARCH',
            'VERIFY_EXTREMUM',
            'DESIGN_OR_MERGE_FILL',
            'ESCAPE_REPULSE',
            *(
                ['DESIGN_OR_MERGE_FILL', 'ESCAPE_ASSIST']
                if assist else []
            ),
            'RECENTER',
            'SEARCH',
            'VERIFY_EXTREMUM',
            'GOAL_HOLD',
        ]
        required_events = [
            'CONVERGENCE_CONFIRMED',
            'FILL_CREATED',
            'ESCAPE_STARTED',
            *(['ESCAPE_STALLED'] if assist else []),
            'RECENTER_STARTED',
            'RECENTER_COMPLETE',
            'GOAL_REACHED',
        ]
        outcome = 'below_target_extremum'
    else:
        path = ['SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD']
        required_events = ['CONVERGENCE_CONFIRMED', 'GOAL_REACHED']
        outcome = 'goal'
    required_event_sequence = (
        ['FILL_SUPERSEDED', 'FILL_MERGED']
        if merge else []
    )
    if merge:
        required_events.extend(required_event_sequence)
    all_of = [
        'recording_complete',
        'cleanup_complete',
        'controller_goal',
        'ground_truth_goal',
        'expected_terminal_state',
        'required_state_path',
        'required_events',
        'no_forbidden_states',
        'no_forbidden_events',
        'collision_expectation',
    ]
    if required_event_sequence:
        all_of.append('required_event_sequence')
    if saturation:
        all_of.append('minimum_saturation_samples')
    controller = {
        'contract_id': case_id,
        'expected_verification_outcome': outcome,
        'reachability_argument': (
            'The aggregate-qualified target reaches the fixed score, '
            'and any declared local branch is below it.'
        ),
        'expected_terminal_state': 'GOAL_HOLD',
        'required_state_path': path,
        'required_events': required_events,
        'required_event_sequence': required_event_sequence,
        'forbidden_states': ['FAILSAFE'],
        'forbidden_events': ['TIMEOUT', 'FAILSAFE'],
    }
    success = {
        'all_of': all_of,
        'controller': controller,
        'ground_truth': {
            'method': 'aggregate_field',
            'final_position_tolerance_m': 0.35,
            'wall_margin_m': 0.35,
            'minimum_source_score': 0.95,
            'aggregate_field': None,
        },
        'minimum_saturation_samples': 1 if saturation else 0,
        'collision_expected': False,
        'result_scopes': {
            'full_lifecycle': {
                'anchor_state': 'SEARCH',
                'boundary_state': None,
                'graceful_stop': False,
                'all_of': list(all_of),
            },
        },
    }
    applicability = {
        'escape_attempt': escape,
        'escape_duration': escape,
        'orbit_count': escape,
        'revisit': revisit,
        'delay': False,
        'saturation': saturation,
    }
    return success, applicability


def _v3_normalized_success(success):
    normalized = json.loads(json.dumps(success))
    controller = normalized['controller']
    controller['verification_timing'] = scenario_schema._verification_timing(
        V3_COMMON_OVERRIDES,
        controller['expected_verification_outcome'],
        'v3 generator',
    )
    controller.setdefault('required_state_sequence', [])
    return normalized


def _v3_resolved_case(suite, case, frozen_profile=None):
    """Build the exact normalized one-run identity from the suite document."""
    resolved = {
        'schema_version': 4,
        'suite_id': suite['suite_id'],
        'case_id': case['case_id'],
        'family': case['family'],
        'description': case['description'],
        'profile': 'robust_gaussian_v1',
        'start': json.loads(json.dumps(case['starts'][0])),
        'sources': json.loads(json.dumps(case['sources'])),
        'source_level_tuple': [None] * len(case['sources']),
        'bounds_m': [-2.0, 2.0, -2.0, 2.0],
        'room_center_m': [0.0, 0.0],
        'disturbances': json.loads(json.dumps(
            case.get('disturbances', suite['defaults']['disturbances'])
        )),
        'validation': {
            'world': True,
            'contacts_enabled': True,
        },
        'frozen_profile': json.loads(json.dumps(frozen_profile)),
        'algorithm': {
            'ablations': {
                'gaussian_fill_enabled': True,
                'affine_assist_enabled': True,
                'recenter_enabled': True,
            },
            'launch_overrides': {
                **(
                    frozen_profile.get('launch_overrides', {})
                    if frozen_profile else {}
                ),
                **V3_COMMON_OVERRIDES,
            },
        },
        'success': _v3_normalized_success(case['success']),
        'seed': case['seeds'][0],
        'acceptance_family': case['acceptance_family'],
        'acceptance_partition': case['acceptance_partition'],
        'repeat_reference': json.loads(json.dumps(
            case.get('repeat_reference')
        )),
        'metric_applicability': json.loads(json.dumps(
            case['metric_applicability']
        )),
    }
    resolved['case_key'] = deterministic_case_key(resolved)
    return resolved


def _v3_ordered_sources(
    level_a,
    level_b,
    quarter_turns,
    settings,
    escape,
):
    for separation in (1.20, 1.00, 0.80, 0.60, 0.40, 0.25, 0.10):
        if escape:
            role_a = (
                'local_minimum' if level_a < level_b else 'goal'
            )
            role_b = (
                'local_minimum' if level_b < level_a else 'goal'
            )
        else:
            role_a = 'goal' if level_a >= level_b else 'context'
            role_b = 'goal' if level_b > level_a else 'context'
        sources = [
            _v3_source(
                'source_a',
                (-separation / 2.0, 0.0),
                level_a,
                role_a,
                quarter_turns,
            ),
            _v3_source(
                'source_b',
                (separation / 2.0, 0.0),
                level_b,
                role_b,
                quarter_turns,
            ),
        ]
        try:
            truth = derive_aggregate_field_truth(
                sources,
                [-2.0, 2.0, -2.0, 2.0],
                {'sensor_noise': {'model': 'none', 'bound': 0.0}},
                solver_settings=settings,
            )
            return sources, truth, separation
        except ValueError:
            continue
    raise RuntimeError(
        f'no aggregate-qualified separation for {level_a}, {level_b}'
    )


def _v3_family_specs(family, count):
    specs = []
    for index in range(count):
        if family == 'ordered_two_source':
            escape = index in V3_ORDERED_ESCAPE_INDEXES
        else:
            escape = (
                index
                < V3_FAMILY_ALLOCATION[family]['escape_attempt']
            )
        revisit = index < V3_REVISIT_COUNTS[family]
        saturation = family == 'constraint_recovery' or (
            family == 'wall_corner' and index % 2 == 0
        )
        merge = (
            family == 'lifecycle' and index in {6, 7}
        ) or (
            family == 'multi_close_overlap' and index in {4, 5}
        )
        assist = (
            family == 'lifecycle' and index in {3, 4, 5}
        ) or (
            family == 'constraint_recovery' and index in {0, 1, 2}
        )
        noise = None
        sensor_delay = 0.0
        pose_delay = 0.0
        if family == 'noise_delay':
            if index < 2:
                noise = {'model': 'uniform', 'bound': 0.01}
            elif index < 4:
                noise = {
                    'model': 'gaussian',
                    'bound': 0.0,
                    'std_dev': 0.01,
                }
            elif index < 6:
                sensor_delay = 0.05 if index == 4 else 0.10
            else:
                sensor_delay = 0.05 if index == 6 else 0.10
                pose_delay = sensor_delay
        specs.append({
            'escape': escape,
            'revisit': revisit,
            'saturation': saturation,
            'merge': merge,
            'assist': assist,
            'noise': noise,
            'sensor_delay_sec': sensor_delay,
            'pose_delay_sec': pose_delay,
        })
    return specs


def _v3_template_sources(family, index, quarter_turns):
    target_level = 2500.0
    local_level = 650.0 + 50.0 * (index % 4)
    if family == 'multi_close_overlap':
        if index < 3:
            weak_points = [(-1.05, -0.80), (-0.45, -0.25)]
        elif index < 5:
            weak_points = [
                (-1.05, -0.80),
                (-0.45, -0.25),
                (0.10, -0.60),
            ]
        elif index < 7:
            weak_points = [(-1.00, -0.55), (-0.68, -0.48)]
        else:
            weak_points = [
                (-0.95, -0.70),
                (-0.72, -0.50),
                (-0.50, -0.32),
            ]
        escape_case = (
            index
            < V3_FAMILY_ALLOCATION[family]['escape_attempt']
        )
        merge_case = index in {4, 5}
        sources = []
        for offset, point in enumerate(weak_points):
            role = (
                'local_minimum'
                if escape_case
                and (offset == 0 or merge_case and offset == 1)
                else 'context'
            )
            sources.append(_v3_source(
                f'weak_{offset + 1}',
                point,
                local_level + 25.0 * offset,
                role,
                quarter_turns,
            ))
        sources.append(_v3_source(
            'target',
            (1.20, 1.10),
            target_level,
            'goal',
            quarter_turns,
        ))
        return sources
    if family == 'wall_corner':
        wall_points = (
            (1.45, 0.0),
            (-1.45, 0.0),
            (0.0, 1.45),
            (0.0, -1.45),
            (1.35, 1.35),
            (-1.35, 1.35),
            (-1.35, -1.35),
            (1.35, -1.35),
        )
        local = wall_points[index]
        return [
            _v3_source(
                'local',
                local,
                local_level,
                (
                    'local_minimum'
                    if index < V3_FAMILY_ALLOCATION[family][
                        'escape_attempt'
                    ]
                    else 'context'
                ),
                0,
            ),
            _v3_source(
                'target',
                (
                    -1.10 if local[0] >= 0.0 else 1.10,
                    -1.10 if local[1] >= 0.0 else 1.10,
                ),
                target_level,
                'goal',
                0,
            ),
        ]
    escape = (
        index < V3_FAMILY_ALLOCATION[family]['escape_attempt']
    )
    return [
        _v3_source(
            'local',
            (-1.05, -0.75),
            local_level,
            'local_minimum' if escape else 'context',
            quarter_turns,
        ),
        _v3_source(
            'target',
            (1.20, 1.10),
            target_level,
            'goal',
            quarter_turns,
        ),
    ]


def _v3_make_case(
    suite,
    rng,
    family,
    index,
    partition,
    solver_settings,
    ordered_levels=None,
):
    token = f'{rng.getrandbits(48):012x}'
    case_id = f'v3_{family}_{index + 1:02d}_{token}'
    quarter_turns = rng.randrange(4)
    spec = _v3_family_specs(
        family,
        V3_FAMILY_ALLOCATION[family]['unique'],
    )[index]
    disturbances = {
        'sensor_noise': (
            spec['noise'] or {'model': 'none', 'bound': 0.0}
        ),
        'sensor_delay_sec': spec['sensor_delay_sec'],
        'pose_delay_sec': spec['pose_delay_sec'],
    }
    if ordered_levels is not None:
        sources, truth, separation = _v3_ordered_sources(
            ordered_levels[0],
            ordered_levels[1],
            quarter_turns,
            solver_settings,
            spec['escape'],
        )
        description = (
            f'Ordered levels {ordered_levels[0]:g}/{ordered_levels[1]:g}; '
            f'qualified separation {separation:.2f} m.'
        )
    else:
        sources = _v3_template_sources(family, index, quarter_turns)
        truth = derive_aggregate_field_truth(
            sources,
            [-2.0, 2.0, -2.0, 2.0],
            disturbances,
            solver_settings=solver_settings,
        )
        description = f'Fresh sealed {family} slot {index + 1}.'
    local_sources = [
        source for source in sources
        if source.get('evaluation_role') == 'local_minimum'
    ]
    if spec['escape']:
        if not local_sources:
            raise RuntimeError(
                f'{case_id} has no designated local branch'
            )
        truth = attach_local_branch_qualifications(
            truth,
            sources,
            [source['id'] for source in local_sources],
            disturbances,
        )
    elif local_sources:
        raise RuntimeError(
            f'{case_id} has an undeclared local branch'
        )
    success, applicability = _v3_case_success(
        case_id,
        spec['escape'],
        spec['revisit'],
        spec['saturation'],
        merge=spec['merge'],
        assist=spec['assist'],
    )
    success['ground_truth']['aggregate_field'] = truth
    applicability['delay'] = (
        spec['sensor_delay_sec'] > 0.0
        or spec['pose_delay_sec'] > 0.0
    )
    starts = (
        (-1.30, -1.00, 0.0),
        (-1.20, 0.95, math.pi / 2.0),
        (1.10, -1.10, math.pi),
        (1.20, 0.90, 3.0 * math.pi / 2.0),
        (0.0, -1.35, math.pi / 4.0),
    )
    unused_x, unused_y, yaw = starts[
        (index + quarter_turns) % len(starts)
    ]
    if spec['escape']:
        start_x = float(local_sources[0]['x_m'])
        start_y = float(local_sources[0]['y_m'])
    else:
        start_x = unused_x
        start_y = unused_y
    case = {
        'case_id': case_id,
        'family': {
            'ordered_two_source': 'two_source',
            'multi_close_overlap': 'multi_source',
            'wall_corner': 'boundary',
            'noise_delay': 'noise_delay',
            'constraint_recovery': 'starts_saturation',
            'lifecycle': 'escape',
        }[family],
        'description': description,
        'status': 'executable_unverified',
        'profiles': ['robust_gaussian_v1'],
        'seeds': [rng.randrange(100000, 1000000)],
        'starts': [{
            'id': 'sealed_start',
            'x_m': start_x,
            'y_m': start_y,
            'yaw_rad': yaw,
        }],
        'sources': sources,
        'disturbances': disturbances,
        'algorithm': {
            'ablations': {
                'gaussian_fill_enabled': True,
                'affine_assist_enabled': True,
                'recenter_enabled': True,
            },
            'launch_overrides': dict(V3_COMMON_OVERRIDES),
        },
        'success': success,
        'acceptance_family': family,
        'acceptance_partition': partition,
        'metric_applicability': applicability,
    }
    return case


def generate_v3_acceptance_population(
    seed_bytes,
    historical_case_keys=None,
    solver_settings=None,
):
    """Generate the complete predeclared 70+10 schema-v4 population."""
    if not isinstance(seed_bytes, bytes) or len(seed_bytes) != 32:
        raise ValueError('v3 generator seed must contain exactly 256 bits')
    rng = random.Random(int.from_bytes(seed_bytes, byteorder='big'))
    suite = {
        'schema_version': 4,
        'suite_id': 'phase08_v3_sealed_acceptance',
        'description': (
            'Predeclared Phase 08.3 unique and reproducibility cases.'
        ),
        'mode': 'simulation',
        'execution': {
            'max_parallel_runs': 1,
            'gazebo_gui': False,
            'preflight_timeout_sec': 150.0,
            'run_timeout_sec': 240.0,
            'wall_timeout_sec': 600.0,
            'shutdown_grace_sec': 30.0,
            'stop_on_run_failure': False,
            'stop_on_cleanup_failure': True,
        },
        'metadata': {
            'experiment_version': 'phase08-v3',
            'operator_notes': (
                'Generated, hashed, and checkpointed before activation; '
                'identities were researcher-visible.'
            ),
            'population_visibility': (
                'researcher_visible_before_activation'
            ),
            'selection_blind': False,
        },
        'level_map': {},
        'defaults': {
            'bounds_m': [-2.0, 2.0, -2.0, 2.0],
            'room_center_m': [0.0, 0.0],
            'disturbances': {
                'sensor_noise': {'model': 'none', 'bound': 0.0},
                'sensor_delay_sec': 0.0,
                'pose_delay_sec': 0.0,
            },
            'validation_world': True,
            'simulation_contacts_enabled': True,
        },
        'cases': [],
    }
    levels = (450.0, 800.0, 1200.0, 1800.0, 2500.0)
    for family in sorted(ACCEPTANCE_FAMILIES):
        allocation = V3_FAMILY_ALLOCATION[family]
        count = allocation['unique']
        holdout_indexes = set(rng.sample(
            range(count),
            allocation['holdout'],
        ))
        for index in range(count):
            partition = (
                'holdout' if index in holdout_indexes else 'validation'
            )
            ordered_levels = None
            if family == 'ordered_two_source':
                ordered_levels = (
                    levels[index // len(levels)],
                    levels[index % len(levels)],
                )
            suite['cases'].append(_v3_make_case(
                suite,
                rng,
                family,
                index,
                partition,
                solver_settings,
                ordered_levels=ordered_levels,
            ))
    unique_cases = list(suite['cases'])
    by_family = {
        family: [
            case for case in unique_cases
            if case['acceptance_family'] == family
        ]
        for family in sorted(ACCEPTANCE_FAMILIES)
    }
    repeat_cases = []
    for family in sorted(ACCEPTANCE_FAMILIES):
        references = rng.sample(
            by_family[family],
            V3_FAMILY_ALLOCATION[family]['reproducibility'],
        )
        for index, reference in enumerate(references, start=1):
            reference_resolved = _v3_resolved_case(suite, reference)
            repeat = json.loads(json.dumps(reference))
            repeat['case_id'] = (
                f'v3_repeat_{family}_{index:02d}_'
                f'{rng.getrandbits(48):012x}'
            )
            repeat['description'] = (
                f'Preselected repeat of {reference["case_id"]}.'
            )
            repeat['acceptance_partition'] = 'reproducibility'
            repeat['repeat_reference'] = {
                'partition': reference['acceptance_partition'],
                'case_key': reference_resolved['case_key'],
            }
            repeat['success']['controller']['contract_id'] = (
                repeat['case_id']
            )
            repeat_cases.append(repeat)
    suite['cases'].extend(repeat_cases)
    validation = validate_v3_population(
        suite,
        historical_case_keys=historical_case_keys,
    )
    if not validation['passed']:
        raise RuntimeError(
            'generated v3 population is invalid: '
            + '; '.join(validation['reasons'])
        )
    return suite


def validate_v3_population(document, historical_case_keys=None):
    """Validate counts, aggregate records, identities, and repeat mappings."""
    reasons = []
    cases = document.get('cases', [])
    if document.get('schema_version') != 4:
        reasons.append('scenario schema version is not 4')
    if len(cases) != V3_EXPECTED_COUNTS['acceptance_total']:
        reasons.append('population does not contain exactly 80 cases')
    partition_counts = Counter(
        case.get('acceptance_partition') for case in cases
    )
    for partition in ('holdout', 'validation', 'reproducibility'):
        expected = V3_EXPECTED_COUNTS[partition]
        if partition_counts[partition] != expected:
            reasons.append(
                f'{partition} count is {partition_counts[partition]}, '
                f'expected {expected}'
            )
    unique_cases = [
        case for case in cases
        if case.get('acceptance_partition') in {'holdout', 'validation'}
    ]
    resolved_pairs = []
    for case in cases:
        try:
            truth = case['success']['ground_truth']['aggregate_field']
            validate_aggregate_field_truth(
                truth,
                case['sources'],
                [-2.0, 2.0, -2.0, 2.0],
                case.get(
                    'disturbances',
                    document['defaults']['disturbances'],
                ),
            )
            resolved_pairs.append((
                case,
                _v3_resolved_case(document, case),
            ))
        except Exception as exc:
            reasons.append(
                f'{case.get("case_id", "<missing>")} qualification failed: '
                f'{type(exc).__name__}: {exc}'
            )
    resolved = [item for unused, item in resolved_pairs]
    keys = [item['case_key'] for item in resolved]
    if len(keys) != len(set(keys)):
        reasons.append('population case keys are not unique')
    historical = set(historical_case_keys or [])
    collisions = sorted(historical & set(keys))
    if collisions:
        reasons.append(
            f'{len(collisions)} population keys collide with prior inputs'
        )
    unique_by_key = {
        item['case_key']: (case, item)
        for case, item in resolved_pairs
        if item['acceptance_partition'] in {'holdout', 'validation'}
    }
    unique_keys = set(unique_by_key)
    family_partition = Counter(
        (
            case.get('acceptance_family'),
            case.get('acceptance_partition'),
        )
        for case in unique_cases
    )
    for family, allocation in V3_FAMILY_ALLOCATION.items():
        for partition in ('holdout', 'validation'):
            if family_partition[(family, partition)] != allocation[partition]:
                reasons.append(
                    f'{family} {partition} allocation drifted'
                )
    lifecycle_counts = Counter()
    ordered_pairs = set()
    expected_ordered_pairs = {
        (left, right)
        for left in (450.0, 800.0, 1200.0, 1800.0, 2500.0)
        for right in (450.0, 800.0, 1200.0, 1800.0, 2500.0)
    }
    multi_source_counts = {}
    for case in unique_cases:
        family = case.get('acceptance_family')
        match = re.fullmatch(
            rf'v3_{re.escape(str(family))}_(\d{{2}})_[0-9a-f]{{12}}',
            str(case.get('case_id', '')),
        )
        if match is None:
            reasons.append(
                f'{case.get("case_id")} does not match generator identity'
            )
            continue
        index = int(match.group(1)) - 1
        allocation = V3_FAMILY_ALLOCATION.get(family)
        if allocation is None or not 0 <= index < allocation['unique']:
            reasons.append(
                f'{case.get("case_id")} generator index is invalid'
            )
            continue
        spec = _v3_family_specs(family, allocation['unique'])[index]
        applicability = case.get('metric_applicability', {})
        for name, expected_value in (
            ('escape_attempt', spec['escape']),
            ('escape_duration', spec['escape']),
            ('orbit_count', spec['escape']),
            ('revisit', spec['revisit']),
            (
                'delay',
                spec['sensor_delay_sec'] > 0.0
                or spec['pose_delay_sec'] > 0.0,
            ),
            ('saturation', spec['saturation']),
        ):
            if applicability.get(name) is not expected_value:
                reasons.append(
                    f'{case.get("case_id")} {name} applicability drifted'
                )
        controller = case.get('success', {}).get('controller', {})
        path = controller.get('required_state_path', [])
        events = controller.get('required_events', [])
        if ('ESCAPE_ASSIST' in path) is not spec['assist']:
            reasons.append(
                f'{case.get("case_id")} assist template drifted'
            )
        if ('FILL_MERGED' in events) is not spec['merge']:
            reasons.append(
                f'{case.get("case_id")} merge template drifted'
            )
        local_sources = [
            source for source in case.get('sources', [])
            if source.get('evaluation_role') == 'local_minimum'
        ]
        aggregate = (
            case.get('success', {})
            .get('ground_truth', {})
            .get('aggregate_field', {})
        )
        proof = aggregate.get('local_branch_qualifications')
        if spec['escape']:
            lifecycle_counts['escape'] += 1
            if not local_sources or not isinstance(proof, dict):
                reasons.append(
                    f'{case.get("case_id")} lacks local branch proof'
                )
            else:
                proof_points = proof.get('points')
                if isinstance(proof_points, list):
                    proof_ids = {
                        point.get('source_id') for point in proof_points
                    }
                else:
                    proof_ids = set(proof.get('source_ids', []))
                if proof_ids != {
                    source['id'] for source in local_sources
                }:
                    reasons.append(
                        f'{case.get("case_id")} local proof IDs drifted'
                    )
                start = case.get('starts', [{}])[0]
                if (
                    start.get('x_m') != local_sources[0].get('x_m')
                    or start.get('y_m') != local_sources[0].get('y_m')
                ):
                    reasons.append(
                        f'{case.get("case_id")} does not start at its '
                        'qualified local branch'
                    )
        elif local_sources or proof is not None:
            reasons.append(
                f'{case.get("case_id")} has an undeclared local branch'
            )
        lifecycle_counts['revisit'] += int(spec['revisit'])
        lifecycle_counts['assist'] += int(spec['assist'])
        lifecycle_counts['merge'] += int(spec['merge'])
        if family == 'ordered_two_source':
            sources = case.get('sources', [])
            if len(sources) != 2:
                reasons.append(
                    f'{case.get("case_id")} ordered topology drifted'
                )
            else:
                ordered_pairs.add(tuple(
                    float(source['relative_lumen_input'])
                    for source in sources
                ))
        elif family == 'multi_close_overlap':
            multi_source_counts[index] = len(case.get('sources', []))
        elif family == 'wall_corner':
            sources = case.get('sources', [])
            if len(sources) != 2:
                reasons.append(
                    f'{case.get("case_id")} boundary topology drifted'
                )
    if ordered_pairs != expected_ordered_pairs:
        reasons.append('ordered two-source Cartesian coverage drifted')
    if multi_source_counts != {
        0: 3,
        1: 3,
        2: 3,
        3: 4,
        4: 4,
        5: 3,
        6: 3,
        7: 4,
        8: 4,
    }:
        reasons.append('multi/close/overlap source topology drifted')
    if lifecycle_counts != Counter({
        'escape': 39,
        'revisit': 24,
        'assist': 6,
        'merge': 4,
    }):
        reasons.append('fixed lifecycle allocation drifted')
    repeat_keys = []
    repeat_families = Counter()
    for case in cases:
        if case.get('acceptance_partition') != 'reproducibility':
            continue
        reference = case.get('repeat_reference', {})
        reference_key = reference.get('case_key')
        if reference_key not in unique_keys:
            reasons.append(
                f'{case.get("case_id")} has an unknown repeat reference'
            )
        else:
            reference_case, reference_resolved = unique_by_key[reference_key]
            if (
                reference.get('partition')
                != reference_resolved['acceptance_partition']
            ):
                reasons.append(
                    f'{case.get("case_id")} repeat partition drifted'
                )
            if (
                case.get('acceptance_family')
                != reference_case.get('acceptance_family')
            ):
                reasons.append(
                    f'{case.get("case_id")} repeat family drifted'
                )
            normalized_repeat = json.loads(json.dumps(case))
            normalized_repeat['case_id'] = reference_case['case_id']
            normalized_repeat['description'] = reference_case['description']
            normalized_repeat['acceptance_partition'] = (
                reference_case['acceptance_partition']
            )
            normalized_repeat.pop('repeat_reference', None)
            normalized_repeat['success']['controller']['contract_id'] = (
                reference_case['success']['controller']['contract_id']
            )
            normalized_reference = json.loads(json.dumps(reference_case))
            normalized_reference.pop('repeat_reference', None)
            if normalized_repeat != normalized_reference:
                reasons.append(
                    f'{case.get("case_id")} repeat inputs drifted'
                )
        repeat_keys.append(reference_key)
        repeat_families[case.get('acceptance_family')] += 1
    if len(repeat_keys) != len(set(repeat_keys)):
        reasons.append('repeat references must be ten distinct unique cases')
    for family, allocation in V3_FAMILY_ALLOCATION.items():
        if repeat_families[family] != allocation['reproducibility']:
            reasons.append(
                f'{family} reproducibility allocation drifted'
            )
    return {
        'passed': not reasons,
        'reasons': reasons,
        'partition_counts': dict(sorted(partition_counts.items())),
        'family_partition_counts': {
            f'{family}.{partition}': count
            for (family, partition), count
            in sorted(family_partition.items())
        },
        'case_keys_sha256': canonical_sha256(sorted(keys)),
        'unique_case_key_count': len(set(keys)),
    }


def _v3_commitment_document(
    document,
    suite_bytes,
    historical_exclusion_hashes,
):
    family_counts = Counter(
        case['acceptance_family']
        for case in document['cases']
        if case['acceptance_partition'] in {'holdout', 'validation'}
    )
    commitment = {
        'schema_version': 1,
        'generator_version': 'phase08-v3-generator-1',
        'scenario_schema_version': 4,
        'counts': {
            'unique': 70,
            'holdout': 20,
            'validation': 50,
            'reproducibility': 10,
        },
        'family_counts': dict(sorted(family_counts.items())),
        'historical_exclusion_hashes': dict(sorted(
            historical_exclusion_hashes.items()
        )),
        'suite_sha256': _sha256_bytes(suite_bytes),
        'population_visibility': (
            'researcher_visible_before_activation'
        ),
        'selection_blind': False,
        'precommit_mechanism': 'canonical_json_sha256',
    }
    commitment['commitment_sha256'] = omission_sha256(
        commitment, 'commitment_sha256'
    )
    return commitment


def _v3_state_path(evidence_root, stage):
    return _state_root(evidence_root) / f'v3_{stage}.json'


def _v3_write_state(evidence_root, stage, document):
    value = dict(document)
    value['schema_version'] = 1
    value['experiment_version'] = 'phase08-v3'
    value['stage'] = stage
    if stage in {
        'contract',
        'holdout',
        'validation',
        'reproducibility',
        'terminal',
    }:
        if stage == 'terminal':
            value.setdefault('contract_sha256', None)
        elif stage != 'contract':
            if (
                not V3_CONTRACT_PATH.is_file()
            ):
                raise RuntimeError(
                    f'v3 {stage} requires the sealed acceptance contract'
                )
            else:
                contract = _load_json(V3_CONTRACT_PATH)
                contract_sha256 = require_omission_sha256(
                    contract,
                    'contract_sha256',
                    'v3 acceptance contract',
                )
                declared = value.get('contract_sha256')
                if declared not in (None, contract_sha256):
                    raise RuntimeError(
                        f'v3 {stage} contract hash drifted'
                    )
                value['contract_sha256'] = contract_sha256
        elif not value.get('contract_sha256'):
            raise RuntimeError(
                'v3 contract state must declare contract_sha256'
            )
    value['state_sha256'] = omission_sha256(value, 'state_sha256')
    path = _v3_state_path(evidence_root, stage)
    if path.exists():
        existing = _load_json(path)
        require_omission_sha256(
            existing, 'state_sha256', f'v3 {stage} state'
        )
        if existing != value:
            raise RuntimeError(
                f'v3 {stage} state is immutable and already exists'
            )
        return existing
    atomic_json(path, value)
    return value


def _v3_require_state(evidence_root, stage, require_pass=True):
    path = _v3_state_path(evidence_root, stage)
    if not path.is_file():
        raise RuntimeError(f'v3 {stage} state is missing')
    state = _load_json(path)
    require_omission_sha256(
        state, 'state_sha256', f'v3 {stage} state'
    )
    if require_pass and state.get('passed') is not True:
        raise RuntimeError(f'v3 {stage} did not pass')
    return state


def _v3_require_operator(state, operator, stage):
    """Keep one declared operator across a v3 workflow lineage."""
    if state.get('operator') != operator:
        raise RuntimeError(f'v3 {stage} operator drifted')


def _v3_historical_case_keys(include_v3_development=True):
    keys = set()
    hashes = {}
    excluded = {
        V3_CANDIDATES_PATH.name,
        V3_FROZEN_PATH.name,
    }
    for path in sorted(SCENARIO_ROOT.glob('phase08*.yaml')):
        if path.name in excluded:
            continue
        if not include_v3_development and path in {
            V3_ACTIVATION_PATH,
            V3_DEVELOPMENT_PATH,
        }:
            continue
        document = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not isinstance(document, dict) or 'cases' not in document:
            continue
        suite = load_suite(path)
        runs, unused = expand_suite(suite)
        del unused
        keys.update(run['case_key'] for run in runs)
        hashes[path.name] = file_sha256(path)
    return keys, hashes


def _v3_prepare_transaction_path(evidence_root):
    return Path(evidence_root) / 'prepare/prepare_transaction.json'


def _v3_load_prepare_transaction(path):
    transaction = _load_json(path)
    require_omission_sha256(
        transaction,
        'transaction_sha256',
        'v3 prepare transaction',
    )
    return transaction


def _v3_publish_prepare_transaction(
    root,
    transaction,
    *,
    operator,
    suite_path,
    commitment_path,
    restore_outputs,
):
    if (
        transaction.get('operator') != operator
        or transaction.get('suite_path')
        != str(suite_path.resolve())
        or transaction.get('commitment_path')
        != str(commitment_path.resolve())
    ):
        raise RuntimeError('v3 prepare transaction invocation drifted')
    suite_bytes = base64.b64decode(
        transaction['suite_base64'],
        validate=True,
    )
    commitment = transaction['commitment']
    commitment_hash = require_omission_sha256(
        commitment,
        'commitment_sha256',
        'acceptance commitment',
    )
    if (
        _sha256_bytes(suite_bytes) != commitment['suite_sha256']
        or commitment_hash != transaction['commitment_sha256']
    ):
        raise RuntimeError('v3 prepare transaction payload drifted')
    commitment_bytes = (
        json.dumps(
            commitment,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + '\n'
    ).encode('utf-8')
    for path, payload, mode in (
        (suite_path, suite_bytes, 0o644),
        (commitment_path, commitment_bytes, 0o644),
    ):
        if path.exists():
            if path.read_bytes() != payload:
                raise RuntimeError(
                    f'v3 prepare output drifted: {path}'
                )
        elif restore_outputs:
            atomic_bytes(path, payload, mode=mode)
        else:
            raise RuntimeError(f'v3 prepare output is missing: {path}')
    state = {
        'passed': True,
        'operator': operator,
        'lineage_id': transaction.get(
            'experiment_version', 'phase08-v3'
        ),
        'suite_path': str(suite_path.resolve()),
        'suite_sha256': commitment['suite_sha256'],
        'commitment_path': str(commitment_path.resolve()),
        'commitment_sha256': commitment_hash,
        'population_visibility': commitment['population_visibility'],
        'selection_blind': commitment['selection_blind'],
        'counts': commitment['counts'],
        'family_counts': commitment['family_counts'],
        'repository': transaction['repository'],
        'disk_forecast': transaction['disk_forecast'],
        'processes_before': transaction['processes_before'],
        'transaction_path': str(
            _v3_prepare_transaction_path(root).resolve()
        ),
        'transaction_sha256': transaction['transaction_sha256'],
    }
    if transaction.get('recovery') is not None:
        state['recovery'] = transaction['recovery']
    return _v3_write_state(root, 'prepare', state)


def _v3_harness_recovery_proof(
    superseded_evidence_root,
    correction_path=V3_CONTACT_CORRECTION_PATH,
):
    """Verify the immutable V3A contamination evidence and correction."""
    superseded_root = Path(
        superseded_evidence_root
    ).expanduser().resolve()
    correction_path = Path(correction_path).resolve()
    correction = _load_json(correction_path)
    correction_sha256 = require_omission_sha256(
        correction,
        'correction_sha256',
        'v3 contact-probe contamination audit',
    )
    if (
        Path(correction.get('superseded_evidence_root', '')).resolve()
        != superseded_root
    ):
        raise RuntimeError(
            'v3 contamination audit names a different superseded root'
        )
    policy = correction.get('correction', {})
    if (
        policy.get('probe_policy') != 'collision_expected_true_only'
        or policy.get('analysis_collision_filter_changed') is not False
        or policy.get('formal_collision_gate_changed') is not False
        or policy.get('fresh_activation_required') is not True
        or policy.get(
            'reuse_precommitted_population_byte_identically'
        ) is not True
    ):
        raise RuntimeError('v3 contamination correction policy drifted')
    contact_audit = correction.get('contact_audit', {})
    if (
        contact_audit.get('non_ground_contact_state_count') != 105
        or contact_audit.get(
            'positive_control_contact_state_count'
        ) != 105
        or contact_audit.get('other_non_ground_contact_state_count') != 0
    ):
        raise RuntimeError('v3 contamination contact audit drifted')

    prepare = _v3_require_state(superseded_root, 'prepare')
    qualification = _v3_require_state(
        superseded_root, 'qualification'
    )
    activation = _v3_require_state(
        superseded_root,
        'activation',
        require_pass=False,
    )
    if (
        activation.get('passed') is not False
        or qualification.get('prepare_state_sha256')
        != prepare['state_sha256']
        or activation.get('qualification_state_sha256')
        != qualification['state_sha256']
        or activation.get('run_count') != 1
        or activation.get('integrity_pass_count') != 0
        or activation.get('contract_pass_count') != 0
        or len(activation.get('not_run_slot_ids', [])) != 9
        or 'non-ground collision' not in str(
            activation.get('stopped_early_reason')
        )
    ):
        raise RuntimeError(
            'superseded v3 activation is not the audited failed state'
        )
    precommit = correction.get('precommit', {})
    if (
        precommit.get('suite_sha256') != prepare.get('suite_sha256')
        or precommit.get('commitment_sha256')
        != prepare.get('commitment_sha256')
    ):
        raise RuntimeError(
            'superseded v3 precommit differs from contamination audit'
        )

    progress_path = superseded_root / 'activation/progress.json'
    records_path = superseded_root / 'activation/records.json'
    activation_path = _v3_state_path(superseded_root, 'activation')
    progress = _v3_load_progress(superseded_root / 'activation')
    records = _load_json(records_path)
    if (
        progress is None
        or progress.get('progress_sha256')
        != activation.get('progress_sha256')
        or len(records) != 1
        or activation.get('records_sha256') != file_sha256(records_path)
    ):
        raise RuntimeError(
            'superseded v3 activation aggregates differ from state'
        )
    record = records[0]
    case_id = 'v3a_goal_aggregate_direct'
    record_path_text = progress.get('final_record_paths', {}).get(
        case_id
    )
    if not record_path_text:
        raise RuntimeError(
            'superseded v3 activation lacks its audited attempt record'
        )
    record_path = Path(record_path_text)
    retained_record = _load_json(record_path)
    if retained_record != record:
        raise RuntimeError(
            'superseded v3 final record differs from its aggregate'
        )
    if (
        record.get('case_id') != case_id
        or record.get('run_id') != correction.get('run_id')
        or record.get('classification', {}).get('status') != 'failed'
        or record.get('classification', {}).get(
            'infrastructure_status'
        ) != 'completed'
        or record.get('analysis', {}).get('metrics', {}).get(
            'collision', {}
        ).get('value') is not True
        or record.get('success_contract', {}).get(
            'collision_expected'
        ) is not False
    ):
        raise RuntimeError(
            'superseded v3 attempt is not the audited contamination run'
        )

    run_directory = Path(record['run_directory'])
    metadata_path = run_directory / 'metadata.yaml'
    resolved_path = run_directory / 'resolved_scenario.yaml'
    result_path = run_directory / 'scenario_result.yaml'
    metadata = yaml.safe_load(
        metadata_path.read_text(encoding='utf-8')
    )
    resolved = yaml.safe_load(
        resolved_path.read_text(encoding='utf-8')
    )
    if (
        'simulation_contact_probe_enabled:=True'
        not in metadata.get('target_argv', [])
        or metadata.get('recording', {}).get(
            'readiness_ever_true'
        ) is not True
        or resolved.get('success', {}).get(
            'collision_expected'
        ) is not False
    ):
        raise RuntimeError(
            'superseded v3 launch does not prove probe contamination'
        )
    corrected_command = build_launch_command(resolved, gui=True)
    if (
        'simulation_contacts_enabled:=True' not in corrected_command
        or 'simulation_contact_probe_enabled:=False'
        not in corrected_command
        or 'simulation_contact_probe_enabled:=True'
        in corrected_command
    ):
        raise RuntimeError(
            'corrected launch does not preserve passive contact evidence'
        )

    raw_hashes = (
        record.get('analysis_completeness', {})
        .get('raw_bag_sha256', {})
    )
    if len(raw_hashes) != 1:
        raise RuntimeError(
            'superseded v3 attempt has ambiguous raw-bag evidence'
        )
    raw_bag_path_text, retained_raw_hash = next(iter(raw_hashes.items()))
    raw_bag_path = Path(raw_bag_path_text)
    artifact_paths = {
        'activation_state_file_sha256': activation_path,
        'activation_progress_file_sha256': progress_path,
        'activation_records_file_sha256': records_path,
        'attempt_record_file_sha256': record_path,
        'raw_bag_file_sha256': raw_bag_path,
        'resolved_scenario_file_sha256': resolved_path,
        'metadata_file_sha256': metadata_path,
        'scenario_result_file_sha256': result_path,
    }
    expected_hashes = correction.get('original_artifacts', {})
    for field, path in artifact_paths.items():
        if (
            not path.is_file()
            or expected_hashes.get(field) != file_sha256(path)
        ):
            raise RuntimeError(
                f'superseded v3 contamination artifact drifted: {field}'
            )
    if (
        retained_raw_hash
        != expected_hashes.get('raw_bag_file_sha256')
        or activation.get('state_sha256')
        != expected_hashes.get('activation_state_sha256')
    ):
        raise RuntimeError(
            'superseded v3 retained hashes differ from contamination audit'
        )
    return {
        'kind': 'contact_probe_instrumentation_contamination',
        'superseded_evidence_root': str(superseded_root),
        'superseded_prepare_state_sha256': prepare['state_sha256'],
        'superseded_qualification_state_sha256': (
            qualification['state_sha256']
        ),
        'superseded_activation_state_sha256': activation['state_sha256'],
        'superseded_suite_sha256': prepare['suite_sha256'],
        'superseded_commitment_sha256': prepare['commitment_sha256'],
        'correction_audit_path': str(correction_path),
        'correction_audit_sha256': correction_sha256,
        'run_id': record['run_id'],
        'original_artifacts': dict(expected_hashes),
        'contact_audit': dict(contact_audit),
        'policy': dict(policy),
    }


def _v3_behavioral_miss_audit(record):
    """Project one retained record into the V3B correction audit."""
    analysis = record.get('analysis', {})
    completeness = record.get('analysis_completeness', {})
    classification = record.get('classification', {})
    predicates = classification.get('predicate_results', {})
    metrics = analysis.get('metrics', {})
    contract_predicate_names = (
        'controller_goal',
        'expected_terminal_state',
        'ground_truth_goal',
        'no_forbidden_events',
        'no_forbidden_states',
        'required_events',
        'required_state_path',
    )
    return {
        'analysis_failures': completeness.get('analysis_failures'),
        'analysis_status': analysis.get('analysis_status'),
        'applicability_integrity_passed': analysis.get(
            'applicability_integrity', {}
        ).get('passed'),
        'applicability_integrity_reasons': analysis.get(
            'applicability_integrity', {}
        ).get('reasons'),
        'classification_status': classification.get('status'),
        'cleanup_complete': record.get('cleanup', {}).get('passed'),
        'collision': metrics.get('collision', {}).get('value'),
        'contract_predicates': {
            name: predicates.get(name)
            for name in contract_predicate_names
        },
        'critical_inputs_complete': (
            isinstance(completeness.get('critical_inputs'), dict)
            and bool(completeness['critical_inputs'])
            and all(
                value is True
                for value in completeness['critical_inputs'].values()
            )
        ),
        'failsafe': metrics.get('failsafe', {}).get('value'),
        'final_aggregate_target_distance_m': metrics.get(
            'final_aggregate_target_distance', {}
        ).get('value'),
        'fresh_phase05_validation_passed': completeness.get(
            'fresh_phase05_validation', {}
        ).get('passed'),
        'infrastructure_status': classification.get(
            'infrastructure_status'
        ),
        'invalid_metric_count': sum(
            metric.get('status') == 'invalid'
            for metric in metrics.values()
        ),
        'observed_state_sequence': record.get('outcomes', {}).get(
            'observed_state_sequence'
        ),
        'recording_complete': record.get('recording_complete'),
        'recording_failures': completeness.get('recording_failures'),
        'terminal_state': metrics.get('terminal_state', {}).get('value'),
        'timeout': metrics.get('timeout', {}).get('value'),
    }


def _v3_hard_stop_policy_recovery_proof(
    superseded_evidence_root,
    correction_path=V3_HARD_STOP_CORRECTION_PATH,
):
    """Verify immutable V3B evidence and the bounded dispatch correction."""
    superseded_root = Path(
        superseded_evidence_root
    ).expanduser().resolve()
    correction_path = Path(correction_path).resolve()
    correction = _load_json(correction_path)
    correction_sha256 = require_omission_sha256(
        correction,
        'correction_sha256',
        'v3 behavioral-miss routing audit',
    )
    if (
        correction.get('classification')
        != 'behavioral_miss_diagnostic_completion'
        or Path(
            correction.get('superseded_evidence_root', '')
        ).resolve() != superseded_root
    ):
        raise RuntimeError(
            'v3 behavioral-miss audit names a different failure'
        )
    retained_audit = correction.get('retained_evidence_audit', {})
    retained_path = Path(retained_audit.get('path', ''))
    if not retained_path.is_absolute():
        retained_path = REPOSITORY_ROOT / retained_path
    retained_path = retained_path.resolve()
    if (
        not retained_path.is_file()
        or retained_audit.get('file_sha256')
        != file_sha256(retained_path)
    ):
        raise RuntimeError('v3 retained behavioral-miss audit drifted')
    retained_correction = _load_json(retained_path)
    retained_sha256 = require_omission_sha256(
        retained_correction,
        'correction_sha256',
        'v3 retained behavioral-miss audit',
    )
    if (
        retained_audit.get('omission_sha256') != retained_sha256
        or retained_correction.get('classification')
        != 'behavioral_miss_routing_misclassified'
        or Path(
            retained_correction.get('superseded_evidence_root', '')
        ).resolve() != superseded_root
    ):
        raise RuntimeError(
            'v3 retained behavioral-miss audit binding drifted'
        )
    policy = correction.get('correction', {})
    if (
        policy.get('hard_stop_policy')
        != 'pure_applicability_partial_is_behavioral_miss'
        or policy.get('fresh_lineage_id') != 'phase08-v3c'
        or policy.get('carry_superseded_behavioral_failure') is not True
        or policy.get('carry_failed_slot_byte_identically') is not True
        or policy.get('execute_only_never_run_activation_cases') is not True
        or policy.get('composite_activation_forced_fail') is not True
        or policy.get('rerun_all_activation_cases') is not False
        or policy.get('rerun_carried_case') is not False
        or policy.get('m4_prohibited') is not True
        or policy.get('phase08_v3_terminal_failure_required') is not True
        or policy.get(
            'reuse_precommitted_population_byte_identically'
        ) is not True
        or policy.get('activation_cases_changed') is not False
        or policy.get('analyzer_output_changed') is not False
        or policy.get('behavior_contract_changed') is not False
        or policy.get('collision_gate_changed') is not False
        or policy.get('final_record_integrity_gate_changed') is not False
    ):
        raise RuntimeError(
            'v3 behavioral-miss correction policy drifted'
        )
    allowed_runtime_correction_sha256 = policy.get(
        'allowed_runtime_correction_sha256'
    )
    if (
        not isinstance(allowed_runtime_correction_sha256, dict)
        or set(allowed_runtime_correction_sha256)
        != set(V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT)
        or any(
            re.fullmatch(r'[0-9a-f]{64}', str(expected)) is None
            or not (REPOSITORY_ROOT / path).is_file()
            or file_sha256(REPOSITORY_ROOT / path) != expected
            for path, expected in (
                allowed_runtime_correction_sha256.items()
            )
        )
    ):
        raise RuntimeError(
            'v3 allowed runtime-correction hash mapping drifted'
        )
    composite_activation = correction.get('composite_activation', {})
    carried_audit = correction.get('carried_record', {})
    expected_execute_case_ids = [
        'v3a_below_target_fill',
        'v3a_pure_escape_recenter',
        'v3a_stalled_assist',
        'v3a_fill_merge',
        'v3a_full_lifecycle_goal',
        'v3a_revisit_guard',
        'v3a_boundary_saturation',
        'v3a_noise_delay',
        'v3a_safe_timeout',
    ]
    if (
        composite_activation.get('carried_record_count') != 1
        or composite_activation.get('new_execution_count') != 9
        or composite_activation.get('composite_slot_count') != 10
        or composite_activation.get('terminal_activation_passed')
        is not False
        or composite_activation.get('execute_case_ids')
        != expected_execute_case_ids
        or carried_audit.get('case_id')
        != 'v3a_goal_aggregate_direct'
        or carried_audit.get('source_lineage_id') != 'phase08-v3b'
    ):
        raise RuntimeError(
            'v3 diagnostic-completion allocation drifted'
        )

    prepare = _v3_require_state(superseded_root, 'prepare')
    qualification = _v3_require_state(
        superseded_root, 'qualification'
    )
    activation = _v3_require_state(
        superseded_root,
        'activation',
        require_pass=False,
    )
    if (
        prepare.get('lineage_id') != 'phase08-v3b'
        or qualification.get('lineage_id') != 'phase08-v3b'
        or qualification.get('prepare_state_sha256')
        != prepare.get('state_sha256')
        or activation.get('qualification_state_sha256')
        != qualification.get('state_sha256')
        or activation.get('passed') is not False
        or activation.get('run_count') != 1
        or activation.get('integrity_pass_count') != 0
        or activation.get('contract_pass_count') != 0
        or activation.get('not_run_slot_ids')
        != expected_execute_case_ids
        or 'analysis is not complete' not in str(
            activation.get('stopped_early_reason')
        )
    ):
        raise RuntimeError(
            'superseded V3B activation is not the audited failed state'
        )

    nested_recovery = prepare.get('recovery')
    nested_audit = correction.get('nested_recovery', {})
    if (
        not isinstance(nested_recovery, dict)
        or nested_recovery.get('kind')
        != 'contact_probe_instrumentation_contamination'
        or nested_audit.get('kind') != nested_recovery.get('kind')
        or nested_audit.get('recovery_sha256')
        != canonical_sha256(nested_recovery)
        or Path(
            nested_audit.get('superseded_evidence_root', '')
        ).resolve()
        != Path(
            nested_recovery.get('superseded_evidence_root', '')
        ).resolve()
    ):
        raise RuntimeError('V3B nested V3A recovery binding drifted')
    observed_nested_recovery = _v3_harness_recovery_proof(
        nested_recovery['superseded_evidence_root'],
        correction_path=nested_recovery['correction_audit_path'],
    )
    if observed_nested_recovery != nested_recovery:
        raise RuntimeError('V3B nested V3A recovery proof drifted')

    progress_path = superseded_root / 'activation/progress.json'
    records_path = superseded_root / 'activation/records.json'
    attempt_records_path = (
        superseded_root / 'activation/attempt_records.json'
    )
    summary_path = superseded_root / 'activation/scenario_summary.yaml'
    transaction_path = _v3_prepare_transaction_path(superseded_root)
    prepare_path = _v3_state_path(superseded_root, 'prepare')
    qualification_path = _v3_state_path(
        superseded_root, 'qualification'
    )
    activation_path = _v3_state_path(superseded_root, 'activation')
    progress = _v3_load_progress(superseded_root / 'activation')
    records = _load_json(records_path)
    attempt_records = _load_json(attempt_records_path)
    transaction = _v3_load_prepare_transaction(transaction_path)
    if (
        progress is None
        or progress.get('progress_sha256')
        != activation.get('progress_sha256')
        or progress.get('stopped_early_reason')
        != activation.get('stopped_early_reason')
        or progress.get('not_run_slot_ids')
        != expected_execute_case_ids
        or len(records) != 1
        or records != attempt_records
        or activation.get('records_sha256')
        != file_sha256(records_path)
        or activation.get('attempt_records_sha256')
        != file_sha256(attempt_records_path)
        or activation.get('scenario_summary_sha256')
        != file_sha256(summary_path)
        or transaction.get('transaction_sha256')
        != prepare.get('transaction_sha256')
        or Path(transaction.get('evidence_root', '')).resolve()
        != superseded_root
    ):
        raise RuntimeError('superseded V3B aggregate evidence drifted')
    case_id = 'v3a_goal_aggregate_direct'
    record_path_text = progress.get('final_record_paths', {}).get(
        case_id
    )
    if not record_path_text:
        raise RuntimeError('superseded V3B attempt record is missing')
    record_path = Path(record_path_text)
    record = _load_json(record_path)
    if record != records[0]:
        raise RuntimeError(
            'superseded V3B final record differs from its aggregate'
        )
    run_directory = Path(record.get('run_directory', ''))
    run_directory_manifest = _v3_directory_manifest(run_directory)
    metadata_path = run_directory / 'metadata.yaml'
    run_completeness_path = run_directory / 'completeness.json'
    bag_metadata_path = run_directory / 'bag/metadata.yaml'
    resolved_path = run_directory / 'resolved_scenario.yaml'
    result_path = run_directory / 'scenario_result.yaml'
    analysis_path = (
        run_directory / 'analysis/phase08/summary_metrics.json'
    )
    completeness_path = (
        run_directory / 'analysis/phase08/analysis_completeness.json'
    )
    raw_hashes = record.get(
        'analysis_completeness', {}
    ).get('raw_bag_sha256', {})
    if not isinstance(raw_hashes, dict) or len(raw_hashes) != 1:
        raise RuntimeError(
            'superseded V3B raw-bag evidence is ambiguous'
        )
    raw_bag_path_text, retained_raw_hash = next(iter(raw_hashes.items()))
    raw_bag_path = Path(raw_bag_path_text)
    artifact_paths = {
        'prepare_state_file_sha256': prepare_path,
        'qualification_state_file_sha256': qualification_path,
        'activation_state_file_sha256': activation_path,
        'transaction_file_sha256': transaction_path,
        'activation_progress_file_sha256': progress_path,
        'activation_records_file_sha256': records_path,
        'activation_attempt_records_file_sha256': attempt_records_path,
        'activation_scenario_summary_file_sha256': summary_path,
        'attempt_record_file_sha256': record_path,
        'metadata_file_sha256': metadata_path,
        'resolved_scenario_file_sha256': resolved_path,
        'scenario_result_file_sha256': result_path,
        'analysis_summary_file_sha256': analysis_path,
        'analysis_completeness_file_sha256': completeness_path,
        'raw_bag_file_sha256': raw_bag_path,
    }
    expected_hashes = retained_correction.get('original_artifacts', {})
    for field, path in artifact_paths.items():
        if (
            not path.is_file()
            or expected_hashes.get(field) != file_sha256(path)
        ):
            raise RuntimeError(
                f'superseded V3B artifact drifted: {field}'
            )
    if (
        carried_audit.get('run_directory_file_count')
        != run_directory_manifest['file_count']
        or carried_audit.get('run_directory_manifest_sha256')
        != run_directory_manifest['manifest_sha256']
        or not run_completeness_path.is_file()
        or carried_audit.get('completeness_sha256')
        != file_sha256(run_completeness_path)
        or not bag_metadata_path.is_file()
        or carried_audit.get('bag_metadata_sha256')
        != file_sha256(bag_metadata_path)
    ):
        raise RuntimeError(
            'superseded V3B run-directory evidence drifted'
        )
    if (
        activation.get('state_sha256')
        != expected_hashes.get('activation_state_sha256')
        or progress.get('progress_sha256')
        != expected_hashes.get('activation_progress_sha256')
        or retained_raw_hash
        != expected_hashes.get('raw_bag_file_sha256')
        or record.get('resolved_scenario_sha256')
        != file_sha256(resolved_path)
        or record.get('analysis_summary_sha256')
        != file_sha256(analysis_path)
        or record.get('analysis_completeness_sha256')
        != file_sha256(completeness_path)
    ):
        raise RuntimeError(
            'superseded V3B retained hashes differ from its audit'
        )
    if (
        record.get('case_id') != case_id
        or record.get('run_id') != carried_audit.get('run_id')
        or str(record_path.resolve())
        != str(Path(carried_audit.get('record_path', '')).resolve())
        or file_sha256(record_path)
        != carried_audit.get('record_sha256')
        or record.get('classification', {}).get('status')
        != carried_audit.get('classification_status')
        or record.get('classification', {}).get(
            'infrastructure_status'
        ) != carried_audit.get('infrastructure_status')
        or _v3_behavioral_miss_audit(record)
        != retained_correction.get('behavioral_result')
    ):
        raise RuntimeError(
            'superseded V3B record is not the audited behavior miss'
        )
    metadata = yaml.safe_load(
        metadata_path.read_text(encoding='utf-8')
    )
    resolved = yaml.safe_load(
        resolved_path.read_text(encoding='utf-8')
    )
    target_argv = metadata.get('target_argv', [])
    if (
        'gazebo_gui:=True' not in target_argv
        or 'simulation_contacts_enabled:=True' not in target_argv
        or 'simulation_contact_probe_enabled:=False'
        not in target_argv
        or 'simulation_contact_probe_enabled:=True' in target_argv
        or resolved.get('success', {}).get(
            'collision_expected'
        ) is not False
    ):
        raise RuntimeError(
            'superseded V3B launch is not the corrected contact run'
        )

    final_integrity = _v3_record_integrity(record)
    if (
        _v3_hard_stop_reason(
            record,
            allow_pure_applicability_miss=True,
        ) is not None
        or final_integrity.get('passed') is not False
        or 'metric applicability integrity failed'
        not in final_integrity.get('reasons', [])
    ):
        raise RuntimeError(
            'v3 behavioral-miss correction weakened or failed its boundary'
        )
    precommit = correction.get('precommit', {})
    commitment = _load_json(V3_COMMITMENT_PATH)
    if (
        precommit.get('suite_sha256') != prepare.get('suite_sha256')
        or precommit.get('commitment_sha256')
        != prepare.get('commitment_sha256')
        or precommit.get('suite_sha256')
        != file_sha256(V3_PRECOMMITTED_SUITE_PATH)
        or precommit.get('commitment_file_sha256')
        != file_sha256(V3_COMMITMENT_PATH)
        or precommit.get('commitment_sha256')
        != require_omission_sha256(
            commitment,
            'commitment_sha256',
            'acceptance commitment',
        )
    ):
        raise RuntimeError('V3B precommit differs from its correction audit')
    qualified = correction.get('qualified_runtime', {})
    qualified_repository = qualification.get('repository', {})
    if (
        qualified.get('qualification_state_sha256')
        != qualification.get('state_sha256')
        or qualified.get('runtime_input_commit')
        != qualified_repository.get('commit')
        or qualified.get('runtime_inputs_sha256')
        != qualified_repository.get(
            'runtime_inputs_sha256'
        )
    ):
        raise RuntimeError(
            'V3B qualified runtime differs from its correction audit'
        )
    runtime_commit = qualified_repository.get('commit')
    declared_execution_commit = qualified.get('execution_commit')
    try:
        resolved_runtime_commit = _git(
            'rev-parse',
            f'{runtime_commit}^{{commit}}',
        )
        resolved_execution_commit = _git(
            'rev-parse',
            f'{declared_execution_commit}^{{commit}}',
        )
        execution_line = _git(
            'rev-list',
            '--parents',
            '-n',
            '1',
            resolved_execution_commit,
        ).split()
        _git(
            'merge-base',
            '--is-ancestor',
            resolved_execution_commit,
            'HEAD',
        )
        execution_changed_paths = set(
            _git(
                'diff',
                '--name-only',
                resolved_runtime_commit,
                resolved_execution_commit,
            ).splitlines()
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            'V3B qualified execution commit proof failed'
        ) from exc
    if (
        resolved_runtime_commit != runtime_commit
        or len(execution_line) != 2
        or execution_line[0] != resolved_execution_commit
        or execution_line[1] != resolved_runtime_commit
        or qualified.get('execution_commit_resolved')
        != resolved_execution_commit
        or execution_changed_paths
        & set(qualified_repository.get('input_hashes', {}))
    ):
        raise RuntimeError(
            'V3B qualified execution commit boundary drifted'
        )
    baseline_runtime_projection = _v3_runtime_input_projection(
        qualified_repository
    )
    installed_activation = qualification.get(
        'installed_dry_runs', {}
    ).get('activation', {})
    activation_dry_run_path = Path(
        installed_activation.get('path', '')
    )
    if (
        not activation_dry_run_path.is_file()
        or installed_activation.get('sha256')
        != file_sha256(activation_dry_run_path)
    ):
        raise RuntimeError(
            'V3B qualified activation dry run drifted'
        )
    activation_invocation_contract = (
        _v3_activation_invocation_contract(
            yaml.safe_load(
                activation_dry_run_path.read_text(encoding='utf-8')
            )
        )
    )
    return {
        'kind': 'behavioral_miss_diagnostic_completion',
        'superseded_evidence_root': str(superseded_root),
        'superseded_prepare_state_sha256': prepare['state_sha256'],
        'superseded_qualification_state_sha256': (
            qualification['state_sha256']
        ),
        'superseded_activation_state_sha256': activation['state_sha256'],
        'superseded_suite_sha256': prepare['suite_sha256'],
        'superseded_commitment_sha256': prepare['commitment_sha256'],
        'correction_audit_path': str(correction_path),
        'correction_audit_sha256': correction_sha256,
        'run_id': record['run_id'],
        'carried_record': dict(carried_audit),
        'run_directory_manifest': run_directory_manifest,
        'composite_activation': dict(composite_activation),
        'baseline_runtime_projection': baseline_runtime_projection,
        'allowed_runtime_correction_sha256': dict(
            allowed_runtime_correction_sha256
        ),
        'activation_invocation_contract': (
            activation_invocation_contract
        ),
        'execution_commit': resolved_execution_commit,
        'original_artifacts': dict(expected_hashes),
        'behavioral_result': dict(
            retained_correction['behavioral_result']
        ),
        'retained_evidence_audit': dict(retained_audit),
        'nested_recovery': nested_recovery,
        'policy': dict(policy),
    }


def _v3_recovery_fresh_lineage_id(recovery):
    kind = recovery.get('kind')
    if kind == 'contact_probe_instrumentation_contamination':
        return 'phase08-v3b'
    if kind == 'behavioral_miss_diagnostic_completion':
        return 'phase08-v3c'
    raise RuntimeError(f'unsupported v3 recovery kind: {kind}')


def _v3_revalidate_recovery(recovery):
    """Recompute one retained recovery proof from its bound inputs."""
    kind = recovery.get('kind')
    if kind == 'contact_probe_instrumentation_contamination':
        return _v3_harness_recovery_proof(
            recovery['superseded_evidence_root'],
            correction_path=recovery['correction_audit_path'],
        )
    if kind == 'behavioral_miss_diagnostic_completion':
        return _v3_hard_stop_policy_recovery_proof(
            recovery['superseded_evidence_root'],
            correction_path=recovery['correction_audit_path'],
        )
    raise RuntimeError(f'unsupported v3 recovery kind: {kind}')


def _v3_adoption_recovery_proof(
    superseded_evidence_root,
    correction_path=None,
):
    """Select the fixed proof for the exact superseded lineage."""
    if correction_path is not None:
        return _v3_harness_recovery_proof(
            superseded_evidence_root,
            correction_path=correction_path,
        )
    superseded = _v3_require_state(
        superseded_evidence_root,
        'prepare',
    )
    if superseded.get('lineage_id') == 'phase08-v3b':
        return _v3_hard_stop_policy_recovery_proof(
            superseded_evidence_root,
        )
    return _v3_harness_recovery_proof(
        superseded_evidence_root,
    )


def _v3_adoption_matches_invocation(
    transaction,
    operator,
    evidence_root,
    superseded_evidence_root,
):
    recovery = transaction.get('recovery', {})
    expected_fresh_root = Path(evidence_root).expanduser().resolve()
    expected_root = Path(
        superseded_evidence_root
    ).expanduser().resolve()
    if (
        transaction.get('operator') != operator
        or Path(transaction.get('evidence_root', '')).resolve()
        != expected_fresh_root
        or transaction.get('experiment_version')
        != _v3_recovery_fresh_lineage_id(recovery)
        or Path(
            recovery.get('superseded_evidence_root', '')
        ).resolve() != expected_root
        or Path(
            recovery.get('policy', {}).get('fresh_evidence_root', '')
        ).resolve() != expected_fresh_root
    ):
        raise RuntimeError('v3 precommit adoption invocation drifted')


def run_v3_adopt_precommit(
    operator,
    evidence_root,
    superseded_evidence_root,
    *,
    suite_path=V3_PRECOMMITTED_SUITE_PATH,
    commitment_path=V3_COMMITMENT_PATH,
    correction_path=None,
):
    """Adopt the exact v3 precommit into a fresh corrected lineage."""
    root = Path(evidence_root).expanduser().resolve()
    superseded_root = Path(
        superseded_evidence_root
    ).expanduser().resolve()
    suite_path = Path(suite_path)
    commitment_path = Path(commitment_path)
    state_path = _v3_state_path(root, 'prepare')
    transaction_path = _v3_prepare_transaction_path(root)
    if state_path.is_file():
        transaction = _v3_load_prepare_transaction(transaction_path)
        _v3_adoption_matches_invocation(
            transaction,
            operator,
            root,
            superseded_root,
        )
        _v3_verify_repository_snapshot(transaction['repository'])
        observed_recovery = _v3_revalidate_recovery(
            transaction['recovery']
        )
        if observed_recovery != transaction['recovery']:
            raise RuntimeError(
                'v3 interrupted adoption recovery proof drifted'
            )
        _v3_verify_diagnostic_runtime_projection(
            transaction['recovery'],
            transaction['repository'],
        )
        return _v3_publish_prepare_transaction(
            root,
            transaction,
            operator=operator,
            suite_path=suite_path,
            commitment_path=commitment_path,
            restore_outputs=False,
        )
    if transaction_path.is_file():
        transaction = _v3_load_prepare_transaction(transaction_path)
        _v3_adoption_matches_invocation(
            transaction,
            operator,
            root,
            superseded_root,
        )
        _v3_verify_repository_snapshot(transaction['repository'])
        observed_recovery = _v3_revalidate_recovery(
            transaction['recovery']
        )
        if observed_recovery != transaction['recovery']:
            raise RuntimeError(
                'v3 interrupted adoption recovery proof drifted'
            )
        _v3_verify_diagnostic_runtime_projection(
            transaction['recovery'],
            transaction['repository'],
        )
        return _v3_publish_prepare_transaction(
            root,
            transaction,
            operator=operator,
            suite_path=suite_path,
            commitment_path=commitment_path,
            restore_outputs=False,
        )
    if root.exists():
        raise RuntimeError(
            'v3 precommit adoption requires an absent fresh evidence root'
        )
    if root == superseded_root:
        raise RuntimeError(
            'v3 corrected lineage must not reuse the superseded root'
        )
    if not suite_path.is_file() or not commitment_path.is_file():
        raise RuntimeError(
            'v3 precommit adoption requires the committed suite and '
            'commitment'
        )
    _v3_require_precommit_in_head()
    processes_before = _v3_active_processes()
    if processes_before:
        raise RuntimeError(
            'v3 precommit adoption process set is not clean'
        )
    repository = _v3_repository_snapshot(
        require_clean=True,
        extra_paths=(suite_path, commitment_path),
    )
    recovery = _v3_adoption_recovery_proof(
        superseded_root,
        correction_path=correction_path,
    )
    _v3_verify_diagnostic_runtime_projection(recovery, repository)
    declared_fresh_root = Path(
        recovery['policy'].get('fresh_evidence_root', '')
    ).resolve()
    if declared_fresh_root != root:
        raise RuntimeError(
            'v3 contamination audit names a different fresh root'
        )
    suite_bytes = suite_path.read_bytes()
    population = json.loads(suite_bytes.decode('utf-8'))
    if canonical_json_bytes(population) != suite_bytes:
        raise RuntimeError(
            'v3 adopted acceptance suite is not canonical JSON'
        )
    commitment = _load_json(commitment_path)
    commitment_sha256 = require_omission_sha256(
        commitment,
        'commitment_sha256',
        'acceptance commitment',
    )
    if (
        _sha256_bytes(suite_bytes) != commitment.get('suite_sha256')
        or _sha256_bytes(suite_bytes)
        != recovery.get('superseded_suite_sha256')
        or commitment_sha256
        != recovery.get('superseded_commitment_sha256')
        or commitment.get('selection_blind') is not False
        or commitment.get('population_visibility')
        != 'researcher_visible_before_activation'
    ):
        raise RuntimeError(
            'v3 adopted suite differs from its cleartext commitment'
        )
    disk = shutil.disk_usage(root.parent)
    required_free_bytes = _v3_required_free_bytes(
        root,
        V3_EXPECTED_COUNTS['declared_total'],
    )
    if disk.free < required_free_bytes:
        raise RuntimeError('v3 precommit adoption disk forecast failed')
    transaction = {
        'schema_version': 1,
        'experiment_version': _v3_recovery_fresh_lineage_id(
            recovery
        ),
        'operator': operator,
        'evidence_root': str(root),
        'suite_path': str(suite_path.resolve()),
        'commitment_path': str(commitment_path.resolve()),
        'suite_base64': base64.b64encode(suite_bytes).decode('ascii'),
        'commitment': commitment,
        'commitment_sha256': commitment_sha256,
        'repository': repository,
        'disk_forecast': {
            'free_bytes': disk.free,
            'required_free_bytes': required_free_bytes,
            'remaining_declared_slots': (
                V3_EXPECTED_COUNTS['declared_total']
            ),
        },
        'processes_before': processes_before,
        'recovery': recovery,
    }
    transaction['transaction_sha256'] = omission_sha256(
        transaction,
        'transaction_sha256',
    )
    transaction_bytes = (
        json.dumps(
            transaction,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + '\n'
    ).encode('utf-8')
    staging_root = Path(tempfile.mkdtemp(
        prefix=f'.{root.name}.adopt-',
        dir=root.parent,
    ))
    try:
        staging_root.chmod(0o700)
        staging_state_root = _state_root(staging_root)
        staging_state_root.mkdir(parents=True, mode=0o700)
        staging_state_root.chmod(0o700)
        atomic_bytes(
            _v3_prepare_transaction_path(staging_root),
            transaction_bytes,
            mode=0o600,
        )
        os.replace(staging_root, root)
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)
    return _v3_publish_prepare_transaction(
        root,
        transaction,
        operator=operator,
        suite_path=suite_path,
        commitment_path=commitment_path,
        restore_outputs=False,
    )


def run_v3_prepare(
    operator,
    evidence_root,
    *,
    seed_bytes=None,
    suite_path=V3_PRECOMMITTED_SUITE_PATH,
    commitment_path=V3_COMMITMENT_PATH,
):
    """Generate, qualify, and hash the fixed researcher-visible population."""
    root = Path(evidence_root).expanduser().resolve()
    state_path = _v3_state_path(root, 'prepare')
    transaction_path = _v3_prepare_transaction_path(root)
    suite_path = Path(suite_path)
    commitment_path = Path(commitment_path)
    if state_path.is_file():
        transaction = _v3_load_prepare_transaction(transaction_path)
        return _v3_publish_prepare_transaction(
            root,
            transaction,
            operator=operator,
            suite_path=suite_path,
            commitment_path=commitment_path,
            restore_outputs=False,
        )
    if transaction_path.is_file():
        transaction = _v3_load_prepare_transaction(transaction_path)
        _v3_assert_worktree_changes({
            suite_path,
            commitment_path,
        })
        _v3_verify_repository_snapshot(
            transaction['repository'],
            require_clean=False,
        )
        return _v3_publish_prepare_transaction(
            root,
            transaction,
            operator=operator,
            suite_path=suite_path,
            commitment_path=commitment_path,
            restore_outputs=True,
        )
    if root.exists():
        raise RuntimeError('v3 prepare requires an absent fresh evidence root')
    if suite_path.exists() or commitment_path.exists():
        raise RuntimeError(
            'v3 prepare found outputs without a resumable transaction'
        )
    processes_before = _v3_active_processes()
    if processes_before:
        raise RuntimeError('v3 prepare process set is not clean')
    repository = _v3_repository_snapshot(require_clean=True)
    disk = shutil.disk_usage(root.parent)
    required_free_bytes = _v3_required_free_bytes(
        root,
        V3_EXPECTED_COUNTS['declared_total'],
    )
    if disk.free < required_free_bytes:
        raise RuntimeError('v3 prepare disk forecast failed')
    historical_keys, historical_hashes = _v3_historical_case_keys()
    population = generate_v3_acceptance_population(
        seed_bytes or secrets.token_bytes(32),
        historical_case_keys=historical_keys,
    )
    suite_bytes = canonical_json_bytes(population)
    commitment = _v3_commitment_document(
        population,
        suite_bytes,
        historical_hashes,
    )
    transaction = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'operator': operator,
        'suite_path': str(suite_path.resolve()),
        'commitment_path': str(commitment_path.resolve()),
        'suite_base64': base64.b64encode(suite_bytes).decode('ascii'),
        'commitment': commitment,
        'commitment_sha256': commitment['commitment_sha256'],
        'repository': repository,
        'disk_forecast': {
            'free_bytes': disk.free,
            'required_free_bytes': required_free_bytes,
            'remaining_declared_slots': (
                V3_EXPECTED_COUNTS['declared_total']
            ),
        },
        'processes_before': processes_before,
    }
    transaction['transaction_sha256'] = omission_sha256(
        transaction,
        'transaction_sha256',
    )
    transaction_bytes = (
        json.dumps(
            transaction,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + '\n'
    ).encode('utf-8')
    staging_root = Path(tempfile.mkdtemp(
        prefix=f'.{root.name}.prepare-',
        dir=root.parent,
    ))
    try:
        staging_root.chmod(0o700)
        staging_state_root = _state_root(staging_root)
        staging_state_root.mkdir(parents=True, mode=0o700)
        staging_state_root.chmod(0o700)
        staging_transaction = _v3_prepare_transaction_path(
            staging_root
        )
        atomic_bytes(
            staging_transaction,
            transaction_bytes,
            mode=0o600,
        )
        os.replace(staging_root, root)
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)
    del population
    del suite_bytes
    return _v3_publish_prepare_transaction(
        root,
        transaction,
        operator=operator,
        suite_path=suite_path,
        commitment_path=commitment_path,
        restore_outputs=True,
    )


def _v3_run_qualification_command(
    identifier,
    command,
    cwd,
    log_root,
    timeout_sec,
    expected_return_codes=(0,),
    environment=None,
):
    started = _utc_now()
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_sec,
        )
        return_code = result.returncode
        output = result.stdout
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        return_code = 124
        output = (
            exc.stdout.decode('utf-8', errors='replace')
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or '')
        )
        timed_out = True
    log_path = Path(log_root) / f'{identifier}.log'
    atomic_bytes(log_path, output.encode('utf-8', errors='replace'))
    return {
        'identifier': identifier,
        'command': list(command),
        'cwd': str(cwd),
        'timeout_sec': timeout_sec,
        'return_code': return_code,
        'expected_return_codes': list(expected_return_codes),
        'timed_out': timed_out,
        'passed': (
            not timed_out and return_code in expected_return_codes
        ),
        'started_at_utc': _utc_text(started),
        'completed_at_utc': _utc_text(_utc_now()),
        'log_path': str(log_path),
        'log_sha256': file_sha256(log_path),
        'output_tail': output[-4000:],
    }


def _v3_active_processes():
    result = subprocess.run(
        ['ps', '-eo', 'pid=,ppid=,args='],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
        timeout=10.0,
    )
    patterns = (
        'gzserver',
        'gzclient',
        'run_scenario',
        'record_run',
        'ros2 bag record',
        'supervisor_node',
        'controller_node',
        'gaussian_fill_node',
        'validate_robustness',
    )
    process_rows = []
    parents = {}
    for line in result.stdout.splitlines():
        fields = line.strip().split(maxsplit=2)
        if len(fields) != 3:
            continue
        try:
            pid = int(fields[0])
            parent_pid = int(fields[1])
        except ValueError:
            continue
        process_rows.append((pid, fields[2]))
        parents[pid] = parent_pid
    excluded = set()
    cursor = os.getpid()
    while cursor > 0 and cursor not in excluded:
        excluded.add(cursor)
        cursor = parents.get(cursor, 0)
    matches = []
    for pid, command in process_rows:
        if pid in excluded:
            continue
        if any(pattern in command for pattern in patterns):
            matches.append({'pid': pid, 'command': command})
    return matches


def _v3_source_environment():
    environment = dict(os.environ)
    environment['ROS_LOG_DIR'] = (
        '/tmp/dsim_phase08_v3_qualification_ros_logs'
    )
    environment['MPLCONFIGDIR'] = (
        '/tmp/dsim_phase08_v3_qualification_mpl'
    )
    return environment


def _v3_qualification_commands(
    root,
    directory_name='qualification',
    *,
    require_frozen=False,
):
    qualification_root = root / directory_name
    log_root = qualification_root / 'logs'
    log_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    build_root = qualification_root / 'isolated_build'
    build_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    install_root = build_root / 'install'
    environment = _v3_source_environment()
    ros2_workspace = REPOSITORY_ROOT / 'ros2_ws'
    build = _v3_run_qualification_command(
        'isolated_build',
        [
            'colcon',
            '--log-base', str(build_root / 'logs'),
            'build',
            '--build-base', str(build_root / 'build'),
            '--install-base', str(install_root),
            '--packages-up-to',
            'ros_esc',
        ],
        ros2_workspace,
        log_root,
        600.0,
        environment=environment,
    )
    setup_command = (
        f'source /opt/ros/humble/setup.bash && '
        f'source {install_root}/setup.bash && '
    )
    commands = [build]
    if not build['passed']:
        return commands, install_root
    checks = [
        (
            'installed_truth_resources',
            setup_command
            + (
                'python3 -c "from ros_esc.scenario_runner.'
                'aggregate_field_truth import '
                'MODEL_CONFIG_PATH,SENSOR_TRANSFORM_CONFIG_PATH,'
                'SENSOR_GEOMETRY_PATH; '
                'assert MODEL_CONFIG_PATH.is_file(); '
                'assert SENSOR_TRANSFORM_CONFIG_PATH.is_file(); '
                'assert SENSOR_GEOMETRY_PATH.is_file()"'
            ),
            30.0,
            (0,),
        ),
        (
            'installed_v3_resources',
            setup_command
            + (
                'cd /tmp && python3 -c "from '
                'ros_esc.scenario_runner.phase08_validation import '
                'PACKAGE_SCENARIO_ROOT; '
                'assert PACKAGE_SCENARIO_ROOT is not None; '
                'assert (PACKAGE_SCENARIO_ROOT / '
                '\\"phase08_v3_activation.yaml\\").is_file(); '
                'assert (PACKAGE_SCENARIO_ROOT / '
                '\\"phase08_v3_development.yaml\\").is_file(); '
                'assert (PACKAGE_SCENARIO_ROOT / '
                '\\"phase08_v3_candidates.yaml\\").is_file()"'
            ),
            30.0,
            (0,),
        ),
        (
            'installed_entrypoint',
            setup_command
            + 'ros2 run ros_esc validate_robustness --help',
            30.0,
            (0,),
        ),
        (
            'launch_arguments',
            setup_command
            + (
                'ros2 launch turtlebot3_rotating_sensor '
                'gazebo.launch.xml --show-args'
            ),
            30.0,
            (0,),
        ),
        (
            'supervisor_instantiation',
            setup_command
            + (
                'timeout --verbose --signal=INT --kill-after=5s 5s '
                'ros2 run ros_esc supervisor_node --ros-args '
                '-p algorithm_profile:=robust_gaussian_v1 '
                '-p use_sim_time:=false '
                '-p stall_window_sec:=3.0 '
                '-p minimum_radial_progress_m:=0.05'
            ),
            20.0,
            (124,),
        ),
        (
            'fill_instantiation',
            setup_command
            + (
                'timeout --verbose --signal=INT --kill-after=5s 5s '
                'ros2 run ros_esc gaussian_fill_node --ros-args '
                '-p use_sim_time:=false '
                '-p covariance_scale:=2.5 '
                '-p amplitude_depth_scale:=1.5 '
                '-p exit_sigma:=2.5'
            ),
            20.0,
            (124,),
        ),
        (
            'activation_dry_run',
            setup_command
            + (
                f'ros2 run ros_esc run_scenario {V3_ACTIVATION_PATH} '
                '--operator phase08_v3 --dry-run '
                f'--summary-output {qualification_root}/'
                'activation_dry_run.yaml'
            ),
            120.0,
            (0,),
        ),
        (
            'development_dry_run',
            setup_command
            + (
                f'ros2 run ros_esc run_scenario {V3_DEVELOPMENT_PATH} '
                '--operator phase08_v3 --dry-run '
                f'--summary-output {qualification_root}/'
                'development_dry_run.yaml'
            ),
            120.0,
            (0,),
        ),
    ]
    if require_frozen:
        checks.insert(2, (
            'installed_v3_frozen_resources',
            setup_command
            + (
                'cd /tmp && python3 -c "from '
                'ros_esc.scenario_runner.phase08_validation import '
                'PACKAGE_SCENARIO_ROOT; '
                'assert (PACKAGE_SCENARIO_ROOT / '
                '\\"phase08_v3_frozen_parameters.yaml\\").is_file(); '
                'assert (PACKAGE_SCENARIO_ROOT / '
                '\\"phase08_v3_acceptance_suite.json\\").is_file()"'
            ),
            30.0,
            (0,),
        ))
    for identifier, script, timeout_sec, expected in checks:
        commands.append(_v3_run_qualification_command(
            identifier,
            ['bash', '-c', script],
            ros2_workspace,
            log_root,
            timeout_sec,
            expected_return_codes=expected,
            environment=environment,
        ))
        if identifier in {
            'supervisor_instantiation',
            'fill_instantiation',
        }:
            output = commands[-1]['output_tail']
            clean_sigint = (
                'sending signal INT' in output
                and 'sending signal KILL' not in output
            )
            commands[-1]['clean_sigint_shutdown'] = clean_sigint
            commands[-1]['passed'] &= clean_sigint
        if not commands[-1]['passed']:
            break
    return commands, install_root


def _v3_normalize_generated_noise_config(argument):
    """Normalize only the generated Phase 06 noise-config path."""
    if re.fullmatch(
        (
            r'cost_function_config_filepath:=/tmp/'
            r'gesc_phase06_[A-Za-z0-9_]+/'
            r'resolved_cost_function\.json'
        ),
        str(argument),
    ):
        return (
            'cost_function_config_filepath:='
            '<ephemeral-generated-noise-config>'
        )
    return argument


def _v3_normalize_activation_launch_argv(argv):
    """Normalize the one declared ephemeral launch argument."""
    if not isinstance(argv, list):
        raise RuntimeError('v3 activation launch argv is unavailable')
    return [
        _v3_normalize_generated_noise_config(argument)
        for argument in argv
    ]


def _v3_normalize_activation_record_argv(argv):
    """Normalize only declared ephemeral recorder argument values."""
    if not isinstance(argv, list):
        raise RuntimeError('v3 activation record argv is unavailable')
    normalized = list(argv)
    for index, value in enumerate(normalized):
        if value not in {'--metadata-input', '--run-id'}:
            continue
        if index + 1 >= len(normalized):
            raise RuntimeError(
                f'v3 activation record argv ends after {value}'
            )
        normalized[index + 1] = '<ephemeral>'
    return [
        _v3_normalize_generated_noise_config(argument)
        for argument in normalized
    ]


def _v3_activation_invocation_contract(summary):
    """Project one installed activation dry run into a stable contract."""
    if not isinstance(summary, dict):
        raise RuntimeError('v3 activation dry-run summary is malformed')
    runs = summary.get('runs')
    if not isinstance(runs, list):
        raise RuntimeError('v3 activation dry-run runs are unavailable')
    normalized_runs = []
    for run in runs:
        if not isinstance(run, dict):
            raise RuntimeError('v3 activation dry-run run is malformed')
        required = {
            'run_id',
            'case_id',
            'case_key',
            'profile',
            'seed',
            'launch_argv',
            'record_argv',
            'activation_contract',
            'metadata',
        }
        if not required <= set(run):
            raise RuntimeError(
                'v3 activation dry-run invocation fields are missing'
            )
        if not isinstance(run['launch_argv'], list):
            raise RuntimeError(
                'v3 activation launch argv is unavailable'
            )
        normalized_runs.append({
            'run_id': '<ephemeral>',
            'case_id': run['case_id'],
            'case_key': run['case_key'],
            'profile': run['profile'],
            'seed': run['seed'],
            'launch_argv': _v3_normalize_activation_launch_argv(
                run['launch_argv']
            ),
            'record_argv': _v3_normalize_activation_record_argv(
                run['record_argv']
            ),
            'activation_contract': run['activation_contract'],
            'metadata': run['metadata'],
        })
    contract = {
        'schema_version': summary.get('schema_version'),
        'suite_id': summary.get('suite_id'),
        'scenario_schema_version': summary.get(
            'scenario_schema_version'
        ),
        'source_path': summary.get('source_path'),
        'serial_execution': summary.get('serial_execution'),
        'selected_case_ids': summary.get('selected_case_ids'),
        'resolved_run_count': summary.get('resolved_run_count'),
        'unsupported_count': summary.get('unsupported_count'),
        'unsupported': summary.get('unsupported'),
        'dry_run': summary.get('dry_run'),
        'runs': normalized_runs,
    }
    contract['contract_sha256'] = canonical_sha256(contract)
    return contract


def _v3_activation_contact_launch_contract(summary):
    """Verify installed activation commands use passive contact evidence."""
    runs = summary.get('runs')
    reasons = []
    direct_pass_count = 0
    recorder_pass_count = 0
    if not isinstance(runs, list) or len(runs) != V3_EXPECTED_COUNTS[
        'activation'
    ]:
        reasons.append('activation dry run does not contain ten runs')
        runs = []
    required = {
        'gazebo_gui:=True',
        'simulation_contacts_enabled:=True',
        'simulation_contact_probe_enabled:=False',
    }
    forbidden = {'simulation_contact_probe_enabled:=True'}
    for run in runs:
        case_id = run.get('case_id', '<unknown>')
        for field, counter_name in (
            ('launch_argv', 'direct'),
            ('record_argv', 'recorder'),
        ):
            argv = run.get(field)
            if not isinstance(argv, list):
                reasons.append(f'{case_id} {field} is unavailable')
                continue
            missing = sorted(required - set(argv))
            present_forbidden = sorted(forbidden & set(argv))
            if missing or present_forbidden:
                reasons.append(
                    f'{case_id} {field} contact launch contract failed'
                )
                continue
            if counter_name == 'direct':
                direct_pass_count += 1
            else:
                recorder_pass_count += 1
    return {
        'passed': not reasons,
        'direct_pass_count': direct_pass_count,
        'recorder_pass_count': recorder_pass_count,
        'expected_count': V3_EXPECTED_COUNTS['activation'],
        'reasons': reasons,
    }


def run_v3_qualify(operator, evidence_root):
    """Run the pre-activation source, schema, and retained functional gate."""
    root = Path(evidence_root).expanduser().resolve()
    prepare = _v3_require_state(root, 'prepare')
    _v3_require_operator(prepare, operator, 'prepare')
    commitment = _load_json(V3_COMMITMENT_PATH)
    reasons = []
    recovery = prepare.get('recovery')
    if recovery is None:
        raise RuntimeError(
            'v3 corrected qualification requires '
            'v3-adopt-precommit recovery'
        )
    recovery_validation = {
        'required': True,
        'passed': False,
        'recovery_sha256': canonical_sha256(recovery),
        'reasons': [],
    }
    expected_lineage = _v3_recovery_fresh_lineage_id(recovery)
    if prepare.get('lineage_id') != expected_lineage:
        recovery_validation['reasons'].append(
            f'corrected prepare lineage is not {expected_lineage}'
        )
    try:
        observed_recovery = _v3_revalidate_recovery(recovery)
        if observed_recovery != recovery:
            recovery_validation['reasons'].append(
                'corrected prepare recovery proof drifted'
            )
    except (KeyError, OSError, RuntimeError) as exc:
        recovery_validation['reasons'].append(str(exc))
    recovery_validation['passed'] = not recovery_validation['reasons']
    reasons.extend(recovery_validation['reasons'])
    try:
        _v3_assert_worktree_changes({
            V3_PRECOMMITTED_SUITE_PATH,
            V3_COMMITMENT_PATH,
        })
        _v3_verify_repository_snapshot(
            prepare['repository'],
            require_clean=False,
        )
        _v3_verify_diagnostic_runtime_projection(
            recovery,
            prepare['repository'],
        )
    except RuntimeError as exc:
        reasons.append(str(exc))
    before_processes = _v3_active_processes()
    if before_processes:
        reasons.append('pre-qualification ROS/Gazebo process set is not clean')
    disk = shutil.disk_usage(root)
    required_free_bytes = (
        25 * 1024 ** 3
        + V3_EXPECTED_COUNTS['declared_total'] * 512 * 1024 ** 2
    )
    if disk.free < required_free_bytes:
        reasons.append('disk forecast is below the declared v3 minimum')
    if (
        file_sha256(V3_PRECOMMITTED_SUITE_PATH)
        != prepare['suite_sha256']
    ):
        reasons.append('precommitted acceptance suite hash drifted')
    try:
        commitment_hash = require_omission_sha256(
            commitment,
            'commitment_sha256',
            'acceptance commitment',
        )
        if commitment_hash != prepare['commitment_sha256']:
            reasons.append('acceptance commitment state hash drifted')
    except RuntimeError as exc:
        reasons.append(str(exc))
    activation_runs, activation_unsupported = expand_suite(
        load_suite(V3_ACTIVATION_PATH)
    )
    development_runs, development_unsupported = expand_suite(
        load_suite(V3_DEVELOPMENT_PATH)
    )
    load_v3_candidates()
    if len(activation_runs) != V3_EXPECTED_COUNTS['activation']:
        reasons.append('activation count is not exactly ten')
    if len(development_runs) != 10:
        reasons.append('development common-case count is not exactly ten')
    if activation_unsupported or development_unsupported:
        reasons.append('v3 development inputs contain unsupported cases')
    old_keys, unused_historical_hashes = _v3_historical_case_keys(
        include_v3_development=False
    )
    del unused_historical_hashes
    historical_keys, historical_hashes = _v3_historical_case_keys()
    new_keys = {
        run['case_key']
        for run in activation_runs + development_runs
    }
    if old_keys & new_keys:
        reasons.append('v3 activation/development key collision detected')
    if len(new_keys) != 20:
        reasons.append(
            'v3 activation/development keys are not exactly 20 unique cases'
        )
    if historical_hashes != commitment.get(
        'historical_exclusion_hashes'
    ):
        reasons.append(
            'historical exclusion hashes differ from the commitment'
        )
    population_validation = {'passed': False, 'reasons': []}
    try:
        suite_bytes = V3_PRECOMMITTED_SUITE_PATH.read_bytes()
        if _sha256_bytes(suite_bytes) != commitment.get('suite_sha256'):
            raise RuntimeError(
                'acceptance suite differs from its commitment'
            )
        population = json.loads(suite_bytes.decode('utf-8'))
        if canonical_json_bytes(population) != suite_bytes:
            raise RuntimeError(
                'acceptance suite is not canonical JSON'
            )
        population_validation = validate_v3_population(
            population,
            historical_case_keys=historical_keys,
        )
        if not population_validation['passed']:
            reasons.append(
                'precommitted population failed validation: '
                + '; '.join(population_validation['reasons'])
            )
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        population_validation = {
            'passed': False,
            'reasons': [str(exc)],
        }
        reasons.append(str(exc))
    functional = _run_functional_tests()
    if not functional['passed']:
        reasons.append('retained functional test gate failed')
    qualification_commands, install_root = _v3_qualification_commands(root)
    if not all(item['passed'] for item in qualification_commands):
        reasons.append('one or more isolated build/installed dry checks failed')
    dry_run_results = {}
    activation_contact_contract = {
        'passed': False,
        'direct_pass_count': 0,
        'recorder_pass_count': 0,
        'expected_count': V3_EXPECTED_COUNTS['activation'],
        'reasons': ['activation installed dry-run summary is missing'],
    }
    activation_invocation_contract = None
    for name, expected in (
        ('activation', V3_EXPECTED_COUNTS['activation']),
        ('development', V3_EXPECTED_COUNTS['development_per_candidate']),
    ):
        path = root / 'qualification' / f'{name}_dry_run.yaml'
        if not path.is_file():
            reasons.append(f'{name} installed dry-run summary is missing')
            continue
        summary = yaml.safe_load(path.read_text(encoding='utf-8'))
        dry_run_results[name] = {
            'path': str(path),
            'sha256': file_sha256(path),
            'resolved_run_count': summary.get('resolved_run_count'),
            'unsupported_count': summary.get('unsupported_count'),
        }
        if (
            summary.get('resolved_run_count') != expected
            or summary.get('unsupported_count') != 0
            or summary.get('scenario_schema_version') != 4
        ):
            reasons.append(f'{name} installed dry-run contract failed')
        if name == 'activation':
            activation_contact_contract = (
                _v3_activation_contact_launch_contract(summary)
            )
            if not activation_contact_contract['passed']:
                reasons.append(
                    'activation installed contact launch contract failed'
                )
            try:
                activation_invocation_contract = (
                    _v3_activation_invocation_contract(summary)
                )
                if (
                    recovery.get('kind')
                    == 'behavioral_miss_diagnostic_completion'
                    and activation_invocation_contract
                    != recovery.get('activation_invocation_contract')
                ):
                    reasons.append(
                        'activation installed invocation contract '
                        'differs from V3B'
                    )
            except RuntimeError as exc:
                reasons.append(str(exc))
    after_processes = _v3_active_processes()
    if after_processes:
        reasons.append('post-qualification ROS/Gazebo process set is not clean')
    try:
        _v3_assert_worktree_changes({
            V3_PRECOMMITTED_SUITE_PATH,
            V3_COMMITMENT_PATH,
        })
    except RuntimeError as exc:
        reasons.append(str(exc))
    repository = _v3_repository_snapshot(
        require_clean=False,
        extra_paths=(
            V3_PRECOMMITTED_SUITE_PATH,
            V3_COMMITMENT_PATH,
        ),
    )
    return _v3_write_state(root, 'qualification', {
        'passed': not reasons,
        'operator': operator,
        'lineage_id': prepare.get('lineage_id', 'phase08-v3'),
        'prepare_state_sha256': prepare['state_sha256'],
        'recovery_validation': recovery_validation,
        'activation_contact_launch_contract': (
            activation_contact_contract
        ),
        'activation_invocation_contract': (
            activation_invocation_contract
        ),
        'activation_count': len(activation_runs),
        'development_count': len(development_runs),
        'candidate_count': len(V3_CANDIDATES),
        'population_validation': population_validation,
        'functional_tests': functional,
        'isolated_install_root': str(install_root),
        'qualification_commands': qualification_commands,
        'installed_dry_runs': dry_run_results,
        'processes_before': before_processes,
        'processes_after': after_processes,
        'disk_forecast': {
            'free_bytes': disk.free,
            'required_free_bytes': required_free_bytes,
            'remaining_declared_slots': (
                V3_EXPECTED_COUNTS['declared_total']
            ),
        },
        'historical_exclusion_hashes': historical_hashes,
        'repository': repository,
        'reasons': reasons,
    })


def _v3_record_integrity(record, *, require_terminal_outcomes=True):
    analysis = record.get('analysis') or {}
    metrics = analysis.get('metrics', {})
    collision = metrics.get('collision', {})
    classification = record.get('classification', {})
    reasons = []
    if record.get('recording_complete') is not True:
        reasons.append('recording completeness failed')
    if record.get('cleanup', {}).get('passed') is not True:
        reasons.append('cleanup failed')
    if record.get('record_process', {}).get('timed_out'):
        reasons.append('outer wall timeout')
    if classification.get('infrastructure_status') != 'completed':
        reasons.append('infrastructure status is not completed')
    if record.get('analysis_error'):
        reasons.append('analysis raised an exception')
    if analysis.get('analysis_status') != 'complete':
        reasons.append('analysis is not complete')
    if record.get('metric_applicability') is not None and (
        analysis.get('applicability_integrity', {}).get('passed')
        is not True
    ):
        reasons.append('metric applicability integrity failed')
    if collision.get('status') != 'valid':
        reasons.append('collision evidence is unavailable')
    elif collision.get('value') is not False:
        reasons.append('non-ground collision observed')
    if require_terminal_outcomes:
        expected_safe_timeout = (
            record.get('success_contract', {})
            .get('controller', {})
            .get('expected_verification_outcome')
            == 'safe_timeout'
        )
        for name in ('timeout', 'failsafe'):
            metric_value = metrics.get(name, {})
            if metric_value.get('status') != 'valid':
                reasons.append(f'{name} evidence is unavailable')
            elif expected_safe_timeout:
                if metric_value.get('value') is not True:
                    reasons.append(f'expected {name} was not observed')
            elif metric_value.get('value') is not False:
                reasons.append(f'unexpected {name} observed')
    if record.get('metric_applicability') is not None:
        if not record.get('resolved_scenario_sha256'):
            reasons.append('resolved scenario hash is missing')
        if not record.get('analysis_summary_sha256'):
            reasons.append('analysis summary hash is missing')
        analysis_completeness = record.get('analysis_completeness')
        if not isinstance(analysis_completeness, dict):
            reasons.append('analysis completeness evidence is missing')
        else:
            if analysis_completeness.get('status') != 'complete':
                reasons.append('analysis completeness status is not complete')
            raw_hashes = analysis_completeness.get('raw_bag_sha256')
            if not isinstance(raw_hashes, dict) or not raw_hashes:
                reasons.append('raw bag hashes are missing')
            else:
                for path_text, expected in raw_hashes.items():
                    path = Path(path_text)
                    if (
                        not path.is_file()
                        or not isinstance(expected, str)
                        or file_sha256(path) != expected
                    ):
                        reasons.append(
                            f'raw bag hash drifted: {path_text}'
                        )
                        break
    return {
        'passed': not reasons,
        'reasons': reasons,
    }


def _v3_activation_profile():
    return {
        'profile_id': 'V3-ACTIVATION',
        'launch_overrides': dict(V3_CANDIDATES[0]['launch_overrides']),
    }


def _v3_verify_corrected_recovery_before_activation(
    prepare,
    qualification,
):
    """Revalidate a corrected lineage immediately before dispatch."""
    if (
        qualification.get('prepare_state_sha256')
        != prepare.get('state_sha256')
    ):
        raise RuntimeError('v3 qualification is not bound to prepare')
    recovery = prepare.get('recovery')
    if recovery is None:
        raise RuntimeError(
            'v3 corrected activation requires adopted recovery'
        )
    expected_lineage = _v3_recovery_fresh_lineage_id(recovery)
    if (
        prepare.get('lineage_id') != expected_lineage
        or qualification.get('lineage_id') != expected_lineage
    ):
        raise RuntimeError('v3 corrected activation lineage drifted')
    recovery_validation = qualification.get('recovery_validation', {})
    if (
        recovery_validation.get('passed') is not True
        or recovery_validation.get('recovery_sha256')
        != canonical_sha256(recovery)
    ):
        raise RuntimeError(
            'v3 qualification lacks the corrected recovery proof'
        )
    contact_contract = qualification.get(
        'activation_contact_launch_contract', {}
    )
    if (
        contact_contract.get('passed') is not True
        or contact_contract.get('direct_pass_count')
        != V3_EXPECTED_COUNTS['activation']
        or contact_contract.get('recorder_pass_count')
        != V3_EXPECTED_COUNTS['activation']
    ):
        raise RuntimeError(
            'v3 qualification lacks installed passive-contact proof'
        )
    installed_dry_run = qualification.get(
        'installed_dry_runs', {}
    ).get('activation', {})
    dry_run_path = Path(installed_dry_run.get('path', ''))
    if (
        not dry_run_path.is_file()
        or installed_dry_run.get('sha256') != file_sha256(dry_run_path)
    ):
        raise RuntimeError(
            'v3 installed activation dry-run artifact drifted'
        )
    dry_run_summary = yaml.safe_load(
        dry_run_path.read_text(encoding='utf-8')
    )
    if (
        _v3_activation_contact_launch_contract(dry_run_summary)
        != contact_contract
    ):
        raise RuntimeError(
            'v3 installed activation contact proof drifted'
        )
    if recovery.get('kind') == 'behavioral_miss_diagnostic_completion':
        observed_invocation_contract = (
            _v3_activation_invocation_contract(dry_run_summary)
        )
        if (
            qualification.get('activation_invocation_contract')
            != observed_invocation_contract
            or recovery.get('activation_invocation_contract')
            != observed_invocation_contract
        ):
            raise RuntimeError(
                'v3 installed activation invocation contract drifted'
            )
    observed = _v3_revalidate_recovery(recovery)
    if observed != recovery:
        raise RuntimeError('v3 corrected recovery proof drifted')


def _v3_diagnostic_carried_records(recovery):
    """Bind V3C to V3B's immutable failed slot without redispatch."""
    if recovery.get('kind') != 'behavioral_miss_diagnostic_completion':
        return []
    carried = recovery.get('carried_record', {})
    record_path = Path(carried.get('record_path', '')).resolve()
    record_sha256 = carried.get('record_sha256')
    run_directory_manifest = recovery.get(
        'run_directory_manifest'
    )
    if (
        carried.get('case_id') != 'v3a_goal_aggregate_direct'
        or carried.get('source_lineage_id') != 'phase08-v3b'
        or not record_path.is_file()
        or file_sha256(record_path) != record_sha256
    ):
        raise RuntimeError('v3 diagnostic carried record drifted')
    record = _load_json(record_path)
    try:
        _v3_verify_directory_manifest(run_directory_manifest)
    except RuntimeError as exc:
        raise RuntimeError(
            'v3 diagnostic carried run directory drifted'
        ) from exc
    if (
        record.get('run_id') != carried.get('run_id')
        or record.get('classification', {}).get('status') != 'failed'
        or _v3_hard_stop_reason(
            record,
            allow_pure_applicability_miss=True,
        ) is not None
        or _v3_record_integrity(record).get('passed') is not False
    ):
        raise RuntimeError(
            'v3 diagnostic carried record lost its failure boundary'
        )
    return [{
        'case_id': carried['case_id'],
        'record_path': str(record_path),
        'record_sha256': record_sha256,
        'run_id': carried['run_id'],
        'source_lineage_id': carried['source_lineage_id'],
        'source_evidence_root': recovery[
            'superseded_evidence_root'
        ],
        'source_activation_state_sha256': recovery[
            'superseded_activation_state_sha256'
        ],
        'run_directory_manifest': run_directory_manifest,
        'disposition': 'carried_immutable_behavioral_failure',
        'rerun': False,
    }]


def run_v3_activation(operator, evidence_root):
    """Execute the corrected visible activation contract set."""
    root = Path(evidence_root).expanduser().resolve()
    prepare = _v3_require_state(root, 'prepare')
    qualification = _v3_require_state(root, 'qualification')
    _v3_require_operator(prepare, operator, 'prepare')
    _v3_require_operator(qualification, operator, 'qualification')
    _v3_verify_corrected_recovery_before_activation(
        prepare,
        qualification,
    )
    _v3_require_precommit_in_head()
    _v3_verify_repository_snapshot(qualification['repository'])
    stage_root = root / 'activation'
    suite_path = _v3_materialize_profile_suite(
        V3_ACTIVATION_PATH,
        _v3_activation_profile(),
        stage_root / 'resolved_suite.yaml',
    )
    carried_records = _v3_diagnostic_carried_records(
        prepare['recovery']
    )
    diagnostic_completion = (
        prepare.get('lineage_id') == 'phase08-v3c'
    )
    required_execution_case_ids = (
        prepare['recovery'].get(
            'composite_activation', {}
        ).get('execute_case_ids')
        if diagnostic_completion else None
    )
    summary, records, progress = _v3_execute_serial_slots(
        suite_path,
        operator,
        root,
        stage_root,
        'activation',
        runtime_snapshot=qualification['repository'],
        carried_records=carried_records,
        required_execution_case_ids=required_execution_case_ids,
        allow_pure_applicability_miss=diagnostic_completion,
    )
    integrity = [_v3_record_integrity(record) for record in records]
    contract_passes = [
        record.get('classification', {}).get('passed') is True
        for record in records
    ]
    reasons = []
    if diagnostic_completion:
        reasons.append(
            'V3C diagnostic completion carries the immutable V3B '
            'behavioral failure and is not pass-eligible'
        )
    if progress.get('stopped_early_reason'):
        reasons.append(
            f"activation hard stop: {progress['stopped_early_reason']}"
        )
    if len(records) != V3_EXPECTED_COUNTS['activation']:
        reasons.append('activation did not retain exactly ten records')
    if not all(item['passed'] for item in integrity):
        reasons.append('one or more activation integrity checks failed')
    if not all(contract_passes):
        reasons.append('one or more activation behavior contracts failed')
    carried_count = progress.get('carried_count', 0)
    newly_executed_count = progress.get(
        'newly_executed_count',
        len(records),
    )
    if diagnostic_completion and (
        carried_count != 1
        or newly_executed_count != 9
        or len(records) != 10
        or len(progress.get('attempts', [])) < 9
        or any(
            attempt.get('case_id') == 'v3a_goal_aggregate_direct'
            for attempt in progress.get('attempts', [])
        )
    ):
        reasons.append(
            'V3C diagnostic completion did not retain one carried '
            'and nine newly executed slots'
        )
    functional = _run_functional_tests()
    if not functional['passed']:
        reasons.append('post-activation functional test gate failed')
    return _v3_write_state(root, 'activation', {
        'passed': not reasons,
        'operator': operator,
        'qualification_state_sha256': qualification['state_sha256'],
        'run_count': len(records),
        'composite_slot_count': len(records),
        'carried_record_count': carried_count,
        'new_execution_count': newly_executed_count,
        'carried_count': carried_count,
        'newly_executed_count': newly_executed_count,
        'carried_records': progress.get('carried_records', []),
        'pass_eligible': not diagnostic_completion,
        'diagnostic_completion': diagnostic_completion,
        'integrity_pass_count': sum(
            item['passed'] for item in integrity
        ),
        'contract_pass_count': sum(contract_passes),
        'scenario_summary_path': summary.get('summary_path'),
        'scenario_summary_sha256': file_sha256(
            stage_root / 'scenario_summary.yaml'
        ),
        'records_path': str(root / 'activation/records.json'),
        'records_sha256': file_sha256(
            root / 'activation/records.json'
        ),
        'attempt_records_sha256': file_sha256(
            root / 'activation/attempt_records.json'
        ),
        'progress_sha256': progress['progress_sha256'],
        'stopped_early_reason': progress.get('stopped_early_reason'),
        'ambiguous_interrupted_dispatch_case_ids': progress.get(
            'ambiguous_interrupted_dispatch_case_ids',
            [],
        ),
        'not_run_slot_ids': progress.get('not_run_slot_ids', []),
        'replacement_state_sha256': (
            file_sha256(_v3_replacement_state_path(root))
            if _v3_replacement_state_path(root).is_file()
            else None
        ),
        'functional_tests': functional,
        'reasons': reasons,
    })


def _v3_candidate_metrics(candidate_id, records, expected_cases):
    expected_by_key = {
        case.get('case_key'): case
        for case in expected_cases
        if isinstance(case.get('case_key'), str)
    }
    record_keys = [record.get('case_key') for record in records]
    expected_keys = [case.get('case_key') for case in expected_cases]
    identities_valid = (
        len(records) == 10
        and len(expected_cases) == 10
        and len(record_keys) == len(set(record_keys))
        and len(expected_keys) == len(set(expected_keys))
        and set(record_keys) == set(expected_keys)
    )
    evaluations = []
    for record in records:
        expected = expected_by_key.get(record.get('case_key'))
        if expected is not None:
            evaluations.append((
                record,
                expected,
                _v3_case_evaluation(record, expected),
            ))
    family_totals = Counter()
    family_successes = Counter()
    integrity = [
        evaluation['integrity']
        for unused_record, unused_expected, evaluation in evaluations
    ]
    e2e = 0
    behavior = 0
    attempt_count = 0
    attempt_successes = 0
    durations = []
    orbits = []
    revisits = []
    convergence = []
    paths = []
    applicable_valid = True
    unexpected_terminal = False
    binding_valid = True
    for record, expected, evaluation in evaluations:
        analysis = record.get('analysis') or {}
        metrics = analysis.get('metrics', {})
        family = expected.get('acceptance_family')
        passed = evaluation['end_to_end']
        family_totals[family] += 1
        family_successes[family] += int(passed)
        e2e += int(passed)
        behavior += int(evaluation['lifecycle_passed'])
        binding_valid &= not evaluation['binding_reasons']
        applicable_valid &= (
            not evaluation['reasons']
            and evaluation['attempt_metric_valid']
            and evaluation['delay_valid']
            and evaluation['saturation_valid']
        )
        for attempt in evaluation['attempts']:
            attempt_count += 1
            successful = attempt.get('outcome') == 'success'
            attempt_successes += int(successful)
            duration = attempt.get('duration', {})
            orbit = attempt.get('orbit_count', {})
            if successful and duration.get('status') == 'valid':
                durations.append(float(duration['value']))
            elif successful:
                applicable_valid = False
            if successful and orbit.get('status') == 'valid':
                orbits.append(float(orbit['value']))
            elif successful:
                applicable_valid = False
        for name, destination in (
            ('revisit_count', revisits),
            ('convergence_time', convergence),
            ('path_length', paths),
        ):
            value = metrics.get(name, {})
            if value.get('status') == 'valid':
                destination.append(float(value['value']))
        timeout = metrics.get('timeout', {})
        failsafe = metrics.get('failsafe', {})
        if (
            timeout.get('status') == 'valid' and timeout.get('value')
        ) or (
            failsafe.get('status') == 'valid' and failsafe.get('value')
        ):
            unexpected_terminal = True
        if expected.get('metric_applicability', {}).get('revisit'):
            if metrics.get('revisit_count', {}).get('status') != 'valid':
                applicable_valid = False
    family_rates = {
        family: family_successes[family] / total
        for family, total in family_totals.items()
    }
    escape_rate = (
        attempt_successes / attempt_count if attempt_count else None
    )
    reasons = []
    if not identities_valid or len(evaluations) != 10:
        reasons.append(
            'candidate records differ from the exact ten declared slots'
        )
    if not all(item['passed'] for item in integrity):
        reasons.append('integrity failure')
    if not binding_valid:
        reasons.append('candidate evidence differs from declared contracts')
    if e2e < 9:
        reasons.append('fewer than 9/10 end-to-end successes')
    if attempt_count < 8 or attempt_successes != attempt_count:
        reasons.append('escape denominator or success gate failed')
    if behavior < 10:
        reasons.append('one or more lifecycle branches were not reached')
    if not applicable_valid:
        reasons.append('applicable metric evidence is unavailable')
    if unexpected_terminal:
        reasons.append('unexpected timeout or failsafe')
    return {
        'candidate_id': candidate_id,
        'eligible': not reasons,
        'reasons': reasons,
        'run_count': len(records),
        'end_to_end_success_count': e2e,
        'behavior_contract_pass_count': behavior,
        'local_escape_success_rate': escape_rate,
        'minimum_family_success_rate': (
            min(family_rates.values()) if family_rates else None
        ),
        'escape_time_p95_sec': _percentile(durations, 95),
        'escape_time_median_sec': (
            statistics.median(durations) if durations else None
        ),
        'median_orbit_count': (
            statistics.median(orbits) if orbits else None
        ),
        'revisit_rate': (
            sum(value > 0 for value in revisits) / len(revisits)
            if revisits else None
        ),
        'median_convergence_time_sec': (
            statistics.median(convergence) if convergence else None
        ),
        'median_path_length_m': (
            statistics.median(paths) if paths else None
        ),
        'family_rates': family_rates,
        'integrity': integrity,
        'identity_binding_passed': identities_valid and binding_valid,
    }


def _v3_selection_key(metrics):
    def descending(value):
        return -value if value is not None else math.inf

    def ascending(value):
        return value if value is not None else math.inf

    return (
        descending(metrics['end_to_end_success_count']),
        descending(metrics['behavior_contract_pass_count']),
        descending(metrics['local_escape_success_rate']),
        descending(metrics['minimum_family_success_rate']),
        ascending(metrics['escape_time_p95_sec']),
        ascending(metrics['escape_time_median_sec']),
        ascending(metrics['median_orbit_count']),
        ascending(metrics['revisit_rate']),
        ascending(metrics['median_convergence_time_sec']),
        ascending(metrics['median_path_length_m']),
        metrics['candidate_id'],
    )


def select_v3_candidate(metrics):
    """Select the exact lexicographic winner among eligible v3 bundles."""
    eligible = [item for item in metrics if item.get('eligible')]
    return min(eligible, key=_v3_selection_key) if eligible else None


def run_v3_development(operator, evidence_root):
    """Execute the same ten headless cases for all three candidates."""
    root = Path(evidence_root).expanduser().resolve()
    activation = _v3_require_state(root, 'activation')
    qualification = _v3_require_state(root, 'qualification')
    if (
        activation.get('qualification_state_sha256')
        != qualification['state_sha256']
    ):
        raise RuntimeError(
            'v3 activation/qualification state link drifted'
        )
    _v3_verify_repository_snapshot(qualification['repository'])
    load_v3_candidates()
    candidates = []
    hard_stop_reason = None
    for candidate in V3_CANDIDATES:
        profile = {
            'profile_id': candidate['candidate_id'],
            'launch_overrides': candidate['launch_overrides'],
        }
        stage_root = root / 'development' / candidate['candidate_id']
        suite_path = _v3_materialize_profile_suite(
            V3_DEVELOPMENT_PATH,
            profile,
            stage_root / 'resolved_suite.yaml',
        )
        summary, records, progress = _v3_execute_serial_slots(
            suite_path,
            operator,
            root,
            stage_root,
            'development',
            candidate_id=candidate['candidate_id'],
            runtime_snapshot=qualification['repository'],
        )
        expected_cases, unsupported = expand_suite(load_suite(suite_path))
        if unsupported:
            raise RuntimeError(
                'materialized v3 development suite became unsupported'
            )
        metrics = _v3_candidate_metrics(
            candidate['candidate_id'],
            records,
            expected_cases,
        )
        metrics['scenario_summary_path'] = summary.get('summary_path')
        metrics['records_path'] = str(stage_root / 'records.json')
        metrics['scenario_summary_sha256'] = file_sha256(
            stage_root / 'scenario_summary.yaml'
        )
        metrics['records_sha256'] = file_sha256(
            stage_root / 'records.json'
        )
        metrics['attempt_records_sha256'] = file_sha256(
            stage_root / 'attempt_records.json'
        )
        metrics['progress_sha256'] = progress['progress_sha256']
        metrics['stopped_early_reason'] = progress.get(
            'stopped_early_reason'
        )
        metrics['ambiguous_interrupted_dispatch_case_ids'] = (
            progress.get(
                'ambiguous_interrupted_dispatch_case_ids',
                [],
            )
        )
        metrics['not_run_slot_ids'] = progress.get(
            'not_run_slot_ids', []
        )
        candidates.append(metrics)
        if progress.get('stopped_early_reason'):
            hard_stop_reason = (
                f"{candidate['candidate_id']}: "
                f"{progress['stopped_early_reason']}"
            )
            break
    not_run_candidates = [
        candidate['candidate_id']
        for candidate in V3_CANDIDATES[len(candidates):]
    ]
    complete_matrix = (
        len(candidates) == len(V3_CANDIDATES)
        and all(item['run_count'] == 10 for item in candidates)
        and hard_stop_reason is None
    )
    selected = (
        select_v3_candidate(candidates) if complete_matrix else None
    )
    reasons = []
    if hard_stop_reason is not None:
        reasons.append(
            f'development hard stop: {hard_stop_reason}'
        )
    if not complete_matrix:
        reasons.append('development did not complete all 30 declared slots')
    if selected is None:
        reasons.append('no development candidate is eligible')
    if sum(
        item['end_to_end_success_count'] for item in candidates
    ) == 0:
        reasons.append('zero end-to-end development success')
    if sum(
        (
            item['local_escape_success_rate'] or 0.0
        ) > 0.0
        for item in candidates
    ) == 0:
        reasons.append('zero escape activation across candidates')
    return _v3_write_state(root, 'development', {
        'passed': not reasons,
        'operator': operator,
        'activation_state_sha256': activation['state_sha256'],
        'qualification_state_sha256': qualification['state_sha256'],
        'candidates': candidates,
        'selected_candidate': selected,
        'not_run_candidates': not_run_candidates,
        'replacement_state_sha256': (
            file_sha256(_v3_replacement_state_path(root))
            if _v3_replacement_state_path(root).is_file()
            else None
        ),
        'reasons': reasons,
    })


def _v3_repository_snapshot(require_clean=False, extra_paths=()):
    status = _git('status', '--porcelain')
    if require_clean and status:
        raise RuntimeError('v3 freeze requires a clean worktree')
    tracked = _git(
        'ls-files',
        '--',
        'ros2_ws/src/ros_esc',
        'ros2_ws/src/ros_esc_interfaces',
        'ros2_ws/src/turtlebot3_rotating_sensor',
    ).splitlines()
    paths = [REPOSITORY_ROOT / name for name in tracked]
    for path in extra_paths:
        resolved = Path(path).resolve()
        if resolved not in paths:
            paths.append(resolved)
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError(
            'v3 freeze input is missing: '
            + ', '.join(str(path) for path in missing)
        )
    input_hashes = {
        str(path.relative_to(REPOSITORY_ROOT)): file_sha256(path)
        for path in sorted(paths)
    }
    return {
        'commit': _git('rev-parse', 'HEAD'),
        'tree': _git('rev-parse', 'HEAD^{tree}'),
        'clean': not bool(status),
        'input_hashes': input_hashes,
        'runtime_inputs_sha256': canonical_sha256(input_hashes),
    }


def _v3_runtime_input_projection(snapshot):
    """Exclude only four reviewed V3C validation-workflow files."""
    input_hashes = snapshot.get('input_hashes')
    if (
        not isinstance(input_hashes, dict)
        or canonical_sha256(input_hashes)
        != snapshot.get('runtime_inputs_sha256')
    ):
        raise RuntimeError('v3 runtime-input snapshot hash drifted')
    missing_allowed_paths = [
        path
        for path in V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        if path not in input_hashes
    ]
    if missing_allowed_paths:
        raise RuntimeError(
            'v3 diagnostic runtime baseline lacks allowed correction '
            f'paths: {missing_allowed_paths}'
        )
    projected = {
        path: digest
        for path, digest in input_hashes.items()
        if path not in V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
    }
    return {
        'excluded_paths': list(
            V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT
        ),
        'input_count': len(projected),
        'input_hashes_sha256': canonical_sha256(projected),
    }


def _v3_verify_diagnostic_runtime_projection(recovery, snapshot):
    """Reject drift outside four reviewed validation-workflow files."""
    if recovery.get('kind') != 'behavioral_miss_diagnostic_completion':
        return None
    input_hashes = snapshot.get('input_hashes')
    allowed_hashes = recovery.get(
        'allowed_runtime_correction_sha256'
    )
    if (
        not isinstance(input_hashes, dict)
        or not isinstance(allowed_hashes, dict)
        or set(allowed_hashes)
        != set(V3_DIAGNOSTIC_ALLOWED_RUNTIME_DRIFT)
        or any(
            input_hashes.get(path) != expected
            for path, expected in allowed_hashes.items()
        )
    ):
        raise RuntimeError(
            'v3 allowed runtime-correction hash mapping drifted'
        )
    expected = recovery.get('baseline_runtime_projection')
    observed = _v3_runtime_input_projection(snapshot)
    if expected != observed:
        raise RuntimeError(
            'v3 diagnostic runtime inputs drifted outside the allowed '
            'validation-workflow correction'
        )
    return observed


def _v3_assert_worktree_changes(allowed_paths):
    allowed = {Path(path).resolve() for path in allowed_paths}
    unexpected = []
    for line in _git('status', '--porcelain').splitlines():
        path_text = line[3:]
        if ' -> ' in path_text:
            unexpected.append(path_text)
            continue
        if (REPOSITORY_ROOT / path_text).resolve() not in allowed:
            unexpected.append(path_text)
    if unexpected:
        raise RuntimeError(
            'v3 worktree has changes outside the allowed generated '
            f'outputs: {unexpected}'
        )


def _v3_verify_repository_snapshot(snapshot, *, require_clean=True):
    input_hashes = snapshot.get('input_hashes')
    if (
        not isinstance(input_hashes, dict)
        or canonical_sha256(input_hashes)
        != snapshot.get('runtime_inputs_sha256')
    ):
        raise RuntimeError('v3 runtime-input snapshot hash drifted')
    extras = [
        REPOSITORY_ROOT / relative_path
        for relative_path in input_hashes
        if relative_path in {
            str(
                V3_PRECOMMITTED_SUITE_PATH.relative_to(REPOSITORY_ROOT)
            ),
            str(V3_COMMITMENT_PATH.relative_to(REPOSITORY_ROOT)),
            str(V3_FROZEN_PATH.relative_to(REPOSITORY_ROOT)),
            str(V3_SELECTION_PATH.relative_to(REPOSITORY_ROOT)),
        }
    ]
    current = _v3_repository_snapshot(
        require_clean=require_clean,
        extra_paths=extras,
    )
    if current['input_hashes'] != input_hashes:
        raise RuntimeError(
            'v3 runtime inputs differ from the qualified snapshot'
        )
    return current


def _v3_require_precommit_in_head():
    """Require the suite and commitment to be exact tracked HEAD blobs."""
    for path in (V3_PRECOMMITTED_SUITE_PATH, V3_COMMITMENT_PATH):
        relative = str(path.relative_to(REPOSITORY_ROOT))
        try:
            current_blob = _git('hash-object', relative)
            head_blob = _git('rev-parse', f'HEAD:{relative}')
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f'v3 precommit is not tracked in HEAD: {relative}'
            ) from exc
        if current_blob != head_blob:
            raise RuntimeError(
                f'v3 precommit differs from HEAD: {relative}'
            )


def _v3_durable_freeze_document(
    freeze,
    *,
    current_stage,
    freeze_status,
    freeze_commit=None,
    freeze_tree=None,
    contract_sha256=None,
):
    """Project external freeze evidence into the tracked recovery record."""
    document = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'freeze_status': freeze_status,
        'current_stage': current_stage,
        'freeze_commit': freeze_commit,
        'freeze_tree_sha256': freeze_tree,
        'pre_freeze_commit': freeze['repository']['commit'],
        'pre_freeze_tree_sha256': freeze['repository']['tree'],
        'external_freeze_state_sha256': freeze['state_sha256'],
        'frozen_parameters_sha256': freeze[
            'frozen_profile_sha256'
        ],
        'parameter_selection_sha256': freeze['selection_sha256'],
        'acceptance_suite_sha256': file_sha256(
            V3_PRECOMMITTED_SUITE_PATH
        ),
        'suite_commitment_sha256': require_omission_sha256(
            _load_json(V3_COMMITMENT_PATH),
            'commitment_sha256',
            'acceptance commitment',
        ),
        'contract_sha256': contract_sha256,
        'runtime_inputs_sha256': freeze['repository'][
            'runtime_inputs_sha256'
        ],
        'immutable_input_hashes': freeze['repository']['input_hashes'],
        'permitted_evidence_only_commits': [],
    }
    document['freeze_state_sha256'] = omission_sha256(
        document, 'freeze_state_sha256'
    )
    return document


def run_v3_freeze(operator, evidence_root):
    """Freeze the selected profile and every implementation input hash."""
    root = Path(evidence_root).expanduser().resolve()
    state_path = _v3_state_path(root, 'freeze')
    if state_path.is_file():
        state = _v3_require_state(root, 'freeze')
        if state.get('operator') != operator:
            raise RuntimeError('v3 freeze operator drifted')
        if not _v3_state_path(root, 'contract').is_file():
            create_or_verify_json(
                V3_FREEZE_PATH,
                _v3_durable_freeze_document(
                    state,
                    current_stage='freeze',
                    freeze_status='pending_freeze_commit',
                ),
            )
        _v3_assert_worktree_changes({
            V3_FROZEN_PATH,
            V3_SELECTION_PATH,
            V3_FREEZE_PATH,
        })
        _v3_verify_freeze_inputs(state, require_clean=False)
        return state
    development = _v3_require_state(root, 'development')
    qualification = _v3_require_state(root, 'qualification')
    selected = development['selected_candidate']
    frozen = {
        'schema_version': 1,
        'profile_id': selected['candidate_id'],
        'launch_overrides': next(
            item['launch_overrides']
            for item in V3_CANDIDATES
            if item['candidate_id'] == selected['candidate_id']
        ),
    }
    frozen['sha256'] = canonical_sha256(frozen['launch_overrides'])
    selection = {
        'schema_version': 1,
        'selected_candidate': selected,
        'candidate_results': development['candidates'],
        'selection_key': list(_v3_selection_key(selected)),
    }
    pending_outputs = (
        V3_FROZEN_PATH.exists()
        or V3_SELECTION_PATH.exists()
    )
    if pending_outputs:
        _v3_assert_worktree_changes({
            V3_FROZEN_PATH,
            V3_SELECTION_PATH,
        })
        _v3_verify_repository_snapshot(
            qualification['repository'],
            require_clean=False,
        )
    else:
        _v3_verify_repository_snapshot(qualification['repository'])
    create_or_verify_yaml(V3_FROZEN_PATH, frozen)
    create_or_verify_json(V3_SELECTION_PATH, selection)
    reasons = []
    processes_before = _v3_active_processes()
    if processes_before:
        reasons.append('pre-freeze process set is not clean')
    try:
        _v3_assert_worktree_changes({
            V3_FROZEN_PATH,
            V3_SELECTION_PATH,
        })
    except RuntimeError as exc:
        reasons.append(str(exc))
    prepare = _v3_require_state(root, 'prepare')
    commitment = _load_json(V3_COMMITMENT_PATH)
    try:
        commitment_hash = require_omission_sha256(
            commitment,
            'commitment_sha256',
            'acceptance commitment',
        )
        if commitment_hash != prepare['commitment_sha256']:
            reasons.append('pre-freeze commitment hash drifted')
        if (
            file_sha256(V3_PRECOMMITTED_SUITE_PATH)
            != prepare['suite_sha256']
            or file_sha256(V3_PRECOMMITTED_SUITE_PATH)
            != commitment['suite_sha256']
        ):
            reasons.append('pre-freeze acceptance suite hash drifted')
        unused_keys, historical_hashes = _v3_historical_case_keys()
        del unused_keys
        if historical_hashes != commitment[
            'historical_exclusion_hashes'
        ]:
            reasons.append(
                'pre-freeze historical exclusion hashes drifted'
            )
    except (KeyError, OSError, RuntimeError, TypeError) as exc:
        reasons.append(str(exc))
    functional = _run_functional_tests()
    if not functional['passed']:
        reasons.append('pre-freeze functional test gate failed')
    commands, install_root = _v3_qualification_commands(
        root,
        'freeze_qualification',
        require_frozen=True,
    )
    if not all(item['passed'] for item in commands):
        reasons.append('pre-freeze installed qualification failed')
    dry_run_results = {}
    for name, expected in (
        ('activation', V3_EXPECTED_COUNTS['activation']),
        ('development', V3_EXPECTED_COUNTS['development_per_candidate']),
    ):
        path = (
            root
            / 'freeze_qualification'
            / f'{name}_dry_run.yaml'
        )
        if not path.is_file():
            reasons.append(
                f'pre-freeze {name} dry-run summary is missing'
            )
            continue
        summary = yaml.safe_load(path.read_text(encoding='utf-8'))
        dry_run_results[name] = {
            'path': str(path),
            'sha256': file_sha256(path),
            'resolved_run_count': summary.get('resolved_run_count'),
            'unsupported_count': summary.get('unsupported_count'),
            'scenario_schema_version': summary.get(
                'scenario_schema_version'
            ),
        }
        if (
            summary.get('resolved_run_count') != expected
            or summary.get('unsupported_count') != 0
            or summary.get('scenario_schema_version') != 4
        ):
            reasons.append(
                f'pre-freeze {name} dry-run contract failed'
            )
    processes_after = _v3_active_processes()
    if processes_after:
        reasons.append('post-freeze-qualification process set is not clean')
    try:
        _v3_assert_worktree_changes({
            V3_FROZEN_PATH,
            V3_SELECTION_PATH,
        })
    except RuntimeError as exc:
        reasons.append(str(exc))
    repository = _v3_repository_snapshot(
        require_clean=False,
        extra_paths=(
            V3_PRECOMMITTED_SUITE_PATH,
            V3_COMMITMENT_PATH,
            V3_FROZEN_PATH,
            V3_SELECTION_PATH,
        ),
    )
    state = _v3_write_state(root, 'freeze', {
        'passed': not reasons,
        'operator': operator,
        'development_state_sha256': development['state_sha256'],
        'qualification_state_sha256': qualification['state_sha256'],
        'repository': repository,
        'frozen_profile': frozen,
        'frozen_profile_path': str(V3_FROZEN_PATH),
        'frozen_profile_sha256': file_sha256(V3_FROZEN_PATH),
        'selection_sha256': canonical_sha256(selection),
        'requalification': {
            'functional_tests': functional,
            'qualification_commands': commands,
            'installed_dry_runs': dry_run_results,
            'isolated_install_root': str(install_root),
            'processes_before': processes_before,
            'processes_after': processes_after,
        },
        'reasons': reasons,
        'stage_order': [
            'prepare',
            'qualification',
            'activation',
            'development',
            'freeze',
            'seal',
            'holdout',
            'validation',
            'reproducibility',
            'report',
        ],
    })
    if state['passed']:
        atomic_json(
            V3_FREEZE_PATH,
            _v3_durable_freeze_document(
                state,
                current_stage='freeze',
                freeze_status='pending_freeze_commit',
            ),
        )
    return state


def _v3_schema_frozen_profile(freeze):
    frozen = freeze['frozen_profile']
    return {
        'profile_id': frozen['profile_id'],
        'launch_overrides': frozen['launch_overrides'],
        'sha256': frozen['sha256'],
    }


def _v3_runtime_population(population, freeze):
    """Bind the selected profile and rewrite repeat references in memory."""
    document = json.loads(json.dumps(population))
    frozen = _v3_schema_frozen_profile(freeze)
    document['frozen_profile'] = frozen
    unique = [
        case for case in document['cases']
        if case['acceptance_partition'] in {'holdout', 'validation'}
    ]
    population_to_runtime = {}
    for case in unique:
        population_key = _v3_resolved_case(population, case)['case_key']
        runtime_key = _v3_resolved_case(
            document,
            case,
            frozen_profile=frozen,
        )['case_key']
        population_to_runtime[population_key] = runtime_key
    for case in document['cases']:
        if case['acceptance_partition'] != 'reproducibility':
            continue
        reference = case['repeat_reference']
        reference['case_key'] = population_to_runtime[
            reference['case_key']
        ]
    return document


def _v3_contract_document(root, population, freeze, commitment):
    runtime_population = _v3_runtime_population(population, freeze)
    frozen = _v3_schema_frozen_profile(freeze)
    resolved = [
        _v3_resolved_case(
            runtime_population,
            case,
            frozen_profile=frozen,
        )
        for case in runtime_population['cases']
    ]
    unique = [
        item for item in resolved
        if item['acceptance_partition'] in {'holdout', 'validation'}
    ]
    repeats = [
        item for item in resolved
        if item['acceptance_partition'] == 'reproducibility'
    ]
    contract = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'scenario_schema_version': 4,
        'freeze_state_sha256': freeze['state_sha256'],
        'freeze_repository': freeze['repository'],
        'execution_repository': {
            'commit': _git('rev-parse', 'HEAD'),
            'tree': _git('rev-parse', 'HEAD^{tree}'),
        },
        'frozen_profile': frozen,
        'commitment_sha256': commitment['commitment_sha256'],
        'suite_sha256': commitment['suite_sha256'],
        'population_visibility': commitment['population_visibility'],
        'selection_blind': commitment['selection_blind'],
        'runtime_population_sha256': canonical_sha256(
            runtime_population
        ),
        'resolved_cases': resolved,
        'unique_case_keys': sorted(item['case_key'] for item in unique),
        'partition_case_keys': {
            partition: sorted(
                item['case_key']
                for item in unique
                if item['acceptance_partition'] == partition
            )
            for partition in ('holdout', 'validation')
        },
        'repeat_mappings': [
            {
                'repeat_case_key': item['case_key'],
                'reference': item['repeat_reference'],
            }
            for item in repeats
        ],
        'family_allocation': V3_FAMILY_ALLOCATION,
        'family_floors': V3_FAMILY_FLOORS,
        'holdout_family_floors': V3_HOLDOUT_FLOORS,
        'thresholds': {
            'end_to_end_minimum': 63,
            'end_to_end_denominator': 70,
            'holdout_minimum': 18,
            'holdout_denominator': 20,
            'local_escape_rate_minimum': 0.95,
            'local_escape_attempt_minimum': 39,
            'escape_duration_minimum': 38,
            'escape_median_max_sec': 20.0,
            'escape_p95_max_sec': 45.0,
            'orbit_minimum': 38,
            'orbit_median_max': 1.5,
            'revisit_minimum': 24,
            'revisit_rate_maximum': 0.05,
        },
        'replacement_caps': V3_REPLACEMENT_CAPS,
        'early_stop_rules': {
            'activation': (
                'finish ordinary behavioral misses; stop immediately on '
                'safety, evidence, ownership, cleanup, or hash failure'
            ),
            'development': (
                'run all 30 unless a hard safety, evidence, cleanup, or '
                'hash failure occurs'
            ),
            'holdout': (
                'stop when 18/20 or an exact family floor is unreachable'
            ),
            'validation': (
                'stop only on zero-tolerance failure or a mathematically '
                'unreachable declared gate'
            ),
            'reproducibility': 'stop on the first comparison mismatch',
        },
        'behavior_contract_interpretation': {
            'lifecycle_evidence_gate': (
                'The 70/70 gate covers positively observed lifecycle, '
                'safety, completeness, cleanup, and applicability evidence.'
            ),
            'scored_endpoint_predicates': [
                'controller_goal',
                'ground_truth_goal',
                'expected_terminal_state',
                'goal-bearing required_state_path suffix',
                'GOAL_REACHED',
            ],
            'end_to_end_definition': (
                'valid controller_success true and valid '
                'simulation_ground_truth_success true'
            ),
            'rationale': (
                'This Level B evidence-contract clarification preserves the '
                'declared 63/70 and family floors instead of making them '
                'redundant with a 70/70 endpoint gate.'
            ),
        },
        'status_semantics': [
            'passed',
            'failed',
            'not_applicable',
            'unavailable',
            'infrastructure_invalid',
            'not_run',
        ],
        'evidence_root': str(root),
        'proposed_tag': 'gesc-gaussian-simulation-ready-v3',
    }
    contract['contract_sha256'] = omission_sha256(
        contract, 'contract_sha256'
    )
    return contract


def _v3_verify_freeze_inputs(freeze, *, require_clean=True):
    """Verify every source and generated input captured before the freeze."""
    repository = freeze['repository']
    _v3_verify_repository_snapshot(
        repository,
        require_clean=require_clean,
    )
    input_hashes = repository.get('input_hashes', {})
    if canonical_sha256(input_hashes) != repository.get(
        'runtime_inputs_sha256'
    ):
        raise RuntimeError('v3 frozen runtime-input map hash drifted')
    for relative_path, expected in input_hashes.items():
        path = REPOSITORY_ROOT / relative_path
        if not path.is_file() or file_sha256(path) != expected:
            raise RuntimeError(
                f'v3 frozen runtime input drifted: {relative_path}'
            )
    if (
        not V3_FROZEN_PATH.is_file()
        or file_sha256(V3_FROZEN_PATH)
        != freeze['frozen_profile_sha256']
    ):
        raise RuntimeError('v3 frozen parameter file drifted')
    if yaml.safe_load(
        V3_FROZEN_PATH.read_text(encoding='utf-8')
    ) != freeze['frozen_profile']:
        raise RuntimeError('v3 frozen parameter contents drifted')
    selection = _load_json(V3_SELECTION_PATH)
    if canonical_sha256(selection) != freeze['selection_sha256']:
        raise RuntimeError('v3 parameter selection drifted')
    commitment = _load_json(V3_COMMITMENT_PATH)
    require_omission_sha256(
        commitment,
        'commitment_sha256',
        'acceptance commitment',
    )
    if file_sha256(V3_PRECOMMITTED_SUITE_PATH) != commitment[
        'suite_sha256'
    ]:
        raise RuntimeError('v3 precommitted acceptance suite drifted')
    durable = _load_json(V3_FREEZE_PATH)
    require_omission_sha256(
        durable, 'freeze_state_sha256', 'durable freeze state'
    )
    if durable.get('external_freeze_state_sha256') != freeze[
        'state_sha256'
    ]:
        raise RuntimeError('durable and external freeze states differ')
    if durable.get('runtime_inputs_sha256') != repository[
        'runtime_inputs_sha256'
    ]:
        raise RuntimeError('durable freeze runtime inputs drifted')
    return commitment


def _v3_verify_runtime_contract(
    root,
    freeze,
    contract_state,
    *,
    require_clean=True,
):
    """Verify the sealed suite, contract, freeze, and current source inputs."""
    commitment = _v3_verify_freeze_inputs(
        freeze,
        require_clean=require_clean,
    )
    tracked_contract = V3_CONTRACT_PATH.read_bytes()
    sealed_contract_path = Path(contract_state['contract_path'])
    if (
        not sealed_contract_path.is_file()
        or sealed_contract_path.read_bytes() != tracked_contract
    ):
        raise RuntimeError('tracked and sealed v3 contracts differ')
    contract = json.loads(tracked_contract.decode('utf-8'))
    require_omission_sha256(
        contract, 'contract_sha256', 'v3 acceptance contract'
    )
    if contract['contract_sha256'] != contract_state[
        'contract_sha256'
    ]:
        raise RuntimeError('v3 contract state hash differs')
    if contract['freeze_state_sha256'] != freeze['state_sha256']:
        raise RuntimeError('v3 contract freeze binding drifted')
    suite_path = Path(contract_state['suite_path'])
    if (
        not suite_path.is_file()
        or file_sha256(suite_path) != contract_state['suite_sha256']
        or file_sha256(suite_path) != commitment['suite_sha256']
    ):
        raise RuntimeError('v3 sealed suite hash drifted')
    if str(Path(contract['evidence_root']).resolve()) != str(root):
        raise RuntimeError('v3 contract evidence root drifted')
    return contract


def _v3_publish_sealed_durable_freeze(freeze, contract):
    """Advance the tracked freeze projection exactly once after sealing."""
    expected = _v3_durable_freeze_document(
        freeze,
        current_stage='contract',
        freeze_status='sealed',
        freeze_commit=contract['execution_repository']['commit'],
        freeze_tree=contract['execution_repository']['tree'],
        contract_sha256=contract['contract_sha256'],
    )
    prior = _v3_durable_freeze_document(
        freeze,
        current_stage='freeze',
        freeze_status='pending_freeze_commit',
    )
    if V3_FREEZE_PATH.is_file():
        observed = _load_json(V3_FREEZE_PATH)
        if observed not in (prior, expected):
            raise RuntimeError(
                'v3 durable freeze cannot transition from drifted bytes'
            )
    atomic_json(V3_FREEZE_PATH, expected)


def run_v3_seal(operator, evidence_root):
    """Bind the precommitted suite after a clean implementation freeze."""
    root = Path(evidence_root).expanduser().resolve()
    state_path = _v3_state_path(root, 'contract')
    if state_path.is_file():
        state = _v3_require_state(root, 'contract')
        if state.get('operator') != operator:
            raise RuntimeError('v3 seal operator drifted')
        _v3_assert_worktree_changes({
            V3_CONTRACT_PATH,
            V3_FREEZE_PATH,
        })
        freeze = _v3_require_state(root, 'freeze')
        contract = _v3_verify_runtime_contract(
            root,
            freeze,
            state,
            require_clean=False,
        )
        _v3_publish_sealed_durable_freeze(freeze, contract)
        return state
    freeze = _v3_require_state(root, 'freeze')
    partial_contract = V3_CONTRACT_PATH.is_file()
    if partial_contract:
        _v3_assert_worktree_changes({V3_CONTRACT_PATH})
    elif _git('status', '--porcelain'):
        raise RuntimeError('v3 seal requires a clean post-freeze worktree')
    development = _v3_require_state(root, 'development')
    if freeze['development_state_sha256'] != development['state_sha256']:
        raise RuntimeError('v3 freeze/development state link drifted')
    commitment = _v3_verify_freeze_inputs(
        freeze,
        require_clean=not partial_contract,
    )
    suite_bytes = V3_PRECOMMITTED_SUITE_PATH.read_bytes()
    if _sha256_bytes(suite_bytes) != commitment['suite_sha256']:
        raise RuntimeError('v3 precommitted suite hash drifted')
    population = json.loads(suite_bytes.decode('utf-8'))
    historical_keys, historical_hashes = _v3_historical_case_keys()
    if historical_hashes != commitment['historical_exclusion_hashes']:
        raise RuntimeError('v3 historical exclusion inputs drifted')
    validation = validate_v3_population(
        population,
        historical_case_keys=historical_keys,
    )
    if not validation['passed']:
        raise RuntimeError(
            'precommitted population failed validation: '
            + '; '.join(validation['reasons'])
        )
    sealed_directory = root / 'sealed'
    sealed_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    sealed_directory.chmod(0o700)
    suite_path = sealed_directory / 'phase08_v3_acceptance_suite.json'
    create_or_verify_bytes(suite_path, suite_bytes, mode=0o400)
    contract = _v3_contract_document(
        root,
        population,
        freeze,
        commitment,
    )
    contract_bytes = (
        json.dumps(
            contract,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + '\n'
    ).encode('utf-8')
    sealed_contract = (
        sealed_directory / 'phase_08_v3_acceptance_contract.json'
    )
    create_or_verify_bytes(sealed_contract, contract_bytes, mode=0o400)
    create_or_verify_bytes(V3_CONTRACT_PATH, contract_bytes, mode=0o644)
    state = _v3_write_state(root, 'contract', {
        'passed': True,
        'operator': operator,
        'freeze_state_sha256': freeze['state_sha256'],
        'execution_commit': _git('rev-parse', 'HEAD'),
        'execution_tree': _git('rev-parse', 'HEAD^{tree}'),
        'suite_path': str(suite_path),
        'suite_sha256': file_sha256(suite_path),
        'contract_path': str(sealed_contract),
        'contract_sha256': contract['contract_sha256'],
        'population_validation': validation,
    })
    _v3_publish_sealed_durable_freeze(freeze, contract)
    del suite_bytes
    return state


def _v3_runtime_suite(evidence_root):
    root = Path(evidence_root).expanduser().resolve()
    contract_state = _v3_require_state(root, 'contract')
    freeze = _v3_require_state(root, 'freeze')
    if contract_state['freeze_state_sha256'] != freeze['state_sha256']:
        raise RuntimeError('v3 contract/freeze state link drifted')
    _v3_verify_runtime_contract(root, freeze, contract_state)
    population = json.loads(
        Path(contract_state['suite_path']).read_text(encoding='utf-8')
    )
    return _v3_runtime_population(population, freeze), contract_state


def _v3_record_end_to_end(record):
    metrics = (record.get('analysis') or {}).get('metrics', {})
    controller = metrics.get('controller_success', {})
    ground_truth = metrics.get('simulation_ground_truth_success', {})
    return (
        controller.get('status') == 'valid'
        and controller.get('value') is True
        and ground_truth.get('status') == 'valid'
        and ground_truth.get('value') is True
    )


def _v3_partition_stop_decider(
    partition,
    document,
    contract,
    evidence_root,
):
    expected_by_id = {
        case['case_id']: case
        for case in contract['resolved_cases']
        if case['acceptance_partition'] == partition
    }
    if partition == 'holdout':
        prior_records = []
    elif partition == 'validation':
        holdout = _v3_require_state(evidence_root, 'holdout')
        prior_records = _load_json(holdout['records_path'])
    elif partition == 'reproducibility':
        holdout = _v3_require_state(evidence_root, 'holdout')
        validation = _v3_require_state(evidence_root, 'validation')
        prior_records = (
            _load_json(holdout['records_path'])
            + _load_json(validation['records_path'])
        )
    else:
        raise ValueError(f'unsupported v3 partition: {partition}')

    def decide(records, remaining_ids):
        latest = records[-1]
        expected = expected_by_id.get(latest.get('case_id'))
        if expected is None:
            return 'executed case is absent from the sealed contract'
        evaluation = _v3_case_evaluation(latest, expected)
        if (
            not evaluation['integrity']['passed']
            or evaluation['binding_reasons']
            or evaluation['reasons']
        ):
            return (
                f'{partition} zero-tolerance evidence failure in '
                f'{latest.get("case_id")}'
            )
        if not evaluation['lifecycle_passed']:
            return (
                f'{partition} lifecycle contract failed in '
                f'{latest.get("case_id")}'
            )
        if partition == 'reproducibility':
            result = evaluate_v3_reproducibility(
                [latest],
                prior_records,
            )['results'][0]
            if not result['passed']:
                return (
                    'reproducibility first mismatch in '
                    f'{latest.get("case_id")}'
                )
            return None

        pooled = prior_records + records
        successes = sum(_v3_record_end_to_end(item) for item in pooled)
        remaining_cases = [
            expected_by_id[case_id]
            for case_id in remaining_ids
        ]
        if partition == 'holdout':
            if successes + len(remaining_cases) < 18:
                return 'holdout 18/20 floor is mathematically unreachable'
            floors = V3_HOLDOUT_FLOORS
            observed = Counter(
                item.get('acceptance_family')
                for item in records
                if _v3_record_end_to_end(item)
            )
        else:
            if successes + len(remaining_cases) < 63:
                return 'unique 63/70 floor is mathematically unreachable'
            floors = V3_FAMILY_FLOORS
            observed = Counter(
                item.get('acceptance_family')
                for item in pooled
                if _v3_record_end_to_end(item)
            )
        remaining_by_family = Counter(
            case['acceptance_family'] for case in remaining_cases
        )
        for family, floor in floors.items():
            if observed[family] + remaining_by_family[family] < floor:
                return (
                    f'{partition} {family} floor is mathematically '
                    'unreachable'
                )
        if partition == 'validation':
            escape_attempts = []
            revisit_values = []
            revisit_remaining = sum(
                case['metric_applicability']['revisit']
                for case in remaining_cases
            )
            for item in pooled:
                analysis = item.get('analysis') or {}
                if item.get('metric_applicability', {}).get(
                    'escape_attempt'
                ):
                    escape_attempts.extend(
                        analysis.get('escape_attempts', [])
                    )
                if (
                    item.get('metric_applicability', {}).get('revisit')
                    and _v3_record_end_to_end(item)
                ):
                    revisit = analysis.get('metrics', {}).get(
                        'revisit_count', {}
                    )
                    if revisit.get('status') == 'valid':
                        revisit_values.append(float(revisit['value']))
            remaining_escape = sum(
                case['metric_applicability']['escape_attempt']
                for case in remaining_cases
            )
            successes_now = sum(
                attempt.get('outcome') == 'success'
                for attempt in escape_attempts
            )
            optimistic_attempts = len(escape_attempts) + remaining_escape
            optimistic_successes = successes_now + remaining_escape
            if (
                remaining_escape == 0
                and (
                    optimistic_attempts < 39
                    or (
                        optimistic_successes / optimistic_attempts
                    ) < 0.95
                )
            ):
                return (
                    'unique local-escape gate is mathematically '
                    'unreachable'
                )
            optimistic_revisit_denominator = (
                len(revisit_values) + revisit_remaining
            )
            if (
                optimistic_revisit_denominator < 24
                or (
                    sum(value > 0 for value in revisit_values)
                    / optimistic_revisit_denominator
                ) >= 0.05
            ):
                return (
                    'unique revisit gate is mathematically unreachable'
                )
        return None

    return decide


def _v3_execute_partition(partition, operator, evidence_root):
    root = Path(evidence_root).expanduser().resolve()
    document, contract_state = _v3_runtime_suite(root)
    freeze = _v3_require_state(root, 'freeze')
    contract = _load_json(V3_CONTRACT_PATH)
    stage_root = root / partition
    stage_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    stage_root.chmod(0o700)
    document['cases'] = [
        case for case in document['cases']
        if case['acceptance_partition'] == partition
    ]
    suite_path = stage_root / 'resolved_suite.json'
    payload = (
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ) + '\n'
    ).encode('utf-8')
    if suite_path.exists():
        if suite_path.read_bytes() != payload:
            raise RuntimeError(f'{partition} materialized suite drifted')
    else:
        atomic_bytes(suite_path, payload, mode=0o400)
    summary, records, unused_progress = _v3_execute_serial_slots(
        suite_path,
        operator,
        root,
        stage_root,
        partition,
        stop_decider=_v3_partition_stop_decider(
            partition,
            document,
            contract,
            root,
        ),
        runtime_snapshot=freeze['repository'],
    )
    del unused_progress
    return summary, records, contract_state


def _v3_gate(identifier, passed, value, threshold, reason=None):
    gate = _gate(identifier, passed, value, threshold, reason)
    gate['status'] = 'evaluated'
    return gate


def _v3_is_subsequence(required, observed):
    cursor = iter(observed)
    return all(any(item == wanted for item in cursor) for wanted in required)


def _v3_contract_case_map(contract, partitions):
    if not isinstance(contract, dict):
        raise ValueError('v3 acceptance contract is missing')
    if 'contract_sha256' in contract:
        require_omission_sha256(
            contract, 'contract_sha256', 'v3 acceptance contract'
        )
    resolved = contract.get('resolved_cases')
    if not isinstance(resolved, list):
        raise ValueError('v3 contract resolved_cases is missing')
    selected = [
        case for case in resolved
        if case.get('acceptance_partition') in set(partitions)
    ]
    keys = [case.get('case_key') for case in selected]
    if (
        any(not isinstance(key, str) or len(key) != 64 for key in keys)
        or len(keys) != len(set(keys))
    ):
        raise ValueError('v3 contract case identities are invalid')
    return {case['case_key']: case for case in selected}


def _v3_boolean_metric(metrics, name, reasons):
    item = metrics.get(name, {})
    if (
        item.get('status') != 'valid'
        or not isinstance(item.get('value'), bool)
    ):
        reasons.append(f'{name} categorical evidence is unavailable')
        return None
    return item['value']


def _v3_case_evaluation(record, expected):
    analysis = record.get('analysis') or {}
    metrics = analysis.get('metrics', {})
    applicability = expected.get('metric_applicability', {})
    reasons = []
    binding_reasons = []
    if record.get('case_key') != expected.get('case_key'):
        binding_reasons.append('case key differs from the sealed contract')
    for name in (
        'acceptance_family',
        'acceptance_partition',
        'metric_applicability',
        'disturbances',
    ):
        if record.get(name) != expected.get(name):
            binding_reasons.append(f'{name} differs from sealed contract')
    expected_truth_hash = (
        expected.get('success', {})
        .get('ground_truth', {})
        .get('aggregate_field', {})
        .get('result_sha256')
    )
    if analysis.get('aggregate_truth_result_sha256') != expected_truth_hash:
        binding_reasons.append('aggregate truth hash differs from contract')
    if analysis.get('acceptance_family') != expected.get(
        'acceptance_family'
    ):
        binding_reasons.append('analysis family differs from contract')
    if analysis.get('acceptance_partition') != expected.get(
        'acceptance_partition'
    ):
        binding_reasons.append('analysis partition differs from contract')
    if analysis.get('metric_applicability') != applicability:
        binding_reasons.append(
            'analysis applicability differs from contract'
        )

    controller_goal = _v3_boolean_metric(
        metrics, 'controller_success', reasons
    )
    ground_truth_goal = _v3_boolean_metric(
        metrics, 'simulation_ground_truth_success', reasons
    )
    end_to_end = (
        controller_goal is True and ground_truth_goal is True
    )
    predicate_results = record.get('classification', {}).get(
        'predicate_results', {}
    )
    for predicate, metric_value in (
        ('controller_goal', controller_goal),
        ('ground_truth_goal', ground_truth_goal),
    ):
        classified = predicate_results.get(predicate)
        if (
            metric_value is not None
            and classified is not None
            and classified is not metric_value
        ):
            reasons.append(
                f'{predicate} disagrees between runner and analyzer'
            )

    scope = record.get('classification', {}).get(
        'result_scopes', {}
    ).get('full_lifecycle')
    lifecycle_reasons = []
    if not isinstance(scope, dict):
        lifecycle_reasons.append('full_lifecycle scope is missing')
    else:
        if scope.get('anchor_observed') is not True:
            lifecycle_reasons.append(
                'full_lifecycle anchor was not observed'
            )
        safe_predicates = {
            'recording_complete',
            'cleanup_complete',
            'required_state_sequence',
            'required_event_sequence',
            'no_forbidden_states',
            'no_forbidden_events',
            'minimum_saturation_samples',
            'collision_expectation',
        }
        scoped_results = scope.get('predicate_results', {})
        for predicate in scope.get('required_predicates', []):
            if (
                predicate in safe_predicates
                and scoped_results.get(predicate) is not True
            ):
                lifecycle_reasons.append(
                    f'lifecycle predicate {predicate} failed'
                )
    controller = expected.get('success', {}).get('controller', {})
    required_path = list(controller.get('required_state_path', []))
    escape_expected = bool(applicability.get('escape_attempt'))
    branch_path = required_path[:-2] if escape_expected else required_path[:-1]
    observed_path = record.get('outcomes', {}).get(
        'observed_state_sequence', []
    )
    if (
        not isinstance(observed_path, list)
        or not _v3_is_subsequence(branch_path, observed_path)
    ):
        lifecycle_reasons.append(
            'pre-endpoint lifecycle path was not observed'
        )
    observed_events = record.get('outcomes', {}).get(
        'observed_events', []
    )
    lifecycle_events = [
        event for event in controller.get('required_events', [])
        if event != 'GOAL_REACHED'
    ]
    if (
        not isinstance(observed_events, list)
        or not all(event in observed_events for event in lifecycle_events)
    ):
        lifecycle_reasons.append(
            'pre-endpoint lifecycle events were not observed'
        )

    attempts = analysis.get('escape_attempts', [])
    if not isinstance(attempts, list):
        attempts = []
        reasons.append('escape attempt rows are invalid')
    successful_attempts = [
        attempt for attempt in attempts
        if attempt.get('outcome') == 'success'
    ]
    duration_values = []
    orbit_values = []
    attempt_metric_valid = True
    for attempt in successful_attempts:
        for name, destination in (
            ('duration', duration_values),
            ('orbit_count', orbit_values),
        ):
            item = attempt.get(name, {})
            value = item.get('value')
            if (
                item.get('status') != 'valid'
                or isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
            ):
                attempt_metric_valid = False
                reasons.append(
                    f'successful escape has unavailable {name}'
                )
            else:
                destination.append(float(value))
    if escape_expected and not attempts:
        lifecycle_reasons.append('designated escape was not attempted')
    if not escape_expected and attempts:
        reasons.append('non-designated case recorded an escape attempt')
    assist_expected = 'ESCAPE_ASSIST' in required_path
    assist_observed = any(
        attempt.get('assisted') is True for attempt in attempts
    )
    if assist_expected and not assist_observed:
        lifecycle_reasons.append('designated assist was not observed')
    merge_expected = 'FILL_MERGED' in controller.get(
        'required_events', []
    )
    merge_metric = metrics.get('merge_count', {})
    merge_observed = (
        merge_metric.get('status') == 'valid'
        and isinstance(merge_metric.get('value'), (int, float))
        and not isinstance(merge_metric.get('value'), bool)
        and merge_metric['value'] >= 1
    )
    if merge_expected and not merge_observed:
        lifecycle_reasons.append('designated merge was not observed')
    fill_metric = metrics.get('fill_count', {})
    fill_observed = (
        fill_metric.get('status') == 'valid'
        and isinstance(fill_metric.get('value'), (int, float))
        and not isinstance(fill_metric.get('value'), bool)
        and fill_metric['value'] >= 1
    )
    if escape_expected and not fill_observed:
        lifecycle_reasons.append('designated fill was not observed')
    recenter_observed = 'RECENTER_COMPLETE' in observed_events
    if escape_expected and not recenter_observed:
        lifecycle_reasons.append(
            'designated recenter completion was not observed'
        )

    delay_valid = True
    disturbances = expected.get('disturbances', {})
    sensor_delay = float(disturbances.get('sensor_delay_sec', 0.0))
    pose_delay = float(disturbances.get('pose_delay_sec', 0.0))
    delay_expectations = {
        'observed_raw_cost_delay': sensor_delay,
        'observed_source_cost_delay': sensor_delay,
        'observed_pose_delay': pose_delay,
    }
    for name, declared in delay_expectations.items():
        item = metrics.get(name, {})
        if declared > 0.0:
            value = item.get('value')
            if (
                item.get('status') != 'valid'
                or isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or abs(float(value) - declared) > 0.02
            ):
                delay_valid = False
                reasons.append(
                    f'{name} does not match the declared delay'
                )
        elif item.get('status') != 'not_applicable':
            delay_valid = False
            reasons.append(f'{name} must be not_applicable')

    saturation_valid = True
    if applicability.get('saturation'):
        fraction = metrics.get('saturation_fraction', {})
        axes = metrics.get('saturation_axis_counts', {})
        excess = metrics.get('maximum_limit_excess', {})
        saturation_valid = (
            fraction.get('status') == 'valid'
            and isinstance(fraction.get('value'), (int, float))
            and not isinstance(fraction.get('value'), bool)
            and fraction['value'] > 0.0
            and axes.get('status') == 'valid'
            and isinstance(axes.get('value'), dict)
            and sum(axes['value'].values()) > 0
            and excess.get('status') == 'valid'
            and isinstance(excess.get('value'), (int, float))
            and not isinstance(excess.get('value'), bool)
            and math.isfinite(float(excess['value']))
        )
        if not saturation_valid:
            reasons.append('declared saturation evidence is invalid')

    final_distance = metrics.get(
        'final_aggregate_target_distance', {}
    )
    value = final_distance.get('value')
    if (
        final_distance.get('status') != 'valid'
        or isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        reasons.append('final aggregate target distance is unavailable')

    revisit_value = None
    if applicability.get('revisit') and end_to_end:
        revisit = metrics.get('revisit_count', {})
        value = revisit.get('value')
        if (
            revisit.get('status') != 'valid'
            or isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            reasons.append('applicable revisit evidence is unavailable')
        else:
            revisit_value = float(value)

    integrity = _v3_record_integrity(record)
    return {
        'passed': (
            integrity['passed']
            and not binding_reasons
            and not reasons
            and not lifecycle_reasons
        ),
        'integrity': integrity,
        'binding_reasons': binding_reasons,
        'reasons': reasons,
        'lifecycle_reasons': lifecycle_reasons,
        'lifecycle_passed': not lifecycle_reasons,
        'end_to_end': end_to_end,
        'attempts': attempts,
        'successful_attempts': successful_attempts,
        'duration_values': duration_values,
        'orbit_values': orbit_values,
        'attempt_metric_valid': attempt_metric_valid,
        'revisit_value': revisit_value,
        'escape_expected': escape_expected,
        'assist_expected': assist_expected,
        'assist_observed': assist_observed,
        'merge_expected': merge_expected,
        'merge_observed': merge_observed,
        'fill_observed': fill_observed,
        'recenter_observed': recenter_observed,
        'delay_valid': delay_valid,
        'saturation_valid': saturation_valid,
    }


def evaluate_v3_unique_gates(records, contract):
    """Evaluate 70 unique records against the sealed v3 contract."""
    contract_reasons = []
    try:
        expected = _v3_contract_case_map(
            contract, {'holdout', 'validation'}
        )
    except (RuntimeError, ValueError) as exc:
        expected = {}
        contract_reasons.append(str(exc))
    record_keys = [record.get('case_key') for record in records]
    duplicates = [
        key for key, count in Counter(record_keys).items()
        if count > 1
    ]
    by_key = {
        record.get('case_key'): record for record in records
        if isinstance(record.get('case_key'), str)
    }
    if len(expected) != 70:
        contract_reasons.append('contract does not contain 70 unique cases')
    if len(records) != 70:
        contract_reasons.append('record set does not contain 70 runs')
    if duplicates:
        contract_reasons.append('record set contains duplicate case keys')
    if set(by_key) != set(expected):
        contract_reasons.append(
            'record case keys differ from the sealed 70-case population'
        )

    evaluations = []
    for key, expected_case in expected.items():
        record = by_key.get(key)
        if record is None:
            continue
        evaluations.append((
            expected_case,
            _v3_case_evaluation(record, expected_case),
        ))
    family_totals = Counter(
        case['acceptance_family'] for case in expected.values()
    )
    declared_allocation = contract.get('family_allocation', {})
    for family, allocation in declared_allocation.items():
        if family_totals[family] != allocation.get('unique'):
            contract_reasons.append(
                f'{family} unique allocation differs from contract'
            )
    if set(family_totals) != set(V3_FAMILY_ALLOCATION):
        contract_reasons.append('acceptance family set differs from plan')
    for family, allocation in V3_FAMILY_ALLOCATION.items():
        if family_totals[family] != allocation['unique']:
            contract_reasons.append(
                f'{family} exact family allocation drifted'
            )

    family_successes = Counter()
    e2e_total = 0
    behavior_passes = 0
    integrity_passes = 0
    binding_passes = 0
    designated_cases = 0
    designated_with_attempt = 0
    attempts = []
    durations = []
    orbits = []
    all_attempt_metrics_valid = True
    revisit_values = []
    revisit_applicable = 0
    fill_observed = 0
    assist_expected = 0
    assist_observed = 0
    merge_expected = 0
    merge_observed = 0
    recenter_observed = 0
    disturbance_constraint_valid = True
    for expected_case, evaluation in evaluations:
        family = expected_case['acceptance_family']
        e2e_total += int(evaluation['end_to_end'])
        family_successes[family] += int(evaluation['end_to_end'])
        behavior_passes += int(evaluation['lifecycle_passed'])
        integrity_passes += int(evaluation['integrity']['passed'])
        binding_passes += int(not evaluation['binding_reasons'])
        if evaluation['escape_expected']:
            designated_cases += 1
            designated_with_attempt += int(bool(evaluation['attempts']))
            attempts.extend(evaluation['attempts'])
            fill_observed += int(evaluation['fill_observed'])
            recenter_observed += int(evaluation['recenter_observed'])
        durations.extend(evaluation['duration_values'])
        orbits.extend(evaluation['orbit_values'])
        all_attempt_metrics_valid &= evaluation['attempt_metric_valid']
        applicability = expected_case['metric_applicability']
        if applicability.get('revisit'):
            revisit_applicable += 1
        if evaluation['revisit_value'] is not None:
            revisit_values.append(evaluation['revisit_value'])
        assist_expected += int(evaluation['assist_expected'])
        assist_observed += int(
            evaluation['assist_expected']
            and evaluation['assist_observed']
        )
        merge_expected += int(evaluation['merge_expected'])
        merge_observed += int(
            evaluation['merge_expected']
            and evaluation['merge_observed']
        )
        disturbance_constraint_valid &= (
            evaluation['delay_valid']
            and evaluation['saturation_valid']
        )

    attempt_successes = sum(
        attempt.get('outcome') == 'success' for attempt in attempts
    )
    attempt_rate = (
        attempt_successes / len(attempts) if attempts else None
    )
    revisit_rate = (
        sum(value > 0 for value in revisit_values) / len(revisit_values)
        if revisit_values else None
    )
    exact_records = (
        not contract_reasons
        and len(evaluations) == 70
    )
    gates = [
        _v3_gate(
            'contract_population_binding',
            exact_records and binding_passes == 70,
            {
                'bound': binding_passes,
                'evaluated': len(evaluations),
                'reasons': contract_reasons,
            },
            'exact sealed 70 keys, partitions, families, and applicability',
        ),
        _v3_gate(
            'completeness_analysis_integrity',
            exact_records and integrity_passes == 70,
            f'{integrity_passes}/{len(evaluations)}',
            '70/70 valid unique runs',
        ),
        _v3_gate(
            'behavior_contracts',
            exact_records and behavior_passes == 70,
            f'{behavior_passes}/{len(evaluations)}',
            (
                '70/70 lifecycle/evidence contracts; controller and '
                'aggregate goal outcomes scored separately'
            ),
        ),
        _v3_gate(
            'end_to_end',
            exact_records and e2e_total >= 63,
            f'{e2e_total}/70',
            'at least 63/70',
        ),
        _v3_gate(
            'family_floors',
            exact_records and all(
                family_successes.get(family, 0) >= floor
                for family, floor in V3_FAMILY_FLOORS.items()
            ),
            dict(sorted(family_successes.items())),
            V3_FAMILY_FLOORS,
        ),
        _v3_gate(
            'local_escape',
            designated_cases == 39
            and designated_with_attempt == 39
            and len(attempts) >= 39
            and attempt_rate is not None
            and attempt_rate >= 0.95,
            {
                'designated_cases': designated_cases,
                'with_attempt': designated_with_attempt,
                'successes': attempt_successes,
                'attempts': len(attempts),
                'rate': attempt_rate,
            },
            '39 designated cases, >=39 attempts, >=0.95 success',
        ),
        _v3_gate(
            'escape_duration',
            all_attempt_metrics_valid
            and len(durations) >= 38
            and statistics.median(durations) <= 20.0
            and _percentile(durations, 95) <= 45.0,
            {
                'all_successful_attempts_valid': (
                    all_attempt_metrics_valid
                ),
                'count': len(durations),
                'median_sec': (
                    statistics.median(durations) if durations else None
                ),
                'p95_sec': _percentile(durations, 95),
            },
            'every success valid; >=38, median <=20 s, p95 <=45 s',
        ),
        _v3_gate(
            'orbit_count',
            all_attempt_metrics_valid
            and len(orbits) >= 38
            and statistics.median(orbits) <= 1.5,
            {
                'all_successful_attempts_valid': (
                    all_attempt_metrics_valid
                ),
                'count': len(orbits),
                'median': statistics.median(orbits) if orbits else None,
            },
            'every success valid; >=38 and median <=1.5',
        ),
        _v3_gate(
            'revisit',
            revisit_applicable == 24
            and len(revisit_values) >= 24
            and revisit_rate is not None
            and revisit_rate < 0.05,
            {
                'applicable': revisit_applicable,
                'valid_successful_runs': len(revisit_values),
                'rate': revisit_rate,
            },
            '24 predeclared valid successful runs and rate <0.05',
        ),
        _v3_gate(
            'lifecycle_coverage',
            designated_cases == 39
            and fill_observed == 39
            and assist_expected == 6
            and assist_observed == 6
            and merge_expected == 4
            and merge_observed == 4
            and recenter_observed >= 38
            and revisit_applicable == 24,
            {
                'fills': fill_observed,
                'assists': assist_observed,
                'merges': merge_observed,
                'recenter_completions': recenter_observed,
                'revisit_applicable': revisit_applicable,
            },
            '39 fills, 6 assists, 4 merges, >=38 recenters, 24 revisits',
        ),
        _v3_gate(
            'disturbance_constraint_evidence',
            exact_records and disturbance_constraint_valid,
            disturbance_constraint_valid,
            'all declared delays and saturation evidence valid',
        ),
        _v3_gate(
            'metric_applicability',
            exact_records and all(
                evaluation['passed']
                for unused, evaluation in evaluations
            ),
            sum(
                evaluation['passed']
                for unused, evaluation in evaluations
            ),
            '70/70 bound applicability and evidence-valid cases',
        ),
    ]
    intervals = {
        'overall': wilson_interval(e2e_total, 70),
        'by_family': {
            family: wilson_interval(
                family_successes[family],
                V3_FAMILY_ALLOCATION[family]['unique'],
            )
            for family in sorted(V3_FAMILY_ALLOCATION)
        },
    }
    return {
        'passed': all(gate['passed'] for gate in gates),
        'gates': gates,
        'confidence_intervals': intervals,
        'case_evaluations': [
            {
                'case_key': expected_case['case_key'],
                **evaluation,
            }
            for expected_case, evaluation in evaluations
        ],
        'contract_reasons': contract_reasons,
    }


def run_v3_holdout(operator, evidence_root):
    """Execute and evaluate the 20-case early holdout gate."""
    root = Path(evidence_root).expanduser().resolve()
    contract_state = _v3_require_state(root, 'contract')
    summary, records, unused = _v3_execute_partition(
        'holdout',
        operator,
        root,
    )
    del unused
    progress = _v3_load_progress(root / 'holdout')
    contract = _load_json(V3_CONTRACT_PATH)
    expected = _v3_contract_case_map(contract, {'holdout'})
    record_keys = [record.get('case_key') for record in records]
    by_key = {
        record.get('case_key'): record for record in records
        if isinstance(record.get('case_key'), str)
    }
    evaluations = [
        (case, _v3_case_evaluation(by_key[key], case))
        for key, case in expected.items()
        if key in by_key
    ]
    family_successes = Counter()
    for case, evaluation in evaluations:
        family_successes[case['acceptance_family']] += int(
            evaluation['end_to_end']
        )
    e2e = sum(
        evaluation['end_to_end']
        for unused_case, evaluation in evaluations
    )
    contracts = all(
        evaluation['lifecycle_passed']
        for unused_case, evaluation in evaluations
    )
    integrity_pass_count = sum(
        evaluation['integrity']['passed']
        for unused_case, evaluation in evaluations
    )
    evidence_valid = all(
        evaluation['passed']
        for unused_case, evaluation in evaluations
    )
    reasons = []
    if progress.get('stopped_early_reason'):
        reasons.append(
            f"holdout hard stop: {progress['stopped_early_reason']}"
        )
    if (
        len(expected) != 20
        or len(records) != 20
        or len(record_keys) != len(set(record_keys))
        or set(record_keys) != set(expected)
    ):
        reasons.append('holdout identities differ from sealed contract')
    if integrity_pass_count != 20 or not evidence_valid:
        reasons.append('holdout integrity or denominator failed')
    if e2e < 18:
        reasons.append('holdout end-to-end floor failed')
    if any(
        family_successes[family] < floor
        for family, floor in V3_HOLDOUT_FLOORS.items()
    ):
        reasons.append('one or more holdout family floors failed')
    if not contracts:
        reasons.append('one or more holdout lifecycle contracts failed')
    return _v3_write_state(root, 'holdout', {
        'passed': not reasons,
        'operator': operator,
        'contract_state_sha256': contract_state['state_sha256'],
        'run_count': len(records),
        'end_to_end_success_count': e2e,
        'family_successes': dict(sorted(family_successes.items())),
        'integrity_pass_count': integrity_pass_count,
        'case_evaluations': [
            {
                'case_key': case['case_key'],
                **evaluation,
            }
            for case, evaluation in evaluations
        ],
        'scenario_summary_path': summary.get('summary_path'),
        'scenario_summary_sha256': file_sha256(
            root / 'holdout/scenario_summary.yaml'
        ),
        'records_path': str(root / 'holdout/records.json'),
        'records_sha256': file_sha256(root / 'holdout/records.json'),
        'attempt_records_sha256': file_sha256(
            root / 'holdout/attempt_records.json'
        ),
        'progress_sha256': progress['progress_sha256'],
        'stopped_early_reason': progress.get('stopped_early_reason'),
        'ambiguous_interrupted_dispatch_case_ids': progress.get(
            'ambiguous_interrupted_dispatch_case_ids',
            [],
        ),
        'not_run_slot_ids': progress['not_run_slot_ids'],
        'replacement_state_sha256': (
            file_sha256(_v3_replacement_state_path(root))
            if _v3_replacement_state_path(root).is_file()
            else None
        ),
        'reasons': reasons,
    })


def run_v3_validation(operator, evidence_root):
    """Execute the additional 50 only after the holdout passes."""
    root = Path(evidence_root).expanduser().resolve()
    holdout = _v3_require_state(root, 'holdout')
    summary, records, contract_state = _v3_execute_partition(
        'validation',
        operator,
        root,
    )
    progress = _v3_load_progress(root / 'validation')
    unique_records = _load_json(holdout['records_path']) + records
    contract = _load_json(V3_CONTRACT_PATH)
    evaluation = evaluate_v3_unique_gates(unique_records, contract)
    return _v3_write_state(root, 'validation', {
        'passed': evaluation['passed'],
        'operator': operator,
        'holdout_state_sha256': holdout['state_sha256'],
        'contract_state_sha256': contract_state['state_sha256'],
        'additional_run_count': len(records),
        'unique_run_count': len(unique_records),
        'scenario_summary_path': summary.get('summary_path'),
        'scenario_summary_sha256': file_sha256(
            root / 'validation/scenario_summary.yaml'
        ),
        'records_path': str(root / 'validation/records.json'),
        'records_sha256': file_sha256(
            root / 'validation/records.json'
        ),
        'attempt_records_sha256': file_sha256(
            root / 'validation/attempt_records.json'
        ),
        'progress_sha256': progress['progress_sha256'],
        'stopped_early_reason': progress.get('stopped_early_reason'),
        'ambiguous_interrupted_dispatch_case_ids': progress.get(
            'ambiguous_interrupted_dispatch_case_ids',
            [],
        ),
        'not_run_slot_ids': progress['not_run_slot_ids'],
        'replacement_state_sha256': (
            file_sha256(_v3_replacement_state_path(root))
            if _v3_replacement_state_path(root).is_file()
            else None
        ),
        'unique_gate_evaluation': evaluation,
        'reasons': (
            (
                ['validation hard stop: {}'.format(
                    progress['stopped_early_reason']
                )]
                if progress.get('stopped_early_reason') else []
            )
            + (
                [] if evaluation['passed']
                else ['one or more fixed 70-case gates failed']
            )
        ),
    })


def _v3_numeric_close(reference, repeat, absolute, relative=0.10):
    if reference is None or repeat is None:
        return False
    tolerance = max(absolute, abs(reference) * relative)
    return abs(repeat - reference) <= tolerance


def _v3_compare_repro_metric(
    reference_metrics,
    repeat_metrics,
    name,
    absolute,
    reasons,
):
    reference = reference_metrics.get(name, {})
    repeat = repeat_metrics.get(name, {})
    statuses = (reference.get('status'), repeat.get('status'))
    if statuses == ('not_applicable', 'not_applicable'):
        return
    if statuses != ('valid', 'valid'):
        reasons.append(f'{name} evidence status differs or is unavailable')
        return
    reference_value = reference.get('value')
    repeat_value = repeat.get('value')
    if name == 'approximate_orbit_count':
        if (
            not isinstance(reference_value, list)
            or not isinstance(repeat_value, list)
            or len(reference_value) != len(repeat_value)
            or any(
                not isinstance(left, (int, float))
                or isinstance(left, bool)
                or not isinstance(right, (int, float))
                or isinstance(right, bool)
                or not math.isfinite(float(left))
                or not math.isfinite(float(right))
                or abs(float(left) - float(right)) > absolute
                for left, right in zip(reference_value, repeat_value)
            )
        ):
            reasons.append('orbit count exceeded tolerance')
        return
    if (
        isinstance(reference_value, bool)
        or not isinstance(reference_value, (int, float))
        or isinstance(repeat_value, bool)
        or not isinstance(repeat_value, (int, float))
        or not math.isfinite(float(reference_value))
        or not math.isfinite(float(repeat_value))
        or not _v3_numeric_close(
            float(reference_value),
            float(repeat_value),
            absolute,
        )
    ):
        reasons.append(f'{name} exceeded tolerance')


def evaluate_v3_reproducibility(
    repeats,
    unique_records,
    contract=None,
):
    """Compare ten repeat/reference pairs with positive evidence checks."""
    reference_keys = [record.get('case_key') for record in unique_records]
    references = {
        record.get('case_key'): record for record in unique_records
        if isinstance(record.get('case_key'), str)
    }
    contract_reasons = []
    expected_repeats = {}
    if contract is not None:
        try:
            expected_repeats = _v3_contract_case_map(
                contract, {'reproducibility'}
            )
        except (RuntimeError, ValueError) as exc:
            contract_reasons.append(str(exc))
        observed_repeat_keys = [
            repeat.get('case_key') for repeat in repeats
        ]
        if (
            len(expected_repeats) != 10
            or len(observed_repeat_keys) != 10
            or len(observed_repeat_keys) != len(set(observed_repeat_keys))
            or set(observed_repeat_keys) != set(expected_repeats)
        ):
            contract_reasons.append(
                'repeat identities differ from the sealed contract'
            )
    if (
        len(reference_keys) != len(set(reference_keys))
        or len(references) != len(unique_records)
    ):
        contract_reasons.append('unique reference identities are invalid')
    results = []
    for repeat in repeats:
        reference_key = repeat.get('repeat_reference', {}).get('case_key')
        reference = references.get(reference_key)
        reasons = []
        if contract is not None:
            expected_repeat = expected_repeats.get(repeat.get('case_key'))
            if expected_repeat is None:
                reasons.append('repeat is not in the sealed contract')
            elif (
                expected_repeat.get('repeat_reference', {}).get('case_key')
                != reference_key
            ):
                reasons.append('repeat reference differs from contract')
        if reference is None:
            reasons.append('reference case key is missing')
        else:
            ref_metrics = (reference.get('analysis') or {}).get(
                'metrics', {}
            )
            rep_metrics = (repeat.get('analysis') or {}).get('metrics', {})
            for item, label in (
                (reference, 'reference'),
                (repeat, 'repeat'),
            ):
                integrity = _v3_record_integrity(item)
                if not integrity['passed']:
                    reasons.append(
                        f'{label} integrity failed: '
                        + '; '.join(integrity['reasons'])
                    )
                outcomes = item.get('outcomes', {})
                if outcomes.get('required_state_path_passed') is not True:
                    reasons.append(
                        f'{label} required state coverage is invalid'
                    )
                if outcomes.get('required_events_passed') is not True:
                    reasons.append(
                        f'{label} required event coverage is invalid'
                    )
            for name in (
                'controller_success',
                'simulation_ground_truth_success',
                'timeout',
                'failsafe',
                'collision',
            ):
                reference_item = ref_metrics.get(name, {})
                repeat_item = rep_metrics.get(name, {})
                if (
                    reference_item.get('status') != 'valid'
                    or repeat_item.get('status') != 'valid'
                    or not isinstance(reference_item.get('value'), bool)
                    or not isinstance(repeat_item.get('value'), bool)
                ):
                    reasons.append(
                        f'{name} categorical evidence is unavailable'
                    )
                elif reference_item['value'] != repeat_item['value']:
                    reasons.append(f'{name} categorical outcome differs')
            for name, absolute in (
                ('escape_time', 2.0),
                ('approximate_orbit_count', 0.25),
                ('convergence_time', 2.0),
                ('path_length', 0.25),
                ('final_aggregate_target_distance', 0.10),
            ):
                _v3_compare_repro_metric(
                    ref_metrics,
                    rep_metrics,
                    name,
                    absolute,
                    reasons,
                )
        results.append({
            'repeat_case_id': repeat.get('case_id'),
            'repeat_case_key': repeat.get('case_key'),
            'reference_case_key': reference_key,
            'passed': not reasons,
            'reasons': reasons,
        })
    return {
        'passed': (
            not contract_reasons
            and len(results) == 10
            and len({
                item['reference_case_key'] for item in results
            }) == 10
            and all(item['passed'] for item in results)
        ),
        'repeat_count': len(results),
        'contract_reasons': contract_reasons,
        'results': results,
    }


def run_v3_reproducibility(operator, evidence_root):
    """Execute ten repeats only after all unique-case gates pass."""
    root = Path(evidence_root).expanduser().resolve()
    validation = _v3_require_state(root, 'validation')
    summary, repeats, contract_state = _v3_execute_partition(
        'reproducibility',
        operator,
        root,
    )
    progress = _v3_load_progress(root / 'reproducibility')
    holdout = _v3_require_state(root, 'holdout')
    unique_records = (
        _load_json(holdout['records_path'])
        + _load_json(validation['records_path'])
    )
    evaluation = evaluate_v3_reproducibility(
        repeats,
        unique_records,
        _load_json(V3_CONTRACT_PATH),
    )
    return _v3_write_state(root, 'reproducibility', {
        'passed': evaluation['passed'],
        'operator': operator,
        'validation_state_sha256': validation['state_sha256'],
        'contract_state_sha256': contract_state['state_sha256'],
        'scenario_summary_path': summary.get('summary_path'),
        'scenario_summary_sha256': file_sha256(
            root / 'reproducibility/scenario_summary.yaml'
        ),
        'records_path': str(root / 'reproducibility/records.json'),
        'records_sha256': file_sha256(
            root / 'reproducibility/records.json'
        ),
        'attempt_records_sha256': file_sha256(
            root / 'reproducibility/attempt_records.json'
        ),
        'progress_sha256': progress['progress_sha256'],
        'stopped_early_reason': progress.get('stopped_early_reason'),
        'ambiguous_interrupted_dispatch_case_ids': progress.get(
            'ambiguous_interrupted_dispatch_case_ids',
            [],
        ),
        'not_run_slot_ids': progress['not_run_slot_ids'],
        'replacement_state_sha256': (
            file_sha256(_v3_replacement_state_path(root))
            if _v3_replacement_state_path(root).is_file()
            else None
        ),
        'evaluation': evaluation,
        'reasons': (
            (
                ['reproducibility hard stop: {}'.format(
                    progress['stopped_early_reason']
                )]
                if progress.get('stopped_early_reason') else []
            )
            + (
                [] if evaluation['passed']
                else ['one or more reproducibility comparisons failed']
            )
        ),
    })


def _v3_serial_artifact_errors(label, state):
    errors = []
    records_path_text = state.get('records_path')
    if not records_path_text:
        return [f'v3 {label} serial records path is missing']
    stage_root = Path(records_path_text).parent
    try:
        progress = _v3_load_progress(stage_root)
        if progress is None:
            raise RuntimeError('progress document is missing')
        if progress['progress_sha256'] != state.get('progress_sha256'):
            raise RuntimeError('progress hash differs from stage state')
        suite_path = Path(progress['suite_path'])
        if (
            not suite_path.is_file()
            or not isinstance(progress.get('suite_sha256'), str)
            or file_sha256(suite_path) != progress['suite_sha256']
        ):
            raise RuntimeError('serial suite hash drifted')
        reconstructed_attempts = []
        for attempt in progress.get('attempts', []):
            for path_field, hash_field in (
                ('summary_path', 'summary_sha256'),
                ('record_path', 'record_sha256'),
                ('error_path', 'error_sha256'),
            ):
                path_text = attempt.get(path_field)
                if path_text is None:
                    continue
                expected = attempt.get(hash_field)
                path = Path(path_text)
                if (
                    not path.is_file()
                    or not isinstance(expected, str)
                    or file_sha256(path) != expected
                ):
                    raise RuntimeError(
                        f'{path_field} drifted in retained progress'
                    )
            if attempt.get('record_path'):
                reconstructed_attempts.append(
                    _load_json(attempt['record_path'])
                )
        attempts_path = stage_root / 'attempt_records.json'
        expected_attempt_hash = state.get('attempt_records_sha256')
        if (
            not attempts_path.is_file()
            or not isinstance(expected_attempt_hash, str)
            or file_sha256(attempts_path) != expected_attempt_hash
            or _load_json(attempts_path) != reconstructed_attempts
        ):
            raise RuntimeError('attempt-record aggregate drifted')
        carried_by_case = {
            item['case_id']: item
            for item in progress.get('carried_records', [])
        }
        aggregate_records = []
        for case_id in progress.get('slot_ids', []):
            if case_id not in progress.get('final_record_paths', {}):
                continue
            if case_id in carried_by_case:
                aggregate_records.append({
                    'schema_version': 1,
                    'case_id': case_id,
                    'disposition': (
                        'carried_immutable_behavioral_failure'
                    ),
                    'carried_record': dict(carried_by_case[case_id]),
                })
            else:
                aggregate_records.append(_load_json(
                    progress['final_record_paths'][case_id]
                ))
        if _load_json(records_path_text) != aggregate_records:
            raise RuntimeError('final records differ from progress')
    except (
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        errors.append(f'v3 {label} serial artifact invalid: {exc}')
    return errors


def _v3_replacement_artifact_errors(root, states):
    errors = []
    serial_states = [
        states.get(stage)
        for stage in (
            'activation',
            'development',
            'holdout',
            'validation',
            'reproducibility',
        )
        if states.get(stage) is not None
    ]
    if not serial_states:
        return errors
    expected_hash = serial_states[-1].get('replacement_state_sha256')
    path = _v3_replacement_state_path(root)
    if not path.is_file():
        if expected_hash is not None:
            errors.append('v3 replacement state is missing')
        return errors
    if not isinstance(expected_hash, str) or file_sha256(path) != expected_hash:
        errors.append('v3 final replacement-state hash drifted')
        return errors
    try:
        replacement = _v3_load_replacement_state(root)
        links = replacement.get('attempt_links', [])
        slots = replacement.get('slots', [])
        if (
            replacement.get('total') != len(slots)
            or len(slots) != len(set(slots))
            or len(links) != len(slots)
            or {link.get('slot_id') for link in links} != set(slots)
        ):
            raise RuntimeError('replacement counts or links drifted')
        if replacement['total'] > V3_REPLACEMENT_CAPS['total']:
            raise RuntimeError('replacement total cap was exceeded')
        for stage, count in replacement.get('by_stage', {}).items():
            if count > V3_REPLACEMENT_CAPS.get(stage, -1):
                raise RuntimeError(
                    f'{stage} replacement cap was exceeded'
                )
        for link in links:
            invalid_path = Path(link['invalid_attempt_record'])
            record = _load_json(invalid_path)
            proof_artifacts = _v3_replacement_proof_artifacts(
                record,
                invalid_path,
            )
            if (
                record.get('classification', {}).get('status')
                != 'infrastructure_invalid'
                or not _v3_replacement_eligible(link.get('evidence'))
                or link.get('evidence')
                != _v3_replacement_evidence(record)
                or link.get('proof_artifacts') != proof_artifacts
            ):
                raise RuntimeError(
                    'replacement link lacks eligible invalid evidence'
                )
    except (
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        errors.append(f'v3 replacement artifact invalid: {exc}')
    return errors


def run_v3_report(operator, evidence_root):
    """Write terminal v3 gates, manifest, and human-readable report."""
    root = Path(evidence_root).expanduser().resolve()
    terminal_path = _v3_state_path(root, 'terminal')
    if terminal_path.is_file():
        terminal = _v3_require_state(
            root,
            'terminal',
            require_pass=False,
        )
        if terminal.get('operator') != operator:
            raise RuntimeError('v3 terminal report operator drifted')
        for path, field in (
            (V3_GATE_RESULTS_PATH, 'gate_results_sha256'),
            (V3_MANIFEST_PATH, 'manifest_sha256'),
            (V3_REPORT_PATH, 'report_sha256'),
        ):
            if (
                not path.is_file()
                or file_sha256(path) != terminal.get(field)
            ):
                raise RuntimeError(
                    f'v3 terminal artifact drifted: {path}'
                )
        failure_hash = terminal.get('failure_report_sha256')
        if failure_hash is None:
            if V3_FAILURE_PATH.exists():
                raise RuntimeError(
                    'v3 passing terminal has a contradictory failure report'
                )
        elif (
            not V3_FAILURE_PATH.is_file()
            or file_sha256(V3_FAILURE_PATH) != failure_hash
        ):
            raise RuntimeError('v3 terminal failure report drifted')
        return _load_json(V3_GATE_RESULTS_PATH)
    state_errors = []
    states = {}
    for stage in (
        'prepare',
        'qualification',
        'activation',
        'development',
        'freeze',
        'contract',
        'holdout',
        'validation',
        'reproducibility',
    ):
        path = _v3_state_path(root, stage)
        if not path.is_file():
            states[stage] = None
            state_errors.append(f'v3 {stage} state is missing')
            continue
        try:
            state = _load_json(path)
            require_omission_sha256(
                state, 'state_sha256', f'v3 {stage} state'
            )
            states[stage] = state
        except (OSError, ValueError, RuntimeError) as exc:
            states[stage] = None
            state_errors.append(str(exc))

    chain = (
        ('qualification', 'prepare_state_sha256', 'prepare'),
        ('activation', 'qualification_state_sha256', 'qualification'),
        ('development', 'activation_state_sha256', 'activation'),
        ('development', 'qualification_state_sha256', 'qualification'),
        ('freeze', 'development_state_sha256', 'development'),
        ('freeze', 'qualification_state_sha256', 'qualification'),
        ('contract', 'freeze_state_sha256', 'freeze'),
        ('holdout', 'contract_state_sha256', 'contract'),
        ('validation', 'holdout_state_sha256', 'holdout'),
        ('validation', 'contract_state_sha256', 'contract'),
        ('reproducibility', 'validation_state_sha256', 'validation'),
        ('reproducibility', 'contract_state_sha256', 'contract'),
    )
    for child_name, field, parent_name in chain:
        child = states.get(child_name)
        parent = states.get(parent_name)
        if child is None or parent is None:
            continue
        if child.get(field) != parent.get('state_sha256'):
            state_errors.append(
                f'v3 {child_name} state does not link to {parent_name}'
            )

    contract_sha256 = None
    contract_error = None
    if not V3_CONTRACT_PATH.is_file():
        contract_error = 'tracked v3 acceptance contract is missing'
    else:
        try:
            contract = _load_json(V3_CONTRACT_PATH)
            contract_sha256 = require_omission_sha256(
                contract,
                'contract_sha256',
                'v3 acceptance contract',
            )
            contract_state = states.get('contract')
            if (
                contract_state is None
                or contract_state.get('contract_sha256')
                != contract_sha256
            ):
                contract_error = (
                    'tracked contract and contract state differ'
                )
            for stage in (
                'holdout',
                'validation',
                'reproducibility',
            ):
                state = states.get(stage)
                if (
                    state is not None
                    and state.get('contract_sha256') != contract_sha256
                ):
                    state_errors.append(
                        f'v3 {stage} contract hash differs'
                    )
        except (OSError, ValueError, RuntimeError) as exc:
            contract_error = str(exc)
    if contract_error:
        state_errors.append(contract_error)

    prepare = states.get('prepare')
    qualification = states.get('qualification')
    activation = states.get('activation')
    development = states.get('development')
    freeze = states.get('freeze')
    contract_state = states.get('contract')
    holdout = states.get('holdout')
    validation = states.get('validation')
    reproducibility = states.get('reproducibility')
    if prepare is not None:
        try:
            transaction_path = Path(prepare['transaction_path'])
            transaction = _v3_load_prepare_transaction(transaction_path)
            if (
                transaction['transaction_sha256']
                != prepare.get('transaction_sha256')
            ):
                raise RuntimeError(
                    'prepare transaction differs from state'
                )
            for path_field, hash_field in (
                ('suite_path', 'suite_sha256'),
                ('commitment_path', None),
            ):
                path = Path(prepare[path_field])
                if not path.is_file():
                    raise RuntimeError(
                        f'prepare {path_field} is missing'
                    )
                if (
                    hash_field is not None
                    and file_sha256(path) != prepare[hash_field]
                ):
                    raise RuntimeError(
                        f'prepare {path_field} drifted'
                    )
            tracked_commitment = _load_json(
                prepare['commitment_path']
            )
            if require_omission_sha256(
                tracked_commitment,
                'commitment_sha256',
                'acceptance commitment',
            ) != prepare['commitment_sha256']:
                raise RuntimeError('prepare commitment differs from state')
        except (
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            state_errors.append(f'v3 prepare artifact invalid: {exc}')
    for stage, state in states.items():
        if state is None:
            continue
        for path_field, hash_field in (
            ('scenario_summary_path', 'scenario_summary_sha256'),
            ('records_path', 'records_sha256'),
        ):
            path_text = state.get(path_field)
            expected_hash = state.get(hash_field)
            if path_text is None and expected_hash is None:
                continue
            path = Path(path_text) if path_text else None
            if (
                path is None
                or not path.is_file()
                or not isinstance(expected_hash, str)
                or file_sha256(path) != expected_hash
            ):
                state_errors.append(
                    f'v3 {stage} {path_field} artifact drifted'
                )
        commands = list(state.get('qualification_commands', []))
        commands.extend(
            state.get('requalification', {}).get(
                'qualification_commands', []
            )
        )
        for command in commands:
            path_text = command.get('log_path')
            expected_hash = command.get('log_sha256')
            path = Path(path_text) if path_text else None
            if (
                path is None
                or not path.is_file()
                or file_sha256(path) != expected_hash
            ):
                state_errors.append(
                    'v3 qualification command log drifted'
                )
                break
    if development is not None:
        for candidate in development.get('candidates', []):
            for path_field, hash_field in (
                ('scenario_summary_path', 'scenario_summary_sha256'),
                ('records_path', 'records_sha256'),
            ):
                path_text = candidate.get(path_field)
                expected_hash = candidate.get(hash_field)
                path = Path(path_text) if path_text else None
                if (
                    path is None
                    or not path.is_file()
                    or file_sha256(path) != expected_hash
                ):
                    state_errors.append(
                        'v3 development candidate artifact drifted'
                    )
                    break
            state_errors.extend(_v3_serial_artifact_errors(
                f"development {candidate.get('candidate_id')}",
                candidate,
            ))
    for stage in (
        'activation',
        'holdout',
        'validation',
        'reproducibility',
    ):
        state = states.get(stage)
        if state is not None:
            state_errors.extend(
                _v3_serial_artifact_errors(stage, state)
            )
    state_errors.extend(_v3_replacement_artifact_errors(root, states))
    if freeze is not None and contract_state is not None:
        try:
            _v3_verify_runtime_contract(root, freeze, contract_state)
        except (
            OSError,
            ValueError,
            RuntimeError,
            KeyError,
            TypeError,
        ) as exc:
            state_errors.append(str(exc))
    for stage in ('holdout', 'validation', 'reproducibility'):
        state = states.get(stage)
        if state is None or not state.get('records_path'):
            continue
        try:
            formal_records = _load_json(state['records_path'])
            for record in formal_records:
                integrity = _v3_record_integrity(record)
                if not integrity['passed']:
                    state_errors.append(
                        f'v3 {stage} retained raw evidence drifted'
                    )
                    break
        except (OSError, ValueError, RuntimeError) as exc:
            state_errors.append(
                f'v3 {stage} retained evidence unreadable: {exc}'
            )
    gates = [
        _v3_gate(
            'context_qualification',
            (
                not state_errors
                and prepare is not None
                and prepare.get('passed') is True
                and qualification is not None
                and qualification.get('passed') is True
                and freeze is not None
                and freeze.get('passed') is True
                and contract_state is not None
                and contract_state.get('passed') is True
                and contract_sha256 is not None
            ),
            {
                'prepare': (
                    prepare.get('passed') if prepare else None
                ),
                'qualification': (
                    qualification.get('passed')
                    if qualification else None
                ),
                'freeze': freeze.get('passed') if freeze else None,
                'contract': (
                    contract_state.get('passed')
                    if contract_state else None
                ),
                'errors': state_errors,
            },
            'complete verified prepare/qualification/freeze/contract chain',
        ),
        _v3_gate(
            'activation',
            activation is not None and activation.get('passed') is True,
            (
                activation.get('contract_pass_count')
                if activation else None
            ),
            '10/10',
        ),
        _v3_gate(
            'development_freeze',
            (
                development is not None
                and development.get('passed') is True
                and freeze is not None
                and freeze.get('passed') is True
                and contract_state is not None
                and contract_state.get('passed') is True
            ),
            (
                (development or {}).get('selected_candidate') or {}
            ).get('candidate_id'),
            'one eligible winner plus verified freeze and contract',
        ),
    ]
    if holdout is None:
        gates.append(_not_run_gate(
            'holdout',
            '>=18/20 and exact family floors',
            'pre-holdout',
        ))
    else:
        gates.append(_v3_gate(
            'holdout',
            holdout.get('passed') is True,
            holdout.get('end_to_end_success_count'),
            '>=18/20 and exact family floors',
        ))
    if validation is None:
        for identifier in (
            'contract_population_binding',
            'completeness_analysis_integrity',
            'behavior_contracts',
            'end_to_end',
            'family_floors',
            'local_escape',
            'escape_duration',
            'orbit_count',
            'revisit',
            'lifecycle_coverage',
            'disturbance_constraint_evidence',
            'metric_applicability',
        ):
            gates.append(_not_run_gate(
                identifier,
                'fixed acceptance contract',
                'pre-validation',
            ))
        confidence = None
    else:
        unique = validation['unique_gate_evaluation']
        gates.extend(unique['gates'])
        confidence = unique['confidence_intervals']
    if reproducibility is None:
        gates.append(_not_run_gate(
            'reproducibility',
            '10/10 comparisons',
            'pre-reproducibility',
        ))
    else:
        gates.append(_v3_gate(
            'reproducibility',
            reproducibility.get('passed') is True,
            (
                reproducibility.get('evaluation', {})
                .get('repeat_count')
            ),
            '10/10 comparisons',
        ))
    overall = (
        not state_errors
        and all(
            state is not None and state.get('passed') is True
            for state in states.values()
        )
        and validation is not None
        and validation.get('unique_gate_evaluation', {}).get('passed')
        is True
        and reproducibility is not None
        and reproducibility.get('evaluation', {}).get('passed') is True
        and all(gate.get('passed') is True for gate in gates)
    )
    result = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'simulation_ready': overall,
        'outcome': 'passed' if overall else 'failed',
        'contract_sha256': contract_sha256,
        'confidence_intervals': confidence,
        'state_chain_errors': state_errors,
        'gates': gates,
    }
    create_or_verify_json(V3_GATE_RESULTS_PATH, result)
    manifest = {
        'schema_version': 1,
        'experiment_version': 'phase08-v3',
        'operator': operator,
        'evidence_root': str(root),
        'contract_sha256': result['contract_sha256'],
        'stage_state_hashes': {
            stage: (
                states[stage].get('state_sha256')
                if states.get(stage) is not None else None
            )
            for stage in (
                'prepare',
                'qualification',
                'activation',
                'development',
                'freeze',
                'contract',
                'holdout',
                'validation',
                'reproducibility',
            )
        },
        'gate_results_sha256': file_sha256(V3_GATE_RESULTS_PATH),
    }
    create_or_verify_json(V3_MANIFEST_PATH, manifest)
    lines = [
        '# Phase 08.3 Simulation Validation Report',
        '',
        f'Outcome: **{"PASS" if overall else "FAIL"}**.',
        '',
        f'Contract: `{result["contract_sha256"]}`.',
        '',
        '## Gates',
        '',
    ]
    for gate in gates:
        if gate.get('status') == 'not_run':
            lines.append(
                f'- `{gate["gate"]}`: NOT RUN; '
                f'threshold `{gate["threshold"]}`.'
            )
        else:
            lines.append(
                f'- `{gate["gate"]}`: '
                f'{"PASS" if gate["passed"] else "FAIL"}; '
                f'value `{gate["value"]}`; '
                f'threshold `{gate["threshold"]}`.'
            )
    lines.extend([
        '',
        f'Retained evidence root: `{root}`.',
        '',
        'No physical hardware was run.',
        '',
    ])
    report_bytes = '\n'.join(lines).encode('utf-8')
    create_or_verify_bytes(V3_REPORT_PATH, report_bytes)
    failure_hash = None
    if not overall:
        failure_bytes = '\n'.join([
                '# Phase 08.3 Failure Report',
                '',
                'The version is not simulation-ready. Unrun gates remain '
                'not-run; thresholds were not weakened.',
                '',
                f'Contract: `{contract_sha256}`.',
                '',
                'State-chain findings:',
                '',
                *(
                    [f'- {reason}' for reason in state_errors]
                    or ['- No state-chain error; one or more gates failed.']
                ),
                '',
                f'Retained evidence root: `{root}`.',
                '',
            ]).encode('utf-8')
        create_or_verify_bytes(V3_FAILURE_PATH, failure_bytes)
        failure_hash = file_sha256(V3_FAILURE_PATH)
    elif V3_FAILURE_PATH.exists():
        raise RuntimeError(
            'v3 passing report found a pre-existing failure report'
        )
    _v3_write_state(root, 'terminal', {
        'passed': overall,
        'operator': operator,
        'simulation_ready': overall,
        'contract_sha256': contract_sha256,
        'state_chain_errors': state_errors,
        'gate_results_sha256': file_sha256(V3_GATE_RESULTS_PATH),
        'manifest_sha256': file_sha256(V3_MANIFEST_PATH),
        'report_sha256': file_sha256(V3_REPORT_PATH),
        'failure_report_sha256': failure_hash,
    })
    return result


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
    for name in (
        'v3-qualify',
        'v3-activation',
        'v3-development',
        'v3-freeze',
        'v3-seal',
        'v3-holdout',
        'v3-validation',
        'v3-reproducibility',
        'v3-report',
    ):
        subparser = subparsers.add_parser(name)
        subparser.add_argument('--operator', required=True)
        subparser.add_argument('--evidence-root', required=True)
    prepare = subparsers.add_parser('v3-prepare')
    prepare.add_argument('--operator', required=True)
    prepare.add_argument('--evidence-root', required=True)
    adopt = subparsers.add_parser('v3-adopt-precommit')
    adopt.add_argument('--operator', required=True)
    adopt.add_argument('--evidence-root', required=True)
    adopt.add_argument('--superseded-evidence-root', required=True)
    return parser


def _empirical_sigterm_handler(signum, unused_frame):
    """Convert a scoped empirical SIGTERM into controlled interruption."""
    del signum, unused_frame
    raise KeyboardInterrupt('empirical validation received SIGTERM')


def main(argv=None):
    """CLI entry point."""
    arguments = _parser().parse_args(argv)
    previous_sigterm_handler = None
    if arguments.subcommand in EMPIRICAL_SUBCOMMANDS:
        previous_sigterm_handler = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, _empirical_sigterm_handler)
    try:
        if arguments.subcommand == 'v3-prepare':
            result = run_v3_prepare(
                arguments.operator,
                arguments.evidence_root,
            )
        elif arguments.subcommand == 'v3-adopt-precommit':
            result = run_v3_adopt_precommit(
                arguments.operator,
                arguments.evidence_root,
                arguments.superseded_evidence_root,
            )
        elif arguments.subcommand == 'v3-qualify':
            result = run_v3_qualify(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-activation':
            result = run_v3_activation(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-development':
            result = run_v3_development(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-freeze':
            result = run_v3_freeze(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-seal':
            result = run_v3_seal(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-holdout':
            result = run_v3_holdout(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-validation':
            result = run_v3_validation(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-reproducibility':
            result = run_v3_reproducibility(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'v3-report':
            result = run_v3_report(
                arguments.operator, arguments.evidence_root
            )
        elif arguments.subcommand == 'full-pass':
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
    except KeyboardInterrupt:
        print(
            'validate_robustness: empirical execution interrupted',
            file=sys.stderr,
        )
        return 130
    except Exception as exc:
        print(
            f'validate_robustness: {type(exc).__name__}: {exc}',
            file=sys.stderr,
        )
        return 2
    finally:
        if previous_sigterm_handler is not None:
            signal.signal(
                signal.SIGTERM,
                previous_sigterm_handler,
            )
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    if result.get('passed') is False:
        return 1
    if result.get('simulation_ready') is False:
        return 1
    if result.get('level_c_no_eligible_candidate'):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
