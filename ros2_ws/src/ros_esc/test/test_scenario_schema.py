"""Focused tests for strict Phase 06 scenario parsing and expansion."""

from copy import deepcopy
from functools import lru_cache
import hashlib
from pathlib import Path

import pytest

from ros_esc.scenario_runner import aggregate_field_truth
from ros_esc.scenario_runner.scenario_schema import (
    deterministic_case_key,
    expand_suite,
    load_suite,
)

import yaml


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SMOKE = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
)
CATALOG = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase06_catalog.yaml'
)
DIAGNOSTIC_ACTIVATION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/'
    'phase08_1_diagnostic_activation.yaml'
)
RECENTER_RECOVERY = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_2_recenter.yaml'
)
HISTORICAL_V2_ACTIVATION = (
    PACKAGE_ROOT
    / 'ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml'
)


def _document():
    return {
        'schema_version': 1,
        'suite_id': 'unit_suite',
        'description': 'schema fixture',
        'mode': 'simulation',
        'execution': {
            'max_parallel_runs': 1,
            'run_timeout_sec': 10.0,
            'wall_timeout_sec': 20.0,
        },
        'metadata': {
            'experiment_version': 'phase06-test',
            'operator_notes': '',
        },
        'level_map': {},
        'defaults': {
            'bounds_m': [-2.0, 2.0, -2.0, 2.0],
            'room_center_m': [0.0, 0.0],
        },
        'cases': [{
            'case_id': 'case_a',
            'family': 'smoke',
            'status': 'executable_unverified',
            'profiles': ['robust_gaussian_v1'],
            'seeds': [3],
            'starts': [
                {'id': 'center', 'x_m': 0.0, 'y_m': 0.0, 'yaw_rad': 0.0}
            ],
            'sources': [{
                'id': 'goal',
                'x_m': 1.0,
                'y_m': 0.5,
                'relative_lumen_input': 1000.0,
                'evaluation_role': 'goal',
            }],
            'algorithm': {
                'ablations': {
                    'gaussian_fill_enabled': True,
                    'affine_assist_enabled': True,
                    'recenter_enabled': True,
                },
                'launch_overrides': {},
            },
            'success': {
                'all_of': ['recording_complete', 'cleanup_complete'],
                'controller': {
                    'expected_terminal_state': None,
                    'required_state_sequence': [],
                    'required_events': [],
                    'forbidden_events': [],
                },
                'ground_truth': {
                    'goal_source_ids': ['goal'],
                    'final_position_tolerance_m': 0.35,
                },
                'minimum_saturation_samples': 0,
            },
        }],
    }


def _load(tmp_path, document):
    path = tmp_path / 'suite.yaml'
    path.write_text(
        yaml.safe_dump(document, sort_keys=False), encoding='utf-8'
    )
    return load_suite(path)


def _v3_document():
    document = _document()
    document['schema_version'] = 3
    document['defaults'].update({
        'validation_world': True,
        'simulation_contacts_enabled': True,
    })
    document['cases'][0]['algorithm']['launch_overrides'] = {
        'goal_score_threshold': 0.95,
        'goal_score_rotation_period_sec': 3.0,
        'goal_score_required_rotations': 2,
        'goal_hold_sec': 3.0,
        'undesired_score_hold_sec': 3.0,
        'verification_max_sec': 12.0,
    }
    document['cases'][0]['success'] = {
        'all_of': [
            'recording_complete',
            'cleanup_complete',
            'controller_goal',
            'expected_terminal_state',
            'required_state_path',
            'required_events',
            'no_forbidden_states',
            'no_forbidden_events',
            'collision_expectation',
        ],
        'controller': {
            'contract_id': 'case_a',
            'expected_verification_outcome': 'goal',
            'reachability_argument': (
                'A calibrated source sustains the target.'
            ),
            'expected_terminal_state': 'GOAL_HOLD',
            'required_state_path': [
                'SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD',
            ],
            'required_events': [
                'CONVERGENCE_CONFIRMED', 'GOAL_REACHED',
            ],
            'forbidden_states': ['FAILSAFE'],
            'forbidden_events': ['TIMEOUT', 'FAILSAFE'],
        },
        'ground_truth': {
            'goal_source_ids': ['goal'],
            'final_position_tolerance_m': 0.35,
        },
        'collision_expected': False,
    }
    return document


def _v4_document():
    document = _v3_document()
    document['schema_version'] = 4
    case = document['cases'][0]
    case.update({
        'acceptance_family': 'lifecycle',
        'acceptance_partition': 'validation',
        'metric_applicability': {
            'escape_attempt': False,
            'escape_duration': False,
            'orbit_count': False,
            'revisit': False,
            'delay': False,
            'saturation': False,
        },
    })
    case['sources'][0].update({
        'x_m': 0.0,
        'y_m': 0.0,
        'relative_lumen_input': 2500.0,
    })
    record = deepcopy(_v4_production_truth())
    success = case['success']
    success['all_of'].append('ground_truth_goal')
    success['ground_truth'] = {
        'method': 'aggregate_field',
        'final_position_tolerance_m': 0.35,
        'wall_margin_m': 0.35,
        'minimum_source_score': 0.95,
        'aggregate_field': record,
    }
    success['result_scopes'] = {
        'full_lifecycle': {
            'anchor_state': 'SEARCH',
            'boundary_state': None,
            'graceful_stop': False,
            'all_of': list(success['all_of']),
        },
    }
    return document


@lru_cache(maxsize=1)
def _v4_production_truth():
    return aggregate_field_truth.derive_aggregate_field_truth(
        [{
            'id': 'goal',
            'x_m': 0.0,
            'y_m': 0.0,
            'relative_lumen_input': 2500.0,
            'evaluation_role': 'goal',
        }],
        [-2.0, 2.0, -2.0, 2.0],
        {'sensor_noise': {'model': 'none'}},
    )


def test_checked_in_suites_validate_and_catalog_marks_gaps():
    """Validate checked-in suites and their declared unsupported gaps."""
    smoke = load_suite(SMOKE)
    catalog = load_suite(CATALOG)
    diagnostic = load_suite(DIAGNOSTIC_ACTIVATION)
    recenter = load_suite(RECENTER_RECOVERY)
    smoke_runs, smoke_unsupported = expand_suite(smoke)
    catalog_runs, catalog_unsupported = expand_suite(catalog)
    diagnostic_runs, diagnostic_unsupported = expand_suite(diagnostic)
    recenter_runs, recenter_unsupported = expand_suite(recenter)

    assert [run['profile'] for run in smoke_runs] == [
        'robust_gaussian_v1', 'legacy'
    ]
    assert smoke_unsupported == []
    assert len(catalog_runs) >= 20
    assert len(diagnostic_runs) == 10
    assert diagnostic_unsupported == []
    assert len(recenter_runs) == 1
    assert recenter_unsupported == []
    recenter_path = recenter_runs[0]['success']['controller'][
        'required_state_path'
    ]
    assert recenter_path == [
        'SEARCH',
        'VERIFY_EXTREMUM',
        'DESIGN_OR_MERGE_FILL',
        'ESCAPE_REPULSE',
        'RECENTER',
        'SEARCH',
    ]
    assert all(
        run['success']['controller']['verification_timing'][
            'selected_margin_sec'
        ] == pytest.approx(3.0)
        for run in diagnostic_runs
    )
    assert {item['case_id'] for item in catalog_unsupported} >= {
        'ordered_levels_1_to_5',
        'sensor_pose_delay',
        'deterministic_gaussian_noise',
        'physical_wall_collision',
        'raw_attraction_static_ablation',
        'more_than_five_sources',
        'plain_legacy_without_pde',
    }


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (lambda doc: doc.update({'schema_version': 5}), 'schema_version'),
        (
            lambda doc: doc.update({'mode': 'physical'}),
            'mode must be simulation',
        ),
        (
            lambda doc: doc['execution'].update({'max_parallel_runs': 2}),
            'max_parallel_runs',
        ),
        (
            lambda doc: doc['cases'][0].update({'mystery': True}),
            'unknown keys',
        ),
        (
            lambda doc: doc['cases'][0].update({'success': []}),
            'must be a mapping',
        ),
        (
            lambda doc: doc['cases'][0].update({'profiles': ['unknown']}),
            'profiles',
        ),
        (
            lambda doc: doc['cases'][0].update({'seeds': []}),
            'seeds',
        ),
        (
            lambda doc: doc['cases'][0]['starts'][0].update({'x_m': 3.0}),
            'outside bounds',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm']['ablations'].update(
                {'raw_cost_enabled': False}
            ),
            'unknown keys',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {'all_of': ['invented_gate']}
            ),
            'unknown predicates',
        ),
    ],
)
def test_strict_schema_rejects_unknown_invalid_or_unsafe_values(
    tmp_path, mutation, match
):
    """Reject malformed, unknown, nonserial, or unsafe suite values."""
    document = _document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_source_count_is_one_to_five_for_executable_cases(tmp_path):
    """Enforce the simulator's executable one-to-five-source range."""
    document = _document()
    document['cases'][0]['sources'] = []
    with pytest.raises(ValueError, match='1 to 5'):
        _load(tmp_path, document)

    document = _document()
    document['cases'][0]['sources'] *= 6
    for index, source in enumerate(document['cases'][0]['sources']):
        source['id'] = f'source_{index}'
    with pytest.raises(ValueError, match='1 to 5'):
        _load(tmp_path, document)


def test_two_ordered_level_dimensions_expand_to_25(tmp_path):
    """Expand two ordered five-level sources to 25 deterministic cases."""
    document = _document()
    document['level_map'] = {
        str(level): float(level * 100) for level in range(1, 6)
    }
    document['cases'][0]['sources'] = [
        {
            'id': 'local',
            'x_m': -1.0,
            'y_m': 0.0,
            'levels': [1, 2, 3, 4, 5],
            'evaluation_role': 'local_minimum',
        },
        {
            'id': 'goal',
            'x_m': 1.0,
            'y_m': 0.0,
            'levels': [1, 2, 3, 4, 5],
            'evaluation_role': 'goal',
        },
    ]
    suite = _load(tmp_path, document)
    runs, unsupported = expand_suite(suite)

    assert unsupported == []
    assert len(runs) == 25
    assert runs[0]['source_level_tuple'] == ['1', '1']
    assert runs[-1]['source_level_tuple'] == ['5', '5']
    assert [
        source['relative_lumen_input']
        for source in runs[0]['sources']
    ] == [100.0, 100.0]


def test_expansion_order_and_case_keys_are_stable(tmp_path):
    """Keep profile, start, level, seed order and case keys stable."""
    document = _document()
    case = document['cases'][0]
    case['profiles'] = ['legacy', 'robust_gaussian_v1']
    case['starts'].append(
        {'id': 'north', 'x_m': 0.0, 'y_m': 1.0, 'yaw_rad': -1.0}
    )
    case['seeds'] = [7, 5]
    suite = _load(tmp_path, document)
    first, _ = expand_suite(suite)
    second, _ = expand_suite(suite)

    assert [
        (run['profile'], run['start']['id'], run['seed']) for run in first
    ] == [
        ('legacy', 'center', 7),
        ('legacy', 'center', 5),
        ('legacy', 'north', 7),
        ('legacy', 'north', 5),
        ('robust_gaussian_v1', 'center', 7),
        ('robust_gaussian_v1', 'center', 5),
        ('robust_gaussian_v1', 'north', 7),
        ('robust_gaussian_v1', 'north', 5),
    ]
    assert [run['case_key'] for run in first] == [
        run['case_key'] for run in second
    ]
    changed = deepcopy(first[0])
    changed['seed'] = 99
    assert deterministic_case_key(changed) != first[0]['case_key']


@pytest.mark.parametrize(
    ('disturbance', 'reason'),
    [
        ({'sensor_delay_sec': 0.1}, 'sensor delay'),
        ({'pose_delay_sec': 0.1}, 'pose delay'),
        (
            {'sensor_noise': {'model': 'gaussian', 'std_dev': 0.1}},
            'Gaussian noise',
        ),
    ],
)
def test_unsupported_disturbances_are_classified_without_launch(
    tmp_path, disturbance, reason
):
    """Classify unavailable disturbance infrastructure without launching."""
    document = _document()
    document['cases'][0]['disturbances'] = disturbance
    suite = _load(tmp_path, document)
    runs, unsupported = expand_suite(suite)

    assert runs == []
    assert reason in unsupported[0]['reason']


def test_case_filter_rejects_unknown_names(tmp_path):
    """Reject filters that name no declared scenario case."""
    suite = _load(tmp_path, _document())
    with pytest.raises(ValueError, match='unknown --case-id'):
        expand_suite(suite, case_ids=['missing'])


def test_schema_v3_binds_reachable_activation_contract(tmp_path):
    """Expose a strict path and positive verification margin."""
    suite = _load(tmp_path, _v3_document())
    run = expand_suite(suite)[0][0]
    controller = run['success']['controller']

    assert controller['contract_id'] == run['case_id']
    assert controller['required_state_path'] == [
        'SEARCH', 'VERIFY_EXTREMUM', 'GOAL_HOLD',
    ]
    assert controller['verification_timing'] == {
        'goal_score_threshold': 0.95,
        'rotation_period_sec': 3.0,
        'required_rotations': 2,
        'rotation_duration_sec': 6.0,
        'goal_dwell_sec': 3.0,
        'below_target_dwell_sec': 3.0,
        'verification_timeout_sec': 12.0,
        'goal_required_sec': 9.0,
        'below_target_required_sec': 9.0,
        'goal_margin_sec': 3.0,
        'below_target_margin_sec': 3.0,
        'selected_margin_sec': 3.0,
        'timing_sufficient': True,
    }


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'contract_id': 'shared_anchor'}
            ),
            'must equal case_id',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {
                    'required_state_path': [
                        'SEARCH', 'GOAL_HOLD',
                    ]
                }
            ),
            'must include VERIFY_EXTREMUM',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'][
                'forbidden_states'
            ].append('GOAL_HOLD'),
            'requires and forbids states',
        ),
        (
            lambda doc: doc['cases'][0]['success']['all_of'].remove(
                'no_forbidden_events'
            ),
            'does not bind declared controller evidence',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'verification_max_sec': 9.0}),
            'no positive verification timing margin',
        ),
        (
            lambda doc: doc['cases'][0]['algorithm'][
                'launch_overrides'
            ].update({'goal_hold_sec': 0.0}),
            'must be positive',
        ),
        (
            lambda doc: doc['cases'][0].update({'profiles': ['legacy']}),
            'must equal \\[robust_gaussian_v1\\]',
        ),
    ],
)
def test_schema_v3_rejects_decorative_or_unreachable_contracts(
    tmp_path, mutation, match
):
    """Reject inherited, porous, contradictory, or untimed contracts."""
    document = _v3_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v3_allows_only_explicit_timing_insufficient_safe_timeout(
    tmp_path,
):
    """Reserve inadequate verification timing for a bound timeout proof."""
    document = _v3_document()
    case = document['cases'][0]
    case['algorithm']['launch_overrides']['verification_max_sec'] = 8.0
    success = case['success']
    success['all_of'].remove('controller_goal')
    success['all_of'].append('required_event_sequence')
    controller = success['controller']
    controller.update({
        'expected_verification_outcome': 'safe_timeout',
        'expected_terminal_state': 'FAILSAFE',
        'required_state_path': [
            'SEARCH', 'VERIFY_EXTREMUM', 'FAILSAFE',
        ],
        'required_event_sequence': [
            'TIMEOUT', 'FAILSAFE',
        ],
        'required_events': ['CONVERGENCE_CONFIRMED'],
        'forbidden_states': ['GOAL_HOLD'],
        'forbidden_events': ['GOAL_REACHED'],
    })

    suite = _load(tmp_path, document)
    timing = suite['cases'][0]['success']['controller'][
        'verification_timing'
    ]
    assert timing['selected_margin_sec'] == pytest.approx(-1.0)
    assert timing['timing_sufficient'] is False


def _remove_controller_list(document, field, predicate):
    document['cases'][0]['success']['controller'][field] = []
    all_of = document['cases'][0]['success']['all_of']
    if predicate not in all_of:
        all_of.append(predicate)


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'expected_terminal_state': None}
            ),
            'must expect terminal GOAL_HOLD',
        ),
        (
            lambda doc: _remove_controller_list(
                doc, 'required_state_sequence', 'required_state_sequence'
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: _remove_controller_list(
                doc, 'required_events', 'required_events'
            ),
            'must require events',
        ),
        (
            lambda doc: doc['cases'][0]['success']['all_of'].append(
                'required_event_sequence'
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'forbidden_states': []}
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success']['controller'].update(
                {'forbidden_events': []}
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {'collision_expected': None}
            ),
            'undeclared or vacuous evidence',
        ),
        (
            lambda doc: doc['cases'][0]['success'].update(
                {
                    'minimum_saturation_samples': 0,
                    'all_of': (
                        doc['cases'][0]['success']['all_of']
                        + ['minimum_saturation_samples']
                    ),
                }
            ),
            'undeclared or vacuous evidence',
        ),
    ],
)
def test_schema_v3_rejects_selected_vacuous_predicates(
    tmp_path,
    mutation,
    match,
):
    """Do not let an empty declaration satisfy a selected success fact."""
    document = _v3_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v3_safe_timeout_requires_ordered_timeout_then_failsafe(
    tmp_path,
):
    """Reject an unordered or reversed timeout lifecycle declaration."""
    document = _v3_document()
    case = document['cases'][0]
    case['algorithm']['launch_overrides']['verification_max_sec'] = 8.0
    success = case['success']
    success['all_of'].remove('controller_goal')
    success['all_of'].append('required_event_sequence')
    success['controller'].update({
        'expected_verification_outcome': 'safe_timeout',
        'expected_terminal_state': 'FAILSAFE',
        'required_state_path': [
            'SEARCH', 'VERIFY_EXTREMUM', 'FAILSAFE',
        ],
        'required_event_sequence': [
            'FAILSAFE', 'TIMEOUT',
        ],
        'required_events': ['CONVERGENCE_CONFIRMED'],
        'forbidden_states': ['GOAL_HOLD'],
        'forbidden_events': ['GOAL_REACHED'],
    })

    with pytest.raises(ValueError, match='ordered TIMEOUT then FAILSAFE'):
        _load(tmp_path, document)


def test_schema_v4_resolves_aggregate_truth_and_named_scope(tmp_path):
    """Bind aggregate targets and every formal predicate to full lifecycle."""
    document = _v4_document()
    suite = _load(tmp_path, document)
    runs, unsupported = expand_suite(suite)
    run = runs[0]

    assert unsupported == []
    assert run['acceptance_family'] == 'lifecycle'
    assert run['acceptance_partition'] == 'validation'
    assert run['repeat_reference'] is None
    assert run['success']['result_scopes'] == {
        'full_lifecycle': {
            'anchor_state': 'SEARCH',
            'boundary_state': None,
            'graceful_stop': False,
            'all_of': document['cases'][0]['success']['all_of'],
        },
    }
    assert (
        run['success']['ground_truth']['aggregate_field']['result_sha256']
        == document['cases'][0]['success']['ground_truth'][
            'aggregate_field'
        ]['result_sha256']
    )
    assert deterministic_case_key(run) == run['case_key']


def test_schema_v4_allows_development_only_graceful_activation_scope(
    tmp_path,
):
    """Permit a declared branch boundary while retaining global shutdown."""
    document = _v4_document()
    case = document['cases'][0]
    case['acceptance_partition'] = 'activation'
    scoped = case['success']['result_scopes']
    activation_predicates = [
        'required_state_path',
        'required_events',
    ]
    scoped['activation_window'] = {
        'anchor_state': 'VERIFY_EXTREMUM',
        'boundary_state': 'GOAL_HOLD',
        'graceful_stop': True,
        'all_of': activation_predicates,
    }
    scoped['full_lifecycle']['all_of'] = [
        predicate
        for predicate in scoped['full_lifecycle']['all_of']
        if predicate not in activation_predicates
    ]

    run = expand_suite(_load(tmp_path, document))[0][0]

    assert run['success']['result_scopes'][
        'activation_window'
    ]['graceful_stop'] is True


@pytest.mark.parametrize(
    ('mutation', 'match'),
    [
        (
            lambda doc: doc['cases'][0]['success']['ground_truth'].update(
                {'goal_source_ids': ['goal']}
            ),
            'unknown keys',
        ),
        (
            lambda doc: doc['cases'][0]['success']['result_scopes'].update({
                'activation_window': {
                    'anchor_state': 'VERIFY_EXTREMUM',
                    'boundary_state': 'GOAL_HOLD',
                    'graceful_stop': False,
                    'all_of': ['required_state_path'],
                },
            }),
            'assign each predicate',
        ),
        (
            lambda doc: doc['cases'][0]['metric_applicability'].update(
                {'escape_duration': True}
            ),
            'require escape_attempt',
        ),
        (
            lambda doc: doc['cases'][0].update({
                'repeat_reference': {
                    'partition': 'validation',
                    'case_key': 'a' * 64,
                },
            }),
            'only valid for reproducibility',
        ),
        (
            lambda doc: doc['cases'][0]['success']['ground_truth'].update(
                {'minimum_source_score': 0.94}
            ),
            'must retain tolerances',
        ),
    ],
)
def test_schema_v4_rejects_porosity_or_contract_drift(
    tmp_path,
    mutation,
    match,
):
    """Reject manual goals, overlapping scopes, and applicability drift."""
    document = _v4_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        _load(tmp_path, document)


def test_schema_v4_requires_repeat_reference_only_for_reproducibility(
    tmp_path,
):
    """Bind every reproducibility case to one sealed unique-case key."""
    document = _v4_document()
    case = document['cases'][0]
    case['acceptance_partition'] = 'reproducibility'
    case['repeat_reference'] = {
        'partition': 'validation',
        'case_key': 'a' * 64,
    }

    run = expand_suite(_load(tmp_path, document))[0][0]

    assert run['repeat_reference']['case_key'] == 'a' * 64


def test_historical_v2_activation_hash_and_case_keys_are_unchanged():
    """Keep sealed v2 YAML and normalized identities immutable under v3."""
    historical_sha = hashlib.sha256(
        HISTORICAL_V2_ACTIVATION.read_bytes()
    ).hexdigest()
    assert historical_sha == (
        'a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72'
    )
    runs, unsupported = expand_suite(load_suite(HISTORICAL_V2_ACTIVATION))
    assert unsupported == []
    assert [run['case_key'] for run in runs] == [
        'ab47b3264bcfa5da8880354c998b6152b9990be4f05e22b9da5d47ebdddd2f3e',
        '966c661dc8282b140efaf8b87ee2215b6dc7696798647a03b09d61b31cfa9603',
        '3877fb6052d7a0efd94070d6a7b6771b9726eea4fef900c4c317f6ad144cc040',
        '5f1597bda8d261e7845568f1f2246d27fc275d4426d2b2131ad6551461fce608',
        'b16f10d2ba9b8cfa62571bd5ace28014ee6fed979c4d8b91b49b238e17d5c587',
        '70bc3ab8801d66939eef679bc0934480358fa5b8c5947aebd04fbb735aaa13fd',
        'd5039ba75fcf0db9e36921b686f607406cbfcfc25a6dc924a3ce3424c84f9886',
        '86c8af432cfe9570267bc10911472c2561b1415907939bbf9d7c134009e41e08',
        '2d9d00a07b06fc59151054b7b1936eacdbfab7146c459ea6f9c6d106d2c69e93',
        'c91832a5506809efe3f1f181e0e422dd67e0f64219bd5c03497e86bf98249066',
    ]
