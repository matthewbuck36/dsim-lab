"""Construct the approved M4 population through existing scenario resources.

This performs no model evaluation or dispatch. The ordinary schema owner must
validate the generated resource, including its authoritative topology checks,
before it can be frozen for execution.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import yaml


SCENARIOS = Path(__file__).resolve().parent / 'scenarios'
TEMPLATES = {
    'primary': ('phase08_v8_10_primary_visible_probe.yaml',
                'c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b'),
    'secondary': ('phase08_v8_11_secondary_visible_probe.yaml',
                  'ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0'),
}
ARMS = ('A', 'B', 'C', 'D')
CONDITIONS = ('nominal', 'noise', 'delay')
DEFAULT_EXPERIMENT_VERSION = 'm4-pilot-v1'
EXPERIMENT_VERSIONS = ('m4-pilot-v1', 'm4-pilot-v2', 'm4-pilot-v3', 'm4-pilot-v4', 'm4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', 'm4-pilot-v10', 'm4-pilot-v11', 'm4-pilot-v12', 'm4-pilot-v13', 'm4-pilot-v14')
V10_EXPERIMENT_VERSION = 'm4-pilot-v10'
V10_METHOD_VERSION = 'recurrent_arrival_v10'
V11_EXPERIMENT_VERSION = 'm4-pilot-v11'
V11_METHOD_VERSION = 'recurrent_arrival_v11'
V12_EXPERIMENT_VERSION = 'm4-pilot-v12'
V12_METHOD_VERSION = 'recurrent_integrated_arrival_v12'
V13_EXPERIMENT_VERSION = 'm4-pilot-v13'
V13_METHOD_VERSION = 'recurrent_trapping_integrated_arrival_v13'
V14_EXPERIMENT_VERSION = 'm4-pilot-v14'
V14_METHOD_VERSION = 'recurrent_trapping_integrated_arrival_v14'
ARRIVAL_EXPERIMENT_VERSIONS = (V10_EXPERIMENT_VERSION, V11_EXPERIMENT_VERSION, V12_EXPERIMENT_VERSION, V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION)
ARRIVAL_SUITE_IDS = tuple(version.replace('-', '_') for version in ARRIVAL_EXPERIMENT_VERSIONS)
V10_RELEASE_POLICY = 'usable_four_arm_analysis_v1'
V12_RELEASE_POLICY = 'component_response_integrated_arrival_v1'
V13_RELEASE_POLICY = 'qualified_trapping_integrated_arrival_v1'
V14_RELEASE_POLICY = 'retained_development_integrated_arrival_v1'
V14_RETAINED_SOURCE_CONTRACT = {
    'path': '/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v13/preflight/contract.json',
    'sha256': '47fa4a8239d9a87f479461cba01790ce8aaa234a022a1cdeb206220152560efe',
}
PILOT_ROOT = Path('/home/mattb/Experiments/GESC-Gaussian/v2/pilot')
_CONTROLLER_DIRECTORY = (SCENARIOS.parent.parent / 'controller_node' /
                         'controller_config_files/turtlebot_vehicle/gradient_methods')
_BASELINE_CONTROLLER_PATH = _CONTROLLER_DIRECTORY / 'gesc_controller_full_rotation_voltage.json'
_BASELINE_CONTROLLER_SHA256 = '3f255699385cc16d830fd79f560d91f1206321606b763be2971bdbc9bf6912a1'
V6_CONTROLLER_PATH = _CONTROLLER_DIRECTORY / 'gesc_controller_full_rotation_voltage_m4_v6_gain_half.json'
V6_CONTROLLER_SHA256 = 'e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606'
V6_CONTROL_PROFILE_ID = 'm4_gain_half_control_v6'


def v6_controller_configuration():
    """Bind the adopted single-value JSON change through the existing owner."""
    original = _BASELINE_CONTROLLER_PATH.read_bytes()
    selected = V6_CONTROLLER_PATH.read_bytes()
    if (hashlib.sha256(original).hexdigest() != _BASELINE_CONTROLLER_SHA256
            or original.count(b'"k_vx": 1.0') != 1
            or selected != original.replace(b'"k_vx": 1.0', b'"k_vx": 0.5')
            or hashlib.sha256(selected).hexdigest() != V6_CONTROLLER_SHA256):
        raise ValueError('M4 v6 controller differs from the exact adopted gain-only configuration')
    return dict(path=str(V6_CONTROLLER_PATH), sha256=V6_CONTROLLER_SHA256,
                profile_id=V6_CONTROL_PROFILE_ID)


def is_arrival_experiment_version(experiment_version):
    """Select only the explicitly adopted arrival comparison versions."""
    return experiment_version in ARRIVAL_EXPERIMENT_VERSIONS


def is_integrated_arrival_experiment_version(experiment_version):
    """Select only versions with completed recovery as the primary path test."""
    return experiment_version in (V12_EXPERIMENT_VERSION, V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION)


def is_retained_development_experiment_version(experiment_version):
    """Select the one comparison with four authenticated retained source slots."""
    return experiment_version == V14_EXPERIMENT_VERSION


def is_trapping_experiment_version(experiment_version):
    """Select only the authenticated recurrent-trapping comparison family."""
    return experiment_version in (V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION)


def experiment_identity(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    """Resolve only the prospectively declared experiment identities."""
    if experiment_version not in EXPERIMENT_VERSIONS:
        raise ValueError('unsupported M4 experiment version')
    number = experiment_version.rsplit('v', 1)[1]
    return {'experiment_version': experiment_version, 'suite_id': 'm4_pilot_v'+number,
            'root': str(PILOT_ROOT/('m4_pilot_v'+number)),
            'process_ownership_mode': {'1': 'observed_tree_v1', '2': 'subreaper_v2',
                                       '3': 'subreaper_group_v3', '4': 'subreaper_group_v3',
                                       '5': 'subreaper_group_v3',
                                       '6': 'subreaper_group_v3',
                                       '7': 'subreaper_group_v3',
                                       '8': 'subreaper_group_v3',
                                       '9': 'subreaper_group_v3',
                                       '10': 'subreaper_group_v3',
                                       '11': 'subreaper_group_v3',
                                       '12': 'subreaper_group_v3',
                                       '13': 'subreaper_group_v3',
                                       '14': 'subreaper_group_v3'}[number]}


def experiment_method_version(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    experiment_identity(experiment_version)
    return {V10_EXPERIMENT_VERSION: V10_METHOD_VERSION,
            V11_EXPERIMENT_VERSION: V11_METHOD_VERSION,
            V12_EXPERIMENT_VERSION: V12_METHOD_VERSION,
            V13_EXPERIMENT_VERSION: V13_METHOD_VERSION,
            V14_EXPERIMENT_VERSION: V14_METHOD_VERSION}.get(experiment_version, DEFAULT_EXPERIMENT_VERSION)


def experiment_release_policy(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    """Keep each integrated version's adopted prerequisite policy explicit."""
    experiment_identity(experiment_version)
    if is_retained_development_experiment_version(experiment_version):
        return V14_RELEASE_POLICY
    if experiment_version == V13_EXPERIMENT_VERSION:
        return V13_RELEASE_POLICY
    if experiment_version == V12_EXPERIMENT_VERSION:
        return V12_RELEASE_POLICY
    return V10_RELEASE_POLICY if is_arrival_experiment_version(experiment_version) else None


def experiment_execution_budgets(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    """Return fixed caps without changing historical contract serialization."""
    experiment_identity(experiment_version)
    current = is_arrival_experiment_version(experiment_version)
    return dict(suite_timeout_sec=15800. if current else 15300.,
                science_budget_sec=1400. if current else 900., case_timeout_sec=900.,
                recording_sec=720., shutdown_grace_sec=45., cleanup_reserve_sec=30.,
                labels_sec=240. if current else 120., references_sec=45.,
                summary_sec=10., freeze_report_sec=40. if current else 20.)


def experiment_run_id(slot, experiment_version=DEFAULT_EXPERIMENT_VERSION):
    experiment_identity(experiment_version)
    if is_retained_development_experiment_version(experiment_version) and slot['slot'] in (1, 2, 3, 4):
        expected = expected_slots(V13_EXPERIMENT_VERSION)[slot['slot']-1]
        if any(slot.get(key) != value for key, value in expected.items()):
            raise ValueError('M4 v14 retained run descriptor differs from the original V13 slot')
        experiment_version = V13_EXPERIMENT_VERSION
    return f'{experiment_version}-slot{slot["slot"]:02d}-{slot["arm"]}-{slot["seed"]}'


def _retained_development_plans(contract):
    """Authenticate only the declared original four complete planned records.

    The workflow additionally authenticates acquisition, science, source bridges
    and R22's allowed measurement composition. This owner never rewrites old records.
    """
    binding = contract.get('retained_development', {})
    if not isinstance(binding, dict):
        raise ValueError('M4 v14 retained development binding must be a mapping')
    slots = binding.get('source_slots')
    if (binding.get('policy') != 'v13_development_r22_motion_v1'
            or binding.get('source_contract') != V14_RETAINED_SOURCE_CONTRACT
            or slots != [1, 2, 3, 4] or any(type(slot) is not int for slot in slots)):
        raise ValueError('M4 v14 retained development selection differs')
    raw = Path(V14_RETAINED_SOURCE_CONTRACT['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != V14_RETAINED_SOURCE_CONTRACT['sha256']:
        raise ValueError('M4 v14 original V13 source contract changed')
    original = json.loads(raw)
    if original.get('version') != V13_EXPERIMENT_VERSION:
        raise ValueError('M4 v14 retained source experiment differs')
    plans = original['runs'][:4]
    if contract.get('runs', [])[:4] != plans:
        raise ValueError('M4 v14 retained planned records differ from original V13')
    return plans


def validate_experiment_contract(contract):
    """Reject v2 substitutions while preserving the historical v1 contract."""
    identity = experiment_identity(contract.get('version'))
    if contract['version'] == DEFAULT_EXPERIMENT_VERSION:
        return identity
    root = Path(identity['root'])
    if (contract.get('method_version') != experiment_method_version(contract['version'])
            or contract.get('experiment_version') != identity['experiment_version']
            or Path(contract.get('root', '')).resolve() != root
            or Path(contract.get('contract_path', '')).resolve() != root/'preflight/contract.json'
            or Path(contract.get('scenario', {}).get('path', '')).resolve() != root/'scenario.yaml'
            or Path(contract.get('execution', {}).get('runs_root', '')).resolve() != root/'runs'
            or contract.get('execution', {}).get('process_ownership_mode') != identity['process_ownership_mode']):
        raise ValueError('M4 v2 experiment root/method/ownership identity differs')
    if (is_arrival_experiment_version(contract['version'])
            and contract.get('development_release_policy') != experiment_release_policy(contract['version'])):
        raise ValueError('M4 v10 usable development release policy is absent or changed')
    plans = contract.get('runs', [])
    if len(plans) != 16:
        raise ValueError('M4 v2 requires sixteen fresh slots')
    retained = (_retained_development_plans(contract)
                if is_retained_development_experiment_version(contract['version']) else [])
    primary_topology = None
    if contract['version'] in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
        topology_receipts = contract.get('topology_receipts', {})
        if (set(topology_receipts) != {*CONDITIONS, 'primary_nominal'}
                or Path(topology_receipts['primary_nominal'].get('path', '')).resolve()
                != root/'preflight/topology_primary_nominal.json'):
            raise ValueError('M4 v5 requires its explicit primary nominal topology receipt')
    v6_configuration = None
    if contract['version'] in ('m4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
        v6_configuration = v6_controller_configuration()
        if contract.get('controller_configuration') != v6_configuration:
            raise ValueError('M4 v6 controller configuration receipt differs')
        pins = {row.get('path'): row.get('sha256') for row in contract.get('source_files', [])}
        if (pins.get(str(_BASELINE_CONTROLLER_PATH)) != _BASELINE_CONTROLLER_SHA256
                or pins.get(v6_configuration['path']) != v6_configuration['sha256']):
            raise ValueError('M4 v6 controller configurations are not bound by source receipts')
        v6_templates = {name: _template(name) for name in TEMPLATES}
        v6_frozen = deepcopy(v6_templates['primary']['frozen_profile']['launch_overrides'])
        v6_frozen['controller_config_filepath'] = v6_configuration['path']
    for expected, actual in zip(expected_slots(contract['version']), plans):
        if retained and expected['slot'] <= 4:
            if (any(actual.get(key) != value for key, value in expected.items())
                    or actual.get('run_id') != experiment_run_id(expected, contract['version'])):
                raise ValueError('M4 v14 original retained slot identity differs')
            continue
        if (any(actual.get(key) != value for key, value in expected.items())
                or actual.get('run_id') != experiment_run_id(expected, contract['version'])
                or actual.get('resolved_scenario', {}).get('suite_id') != identity['suite_id']
                or Path(actual.get('summary_path', '')).resolve() != root/'acquisition'/f'summary_{expected["slot"]}.yaml'):
            raise ValueError('M4 v2 slot/scenario/run identity differs')
        if contract['version'] in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
            controls = actual['resolved_scenario'].get('algorithm', {}).get('launch_overrides', {})
            if (controls.get('open_field_escape_approach_continuity_enabled') is not True
                    or controls.get('open_field_escape_interior_anchor_fallback_enabled') is not True
                    or controls.get('open_field_escape_interior_anchor_min_displacement_m') != .50):
                raise ValueError('M4 v5 requires the matched bounded interior-anchor selection')
            if expected['geometry'] == 'primary':
                recovery = actual['resolved_scenario'].get('success', {}).get('staged_recovery', {})
                candidate = recovery.get('topology_qualification')
                if recovery.get('local_association_mode') != 'verified_trap':
                    raise ValueError('M4 v5 primary association requires verified_trap')
                if primary_topology is None:
                    primary_template = (v6_templates['primary'] if v6_configuration is not None
                                        else _template('primary'))
                    _validate_primary_topology_input(candidate, primary_template)
                    primary_topology = candidate
                elif candidate != primary_topology:
                    raise ValueError('M4 v5 primary topology differs across matched arms')
        if v6_configuration is not None:
            resolved = actual['resolved_scenario']
            frozen = resolved.get('frozen_profile', {})
            controls = resolved.get('algorithm', {}).get('launch_overrides', {})
            if (frozen.get('profile_id') != V6_CONTROL_PROFILE_ID
                    or frozen.get('launch_overrides') != v6_frozen
                    or any(isinstance(value, bool)
                           and type(frozen['launch_overrides'].get(key)) is not bool
                           for key, value in v6_frozen.items())):
                raise ValueError('M4 v6 requires the exact matched controller profile in every slot')
            arm_overrides = _arm_overrides(expected['arm'], contract['version'])
            expected_controls = {
                **v6_frozen,
                **v6_templates[expected['geometry']]['cases'][0]['algorithm']['launch_overrides'],
                **arm_overrides,
            }
            if (expected['arm'] in ('A', 'C')
                    and 'centroid_invalid_status_heartbeat_enabled' in controls):
                expected_controls['centroid_invalid_status_heartbeat_enabled'] = False
            if (controls != expected_controls
                    or any((isinstance(value, bool) and type(controls.get(key)) is not bool)
                           or (isinstance(value, (int, float)) and not isinstance(value, bool)
                               and isinstance(controls.get(key), bool))
                           for key, value in expected_controls.items())):
                raise ValueError('M4 v6 detector/direction method differs from the fixed arm')
            heartbeat = controls.get('centroid_invalid_status_heartbeat_enabled', False)
            if (type(heartbeat) is not bool
                    or heartbeat is not (expected['arm'] in ('B', 'D') and
                                         not is_arrival_experiment_version(contract['version']))):
                raise ValueError('M4 v6 centroid heartbeat selection differs from the fixed arms')
            arguments = actual.get('launch_argv', [])
            controller_arguments = [arg for arg in arguments
                                    if isinstance(arg, str) and arg.startswith('controller_config_filepath:=')]
            heartbeat_arguments = [arg for arg in arguments
                                   if isinstance(arg, str) and arg.startswith('centroid_invalid_status_heartbeat_enabled:=')]
            expected_heartbeat = (['centroid_invalid_status_heartbeat_enabled:=True']
                                  if heartbeat else ([] if 'centroid_invalid_status_heartbeat_enabled' not in controls
                                                     else ['centroid_invalid_status_heartbeat_enabled:=False']))
            if (controller_arguments != ['controller_config_filepath:=' + v6_configuration['path']]
                    or heartbeat_arguments != expected_heartbeat):
                raise ValueError('M4 v6 launch argv differs from its controller or heartbeat selection')
            if is_arrival_experiment_version(contract['version']):
                success = resolved.get('success', {})
                controller = success.get('controller', {})
                required = {'recording_complete', 'cleanup_complete', 'ground_truth_goal',
                            'local_recovery_stage', 'escape_command_ownership',
                            'post_recovery_global_proximity', 'fill_cardinality'}
                if (success.get('criterion') != 'post_recovery_arrival_v1'
                        or not required <= set(success.get('all_of', []))
                        or controller.get('expected_terminal_state') is not None
                        or 'GOAL_REACHED' in controller.get('required_events', [])
                        or success.get('staged_recovery', {}).get('global_proximity_radius_m') != .5):
                    raise ValueError('M4 v10 requires complete local recovery and selected global arrival')
                if is_integrated_arrival_experiment_version(contract['version']):
                    required.update({'required_events', 'required_event_sequence',
                                     'no_forbidden_states', 'no_forbidden_events'})
                    scoped = success.get('result_scopes', {})
                    if (set(success.get('all_of', [])) != required
                            or set(scoped) != {'full_lifecycle'}
                            or set(scoped['full_lifecycle'].get('all_of', [])) != required):
                        raise ValueError('M4 v12 requires all eleven primary predicates; first path remains diagnostic')
    science = contract.get('science', {})
    required = dict(labels_sec=experiment_execution_budgets(contract['version'])['labels_sec'], references_sec=45., summary_sec=10.,
                    freeze_report_sec=experiment_execution_budgets(contract['version'])['freeze_report_sec'], maximum_observations=40000,
                    targets_sec=[15+30*k for k in range(24)])
    if any(isinstance(science.get(k), bool) or science.get(k) != value for k, value in required.items()):
        raise ValueError('M4 v2 scientific method/budget differs')
    return identity


def m4_population(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    """Return fresh fixed slot identities, including all twelve holdouts."""
    identity = experiment_identity(experiment_version)
    prefix = 'm4' if experiment_version == DEFAULT_EXPERIMENT_VERSION else 'm4_v'+experiment_version.rsplit('v', 1)[1]
    result = []
    blocks = (
        ('development', 'primary', 'nominal', 26090801),
        ('holdout', 'secondary', 'nominal', 26090802),
        ('holdout', 'secondary', 'noise', 26090803),
        ('holdout', 'secondary', 'delay', 26090804),
    )
    if is_arrival_experiment_version(experiment_version):
        first_seed = {V10_EXPERIMENT_VERSION: 26091011,
                      V11_EXPERIMENT_VERSION: 26091021,
                      V12_EXPERIMENT_VERSION: 26091131,
                      V13_EXPERIMENT_VERSION: 26091141,
                      V14_EXPERIMENT_VERSION: 26091151}[experiment_version]
        blocks = tuple((partition, geometry, condition, first_seed+index)
                       for index, (partition, geometry, condition, _) in enumerate(blocks))
    for block, (partition, geometry, condition, seed) in enumerate(blocks):
        for arm in ARMS:
            slot = len(result) + 1
            result.append(dict(slot=slot, block=block, partition=partition,
                geometry=geometry, condition=condition, seed=seed, arm=arm,
                visible=block == 0,
                case_id=f'{prefix}_{partition}_{condition}_{arm}_{seed}',
                **({'experiment_version': identity['experiment_version']} if experiment_version != DEFAULT_EXPERIMENT_VERSION else {})))
    if is_retained_development_experiment_version(experiment_version):
        result[:4] = m4_population(V13_EXPERIMENT_VERSION)[:4]
    return result


def expected_slots(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    """Canonical slot descriptors for freeze, dispatch and independent matching."""
    return m4_population(experiment_version)


def _arm_overrides(arm, experiment_version):
    """One owner for the existing detector/direction selections and V6 admission."""
    if is_arrival_experiment_version(experiment_version):
        from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
        from ros_esc.stationary_fill_protocol import STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
        recurrent, moving = arm in ('B', 'D'), arm in ('C', 'D')
        overrides = dict(open_field_escape_interior_anchor_fallback_enabled=True,
            open_field_escape_interior_anchor_min_displacement_m=.50,
            convergence_metric_mode=RECURRENT_MODE if recurrent else 'pde_mean_v1',
            continuous_search_mode='rolling_gesc_v2' if moving else 'stationary_v1',
            v2_qualification_observation_only=False, centroid_invalid_status_heartbeat_enabled=False,
            v2_verification_motion_mode='centered_tracking_v1' if moving else 'rolling_neighborhood_v1')
        if recurrent:
            overrides['recurrent_diagnostics_topic'] = RECURRENT_TOPIC
        if arm == 'B':
            overrides['stationary_recurrent_fill_request_topic'] = STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
        if moving:
            overrides.update(v2_direction_policy='moving_cycle_coherence_v1',
                             v2_candidate_radius_m=.75, v2_candidate_epsilon_m=.15)
        if experiment_version in (V11_EXPERIMENT_VERSION, V12_EXPERIMENT_VERSION, V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION):
            overrides['controller_spawner_load_recovery_enabled'] = True
        if is_trapping_experiment_version(experiment_version) and arm == 'D':
            overrides['v2_verification_evidence_policy'] = 'recurrent_trapping_v1'
        return overrides
    overrides = {}
    if experiment_version in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
        overrides.update(open_field_escape_interior_anchor_fallback_enabled=True,
                         open_field_escape_interior_anchor_min_displacement_m=.50)
    overrides.update(convergence_metric_mode=(
        'centroid_two_block_v2' if arm in ('B', 'D') else 'pde_mean_v1'),
        continuous_search_mode='rolling_gesc_v2' if arm in ('C', 'D') else 'stationary_v1',
        v2_qualification_observation_only=False)
    if arm in ('B', 'D'):
        overrides.update(centroid_window_sec=6., centroid_epsilon_m=.18,
                         centroid_maximum_radius_m=.5)
        if experiment_version in ('m4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
            overrides['centroid_invalid_status_heartbeat_enabled'] = True
    if arm in ('C', 'D'):
        overrides.update(v2_direction_policy='moving_cycle_coherence_v1',
                         v2_candidate_radius_m=.75, v2_candidate_epsilon_m=.15)
    return overrides


def _v10_arrival_success(success):
    """Select the adopted arrival criterion on the inherited recovery contract."""
    success['criterion'] = 'post_recovery_arrival_v1'
    optional = {'controller_goal', 'expected_terminal_state'}
    success['all_of'] = [name for name in success['all_of'] if name not in optional]
    for scope in success['result_scopes'].values():
        scope['all_of'] = [name for name in scope['all_of'] if name not in optional]
    controller = success['controller']
    controller.pop('expected_terminal_state')
    controller['required_state_paths'] = [path[:-2] for path in controller['required_state_paths']]
    controller['required_state_path'] = controller['required_state_paths'][0]
    controller['required_events'] = [name for name in controller['required_events'] if name != 'GOAL_REACHED']
    controller['required_event_sequence'] = ['CONVERGENCE_CONFIRMED', 'FILL_CREATED', 'ESCAPE_STARTED']
    controller['reachability_argument'] = (
        'A valid local fill and owned direct or assisted escape must restore SEARCH '
        'before evaluator-only arrival within0.5m of the global source.')


def _template(geometry):
    name, expected = TEMPLATES[geometry]
    raw = (SCENARIOS/name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('M4 inherited scenario template changed: ' + name)
    return yaml.safe_load(raw)


def _validate_primary_topology_input(record, template):
    """Bind v5's additional input; numerical qualification remains in load_suite."""
    if not isinstance(record, dict):
        raise ValueError('M4 v5 requires an explicit primary topology input')
    def digest(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    payload = dict(record)
    result_digest = payload.pop('result_sha256', None)
    case = template['cases'][0]
    expected = dict(schema_version=1, method='authoritative_two_source_local_first_topology',
        source_list_sha256=digest([{key: source[key] for key in
            ('id', 'x_m', 'y_m', 'relative_lumen_input')} for source in case['sources']]),
        start_sha256=digest(case['starts'][0]), bounds_sha256=digest(template['defaults']['bounds_m']),
        disturbances_sha256=digest({'sensor_noise': {'model': 'none', 'bound': 0.},
                                   'sensor_delay_sec': 0., 'pose_delay_sec': 0.}),
        local_source_id='local', global_source_id='global')
    if result_digest != digest(payload) or any(record.get(key) != value for key, value in expected.items()):
        raise ValueError('M4 v5 primary topology input hash or original geometry binding differs')


def build_m4_document(topology_receipts_by_condition, *, runs_root, experiment_version=DEFAULT_EXPERIMENT_VERSION, primary_topology=None):
    """Build exact schema14 cases using supplied authoritative secondary laws.

Each supplied value is the existing topology qualification mapping, not a
filesystem receipt. Full model validation stays in ``load_suite``; this owner
only checks completeness/hash binding and preserves exact condition mappings.
"""
    identity = experiment_identity(experiment_version)
    if experiment_version != DEFAULT_EXPERIMENT_VERSION and Path(runs_root).resolve() != Path(identity['root'])/'runs':
        raise ValueError('M4 v2 scenario runs root differs from its declared experiment')
    if set(topology_receipts_by_condition) != set(CONDITIONS):
        raise ValueError('M4 requires separate nominal/noise/delay topology records')
    for condition, record in topology_receipts_by_condition.items():
        if not isinstance(record, dict):
            raise ValueError('M4 topology must be an evaluator record: ' + condition)
        payload = dict(record)
        digest = payload.pop('result_sha256', None)
        actual = hashlib.sha256(json.dumps(payload, sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        if digest != actual:
            raise ValueError('M4 topology record hash differs: ' + condition)
    templates = {name: _template(name) for name in TEMPLATES}
    primary = templates['primary']
    if experiment_version in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
        _validate_primary_topology_input(primary_topology, primary)
    elif primary_topology is not None:
        raise ValueError('The explicit primary topology input is selected only by M4 v5')
    if (primary['frozen_profile']['launch_overrides']
            != templates['secondary']['frozen_profile']['launch_overrides']):
        raise ValueError('M4 inherited primary/secondary controls differ')
    document = deepcopy(primary)
    document.update(schema_version=14, suite_id=identity['suite_id'],
                    description='Exact approved M4 sixteen-slot simulation comparison.')
    document['execution'].update(gazebo_gui=False, runs_root=str(Path(runs_root).resolve()),
        run_timeout_sec=720., wall_timeout_sec=900., shutdown_grace_sec=45.,
        stop_on_run_failure=False, stop_on_cleanup_failure=True)
    document['metadata'].update(experiment_version=experiment_version,
        operator_notes='Four visible development slots and twelve sealed holdouts; '
                       'exclusive frozen dispatch only; no replacement cases.')
    if is_arrival_experiment_version(experiment_version):
        document['metadata']['operator_notes'] = (
            'Four visible development slots and twelve fresh confirmation slots on exposed conditions; '
            'internal holdout partition spelling is retained; no replacements or tuning.')
    if is_retained_development_experiment_version(experiment_version):
        document['metadata']['operator_notes'] = (
            'Four retained V13 development acquisitions and twelve fresh V14 confirmations; '
            'no development dispatch, replacements or tuning.')
    document['frozen_profile']['profile_id'] = 'm4_inherited_control_v1'
    if experiment_version in ('m4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
        configuration = v6_controller_configuration()
        document['frozen_profile']['profile_id'] = configuration['profile_id']
        document['frozen_profile']['launch_overrides']['controller_config_filepath'] = configuration['path']
    document['cases'] = []
    for slot in m4_population(experiment_version):
        case = deepcopy(templates[slot['geometry']]['cases'][0])
        case.update(case_id=slot['case_id'], seeds=[slot['seed']],
            acceptance_partition=slot['partition'],
            description=f"M4 slot {slot['slot']}: {slot['geometry']} {slot['condition']} arm {slot['arm']}.")
        case['success']['controller']['contract_id'] = slot['case_id']
        case['disturbances'] = {
            'sensor_noise': ({'model': 'gaussian', 'bound': 0., 'std_dev': .015}
                             if slot['condition'] == 'noise' else {'model': 'none', 'bound': 0.}),
            'sensor_delay_sec': .1 if slot['condition'] == 'delay' else 0.,
            'pose_delay_sec': .1 if slot['condition'] == 'delay' else 0.,
        }
        case['metric_applicability']['delay'] = slot['condition'] == 'delay'
        if slot['geometry'] == 'secondary':
            case['success']['staged_recovery']['topology_qualification'] = deepcopy(
                topology_receipts_by_condition[slot['condition']])
        elif experiment_version in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9', *ARRIVAL_EXPERIMENT_VERSIONS):
            case['success']['staged_recovery'].update(local_association_mode='verified_trap',
                topology_qualification=deepcopy(primary_topology))
        overrides = case['algorithm']['launch_overrides']
        overrides.update(_arm_overrides(slot['arm'], experiment_version))
        if is_arrival_experiment_version(experiment_version):
            _v10_arrival_success(case['success'])
        if is_integrated_arrival_experiment_version(experiment_version):
            # Keep the original first-verification path declarations and metric;
            # existing Stage A establishes a completed recovery before arrival.
            success = case['success']
            success['all_of'] = [name for name in success['all_of'] if name != 'required_state_path']
            for scope in success['result_scopes'].values():
                scope['all_of'] = [name for name in scope['all_of'] if name != 'required_state_path']
        document['cases'].append(case)
    return document


def write_m4_scenario(path, topology_receipts_by_condition, *, runs_root, experiment_version=DEFAULT_EXPERIMENT_VERSION, primary_topology=None):
    """Write one fresh resource exclusively; callers validate before freeze."""
    path = Path(path).resolve()
    document = build_m4_document(topology_receipts_by_condition, runs_root=runs_root,
        experiment_version=experiment_version, primary_topology=primary_topology)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        yaml.safe_dump(document, stream, sort_keys=False)
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
