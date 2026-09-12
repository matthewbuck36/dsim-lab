"""Finite acquisition identity/path binding; scientific Q1 semantics are fixed."""
import hashlib
import json
from pathlib import Path


SCIENCE_VERSION = 'q1-primary-shadow-v1'
Q2_SCIENCE_VERSION = 'q2-primary-shadow-v1'
Q2_CORRECTED_VERSION = 'q2-primary-shadow-v2'
Q2_VERSIONS = (Q2_SCIENCE_VERSION, Q2_CORRECTED_VERSION)
REPOSITORY = Path('/home/mattb/dsim-lab')
BASE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/qualification')
BUILD_BASE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/builds')
ACQUISITION_ROOTS = {
    SCIENCE_VERSION: BASE / 'q1_primary_shadow_v1',
    f'{SCIENCE_VERSION}-recovery1': BASE / 'q1_primary_shadow_v1_recovery1',
    f'{SCIENCE_VERSION}-recovery2': BASE / 'q1_primary_shadow_v1_recovery2',
    f'{SCIENCE_VERSION}-recovery3': BASE / 'q1_primary_shadow_v1_recovery3',
    f'{SCIENCE_VERSION}-recovery4': BASE / 'q1_primary_shadow_v1_recovery4',
    Q2_SCIENCE_VERSION: BASE / 'q2_primary_shadow_v1',
    Q2_CORRECTED_VERSION: BASE / 'q2_primary_shadow_v2',
}


def acquisition_science_version(version):
    acquisition_root(version)
    return version if version in Q2_VERSIONS else SCIENCE_VERSION


def acquisition_expected_build(version):
    acquisition_root(version)
    name = 'q2_policy_runtime_v1' if version in Q2_VERSIONS else 'initial'
    return BUILD_BASE / name


def acquisition_scenario(version):
    science = acquisition_science_version(version).replace('-', '_')
    return REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios' / (science + '.yaml')


def acquisition_population(version):
    acquisition_root(version)
    first = {Q2_SCIENCE_VERSION: 26090921, Q2_CORRECTED_VERSION: 26090931}.get(version, 26090911)
    return [(seed, partition, exposure)
            for partition, start in (('discovery', first), ('confirmation', first + 2))
            for seed, exposure in ((start, 'residence'), (start + 1, 'approach'))]


def require_unused_q2_acquisition(contract_path, *, version=Q2_SCIENCE_VERSION,
                                  allow_reserved_contract=False):
    """Check only acquisition identity manifests; never read recording content."""
    if version not in Q2_VERSIONS:
        raise ValueError('unsupported Q2 nonuse version')
    root = acquisition_root(version)
    contract_path = contract_output(root, contract_path)
    if any((root / name).exists() for name in (
            'runs', 'acquisition', 'study_manifest.json', 'acquisition_closed.json')):
        raise ValueError('Q2 acquisition root already contains run evidence')
    if contract_path.exists() and not allow_reserved_contract:
        raise ValueError('Q2 contract is already reserved')
    seeds = {row[0] for row in acquisition_population(version)}
    manifests = set(BASE.glob('*/preflight/contract.json'))
    manifests.update(BASE.glob('*/acquisition/acquisition.json'))
    manifests.update(BASE.glob('*/study_manifest.json'))
    for path in sorted(manifests):
        if allow_reserved_contract and path == contract_path:
            continue
        document = json.loads(path.read_text())
        rows = document.get('runs', []) + document.get('verified_input_runs', [])
        rows += document.get('completed_runner_results', [])
        if any(row.get('seed') in seeds
               or str(row.get('run_id', '')).startswith(version + '-') for row in rows):
            raise ValueError('Q2 seed or run identity already reserved in ' + str(path))


def read_receipt(ref):
    path = Path(ref['path'])
    if hashlib.sha256(path.read_bytes()).hexdigest() != ref['sha256']:
        raise ValueError('Q1 receipt changed: ' + str(path))
    return json.loads(path.read_text())


def _verify_equivalence(contract, old, imports):
    proof = read_receipt(imports['source_equivalence'])
    if (proof.get('schema_version') != 1 or proof.get('version') != 'q1-recovery4-source-equivalence-v1'
            or proof.get('status') != 'PASS' or proof.get('prior_contract') != imports['prior_contract']
            or proof.get('expiry_audit') != imports['expiry_audit']
            or proof.get('valid_nonexpiry_path_unchanged') is not True
            or proof.get('scientific_confirmation_opened') is not False or not proof.get('evidence')):
        raise ValueError('Q1 recovery4 source-equivalence evidence unavailable')
    for ref in proof['evidence']:
        if hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest() != ref['sha256']:
            raise ValueError('Q1 equivalence test/review evidence changed')
    prior = {r['path']: r['sha256'] for r in old['source_files']}
    current = {r['path']: r['sha256'] for r in contract['source_files']}
    if not prior.keys() <= current.keys():
        raise ValueError('Q1 recovery4 dropped an original source receipt')
    expected = []
    runtime = {str(REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc/filter_node' / name)
               for name in ('rolling_gesc.py', 'v2_runtime.py')}
    for path, digest in sorted(current.items()):
        if prior.get(path) == digest:
            continue
        if path in runtime:
            classification = 'runtime_expiry_only'
        elif (Path(path).is_relative_to(REPOSITORY / 'docs/codex/gesc_gaussian/v2')
              or Path(path).is_relative_to(REPOSITORY / 'ros2_ws/src/ros_esc/test')):
            classification = 'workflow_or_test'
        else:
            raise ValueError('Q1 recovery4 source change is outside the frozen correction: '+path)
        expected.append({'path':path, 'old_sha256':prior.get(path), 'new_sha256':digest,
                         'classification':classification})
    if sorted(proof.get('source_changes', []), key=lambda r:r['path']) != expected:
        raise ValueError('Q1 recovery4 source-equivalence delta is incomplete or changed')


def imported_inputs(contract):
    """Validate the sole finite two-input exception; return original rows unchanged."""
    if contract.get('acquisition_version') != f'{SCIENCE_VERSION}-recovery4':
        return []
    from ros_esc.plotting_scripts import gesc_gaussian_bag_analysis as analysis
    root = acquisition_root(f'{SCIENCE_VERSION}-recovery4')
    prior_root = acquisition_root(f'{SCIENCE_VERSION}-recovery3')
    imports = contract.get('imports', {})
    if set(imports) != {'prior_contract','prior_acquisition','prior_closure','input_files',
                        'expiry_audit','source_equivalence'}:
        raise ValueError('Q1 recovery4 requires its exact finite import block')
    expected_paths = {'prior_contract':prior_root/'preflight/contract.json',
        'prior_acquisition':prior_root/'acquisition/acquisition.json',
        'prior_closure':prior_root/'acquisition_closed.json',
        'expiry_audit':prior_root/'diagnostics/discovery_expiry_audit_v1/result.json',
        'source_equivalence':root/'preflight/source_equivalence.json'}
    if any(Path(imports[name]['path']) != path for name,path in expected_paths.items()):
        raise ValueError('Q1 recovery4 import reference is outside its fixed prior boundary')
    old = read_receipt(imports['prior_contract'])
    acquisition = read_receipt(imports['prior_acquisition'])
    closure = read_receipt(imports['prior_closure'])
    audit = read_receipt(imports['expiry_audit'])
    prior_version = f'{SCIENCE_VERSION}-recovery3'
    if (old.get('version') != SCIENCE_VERSION or old.get('acquisition_version') != prior_version
            or acquisition.get('contract') != imports['prior_contract']
            or acquisition.get('acquisition_version') != prior_version
            or acquisition.get('status') != 'INCOMPLETE'
            or acquisition.get('scientific_confirmation_opened') is not False
            or closure.get('status') != 'CLOSED_INCOMPLETE'
            or closure.get('acquisition_version') != prior_version
            or closure.get('verified_runs') != 2 or closure.get('dispatched_cases') != 3
            or closure.get('remaining_cases_dispatched') is not False
            or closure.get('failed_case_pre_readiness') is not True
            or closure.get('all_cleanup_passed') is not True
            or closure.get('scientific_confirmation_opened') is not False):
        raise ValueError('Q1 recovery4 prior acquisition is not the frozen two-input boundary')
    attempts = acquisition.get('completed_runner_results', [])
    if (len(attempts) != 3 or len(closure.get('runs', [])) != 3
            or [r['runner_result'].get('run_id') for r in attempts] != [r['run_id'] for r in old['runs'][:3]]
            or [r['runner_result'].get('classification', {}).get('passed') for r in attempts] != [True,True,False]
            or any(r['runner_result'].get('cleanup', {}).get('passed') is not True for r in attempts)
            or closure['runs'][2].get('recording', {}).get('readiness_ever_true') is not False):
        raise ValueError('Q1 recovery4 prior case outcomes or sealed boundary changed')
    artifacts = {r['path']:r['sha256'] for r in closure.get('artifacts', [])}
    if artifacts.get(imports['prior_acquisition']['path']) != imports['prior_acquisition']['sha256']:
        raise ValueError('Q1 recovery4 closure does not bind the prior acquisition')
    for name in ('scenario','detector','reference','label_geometry','geometry_recovery','geometry_receipts','spawn_check','coordinate_preflight'):
        if contract.get(name) != old.get(name):
            raise ValueError('Q1 recovery4 scientific/geometry contract changed: '+name)
    allowed = {'runs_root','outer_acquisition_ceiling_sec'}
    if ({k:v for k,v in contract['execution'].items() if k not in allowed}
            != {k:v for k,v in old['execution'].items() if k not in allowed}
            or contract['execution'].get('outer_acquisition_ceiling_sec') != 600.
            or contract['execution'].get('recorder_process_ceiling_sec') != 240.
            or contract['runs'][:2] != old['runs'][:2]
            or any(new['resolved_scenario'] != prior['resolved_scenario'] or new['visible'] != prior['visible']
                   or new['launch_argv'] != [arg.replace(prior['run_id'],new['run_id']) for arg in prior['launch_argv']]
                   for new,prior in zip(contract['runs'][2:],old['runs'][2:]))):
        raise ValueError('Q1 recovery4 imported plan, fresh controls or execution bounds changed')
    _verify_equivalence(contract, old, imports)
    refs = imports['input_files']
    if (len(refs) != 2 or [r['path'] for r in refs] != [str(prior_root/'acquisition'/f'input_{s}.json')
                                                     for s in (26090911,26090912)]):
        raise ValueError('Q1 recovery4 imports must be exactly the two accepted discovery files')
    rows = [read_receipt(ref) for ref in refs]
    if rows != acquisition.get('verified_input_runs'):
        raise ValueError('Q1 recovery4 input differs from the original accepted ledger')
    if (audit.get('status') != 'COMPLETE' or audit.get('contract') != imports['prior_contract']
            or audit.get('closure') != imports['prior_closure']
            or audit.get('confirmation_scientific_outputs_opened') is not False
            or len(audit.get('results', [])) != 2):
        raise ValueError('Q1 recovery4 lacks its fixed integrity-only expiry audit')
    for index,(row,ref) in enumerate(zip(rows,refs)):
        planned = old['runs'][index]
        directory = Path(row['run_directory'])
        if (artifacts.get(ref['path']) != ref['sha256'] or row['run_id'] != planned['run_id']
                or row['seed'] != planned['seed'] or row['partition'] != 'discovery'
                or not directory.is_relative_to(prior_root/'runs') or directory.name != row['run_id']):
            raise ValueError('Q1 recovery4 imported identity/path changed')
        # Existing owner verifies original files/configuration and the copied plan;
        # never substitute a new binding or waive historical source hash failures.
        analysis._q1_verify_run(row, contract)
        report = json.loads((directory/'completeness.json').read_text())
        result = analysis.load_yaml(directory/'scenario_result.yaml')
        metadata = analysis.load_yaml(directory/'metadata.yaml')
        recording = metadata.get('recording', {})
        duration = recording.get('simulation_duration', {})
        predicates = result.get('classification', {}).get('predicate_results', {})
        if (report.get('passed') is not True or result.get('classification', {}).get('passed') is not True
                or any(predicates.get(k) is not True for k in ('recording_complete','cleanup_complete','no_forbidden_events'))
                or recording.get('completion_reason') != 'simulation_duration_elapsed'
                or duration.get('completed') is not True or duration.get('requested_sec') != 125.
                or duration.get('elapsed_sec') != 125.):
            raise ValueError('Q1 recovery4 imported input is not an original complete safe125s run')
        spawn = read_receipt(row['spawn_check'])
        if Path(row['spawn_check']['path']) != prior_root/'acquisition'/f"spawn_{row['seed']}.json" or spawn.get('passed') is not True:
            raise ValueError('Q1 recovery4 imported spawn receipt failed or changed')
        observed = read_receipt(audit['results'][index])
        if (observed.get('input') != ref or observed.get('seed') != row['seed']
                or observed.get('diagnostic_sequence_discontinuities') != []
                or observed.get('reset_sequence_jumps_or_regressions') != []
                or any(count != 0 for phase in observed['expiry_reason_message_counts'].values() for count in phase.values())):
            raise ValueError('Q1 recovery4 imported path lacks unchanged expiry-free evidence')
    return rows


def acquisition_root(version):
    if not isinstance(version, str) or version not in ACQUISITION_ROOTS:
        raise ValueError('unsupported finite Q1 acquisition version')
    return ACQUISITION_ROOTS[version]


def contract_output(root, path=None):
    path = Path(path) if path is not None else root / 'preflight/contract.json'
    if (not path.is_absolute() or path.parent != root / 'preflight'
            or path.resolve() != path):
        raise ValueError('Q1 contract must reside directly in its acquisition preflight directory')
    return path


def validate_acquisition_layout(contract, contract_path):
    """Reject mismatched roots/IDs before any output or dispatch.

    Missing acquisition fields mean the original identity for old contracts;
    all newly frozen contracts carry both fields explicitly.
    """
    version = contract.get('acquisition_version', SCIENCE_VERSION)
    root = acquisition_root(version)
    if contract.get('version') != acquisition_science_version(version):
        raise ValueError('qualification scientific/acquisition version mismatch')
    declared = contract.get('acquisition_root', str(root) if version == SCIENCE_VERSION else None)
    if declared != str(root) or Path(declared).resolve() != root:
        raise ValueError('Q1 acquisition root differs from its finite version')
    if (contract.get('execution', {}).get('runs_root') != str(root / 'runs')
            or (root / 'runs').resolve() != root / 'runs'):
        raise ValueError('Q1 recorder runs_root differs from acquisition root')
    contract_output(root, contract_path)
    expected = acquisition_population(version)
    runs = contract.get('runs', [])
    fourth_recovery = version == f'{SCIENCE_VERSION}-recovery4'
    if (len(runs) != 4 or any(
            (run.get('seed'), run.get('partition'), run.get('exposure')) != values
            or run.get('run_id') != f"{SCIENCE_VERSION+'-recovery3' if fourth_recovery and values[1]=='discovery' else version}-{values[1]}-{values[2]}-{values[0]}"
            for run, values in zip(runs, expected))):
        raise ValueError('Q1 acquisition run identities or fixed population changed')
    if version in Q2_VERSIONS:
        if ('imports' in contract or 'recovery' in contract
                or contract.get('expected_build') != str(acquisition_expected_build(version))
                or contract.get('scenario', {}).get('path') != str(acquisition_scenario(version))
                or any(run.get('case_id') != f'q2_{partition}_{exposure}'
                       or run.get('visible') is not (index == 0)
                       for index, (run, (_, partition, exposure)) in enumerate(zip(runs, expected)))):
            raise ValueError('Q2 requires its exact fresh scenario/build and four new cases')
        return root
    if fourth_recovery:
        recovery = contract.get('recovery', {})
        expected_plans = {'amendment':'q1_acquisition_recovery4_plan.md',
                          'source_correction':'q1_filter_expiry_recovery_plan.md'}
        if set(recovery) != set(expected_plans):
            raise ValueError('Q1 recovery4 lacks its exact continuation/correction plans')
        for name, filename in expected_plans.items():
            ref = recovery[name]
            if (Path(ref['path']) != REPOSITORY/'docs/codex/gesc_gaussian/v2'/filename
                    or hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest() != ref['sha256']):
                raise ValueError('Q1 recovery4 plan receipt changed')
        imported_inputs(contract)
        return root
    if version != SCIENCE_VERSION:
        recovery = contract.get('recovery', {})
        second_recovery = version == f'{SCIENCE_VERSION}-recovery2'
        third_recovery = version == f'{SCIENCE_VERSION}-recovery3'
        required_receipts = {'amendment', 'closure', 'prior_acquisition'}
        if second_recovery or third_recovery:
            required_receipts.add('source_correction')
        if set(recovery) != required_receipts:
            raise ValueError('Q1 recovery lacks its preserved amendment/closure receipts')
        for ref in recovery.values():
            if hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest() != ref['sha256']:
                raise ValueError('Q1 recovery receipt changed')
        prior = recovery['prior_acquisition']
        prior_version = (f'{SCIENCE_VERSION}-recovery2' if third_recovery else
                         f'{SCIENCE_VERSION}-recovery1' if second_recovery else SCIENCE_VERSION)
        prior_root = ACQUISITION_ROOTS[prior_version]
        if Path(prior['path']) != prior_root / 'acquisition/acquisition.json':
            raise ValueError('Q1 recovery is not linked to its exact closed prior acquisition')
        result = json.loads(Path(prior['path']).read_text())
        attempts = result.get('completed_runner_results', [])
        if (result.get('version') != SCIENCE_VERSION or result.get('status') != 'INCOMPLETE'
                or result.get('verified_input_runs') != [] or len(attempts) != 1
                or not attempts[0]['runner_result'].get('cleanup', {}).get('passed')):
            raise ValueError('Q1 recovery requires its preserved one-case incomplete outcome')
        if not (second_recovery or third_recovery):
            if attempts[0]['runner_result'].get('run_directory') is not None:
                raise ValueError('Q1 recovery1 requires the preserved pre-exposure failure')
        else:
            attempted = attempts[0]['runner_result']
            expected_id = f'{prior_version}-discovery-residence-26090911'
            directory = attempted.get('run_directory')
            if (result.get('acquisition_version') != prior_version
                    or attempted.get('run_id') != expected_id
                    or not isinstance(directory, str)
                    or not Path(directory).is_relative_to(prior_root / 'runs')
                    or Path(directory).name != expected_id
                    or attempted.get('classification', {}).get('passed') is not False
                    or Path(recovery['closure']['path']) != prior_root / 'acquisition_closed.json'):
                raise ValueError('Q1 recovery requires its fixed prior failure and closure')
            closure = json.loads(Path(recovery['closure']['path']).read_text())
            if (closure.get('status') != 'CLOSED_INCOMPLETE'
                    or closure.get('acquisition_version') != prior_version
                    or closure.get('verified_runs') != 0
                    or closure.get('dispatched_cases') != 1
                    or closure.get('remaining_cases_dispatched') is not False
                    or closure.get('scientific_confirmation_opened') is not False
                    or closure.get('completeness_passed') is not False
                    or not closure.get('cleanup', {}).get('passed')):
                raise ValueError('Q1 recovery closure does not preserve the declared failed boundary')
            prior_receipts = [item for item in closure.get('artifacts', [])
                              if item.get('path') == prior['path']]
            if len(prior_receipts) != 1 or prior_receipts[0].get('sha256') != prior['sha256']:
                raise ValueError('Q1 recovery closure and prior acquisition receipt differ')
            if third_recovery:
                predicates = closure.get('classification', {}).get('predicate_results', {})
                original_predicates = attempted.get('classification', {}).get('predicate_results', {})
                duration = closure.get('simulation_duration', {})
                if (result.get('scientific_confirmation_opened') is not False
                        or predicates.get('no_forbidden_events') is not True
                        or predicates.get('cleanup_complete') is not True
                        or original_predicates.get('no_forbidden_events') is not True
                        or original_predicates.get('cleanup_complete') is not True
                        or closure.get('final_zero_observed') is not True
                        or closure.get('recording_complete') is not True
                        or duration.get('completed') is not True
                        or duration.get('requested_sec') != 125.
                        or duration.get('elapsed_sec') != 125.):
                    raise ValueError('Q1 recovery3 requires the closed safe125s acquisition')
                completeness_path = Path(directory) / 'completeness.json'
                receipts = [r for r in closure.get('artifacts', []) if r.get('path') == str(completeness_path)]
                if (len(receipts) != 1 or hashlib.sha256(completeness_path.read_bytes()).hexdigest()
                        != receipts[0]['sha256']):
                    raise ValueError('Q1 recovery3 original completeness receipt changed')
                report = json.loads(completeness_path.read_text())
                failed = {name: check for name, check in report.get('checks', {}).items()
                          if check.get('passed') is not True}
                detail = failed.get('algorithm_event_producer_identified', {}).get('detail', [])
                if (report.get('passed') is not False
                        or set(failed) != {'algorithm_event_producer_identified'}
                        or closure.get('failed_checks') != failed or len(detail) != 1
                        or detail[0].get('event_type') != 1
                        or detail[0].get('detail') != 'centroid_windows_v2 source-time configuration'):
                    raise ValueError('Q1 recovery3 requires the sole exact producer-attribution failure')
    return root
