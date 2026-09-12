#!/usr/bin/env python3
"""Exclusive M4 preparation and finite science hooks for the existing runner.

No ROS node, recorder, controller or numerical model is defined here. The
dispatcher and analytical owners supply those capabilities under the saved
prospective contract; this module binds their inputs, jobs and output receipts.
"""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json

from q1_environment import installed_entry_points, selected_environment
from ros_esc.scenario_runner.m4_scenario import (
    DEFAULT_EXPERIMENT_VERSION, EXPERIMENT_VERSIONS, experiment_identity,
    experiment_run_id, validate_experiment_contract, v6_controller_configuration,
    V11_EXPERIMENT_VERSION, V12_EXPERIMENT_VERSION, V13_EXPERIMENT_VERSION,
    V14_EXPERIMENT_VERSION, experiment_method_version,
    experiment_execution_budgets, experiment_release_policy, is_arrival_experiment_version,
    is_integrated_arrival_experiment_version, is_retained_development_experiment_version,
)


REPOSITORY = Path('/home/mattb/dsim-lab')
EXPERIMENTS = Path('/home/mattb/Experiments/GESC-Gaussian/v2')
ROOT = EXPERIMENTS / 'pilot/m4_pilot_v1'
BUILD = EXPERIMENTS / 'builds/q5_stationary_centroid_adapter_v1'
TOOLS = REPOSITORY / 'docs/codex/gesc_gaussian/v2/tools'
VERSION = 'm4-pilot-v1'
V10_RELEASE_POLICY = 'usable_four_arm_analysis_v1'
V10_DEVELOPMENT = EXPERIMENTS / 'development/20260910'
V10_ENVIRONMENT = V10_DEVELOPMENT / 'stationary_recurrent_pairing_v1/runtime_environment_v2.sh'
V10_INTERFACE_INSTALL = V10_DEVELOPMENT / 'stationary_recurrent_pairing_v1/build_interfaces_v1/install'
V12_DEVELOPMENT = EXPERIMENTS / 'development/20260911'
R10_ROOT = V12_DEVELOPMENT / 'r10_paired_response_v1'
R10_ARCHIVE = EXPERIMENTS / 'checkpoints/r10_paired_response_v1/manifest.json'
R10_DECISION_SHA256 = 'e9e6cff5869aa3ba8c7d11b470ed00b5b0b34d54fcac34d44676a029e0ef601c'
R10_ARCHIVE_SHA256 = 'df23819df6c4f013f8790e414ce045e2b8d7a1b03959ee40f97ec550a349625d'
R21_ROOT = V12_DEVELOPMENT / 'r21_recurrent_trapping_v1'
D02_ROOT = R21_ROOT / 'visible_integrated_D_02'
D02_ARCHIVE = EXPERIMENTS / 'checkpoints/r21_d02_complete_v1/manifest.json'
D02_ARCHIVE_SHA256 = '3b184f33918c1ca3a7a0be60ecfed208cdba61f14c6e58395ca8c9becf797ec5'
V13_SOURCE_ROOT = V12_DEVELOPMENT / 'm4_v13_source_v1'
V14_SOURCE_ROOT = V12_DEVELOPMENT / 'm4_v14_source_v1'
V14_ROW_CHECKS = frozenset(('acquisition_complete', 'position_labels_complete',
    'confirmation_attribution_complete', 'selected_authority_complete',
    'error_attribution_complete', 'arrival_measurement_complete',
    'path_length_complete', 'motion_measurement_complete', 'direction_inputs_complete'))
V14_SUMMARY_CHECKS = frozenset(('four_arm_analysis_complete', 'both_reference_products_complete'))
V13_FIXTURE_BRIDGE_SHA256 = '7f7c109caa6f5cd1e609f1ca62bd34eedc2c68c173b073ddaf479a992f3cd56f'
V13_FIXTURE_PATHS = frozenset(str(REPOSITORY / 'ros2_ws/src/ros_esc/test' /
    name) for name in (*[f'test_m4_v{version}_versions.py' for version in (3, 4, 5, 6, 7, 8, 9, 11, 12)],
    'test_m4_v2_subreaper_routes.py', 'test_m4_v3_shutdown_routes.py'))
V13_ORCHESTRATION_PATHS = frozenset(str(REPOSITORY / name) for name in (
    'ros2_ws/src/ros_esc/ros_esc/scenario_runner/m4_scenario.py',
    'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py',
    'ros2_ws/src/ros_esc/ros_esc/plotting_scripts/m4_pilot.py',
    'docs/codex/gesc_gaussian/v2/tools/evaluate_m4.py',
    'docs/codex/gesc_gaussian/v2/tools/m4_workflow.py',
    'docs/codex/gesc_gaussian/v2/tools/run_m4.py'))
GEOMETRIES = {
    'primary': ('geometry_1.json', '8f4f7fc53b67144317dd2e4640871c29ac5eb6c0d7e2cbc6ca3521a6c24788dd'),
    'secondary': ('geometry_2.json', 'f76ec43e796092d37a862c7290a0d3bfc49857194689ade0ff9561be09dcea36'),
}


def receipt(path):
    path = Path(path).resolve()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'path': str(path), 'sha256': digest.hexdigest()}


def check_receipts(references):
    seen = {}
    for ref in references:
        actual = receipt(ref['path'])
        if actual != {key: ref[key] for key in ('path', 'sha256')}:
            raise ValueError('M4 retained input changed: ' + str(ref['path']))
        if actual['path'] in seen and seen[actual['path']] != actual['sha256']:
            raise ValueError('M4 conflicting file receipts')
        seen[actual['path']] = actual['sha256']
    return seen


def read_json(path):
    return json.loads(Path(path).read_text())


def slot_spec(contract, slot):
    rows = [row for row in contract['runs'] if row['slot'] == int(slot)]
    if len(rows) != 1:
        raise ValueError('M4 slot is not uniquely reserved')
    return rows[0]


def _v10_runtime_binding(*, recurrent_trapping=False):
    """Bind selected generated wire types without starting a ROS node."""
    from ament_index_python.packages import get_package_prefix
    from ros_esc_interfaces.msg import (
        StationaryRecurrentFillRequest, RecurrentConvergenceDiagnostics, VerificationGuidance,
    )
    install = R21_ROOT / 'build_interfaces_v1/install' if recurrent_trapping else V10_INTERFACE_INSTALL
    environment = R21_ROOT / 'runtime_environment.sh' if recurrent_trapping else V10_ENVIRONMENT
    kinds = (StationaryRecurrentFillRequest, RecurrentConvergenceDiagnostics, VerificationGuidance)
    schemas = {'StationaryRecurrentFillRequest': 1, 'VerificationGuidance': 2}
    if recurrent_trapping:
        from ros_esc_interfaces.msg import RecurrentCandidateSnapshot, RecurrentFillCommand
        kinds += (RecurrentCandidateSnapshot, RecurrentFillCommand)
        for kind in (RecurrentCandidateSnapshot, RecurrentFillCommand):
            fields = kind.get_fields_and_field_types()
            if not {'schema_version', 'policy_id', 'confirmation', 'diagnostic'} <= set(fields):
                raise ValueError('M4 v13 generated recurrent proof schema differs')
            schemas[kind.__name__] = 1
    prefix = Path(get_package_prefix('ros_esc_interfaces')).resolve()
    if prefix != (install / 'ros_esc_interfaces').resolve():
        raise ValueError('M4 v10 requires the selected stationary recurrent interface overlay')
    request, diagnostic, guidance = (StationaryRecurrentFillRequest(),
                                    RecurrentConvergenceDiagnostics(), VerificationGuidance())
    if (not hasattr(request, 'schema_version') or not hasattr(guidance, 'schema_version')
            or not isinstance(request.confirmation, RecurrentConvergenceDiagnostics)
            or not hasattr(diagnostic, 'persistence_start')
            or not all(hasattr(guidance, field) for field in ('publication_sequence', 'state_sha256'))):
        raise ValueError('M4 v10 generated request/diagnostic/guidance schemas differ')
    files = set()
    for kind in kinds:
        path = Path(inspect.getfile(kind)).resolve()
        if not path.is_relative_to(prefix):
            raise ValueError('M4 v10 generated Python type resolves outside selected overlay')
        files.add(path)
    files.update(path.resolve() for path in prefix.rglob('*.py'))
    libraries = {path.resolve() for path in prefix.rglob('*.so')}
    if not libraries:
        raise ValueError('M4 v10 interface overlay has no native type support')
    files.update(libraries)
    scripts = [V10_ENVIRONMENT, V10_DEVELOPMENT / 'centered_runtime_v2/environment.sh',
        Path('/opt/ros/humble/setup.bash'),
        EXPERIMENTS / 'builds/q2_policy_runtime_v1/install/local_setup.bash',
        BUILD / 'install/local_setup.bash',
        V10_DEVELOPMENT / 'centered_runtime_v2/build_interfaces_v1/install/local_setup.bash',
        V10_INTERFACE_INSTALL / 'local_setup.bash']
    files.update(path.resolve() for path in scripts)
    if recurrent_trapping:
        files.update((environment.resolve(), (install / 'local_setup.bash').resolve()))
    return dict(environment_script=receipt(environment), interface_prefix=str(prefix),
        protocol_schemas=schemas,
        generated_fields={kind.__name__: kind.get_fields_and_field_types() for kind in kinds},
        files=[receipt(path) for path in sorted(files)])


def _runtime_binding(version):
    return (_v10_runtime_binding(recurrent_trapping=True)
            if version in (V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION)
            else _v10_runtime_binding())


def _compose_v14_development(source, selected_motion):
    """Compose the four explicitly allowed motion changes without rewriting evidence."""
    rows = source.get('runs', [])
    if ([row.get('slot') for row in rows] != [1, 2, 3, 4]
            or [row.get('arm') for row in rows] != ['A', 'B', 'C', 'D']
            or set(selected_motion) != {3, 4}):
        raise ValueError('V14 requires four ordered original rows and exactly C/D motion')

    def valid_checks(value, names):
        return (isinstance(value, dict) and set(value) == names
                and all(type(flag) is bool for flag in value.values()))

    if (not valid_checks(source.get('scientific_analysis_checks'), V14_SUMMARY_CHECKS)
            or any(not valid_checks(row.get('scientific_analysis_checks'), V14_ROW_CHECKS)
                   for row in rows)):
        raise ValueError('V14 original scientific check population or types differ')
    result = deepcopy(source)
    for row in result['runs'][2:]:
        motion = selected_motion[row['slot']]
        if (not isinstance(motion, dict) or type(motion.get('analysis_complete')) is not bool
                or 'mandatory_stopped_acquisitions' not in motion):
            raise ValueError('V14 selected motion lacks an explicit measured disposition')
        row['mandatory_stop_evidence'] = deepcopy(motion)
        row['mandatory_stopped_acquisitions'] = motion['mandatory_stopped_acquisitions']
        row['scientific_analysis_checks']['motion_measurement_complete'] = motion['analysis_complete']
        row['scientific_analysis_complete'] = all(row['scientific_analysis_checks'].values())
    result['scientific_analysis_checks']['four_arm_analysis_complete'] = all(
        row.get('scientific_analysis_complete') is True
        and all(row['scientific_analysis_checks'].values()) for row in result['runs'])
    result['scientific_analysis_complete'] = all(result['scientific_analysis_checks'].values())
    return result


def _v14_retained_development_binding():
    """Authenticate fixed V13 acquisitions and R22's separate motion evidence.

    This deterministic binding preserves original failed scientific completion.
    The existing workflow separately composes the narrowly allowed V14 view.
    Raw bags and bag metadata are never opened or hashed here.
    """
    from ros_esc.plotting_scripts.bag_reader import load_yaml

    old_root = EXPERIMENTS/'pilot/m4_pilot_v13'
    source_root = V12_DEVELOPMENT/'m4_v14_source_v1'
    r22 = V12_DEVELOPMENT/'r22_readiness_command_pairing_v1'
    analysis_root = old_root/'analysis/block_0'
    contract_ref = dict(path=str(old_root/'preflight/contract.json'),
        sha256='47fa4a8239d9a87f479461cba01790ce8aaa234a022a1cdeb206220152560efe')
    refs = {}

    def require(ok, reason):
        if not ok:
            raise ValueError('M4 v14 retained development: '+reason)

    def raw_path(path):
        return '/bag/' in str(path) or Path(path).suffix in ('.db3', '.mcap')

    def checked(reference):
        reference = {key: reference[key] for key in ('path', 'sha256')}
        require(not raw_path(reference['path']), 'raw data must remain inherited')
        if reference['path'] in refs:
            require(refs[reference['path']] == reference, 'conflicting nested receipt')
        else:
            check_receipts([reference]);refs[reference['path']] = reference
        return reference

    def document(reference):
        return read_json(checked(reference)['path'])

    def fixed(path, digest):
        return document(dict(path=str(path), sha256=digest))

    old = document(contract_ref)
    require(old['version'] == 'm4-pilot-v13' and len(old['runs']) == 16,
            'fixed original comparison identity differs')
    old_pins = {row['path']:row['sha256'] for row in old['source_files']}
    require(len(old_pins) == 948, 'original source population differs')
    archives = []
    for name, digest, count in (
        ('m4_v13_closed_v1', 'f393c5ab1786127c84b17fa5a35b4d95e370b616b172b1a3c2e8e4d2d0b21e58', 669),
        ('r22_readiness_command_pairing_closed_v1', '21385d3af80c3818b581475cbc26db3cb7c381d35eaf488fc394558365a34049', 673)):
        folder = EXPERIMENTS/'checkpoints'/name
        archive = fixed(folder/'manifest.json', digest)
        require(archive['archive_verified'] is True and archive['source_stable'] is True
                and archive['archive_members_verified'] == count and not archive['missing_paths'],
                'closed material archive incomplete')
        for filename, value in archive['artifacts'].items():
            checked(dict(path=str(folder/filename), sha256=value))
        archives.append(archive)
    v13_archive, r22_archive = archives

    def archived(path, archive):
        path = str(path)
        require(path in archive['evidence_files'], 'artifact absent from closed archive: '+path)
        return document(dict(path=path,sha256=archive['evidence_files'][path]))

    manifest_ref = checked(receipt(source_root/'before_manifest.json'))
    before = read_json(manifest_ref['path'])['sources_and_fixtures']
    fixture_ref = dict(path=str(source_root/'version_fixture_bridge.json'),
        sha256='20c8457e701097360a436a6b0f97080b0e152ba2b9e040f6ad8750d7abf2a608')
    fixture = document(fixture_ref)
    production = set(V13_ORCHESTRATION_PATHS)
    fixture_paths = {str(REPOSITORY/'ros2_ws/src/ros_esc/test'/name) for name in (
        *[f'test_m4_v{v}_versions.py' for v in (3,4,5,6,7,8,9,11,12,13)],
        'test_m4_v2_subreaper_routes.py','test_m4_v3_shutdown_routes.py')}
    require(len(production)==6 and len(fixture_paths)==12 and set(before)==production|fixture_paths,
            'source before-copy scope differs')
    require({row['path'] for row in fixture['files']} == fixture_paths
            and fixture['before_manifest'] == manifest_ref, 'fixture bridge scope differs')
    for row in fixture['files']:
        require(row['before_path'] == before[row['path']]['before_path']
                and row['before_sha256'] == before[row['path']]['before_sha256'],
                'fixture before identity differs')
        checked(dict(path=row['path'],sha256=row['after_sha256']))
    for path,row in before.items():
        checked(dict(path=row['before_path'],sha256=row['before_sha256']))
    evaluator = str(TOOLS/'evaluate_m4.py')
    r22_source_sha = 'f6369cdd6a3d659cab5f10997945945050e868140f91bfadd09aeb5f54f6765c'
    before_r22 = checked(dict(path=str(r22/'evaluate_m4.before_r22.py'),
        sha256=r22_archive['evidence_files'][str(r22/'evaluate_m4.before_r22.py')]))
    checked(dict(path=str(r22/'evaluator_change.patch'),
        sha256=r22_archive['evidence_files'][str(r22/'evaluator_change.patch')]))
    require(before_r22['sha256'] == old_pins[evaluator]
            and before[evaluator]['before_sha256'] == r22_source_sha
            and r22_archive['source_files']['docs/codex/gesc_gaussian/v2/tools/evaluate_m4.py'] == r22_source_sha,
            'V13-to-R22 evaluator bridge differs')
    navigation = str(REPOSITORY/'docs/codex/gesc_gaussian/v2/plan.md')
    current_permitted = {}

    def source_pin(path, digest):
        if raw_path(path):
            return  # Only inherited native references below; never open bag metadata.
        if path in production|fixture_paths:
            expected_before = before[path]['before_sha256']
            require(digest == expected_before or (path==evaluator and digest==old_pins[evaluator]),
                    'unapproved source history: '+path)
            current_permitted[path] = checked(receipt(path))['sha256']
        elif path == navigation:
            checked(dict(path=str(V13_SOURCE_ROOT/'closure_before/plan.md'),sha256=digest))
            current_permitted[path] = checked(receipt(path))['sha256']
        else:
            checked(dict(path=path,sha256=digest))

    for path,digest in old_pins.items():
        source_pin(path,digest)
    # The original prerequisite is immutable; do not call the old V13 verifier
    # against legitimately changed V14 fixtures. Its nested chain remains bound.
    prerequisite = old['trapping_integrated_prerequisite']
    for reference in prerequisite['receipts']:
        source_pin(reference['path'],reference['sha256'])

    ledger = archived(old_root/'acquisition/acquisition.json',v13_archive)
    require(ledger['contract']==contract_ref and ledger['status']=='INCOMPLETE'
            and ledger['failure']=='ValueError: M4 v13 usable development analysis: block science incomplete'
            and ledger['holdout_release'] is None and ledger['replacements_dispatched'] is False
            and not (old_root/'preflight/holdout_release.json').exists()
            and [r['status'] for r in ledger['slots']]==['COMPLETE']*4+['UNSTARTED']*12,
            'original failed ledger or unstarted population changed')
    execution = archived(V13_SOURCE_ROOT/'acquisition_execution_v1.json',v13_archive)
    require(execution['returncode']==1 and execution['error'] is None
            and 0<=execution['elapsed_sec']<=15800, 'original source/terminal execution failed')
    checked(execution['console']);checked(execution['release'])
    terminal = archived(V13_SOURCE_ROOT/'v13_terminal_cached_review_v1.json',v13_archive)
    require(terminal['status']=='PASS', 'original independent closure audit failed')
    report = archived(old_root/'report/report_receipt.json',v13_archive)
    require(report['status']=='REPORTED', 'original final report missing')
    checked(report['report']);checked(report['result'])
    require(ledger['final']['receipt']==refs[str(old_root/'report/report_receipt.json')],
            'original final report receipt differs')
    acquired, acquisition_refs, inherited_raw = [], [], []
    for index, recorded in enumerate(ledger['slots'][:4],1):
        reference=recorded['receipt'];saved=document(reference)
        require(reference['path']==str(old_root/f'acquisition/slot_{index}.json')
                and saved=={k:v for k,v in recorded.items() if k!='receipt'}
                and saved['integrity_passed'] is True and saved['runner_result']['recording_complete'] is True
                and all(saved.get(k)==old['runs'][index-1][k] for k in
                        ('slot','arm','run_id','case_id','seed','block','partition','condition','geometry','visible','experiment_version')),
                'original native acquisition differs')
        for cleanup in (saved['outer_cleanup'],saved['independent_inner_cleanup'],saved['runner_result']['cleanup']):
            require(cleanup['passed'] is True and cleanup['strict'] is True
                    and cleanup['inspection_performed'] is True and not cleanup['inspection_errors']
                    and not cleanup['remaining_owned_processes'] and not cleanup['remaining_session_processes']
                    and not cleanup['remaining_new_nodes'], 'original cleanup is not proven')
        deadline=saved['outer_process']['deadline_audit']
        require(saved['outer_process']['timed_out'] is False
                and deadline['owned_descendant_cleanup_proven'] is True
                and deadline['deadline_exhausted'] is False
                and saved['completed_monotonic']<=saved['case_deadline'], 'original case deadline failed')
        planned=old['runs'][index-1]
        checked(planned['geometry_receipt']);checked(planned['expected_cost_configuration'])
        checked(receipt(planned['summary_path']))
        native_summary=load_yaml(planned['summary_path'])
        require(native_summary['suite_id']=='m4_pilot_v13'
                and native_summary['source_path']==old['scenario']['path']
                and native_summary['selected_case_ids']==[planned['case_id']]
                and native_summary['runs']==[saved['runner_result']], 'original runner summary differs')
        for reference_input in saved['input_files']:
            if raw_path(reference_input['path']):
                st=Path(reference_input['path']).stat()
                inherited_raw.append({**reference_input,'stat':dict(size=st.st_size,mtime_ns=st.st_mtime_ns,ino=st.st_ino,dev=st.st_dev),
                    'sha256_origin':reference,'hash_recomputed':False,
                    'stat_basis':'first_v14_freeze_stat_baseline'})
            else:
                checked(reference_input)
        for configuration in saved['binding']['selected_configurations'].values():checked(configuration)
        if saved['runner_result'].get('captured_cost_configuration'):
            checked(saved['runner_result']['captured_cost_configuration'])
        acquired.append(recorded);acquisition_refs.append(reference)
    require([row['behavior_passed'] for row in acquired]==[False,True,True,True],
            'original observed A failure or enabled outcomes changed')
    block_ref=refs.get(str(analysis_root/'block_receipt.json')) or dict(
        path=str(analysis_root/'block_receipt.json'),sha256=v13_archive['evidence_files'][str(analysis_root/'block_receipt.json')])
    block=document(block_ref);summary=document(block['result'])
    require(block['block']==0 and block['complete'] is True and block['integrity_passed'] is True
            and block['cases']==acquisition_refs and block['scientific_analysis_complete'] is False
            and summary['contract']==contract_ref and summary['scientific_analysis_checks']==
                dict(four_arm_analysis_complete=False,both_reference_products_complete=True),
            'original complete jobs/partial science distinction changed')
    require(ledger['analysis_blocks']==[{**block,'receipt':checked(block_ref)}],
            'original ledger/block binding differs')
    require(len(block['jobs'])==4,'four original completed jobs required')
    for job,(name,stage,selector,number,cap) in zip(block['jobs'],(
        ('labels','labels','--block',0,240),('references_3','references','--slot',3,45),
        ('references_4','references','--slot',4,45),('summary','summary','--block',0,10))):
        saved=document(job['receipt'])
        require(job['receipt']['path']==str(analysis_root/(name+'_job.json'))
                and saved=={k:v for k,v in job.items() if k!='receipt'}
                and job['argv']==['/usr/bin/python3',evaluator,stage,'--contract',contract_ref['path'],selector,str(number)]
                and job['source']==dict(kind='script',path=evaluator,sha256=old_pins[evaluator])
                and all(job[k] is True for k in ('complete','integrity_passed','launched','clean_termination'))
                and job['return_code']==0 and job['timed_out'] is False
                and job['unexpected_observed_descendants'] is False and not job['remaining_owned_processes']
                and job['process_ownership_mode']=='subreaper_group_v3'
                and 0<=job['elapsed_wall_sec']<=job['cap_sec']<=cap
                and job['process_ownership']['kernel_proof']['complete'] is True,
                'original science process/invocation/source/cap differs')
        require(job['log_path']==str(analysis_root/(name+'.log')),'original job log path differs')
        checked(dict(path=job['log_path'],sha256=job['log_sha256']))
    labels=document(summary['labels'])
    require(labels['contract']==contract_ref and labels['complete'] is True and labels['integrity_passed'] is True
            and labels['input_files']==acquisition_refs,'original labels input binding differs')
    _verify_science_rows(old,summary['runs'],acquired)
    _verify_science_rows(old,labels['runs'],acquired)
    for row,labeled in zip(summary['runs'],labels['runs']):
        checked(row['labels'])
        metric_ref=checked(receipt(analysis_root/f'slot_{row["slot"]}_metrics.json'))
        require(read_json(metric_ref['path'])==labeled,'original metric/labels mismatch')
        if row['arm'] in ('C','D'):
            reference=next(r for r in summary['references'] if r['path']==str(analysis_root/f'slot_{row["slot"]}_references.json'))
            product=document(reference);checked(product['normalized_inputs'])
            require(product['normalized_inputs']==labeled['normalized_inputs']
                    and product['complete'] is True and product['integrity_passed'] is True
                    and product['direction_analysis_complete'] is True and product['contract']==contract_ref
                    and product['slot']==row['slot'] and product['run_id']==row['run_id']
                    and product['rows']==row['direction_rows'] and product['summary']==row['direction_summary']
                    and len(product['rows'])==24
                    and [r['offset_sec'] for r in product['rows']]==[15+30*k for k in range(24)],
                    'original direction product/24-target identity differs')

    capture=archived(r22/'capture/receipt.json',r22_archive)
    require(capture['status']=='COMPLETE' and capture['source_inputs_stable'] is True
            and capture['expected_sha256']==capture['after_sha256'] and len(capture['expected_sha256'])==144
            and capture['raw_stat_stable'] is True and not capture['subprocess_events']
            and capture['physical_scans_attempted']==capture['physical_scans_completed']==2,
            'R22 capture qualification changed')
    document(capture['prepared'])
    for reference in capture['outputs'].values():checked(reference)
    for path,digest in capture['expected_sha256'].items():source_pin(path,digest)
    capture_result=document(capture['outputs']['result.json'])
    capture_review=archived(r22/'capture_cached_review_v1.json',r22_archive)
    require(capture_result['structural_proof_passed'] is True and capture_review['status']=='PASS'
            and not capture_review['failed_checks'],'independent structural capture proof failed')
    raw_before=document(capture['outputs']['raw_stat_before.json'])
    raw_after=document(capture['outputs']['raw_stat_after.json'])
    require(raw_before==raw_after and len(raw_before)==2,'R22 raw stat proof differs')
    for item in inherited_raw:
        if item['path'] in raw_before:
            prior=raw_before[item['path']]
            require(item['stat']==dict(size=prior['size'],mtime_ns=prior['mtime_ns'],ino=prior['inode'],dev=prior['device']),
                    'C/D raw file stat changed since R22')
            recorded=next(r for r in capture_result['inherited_raw_files'] if r['path']==item['path'])
            require(recorded['sha256']==item['sha256'] and recorded['sha256_origin']==item['sha256_origin'],
                    'R22/native raw SHA provenance differs')
            item['stat_basis']='r22_capture_before_after_and_current_equal'
    focused=archived(r22/'focused_test_receipt.json',r22_archive)
    require(focused['status']=='PASS' and focused['terminal_exit_code']==0
            and focused['source_pins_stable'] is True and focused['source_pin_count']==7
            and focused['source_sha256']==r22_source_sha
            and {k:int(focused['pytest'][k]) for k in ('tests','errors','failures','skipped')}==
                dict(tests=91,errors=0,failures=0,skipped=0),'R22 focused validation failed')
    for name,digest in focused['files'].items():checked(dict(path=str(r22/name),sha256=digest))
    source_review=archived(r22/'source_review.json',r22_archive)
    require(source_review['status']=='PASS' and not source_review['defects']
            and source_review['root_verified_ast_outside_function_identical'] is True
            and source_review['source_sha256']==r22_source_sha,'R22 scope/default source review failed')
    component=archived(r22/'cached_component/receipt.json',r22_archive)
    result=fixed(r22/'cached_component/result.json','02e07e19c34fdb97716c4570037e046f4cf7709bc5a1b700c3afd04205dc28af')
    review=fixed(r22/'cached_component_review.json','26f04870988809a1160c550098fde24a1b370041b46be8ab5987bf2835b62a89')
    component_prepared=document(component['prepared'])
    require(component['status']==result['status']=='COMPLETE'
            and component['source_inputs_stable'] is True and component['expected_sha256']==component['after_sha256']
            and len(component['expected_sha256'])==179 and component['motion_owner_calls']==4 and component['bag_reads']==0
            and result['source_inputs_stable'] is True and not result['errors'] and not result['subprocess_events']
            and len(result['checks'])==11 and all(v is True for v in result['checks'].values())
            and review['status']=='PASS' and review['check_count']==len(review['checks'])==39
            and not review['failures'] and all(v is True for v in review['checks'].values())
            and review['result']==refs[str(r22/'cached_component/result.json')]
            and review['receipt']==refs[str(r22/'cached_component/receipt.json')]
            and review['prepared']==component['prepared'], 'R22 motion component/review qualification failed')
    require(component['expected_sha256']=={**component_prepared['expected_sha256'],
        component['prepared']['path']:component['prepared']['sha256']},'R22 prepared input population differs')
    for reference in component['outputs'].values():checked(reference)
    for path,digest in component['expected_sha256'].items():source_pin(path,digest)
    component_execution=archived(r22/'component_execution.json',r22_archive)
    require(component_execution['status']=='COMPLETE' and component_execution['terminal_exit_code']==0
            and 0<=component_execution['elapsed_sec']<=30
            and component_execution['command']==component_prepared['command']
            and component_execution['result_sha256']==refs[str(r22/'cached_component/result.json')]['sha256']
            and component_execution['receipt_sha256']==refs[str(r22/'cached_component/receipt.json')]['sha256'],
            'R22 component terminal/finite command differs')
    selected_motion={}
    for slot in (3,4):
        default=document(component['outputs'][f'slot_{slot}_default.json'])
        selected_ref=component['outputs'][f'slot_{slot}_selected.json'];selected=document(selected_ref)
        require(default==labels['runs'][slot-1]['mandatory_stop_evidence']
                and selected['status']=='OBSERVED_CONTINUOUS_ACQUISITION'
                and selected['analysis_complete'] is True and selected['command_pairing_complete'] is True
                and type(selected['mandatory_stopped_acquisitions']) is int and selected['mandatory_stopped_acquisitions']==0
                and selected['command_pairing_scope']=='full_publication_order_v1', 'R22 default parity/selected qualification differs')
        if slot==3:
            require(all(selected.get(k)==v for k,v in default.items() if k!='command_pairing_scope'),
                    'C original motion fields changed')
        selected_motion[str(slot)]=selected_ref
    return dict(policy='v13_development_r22_motion_v1',status='PASS',source_contract=contract_ref,
        source_slots=[1,2,3,4],source_acquisitions=acquisition_refs,source_summary=block['result'],
        source_block=checked(block_ref),selected_motion=selected_motion,
        receipts=[refs[path] for path in sorted(refs)],inherited_raw_files=inherited_raw,
        source_binding=dict(before_manifest=manifest_ref,fixture_bridge=fixture_ref,
            current_permitted_sha256=dict(sorted(current_permitted.items())),
            original_source_count=len(old_pins),r22_component_source_count=179,
            raw_sha_scope='Inherited native hashes; no raw or bag-metadata reads. A/B and metadata stats first frozen here; C/D DB3 stats also equal R22 baseline.'),
        trapping_integrated_prerequisite=deepcopy(prerequisite))


def _load_v14_reuse(contract):
    if not is_retained_development_experiment_version(contract.get('version')):
        raise ValueError('retained development requires the exact V14 comparison')
    selection = contract.get('retained_development', {})
    reference = selection.get('reuse_receipt', {})
    expected_path = Path(contract['root'])/'preflight/retained_development.json'
    if reference.get('path') != str(expected_path.resolve()):
        raise ValueError('V14 retained receipt path differs')
    check_receipts([reference])
    saved = read_json(reference['path'])
    if (saved != _v14_retained_development_binding()
            or any(selection.get(key) != saved.get(key)
                   for key in ('policy', 'source_contract', 'source_slots'))):
        raise ValueError('V14 retained evidence or source bridge changed')
    return saved


def _check_v14_receipts(contract, references):
    """Check ordinary files; old raw content hashes retain their stated provenance."""
    selection = contract['retained_development']
    check_receipts([selection['reuse_receipt']])
    saved = read_json(selection['reuse_receipt']['path'])
    inherited = {row['path']: row for row in saved['inherited_raw_files']}
    ordinary = []
    for ref in references:
        if ref['path'] not in inherited:
            ordinary.append(ref)
            continue
        original = inherited[ref['path']]
        observed = Path(ref['path']).stat()
        stat = dict(size=observed.st_size, mtime_ns=observed.st_mtime_ns,
                    ino=observed.st_ino, dev=observed.st_dev)
        if ref['sha256'] != original['sha256'] or stat != original['stat']:
            raise ValueError('V14 inherited raw receipt/stat changed')
    return check_receipts(ordinary)


def _v14_development_document(contract, reuse):
    from ros_esc.plotting_scripts.m4_pilot import experiment_fields
    check_receipts([reuse['source_summary'], *reuse['selected_motion'].values()])
    source = read_json(reuse['source_summary']['path'])
    motion = {int(slot): read_json(ref['path']) for slot, ref in reuse['selected_motion'].items()}
    result = _compose_v14_development(source, motion)
    result.update(**experiment_fields(contract['version']), contract=receipt(contract['contract_path']),
                  source_development=reuse['source_summary'],
                  retained_development=contract['retained_development']['reuse_receipt'])
    return result


def _verify_v14_development_science(contract, acquired, block, development):
    """Validate a new view of authenticated old measurements before fresh work."""
    from ros_esc.plotting_scripts.m4_pilot import (
        direction_product_complete, integrated_method_run_checks,
    )
    reuse = _load_v14_reuse(contract)
    expected = _v14_development_document(contract, reuse)
    if (development != expected or acquired != [
            {**read_json(ref['path']), 'receipt': ref} for ref in reuse['source_acquisitions']]):
        raise ValueError('V14 development view changed fields outside qualified motion composition')
    if (block.get('scientific_analysis_complete') is not True
            or development.get('scientific_analysis_complete') is not True
            or any(set(row['scientific_analysis_checks']) != V14_ROW_CHECKS
                   or not all(value is True for value in row['scientific_analysis_checks'].values())
                   for row in development['runs'])):
        raise ValueError('V14 usable development measurements are incomplete')
    if (block.get('jobs') != [] or block.get('acquisition_origin') != 'retained_v13'
            or block.get('source_block') != reuse['source_block']
            or block.get('retained_development') != contract['retained_development']['reuse_receipt']):
        raise ValueError('V14 cached block misrepresents inherited scientific work')
    for row in development['runs'][2:]:
        if not direction_product_complete(row.get('direction_rows', []), row):
            raise ValueError('V14 requires both complete 24-target direction products')
    enabled = [row['slot'] for row in development['runs'] if row['arm'] in ('B', 'D')
               and row.get('combined_sequence_passed') is True
               and row.get('arrival_passed') is True
               and row.get('arrival_measurement_complete') is True]
    if enabled != [2, 4]:
        raise ValueError('V14 requires both B and D recovery through global arrival')
    d = development['runs'][3]
    checks = integrated_method_run_checks(d)
    if checks['status'] != 'PASS' or d.get('direction_summary') != checks['direction_summary']:
        raise ValueError('V14 D integrated arrival/continuous/direction gates failed or unavailable')
    return dict(policy=experiment_release_policy(contract['version']),
        scientific_analysis_complete=True, enabled_arrival_slots=enabled,
        continuous_development_slot=4, integrated_D_checks=checks,
        retained_development=contract['retained_development']['reuse_receipt'],
        nested_receipts=[contract['retained_development']['reuse_receipt'],
                         reuse['source_summary'], reuse['source_block'], *reuse['source_acquisitions']])


def prepare_retained_development(contract, *, absolute_deadline):
    """One bounded cached composition job; it issues no dispatch release."""
    if time.monotonic() >= absolute_deadline:
        raise TimeoutError('V14 cached development deadline exhausted')
    verify_frozen(contract)
    reuse = _load_v14_reuse(contract)
    output = Path(contract['root'])/'analysis/block_0'
    output.mkdir(parents=True, exist_ok=False)
    began = time.monotonic()
    atomic_exclusive_json(output/'cached_started.json', dict(status='INCOMPLETE',
        contract=receipt(contract['contract_path']), absolute_deadline=absolute_deadline,
        retained_development=contract['retained_development']['reuse_receipt']))
    acquired = [{**read_json(ref['path']), 'receipt': ref} for ref in reuse['source_acquisitions']]
    _verify_cases(contract, acquired, range(1, 5))
    result = _v14_development_document(contract, reuse)
    atomic_exclusive_json(output/'result.json', result)
    block = dict(block=0, complete=True, integrity_passed=True,
        scientific_analysis_complete=result['scientific_analysis_complete'],
        result=receipt(output/'result.json'), cases=[row['receipt'] for row in acquired],
        jobs=[], acquisition_origin='retained_v13', source_block=reuse['source_block'],
        retained_development=contract['retained_development']['reuse_receipt'],
        elapsed_sec=time.monotonic()-began, absolute_deadline=absolute_deadline)
    # Save the observed disposition even when a release requirement fails.
    atomic_exclusive_json(output/'block_receipt.json', block)
    evidence = _verify_v14_development_science(contract, acquired, block, result)
    verify_frozen(contract)
    if time.monotonic() >= absolute_deadline:
        raise TimeoutError('V14 cached development inclusive deadline exceeded')
    qualified = dict(status='QUALIFIED', contract=receipt(contract['contract_path']),
        block=receipt(output/'block_receipt.json'), development_evidence=evidence,
        elapsed_sec=time.monotonic()-began, no_new_acquisition=True,
        no_scientific_replay=True, dispatch_released=False)
    atomic_exclusive_json(output/'cached_qualification.json', qualified)
    return {**qualified, 'receipt': receipt(output/'cached_qualification.json')}


def load_retained_development(contract, suite_end):
    """Read the independently reviewable cached result for the sole dispatcher."""
    if time.monotonic() >= suite_end:
        raise TimeoutError('V14 retained loading exhausted the suite deadline')
    reuse = _load_v14_reuse(contract)
    output = Path(contract['root'])/'analysis/block_0'
    qualified = read_json(output/'cached_qualification.json')
    block = read_json(output/'block_receipt.json')
    if (qualified.get('status') != 'QUALIFIED'
            or qualified.get('contract') != receipt(contract['contract_path'])
            or qualified.get('block') != receipt(output/'block_receipt.json')):
        raise ValueError('V14 cached development was not qualified for this contract')
    check_receipts([block['result'], *block['cases']])
    rows = [{**read_json(ref['path']), 'receipt': ref} for ref in reuse['source_acquisitions']]
    result = read_json(block['result']['path'])
    evidence = _verify_v14_development_science(contract, rows, block, result)
    if qualified.get('development_evidence') != evidence:
        raise ValueError('V14 cached qualification differs from retained evidence')
    return rows, {**block, 'receipt': receipt(output/'block_receipt.json')}


def _v12_component_response_binding(*, r21_source_bridge=False):
    """Verify the adopted component receipts and unchanged method, without replay."""
    refs = {}

    def document(path, expected):
        ref = {'path': str(Path(path).resolve()), 'sha256': expected}
        check_receipts([ref]); refs[ref['path']] = ref
        return read_json(path)

    def require(condition, reason):
        if not condition:
            raise ValueError('M4 v12 R10 prerequisite: ' + reason)

    decision = document(R10_ROOT / 'decision.json', R10_DECISION_SHA256)
    keys = {'adapter_checks_pass', 'all_execution_complete', 'all_independent_reviews_pass',
        'new_detector_empirical_advantage_beyond_resolution', 'new_detector_finite_reliability_pass',
        'new_detector_lower_full_positive_capped_median', 'paired_empirical_analysis_complete',
        'paired_synthetic_analysis_complete'}
    require(decision.get('status') == 'PASS' and set(decision.get('criteria', {})) == keys
        and all(value is True for value in decision['criteria'].values()), 'eight passing criteria required')
    names = ('checks/result.json', 'empirical/result.json', 'synthetic/result.json',
        'synthetic/receipt.json', 'helper_review.json', 'empirical_review.json',
        'synthetic_review.json', 'execution_checks.json', 'execution_empirical.json',
        'execution_synthetic.json')
    require(set(decision.get('inputs_sha256', {})) == {str(R10_ROOT / name) for name in names},
            'selected decision input population differs')
    documents = {name: document(R10_ROOT / name, decision['inputs_sha256'][str(R10_ROOT / name)])
                 for name in names}
    archive = document(R10_ARCHIVE, R10_ARCHIVE_SHA256)
    require(archive.get('archive_verified') is True and archive.get('source_stable') is True,
            'material archive was not verified')
    prepared = []
    for job, cap in (('checks', 60), ('empirical', 120), ('synthetic', 180)):
        execution = documents['execution_' + job + '.json']
        require(execution.get('job') == job and execution.get('returncode') == 0
            and execution.get('error') is None
            and all(execution.get(key) is True for key in ('source_stable', 'terminal_reaped',
                'prepared_stable', 'within_inclusive_budget'))
            and execution.get('inclusive_limit_sec') == cap
            and type(execution.get('elapsed_sec')) in (int, float)
            and 0 <= execution['elapsed_sec'] <= cap, 'completed finite ' + job + ' job required')
        item = document(R10_ROOT / ('prepared_' + job + '.json'), execution['prepared_sha256'])
        require(item.get('job') == job and item.get('command') == execution.get('command'),
                'prepared invocation differs')
        prepared.append(item)
    require(all(documents[name].get('status') == 'PASS' for name in
        ('checks/result.json', 'helper_review.json', 'empirical_review.json', 'synthetic_review.json')),
        'focused checks or independent review failed')
    require(documents['empirical/result.json'].get('status') == 'COMPLETE'
        and documents['empirical/result.json'].get('source_inputs_stable') is True
        and documents['synthetic/result.json'].get('status') == 'COMPLETE'
        and documents['synthetic/receipt.json'].get('status') == 'COMPLETE'
        and documents['synthetic/receipt.json'].get('source_inputs_stable') is True,
        'paired component analysis incomplete')
    base = prepared[0]
    for item in prepared[1:]:
        require(all(item.get(key) == base.get(key) for key in
            ('detector_parameters', 'history_parameters', 'parameter_origin_path', 'synthetic_ready')),
            'captured method configuration differs across component jobs')
    origin = base['parameter_origin_path']
    origin_ref = {'path': origin, 'sha256': base['expected_sha256'][origin]}
    require(all(item['expected_sha256'].get(origin) == origin_ref['sha256'] for item in prepared),
            'parameter origin binding differs')
    check_receipts([origin_ref]); refs[origin] = origin_ref
    ready_ref = base['synthetic_ready']
    require(ready_ref['path'] == str(R10_ROOT / 'synthetic_ready.json'), 'cached method identity path differs')
    ready = document(ready_ref['path'], ready_ref['sha256'])
    method_paths = [REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc' / name for name in (
        'convergence_detector_node/recurrent_geometry.py', 'convergence_detector_node/recurrent_contract.py',
        'convergence_detector_node/centroid_windows.py', 'convergence_detector_node/centroid_contract.py',
        'convergence_detector_node/convergence_detector_node_script.py',
        'pde_history_node/pde_history_script.py', 'search_epoch.py', 'v2_lifecycle.py')]
    for path in method_paths:
        key = str(path)
        digest = base['expected_sha256'][key]
        require(all(item['expected_sha256'].get(key) == digest for item in prepared),
                'method source differs across component jobs')
        if key in ready['cache_identity']['core_dependency_sha256']:
            require(ready['cache_identity']['core_dependency_sha256'][key] == digest,
                    'reused recurrent core differs from original cache')
        old_copy = {'recurrent_contract.py': 'recurrent_contract.py.detector_before',
                    'v2_lifecycle.py': 'v2_lifecycle.py.trapping_before'}.get(path.name)
        ref = {'path': str(R21_ROOT / old_copy) if r21_source_bridge and old_copy else key,
               'sha256': digest}
        check_receipts([ref]); refs[ref['path']] = ref
        if r21_source_bridge and path.name == 'recurrent_contract.py':
            require(path.read_bytes().startswith(Path(ref['path']).read_bytes()),
                    'R10 recurrent contract prefix changed')
    for name in ('adapter.py', 'adapter_checks.py', 'empirical.py', 'synthetic.py',
                 'prepare.py', 'run_job.py', 'empirical_ready.json', 'decide.py'):
        key = str(R10_ROOT / name)
        digest = (decision['decision_helper_sha256'] if name == 'decide.py'
                  else base['expected_sha256'][key])
        ref = {'path': key, 'sha256': digest}
        check_receipts([ref]); refs[key] = ref
    launch = REPOSITORY / 'ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml'
    launch_ref = {'path': str(launch), 'sha256': archive['source_files'][str(launch.relative_to(REPOSITORY))]}
    if r21_source_bridge:
        # The exact old launch remains in the verified R10 source archive; the
        # new launch is separately bound to the completed D02 runtime below.
        source_archive = R10_ARCHIVE.parent / 'source.tar.gz'
        ref = {'path': str(source_archive), 'sha256': archive['artifacts']['source.tar.gz']}
        check_receipts([ref]); refs[ref['path']] = ref
        launch_ref = receipt(launch)
    check_receipts([launch_ref]); refs[str(launch)] = launch_ref
    for key, ref in refs.items():
        if Path(key).is_relative_to(R10_ROOT):
            require(archive['evidence_files'].get(key) == ref['sha256'], 'archive/evidence binding differs')
    check_receipts(list(refs.values()))
    binding = dict(policy='component_response_integrated_arrival_v1', status='PASS',
        decision=refs[str(R10_ROOT / 'decision.json')], archive=refs[str(R10_ARCHIVE)],
        detector_parameters=base['detector_parameters'], history_parameters=base['history_parameters'],
        recurrent_config_fields=ready['cache_identity']['recurrent_config_fields'],
        launch=launch_ref, receipts=sorted(refs.values(), key=lambda ref: ref['path']),
        scope='Selected completed component receipt chain and current method/configuration; raw inputs and large timelines remain bound by original completed receipts')
    if r21_source_bridge:
        binding.update(scope='Completed R10 component evidence; unchanged numerical detector sources and exact old contract prefix. R21 lifecycle and launch changes require the separate completed D02 binding.',
            archived_launch_sha256=archive['source_files'][str(launch.relative_to(REPOSITORY))])
    return binding


def _v13_trapping_integrated_binding():
    """Bind the closed R21/D02 chain without reading bags or replaying science."""
    archive_ref = {'path': str(D02_ARCHIVE), 'sha256': D02_ARCHIVE_SHA256}
    check_receipts([archive_ref])
    archive = read_json(D02_ARCHIVE)
    refs = {str(D02_ARCHIVE): archive_ref}

    def require(condition, reason):
        if not condition:
            raise ValueError('M4 v13 R21/D02 prerequisite: ' + reason)

    def document(path):
        path = str(path)
        require(path in archive['evidence_files'], 'missing archived receipt: ' + path)
        ref = {'path': path, 'sha256': archive['evidence_files'][path]}
        check_receipts([ref]); refs[path] = ref
        return read_json(path)

    def complete_flags(flags):
        return isinstance(flags, dict) and bool(flags) and all(value is True for value in flags.values())

    require(archive.get('archive_verified') is True and archive.get('source_stable') is True
            and archive.get('archive_members_verified') == 661, 'material archive incomplete')
    # These are immutable completed receipts. Their historical source maps are
    # not claims that later authorized orchestration edits already existed.
    for path in (R21_ROOT/'focused_execution.json', R21_ROOT/'interface_build.json',
                 D02_ROOT/'source_validation.json'):
        data = document(path)
        require(data.get('returncode') == 0 and data.get('source_stable') is True
                and data.get('expected_sha256') == data.get('after_sha256')
                and bool(data.get('expected_sha256')), 'source/interface validation incomplete')
    document(R21_ROOT/'focused_prepared.json')
    require(document(R21_ROOT/'focused_execution.json')['prepared_sha256'] ==
            refs[str(R21_ROOT/'focused_prepared.json')]['sha256'], 'focused preparation differs')
    retained = document(R21_ROOT/'retained_component/result.json')
    require(retained.get('status') == 'COMPLETE' and retained.get('errors') == []
            and retained.get('source_inputs_stable') is True and retained.get('candidate_passed') is True
            and complete_flags(retained.get('decision_checks')) and len(retained.get('rows', [])) == 8
            and retained.get('proposal_calls') == 4, 'four-D retained component incomplete')
    execution = document(R21_ROOT/'retained_execution.json')
    document(R21_ROOT/'retained_prepared.json')
    require(execution.get('returncode') == 0 and 0 <= execution['elapsed_sec'] <= 90
            and execution['prepared_sha256'] == refs[str(R21_ROOT/'retained_prepared.json')]['sha256'],
            'retained finite execution differs')
    review = document(R21_ROOT/'cached_review_v4.json')
    review_receipt = document(R21_ROOT/'cached_review_v4_receipt.json')
    require(review.get('status') == 'PASS' and review.get('errors') == []
            and review.get('source_inputs_stable') is True and review.get('legacy_uninformative') == 8
            and review_receipt.get('status') == 'PASS'
            and review_receipt.get('scientific_result') == refs[str(R21_ROOT/'retained_component/result.json')]
            and review_receipt.get('result') == refs[str(R21_ROOT/'cached_review_v4.json')],
            'retained independent review incomplete')
    preservation = document(R21_ROOT/'r10_source_preservation.json')
    require(preservation.get('passed') is True, 'R10 source preservation failed')

    prepared = document(D02_ROOT/'prepared.json')
    run_id = 'v2_method_development_D_20260911_r21_02'
    require(prepared.get('run_id') == run_id
            and prepared.get('environment') == str(R21_ROOT/'runtime_environment.sh')
            and prepared.get('arrival_binding_method') == 'recorded_pose_arrival_v1'
            and prepared.get('state_duration_basis') == 'simulation_publication_v1', 'D02 selection differs')
    old_sources = prepared['source_files']
    prepared_orchestration = {path for path in V13_ORCHESTRATION_PATHS
                             if Path(path).is_relative_to(REPOSITORY/'ros2_ws/src')}
    require(len(old_sources) == 607 and V13_ORCHESTRATION_PATHS.intersection(old_sources) == prepared_orchestration,
            'D02 prepared source population differs')
    fixture_ref = receipt(V13_SOURCE_ROOT/'version_fixture_bridge.json')
    require(fixture_ref['sha256'] == V13_FIXTURE_BRIDGE_SHA256, 'declared version-fixture bridge changed')
    fixtures = read_json(fixture_ref['path'])['files']
    require(set(fixtures) == V13_FIXTURE_PATHS, 'declared version-fixture population differs')
    refs[fixture_ref['path']] = fixture_ref
    for path, item in fixtures.items():
        before = str(V13_SOURCE_ROOT/'before'/Path(path).relative_to(REPOSITORY))
        require(item['before_path'] == before and old_sources.get(path) == item['before_sha256'],
                'version fixture differs from D02 source')
        for ref in ({'path': before, 'sha256': item['before_sha256']},
                    {'path': path, 'sha256': item['after_sha256']}):
            check_receipts([ref]); refs[ref['path']] = ref
    preserved = [{'path': path, 'sha256': digest} for path, digest in old_sources.items()
                 if path not in V13_ORCHESTRATION_PATHS | V13_FIXTURE_PATHS]
    check_receipts(preserved)
    refs.update((ref['path'], ref) for ref in preserved)
    attempt = document(D02_ROOT/'attempt_result.json')
    require(attempt.get('run_id') == run_id and attempt.get('source_stable') is True
            and attempt.get('within_root_deadline') is True
            and attempt.get('prepared_sha256') == refs[str(D02_ROOT/'prepared.json')]['sha256'],
            'D02 acquisition/preparation binding differs')
    runs = attempt['summary']['runs']
    require(len(runs) == 1 and runs[0]['run_id'] == run_id and runs[0].get('recording_complete') is True
            and runs[0]['classification'].get('passed') is True
            and len(runs[0]['classification'].get('predicate_results', {})) == 11
            and complete_flags(runs[0]['classification']['predicate_results'])
            and all(owner.get('passed') is True and owner.get('strict') is True for owner in
                    (runs[0]['cleanup'], attempt['outer_cleanup'])), 'D02 acquisition or cleanup incomplete')
    state = document(D02_ROOT/'cached_state_component/result.json')
    require(state.get('status') == 'COMPLETE' and state.get('errors') == []
            and state.get('source_inputs_stable') is True and complete_flags(state.get('checks')),
            'publication-clock component incomplete')
    analysis = document(D02_ROOT/'analysis_v1/receipt.json')
    require(analysis.get('analysis_complete') is True and analysis.get('analyzer_status') == 'complete'
            and analysis.get('errors') == [] and analysis.get('source_inputs_stable') is True
            and {key: analysis['acquisition_prepared'][key] for key in ('path', 'sha256')} == refs[str(D02_ROOT/'prepared.json')]
            and analysis['acquisition_prepared'].get('recorded_source_files') == old_sources
            and complete_flags(analysis.get('measurement_checks'))
            and [row['owner'] for row in analysis['physical_scans']] == ['analysis.read_run_bag', 'validate_run._read_bag']
            and all(row['status'] == 'COMPLETE' for row in analysis['physical_scans']), 'native analysis incomplete')
    measured = document(D02_ROOT/'analysis_v1/motion_arrival_development.json')
    motion, arrival = measured['motion'], measured['arrival']
    require(arrival.get('arrival_passed') is True and arrival.get('arrival_measurement_complete') is True
            and arrival.get('arrival_binding_method') == 'recorded_pose_arrival_v1'
            and motion.get('status') == 'OBSERVED_CONTINUOUS_ACQUISITION'
            and type(motion.get('mandatory_stopped_acquisitions')) is int
            and motion['mandatory_stopped_acquisitions'] == 0
            and all(motion.get(key) is True for key in ('analysis_complete', 'command_pairing_complete', 'authority_complete')),
            'D02 arrival or continuous acquisition unavailable')
    reference = document(D02_ROOT/'direction_reference_v1/receipt.json')
    product = document(D02_ROOT/'direction_reference_v1/result.json')['result']
    require(reference.get('source_inputs_stable') is True and reference.get('run_id') == run_id
            and reference.get('summary') == product['summary'] and product['summary'].get('status') == 'PASS'
            and product['summary']['counts']['scheduled'] == 24 and len(product['rows']) == 24,
            'D02 direction product incomplete or failed')
    for name, cap in (('execution.json', 720), ('analysis_execution_v1.json', 120),
                      ('direction_reference_execution_v1.json', 45)):
        data = document(D02_ROOT/name)
        require(data.get('returncode') == 0 and 0 <= data['elapsed_sec'] <= cap,
                'D02 finite execution failed: ' + name)
    review = document(D02_ROOT/'cached_complete_review_v1.json')
    reviewed = document(D02_ROOT/'cached_complete_review_receipt_v1.json')
    require(review.get('status') == 'PASS' and review.get('run_id') == run_id
            and len(review.get('checks', {})) == 34 and complete_flags(review['checks'])
            and review.get('principal_input_sha256_before') == review.get('principal_input_sha256_after')
            and reviewed.get('status') == 'PASS'
            and {key: reviewed['result'][key] for key in ('path', 'sha256')} ==
                refs[str(D02_ROOT/'cached_complete_review_v1.json')], 'D02 independent review incomplete')
    component = _v12_component_response_binding(r21_source_bridge=True)
    refs.update((ref['path'], ref) for ref in component['receipts'])
    check_receipts(list(refs.values()))
    return dict(policy=experiment_release_policy(V13_EXPERIMENT_VERSION), status='PASS',
        component_response=component, archive=archive_ref,
        development_prepared=refs[str(D02_ROOT/'prepared.json')],
        development_review=refs[str(D02_ROOT/'cached_complete_review_v1.json')],
        permitted_orchestration_changes=sorted(V13_ORCHESTRATION_PATHS),
        version_fixture_bridge=fixture_ref,
        receipts=sorted(refs.values(), key=lambda ref: ref['path']),
        scope='Completed R10/R21/D02 evidence and preserved scientific/runtime/helper sources; six prospectively authorized V13 orchestration owners are frozen separately. No scientific replay or raw bag read.')


def _verify_v12_method_configuration(contract, binding):
    """Check the effective scalar overrides through the unchanged launch owner."""
    import xml.etree.ElementTree as ET
    defaults = {arg.attrib['name']: arg.attrib['default']
                for arg in ET.parse(binding['launch']['path']).getroot().findall('arg')
                if 'default' in arg.attrib}
    mapping = dict(omega='pde_omega', threshold='convergence_threshold',
        decay_rate='convergence_decay_rate', min_fill_periods='convergence_min_fill_periods',
        state_gating_enabled='convergence_state_gating_enabled',
        minimum_path_length_m='convergence_minimum_path_length_m',
        maximum_path_efficiency='convergence_maximum_path_efficiency',
        convergence_confirmation_policy='convergence_confirmation_policy',
        convergence_confirmation_dwell_sec='convergence_confirmation_dwell_sec',
        convergence_confirmation_exit_threshold_scale='convergence_confirmation_exit_threshold_scale',
        algorithm_profile='algorithm_profile',
        robust_search_epoch_reset_enabled='robust_search_epoch_reset_enabled')
    parameters = {**binding['detector_parameters'],
        'robust_search_epoch_reset_enabled': binding['history_parameters']['robust_search_epoch_reset_enabled']}
    for row in contract['runs']:
        # Includes runner-owned values such as algorithm_profile; verify_frozen
        # independently reconstructs this argv through build_launch_command.
        controls = dict(value.split(':=', 1) for value in row['launch_argv'] if ':=' in value)
        for key, argument in mapping.items():
            expected = parameters[key]
            actual = controls.get(argument, defaults.get(argument))
            if type(expected) is bool:
                equal = actual is expected or type(actual) is str and actual.lower() == str(expected).lower()
            elif type(expected) in (int, float):
                equal = not isinstance(actual, bool) and float(actual) == expected
            else:
                equal = actual == expected
            if not equal:
                raise ValueError('M4 v12 R10 selected method configuration differs: ' + argument)
        gap = controls.get('centroid_maximum_gap_sec', defaults['centroid_maximum_gap_sec'])
        if float(gap) != float(binding['recurrent_config_fields']['max_gap_seconds']):
            raise ValueError('M4 v12 R10 recurrent source-gap configuration differs')


def collect_sources(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    names = subprocess.check_output([
        'git', '-C', str(REPOSITORY), 'ls-files', '--cached', '--others',
        '--exclude-standard', '-z', 'ros2_ws/src', 'extremum-seeking/src',
    ]).split(b'\0')
    paths = {REPOSITORY / name.decode() for name in names if name}
    paths.update(TOOLS.glob('*.py'))
    paths.update(REPOSITORY / 'docs/codex/gesc_gaussian/v2' / name for name in (
        'plan.md', 'm4_plan.md', 'm4_execution_evaluation_plan.md',
        'q7_two_block_method_plan.md', 'validation/m4_prerequisite_audit.md',
        'm4_implementation_clarifications.md', 'm4_v2_recovery_plan.md',
        'm4_v3_recorder_shutdown_plan.md',
        'm4_v4_confirmation_mirror_plan.md',
        'm4_v5_moving_fill_plan.md',
        'm4_v5_primary_topology_amendment.md',
        'm4_v6_centroid_heartbeat_plan.md',
        'm4_v6_matched_gain_plan.md',
        'm4_v7_recording_clock_range_plan.md',
        'm4_v7_clock_range_comparison_plan.md',
        'm4_v8_stationary_causality_plan.md',
        'm4_v8_stationary_causality_comparison_plan.md',
        'm4_v9_budget_comparison_plan.md',
    ))
    paths.update(Path(path) for path in (
        '/opt/ros/humble/lib/libgazebo_ros_diff_drive.so',
        '/opt/ros/humble/lib/gazebo_ros/spawn_entity.py',
        '/opt/ros/humble/share/gazebo_msgs/srv/SpawnEntity.srv',
        '/opt/ros/humble/lib/python3.10/site-packages/ros2run/api/__init__.py',
    ))
    if is_arrival_experiment_version(experiment_version):
        paths.update(REPOSITORY / 'docs/codex/gesc_gaussian/v2' / name for name in (
            'm4_v10_arrival_comparison_plan.md', 'method_development_20260910.md',
            'global_arrival_acceptance_20260910.md', 'r4_stationary_integrated_handoff.md',
            'r4_stationary_recurrent_pairing_plan.md', 'r4_stationary_integrated_02_plan.md',
            'r4_stationary_analysis_02_plan.md', 'r4_frozen_component_confirmation_plan.md',
            'r2_recurrent_detector_runtime_plan.md', 'r2_centered_verification_runtime_plan.md',
            'r2_centered_guidance_revision_plan.md',
            'validation/r4_stationary_recurrent_pairing.md',
            'validation/r4_stationary_integrated_02.md',
            'validation/r4_frozen_component_confirmation.md'))
        paths.update(Path(ref['path']) for ref in _runtime_binding(experiment_version)['files'])
        installed = installed_entry_points(expected_build=BUILD)
        paths.update(Path(ref['path']) for ref in installed['metadata_files'])
        paths.update(Path(entry[key]['path']) for entry in installed['entry_points']
                     for key in ('wrapper', 'module'))
    if is_retained_development_experiment_version(experiment_version):
        binding = _v14_retained_development_binding()
        paths.update(Path(ref['path']) for ref in binding['receipts'])
        paths.update(REPOSITORY/'docs/codex/gesc_gaussian/v2'/name for name in (
            'm4_v14_retained_development_comparison_plan.md',
            'm4_v13_integrated_comparison_plan.md', 'm4_v13_handoff.md',
            'r22_readiness_command_pairing_plan.md', 'r22_readiness_command_pairing_handoff.md',
            'validation/r22_readiness_command_pairing.md'))
        return [receipt(path) for path in sorted(paths) if path.is_file()]
    if experiment_version in (V11_EXPERIMENT_VERSION, V12_EXPERIMENT_VERSION, V13_EXPERIMENT_VERSION):
        required = {REPOSITORY / 'docs/codex/gesc_gaussian/v2' / name for name in (
            'm4_v11_draft_plan.md', 'r5_centered_commit_handoff_plan.md',
            'r6_verification_expiry_plan.md', 'r7_approach_feasibility_plan.md',
            'r7_approach_runtime_plan.md', 'r7_visible_c03_plan.md',
            'r8_pde_evaluator_timestamp_plan.md',
            'validation/r5_centered_commit_handoff.md',
            'validation/r6_verification_expiry.md', 'validation/r7_approach_feasibility.md',
            'validation/r7_approach_runtime.md', 'validation/r7_visible_c03.md',
            'validation/r8_pde_evaluator_timestamp.md')}
        required.update(V10_DEVELOPMENT / name for name in (
            'r5_validation_v1/focused_v1/source_validation.json',
            'r6_validation_v1/focused_v1/source_validation.json',
            'r7_runtime_validation_v1/focused_v1/source_validation.json',
            'r8_pde_evaluator_v1/focused_v1/source_validation.json',
            'visible_integrated_C_03/prepared.json',
            'visible_integrated_C_03/attempt_result.json',
            'visible_integrated_C_03/analysis_v1/receipt.json',
            'visible_integrated_C_03/direction_reference_v1/receipt.json',
            'visible_integrated_C_03/startup_validation_v1/source_validation.json',
            'r8_pde_evaluator_v1/cached_c03_v1/receipt.json',
            'r8_pde_evaluator_v1/cached_c03_v1/result.json',
            'm4_v11_source_v1/validate_source.py', 'm4_v11_source_v1/tests_v1.json',
            'm4_v11_source_v1/save_source_checkpoint.py',
            'm4_v11_source_v1/prepare_once.py', 'm4_v11_source_v1/archive_preparation.py',
            'm4_v11_source_v1/release_dispatch.py', 'm4_v11_source_v1/acquire_once.py'))
        missing = sorted(str(path) for path in required if not path.is_file())
        if missing:
            raise ValueError('M4 v11 prerequisite source/evidence missing: ' + ', '.join(missing))
        paths.update(required)
    if is_integrated_arrival_experiment_version(experiment_version):
        required = {REPOSITORY / 'docs/codex/gesc_gaussian/v2' / name for name in (
            'm4_v12_integrated_comparison_plan.md', 'r9_motion_readiness_plan.md',
            'r9_motion_readiness_handoff.md', 'validation/r9_motion_readiness.md',
            'r10_paired_response_plan.md', 'r10_paired_response_handoff.md',
            'validation/r10_paired_response.md')}
        required.update(V10_DEVELOPMENT / 'r9_motion_readiness_v1' / name for name in (
            'source_validation.json', 'reassessment_C.json', 'motion_component_C.json',
            'independent_review.json', 'execution_C.json'))
        source_root = V13_SOURCE_ROOT if experiment_version == V13_EXPERIMENT_VERSION else V12_DEVELOPMENT/'m4_v12_source_v1'
        required.update(source_root / name for name in (
            'validate_source.py', 'tests_v1.json', 'save_source_checkpoint.py',
            'prepare_once.py', 'archive_preparation.py', 'release_dispatch.py', 'acquire_once.py'))
        required.add(EXPERIMENTS / 'checkpoints/r9_motion_readiness_v1/manifest.json')
        binding = (_v13_trapping_integrated_binding() if experiment_version == V13_EXPERIMENT_VERSION
                   else _v12_component_response_binding())
        required.update(Path(ref['path']) for ref in binding['receipts'])
        if experiment_version == V13_EXPERIMENT_VERSION:
            required.update(REPOSITORY / 'docs/codex/gesc_gaussian/v2' / name for name in (
                'm4_v13_integrated_comparison_plan.md', 'r21_recurrent_trapping_plan.md',
                'r21_recurrent_trapping_handoff.md', 'r21_visible_d02_plan.md',
                'validation/r21_recurrent_trapping.md', 'validation/r21_visible_d02.md',
                'r12_measurement_correction_plan.md', 'validation/r12_measurement_correction.md'))
        missing = sorted(str(path) for path in required if not path.is_file())
        if missing:
            raise ValueError('M4 v12 prerequisite source/evidence missing: ' + ', '.join(missing))
        paths.update(required)
    return [receipt(path) for path in sorted(paths) if path.is_file()]


def verify_frozen(contract, *, verify_geometry_points=True):
    """Read-only source/configuration/installed binding check before any work."""
    validate_experiment_contract(contract)
    if (contract.get('schema_version') != 1
            or len(contract.get('runs', [])) != 16
            or [row['slot'] for row in contract['runs']] != list(range(1, 17))):
        raise ValueError('M4 fixed contract identity/population invalid')
    current = read_json(contract['contract_path'])
    if current != contract:
        raise ValueError('M4 in-memory contract differs from frozen file')
    if selected_environment() != contract['environment']:
        raise ValueError('M4 process environment differs from preparation')
    if installed_entry_points(expected_build=BUILD) != contract['installed_entry_points']:
        raise ValueError('M4 installed entrypoints differ from frozen source')
    if is_arrival_experiment_version(contract['version']):
        if (contract.get('runtime_binding') != _runtime_binding(contract['version'])
                or contract.get('development_release_policy') != experiment_release_policy(contract['version'])):
            raise ValueError('M4 v10 runtime or development release policy differs')
    if contract['version'] == V12_EXPERIMENT_VERSION:
        binding = _v12_component_response_binding()
        if contract.get('component_response_prerequisite') != binding:
            raise ValueError('M4 v12 R10 prerequisite differs from frozen contract')
        _verify_v12_method_configuration(contract, binding)
    if contract['version'] == V13_EXPERIMENT_VERSION:
        binding = _v13_trapping_integrated_binding()
        if contract.get('trapping_integrated_prerequisite') != binding:
            raise ValueError('M4 v13 R21/D02 prerequisite differs from frozen contract')
        _verify_v12_method_configuration(contract, binding['component_response'])
    if is_retained_development_experiment_version(contract['version']):
        binding = _load_v14_reuse(contract)
        _verify_v12_method_configuration(contract,
            binding['trapping_integrated_prerequisite']['component_response'])
    check_receipts(contract['source_files'])
    check_receipts([contract['scenario'], *contract['topology_receipts'].values()])
    if (contract['version'] in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9')
            or is_arrival_experiment_version(contract['version'])):
        primary = read_json(contract['topology_receipts']['primary_nominal']['path'])
        if any(row['resolved_scenario']['success']['staged_recovery']['topology_qualification']
               != primary for row in contract['runs'][:4]):
            raise ValueError('M4 v5 primary topology receipt differs from resolved cases')
    if (contract['version'] in ('m4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9')
            or is_arrival_experiment_version(contract['version'])):
        selected = v6_controller_configuration()
        if contract.get('controller_configuration') != selected:
            raise ValueError('M4 v6 selected controller differs from its frozen receipt')
        check_receipts([selected])
        from ros_esc.scenario_runner import run_scenario as runner
        from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import load_yaml
        document = load_yaml(contract['scenario']['path'])
        cases = {case['case_id']: case for case in document['cases']}
        for row in contract['runs']:
            if is_retained_development_experiment_version(contract['version']) and row['slot'] <= 4:
                continue  # Exact original plan/configuration equality is checked by the contract owner.
            # Contract JSON sorts mapping keys; recover the schema's original
            # YAML merge order while requiring exactly the frozen values.
            resolved = deepcopy(row['resolved_scenario'])
            controls = {**document['frozen_profile']['launch_overrides'],
                        **cases[row['case_id']]['algorithm']['launch_overrides']}
            if controls != resolved['algorithm']['launch_overrides']:
                raise ValueError('M4 v6 scenario overrides differ from frozen resolved values')
            resolved['algorithm']['launch_overrides'] = controls
            launch = runner.build_launch_command(
                resolved, cost_path=row['expected_cost_configuration']['path'],
                gui=row['visible'], run_id=row['run_id'])
            if row['launch_argv'] != launch:
                raise ValueError('M4 v6 launch argv differs from its frozen resolved scenario')
            actual = runner.resolve_controller_config_filepath(
                resolved['algorithm']['launch_overrides'])
            if str(actual) != selected['path']:
                raise ValueError('M4 v6 controller resolver differs across frozen slots')
            metadata = runner.build_metadata(resolved, 'mattb', contract['version'],
                                             '', run_id=row['run_id'])
            files = metadata['parameter_files']
            if (files.count(selected['path']) != 1 or str(runner.GESC_CONTROLLER) in files):
                raise ValueError('M4 v6 controller metadata differs from selected launch')
    check_receipts([row['expected_cost_configuration'] for row in contract['runs']])
    for context in contract['geometry_contexts'].values():
        check_receipts([context['label_geometry'], context['geometry_recovery']])
        if verify_geometry_points:
            check_receipts(context['geometry_receipts'])
    return True


def geometry_context(name, source_files):
    from ros_esc.plotting_scripts.q1_study import verify_geometry_receipts
    filename, digest = GEOMETRIES[name]
    geometry = {'path': str(EXPERIMENTS / 'replay/m1a_labels_v1' / filename), 'sha256': digest}
    check_receipts([geometry])
    document = read_json(geometry['path'])
    points = [ref for basin in document['basins'] for ref in basin['point_receipts']]
    context = {
        'label_geometry': geometry,
        'geometry_recovery': {
            'path': str(EXPERIMENTS / 'replay/m1a_labels_v1_recovery1/labels.json'),
            'sha256': '2ae8c6e53446ec2ce176f43436d47b726c7c5d8107990a486f021ff787e9620b'},
        'geometry_receipts': points, 'source_files': source_files,
    }
    verify_geometry_receipts(context)
    return context


def verify_dispatch_release(contract_path):
    """Require reviewed source evidence and preparation before the public CLI."""
    contract = read_json(contract_path)
    verify_frozen(contract)
    preflight = Path(contract['root'])/'preflight'
    release = read_json(preflight/'dispatch_release.json')
    initial = list(range(5, 17)) if is_retained_development_experiment_version(contract['version']) else [1, 2, 3, 4]
    if (release.get('status') != 'RELEASED'
            or release.get('initial_slots') != initial
            or release.get('contract') != receipt(contract_path)):
        raise ValueError('M4 public dispatch has no exact development release')
    check_receipts([release[key] for key in (
        'contract', 'prepared', 'source_checkpoint', 'source_validation')])
    prepared = read_json(release['prepared']['path'])
    if prepared.get('status') != 'PREPARED' or prepared.get('contract') != release['contract']:
        raise ValueError('M4 preparation receipt does not release this contract')
    validation = read_json(release['source_validation']['path'])
    if (validation.get('returncode') != 0 or validation.get('source_stable') is not True
            or validation.get('before') != validation.get('after')):
        raise ValueError('M4 release lacks passing immutable source validation')
    pins = validation['after']
    if any(pins.get(row['path']) != row['sha256'] for row in contract['source_files']):
        raise ValueError('M4 frozen source was not covered by release validation')
    checkpoint = read_json(release['source_checkpoint']['path'])
    if checkpoint.get('archive_verified') is not True:
        raise ValueError('M4 source checkpoint archive was not verified')
    if is_retained_development_experiment_version(contract['version']):
        review_ref = release.get('retained_development_review', {})
        qualification_ref = release.get('retained_development_qualification', {})
        check_receipts([review_ref, qualification_ref])
        review = read_json(review_ref['path'])
        if (review.get('status') != 'PASS'
                or review.get('contract') != receipt(contract_path)
                or review.get('qualification') != qualification_ref
                or qualification_ref != receipt(Path(contract['root'])/'analysis/block_0/cached_qualification.json')):
            raise ValueError('V14 requires independent cached development review before dispatch')
        load_retained_development(contract, time.monotonic()+60.)
    return release


def prepare(experiment_version=DEFAULT_EXPERIMENT_VERSION):
    """One finite pre-dispatch receipt job; caller supplies the 600s timeout."""
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from ros_esc.scenario_runner import run_scenario as runner
    from ros_esc.scenario_runner.m4_scenario import expected_slots, write_m4_scenario
    from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite
    from ros_esc.plotting_scripts.gesc_gaussian_bag_analysis import load_yaml
    from ros_esc.plotting_scripts.q1_study import verify_geometry_receipts

    branch = subprocess.check_output(['git', '-C', str(REPOSITORY), 'branch', '--show-current'],
                                     text=True).strip()
    if branch != 'feature/gesc-gaussian-robustness-v2':
        raise ValueError('M4 requires the V2 branch')
    identity = experiment_identity(experiment_version)
    root = ROOT if experiment_version == DEFAULT_EXPERIMENT_VERSION else Path(identity['root'])
    root.mkdir(parents=True, exist_ok=False)
    preflight = root / 'preflight'
    preflight.mkdir()
    started = time.monotonic()
    atomic_exclusive_json(preflight/'started.json', {
        'status': 'INCOMPLETE', 'version': experiment_version, 'budget_sec': 600,
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
    })
    retained = None
    source_contract = None
    if is_retained_development_experiment_version(experiment_version):
        retained = _v14_retained_development_binding()
        source_contract = read_json(retained['source_contract']['path'])
        atomic_exclusive_json(preflight/'retained_development.json', retained)
        check_receipts(list(source_contract['topology_receipts'].values()))
    sources = (collect_sources(experiment_version) if is_arrival_experiment_version(experiment_version)
               else collect_sources())
    geometry = {name: geometry_context(name, sources) for name in GEOMETRIES}
    template = load_yaml(REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
                         'phase08_v8_11_secondary_visible_probe.yaml')
    case = template['cases'][0]
    disturbances = {
        'nominal': {'sensor_noise': {'model': 'none', 'bound': 0.0},
                    'sensor_delay_sec': 0.0, 'pose_delay_sec': 0.0},
        'noise': {'sensor_noise': {'model': 'gaussian', 'bound': 0.0, 'std_dev': 0.015},
                  'sensor_delay_sec': 0.0, 'pose_delay_sec': 0.0},
        'delay': {'sensor_noise': {'model': 'none', 'bound': 0.0},
                  'sensor_delay_sec': 0.10, 'pose_delay_sec': 0.10},
    }
    topology, topology_receipts = {}, {}
    for condition, disturbance in disturbances.items():
        topology[condition] = (read_json(source_contract['topology_receipts'][condition]['path'])
            if retained is not None else truth.derive_two_source_topology_qualification(
                case['sources'], case['starts'][0], template['defaults']['bounds_m'],
                disturbance, 'local', 'global'))
        path = preflight / f'topology_secondary_{condition}.json'
        atomic_exclusive_json(path, topology[condition])
        topology_receipts[condition] = receipt(path)
    primary_options = {}
    if (experiment_version in ('m4-pilot-v5', 'm4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9')
            or is_arrival_experiment_version(experiment_version)):
        primary_template = load_yaml(REPOSITORY / 'ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/'
                                     'phase08_v8_10_primary_visible_probe.yaml')
        primary_case = primary_template['cases'][0]
        primary = (read_json(source_contract['topology_receipts']['primary_nominal']['path'])
            if retained is not None else truth.derive_two_source_topology_qualification(primary_case['sources'],
                primary_case['starts'][0], primary_template['defaults']['bounds_m'],
                disturbances['nominal'], 'local', 'global'))
        path = preflight/'topology_primary_nominal.json'
        atomic_exclusive_json(path, primary)
        topology_receipts['primary_nominal'] = receipt(path)
        primary_options['primary_topology'] = primary
    scenario = write_m4_scenario(root/'scenario.yaml', topology, runs_root=root/'runs',
        experiment_version=experiment_version, **primary_options)
    suite = load_suite(scenario['path'])
    expanded, unsupported = expand_suite(suite)
    specs = expected_slots(experiment_version)
    if unsupported or len(expanded) != 16 or len(specs) != 16:
        raise ValueError('M4 expansion is not the exact executable16 slots')
    by_case = {row['case_id']: row for row in expanded}
    runs = []
    for spec in specs:
        if retained is not None and spec['slot'] <= 4:
            runs.append(deepcopy(source_contract['runs'][spec['slot']-1]))
            continue
        resolved = by_case[spec['case_id']]
        if resolved['seed'] != spec['seed']:
            raise ValueError('M4 expanded seed differs from the fixed block')
        verify_geometry_receipts(geometry[spec['geometry']], resolved)
        run_id = runner.validate_run_id(experiment_run_id(spec, experiment_version))
        cost_path = preflight / f'cost_slot_{spec["slot"]}.json'
        generated = runner.resolved_noise_config(resolved, cost_path)
        expected_cost = receipt(cost_path if generated is not None else runner.MULTI_LIGHT_COST)
        launch = runner.build_launch_command(resolved, cost_path=expected_cost['path'],
                                             gui=spec['visible'], run_id=run_id)
        summary_path = root/'acquisition'/f'summary_{spec["slot"]}.yaml'
        argv = ['ros2', 'run', 'ros_esc', 'run_scenario', scenario['path'],
                '--operator', 'mattb', '--case-id', spec['case_id'], '--run-id', run_id,
                '--runs-root', str(root/'runs'), '--summary-output', str(summary_path),
                '--strict-cleanup']
        if experiment_version != DEFAULT_EXPERIMENT_VERSION:
            argv += ['--process-ownership-mode', identity['process_ownership_mode']]
        if spec['visible']:
            argv.append('--gui')
        runs.append({**spec, 'run_id': run_id, 'resolved_scenario': resolved,
                     'geometry_receipt': geometry[spec['geometry']]['label_geometry'],
                     'expected_cost_configuration': expected_cost, 'launch_argv': launch,
                     'runner_argv': argv, 'summary_path': str(summary_path)})
    contract = {
        'schema_version': 1, 'version': experiment_version, 'root': str(root),
        'contract_path': str(preflight/'contract.json'), 'scenario': scenario,
        'source_files': sources, 'topology_receipts': topology_receipts,
        'geometry_contexts': geometry, 'runs': runs,
        'environment': selected_environment(),
        'installed_entry_points': installed_entry_points(expected_build=BUILD),
        'execution': {'runs_root': str(root/'runs'), 'ros_domain_id': int(os.environ['ROS_DOMAIN_ID']),
                      'recording_sec': 720., 'case_timeout_sec': 900.,
                      'suite_timeout_sec': 15300., 'cleanup_reserve_sec': 30.,
                      'science_budget_sec': 900., 'shutdown_grace_sec': 45.},
        'science': {'targets_sec': [15+30*k for k in range(24)],
                    'labels_sec': 120., 'references_sec': 45., 'summary_sec': 10.,
                    'freeze_report_sec': 20., 'maximum_observations': 40000},
    }
    if experiment_version != DEFAULT_EXPERIMENT_VERSION:
        contract.update(experiment_version=experiment_version,
                        method_version=experiment_method_version(experiment_version))
        contract['execution']['process_ownership_mode'] = identity['process_ownership_mode']
    if (experiment_version in ('m4-pilot-v6', 'm4-pilot-v7', 'm4-pilot-v8', 'm4-pilot-v9')
            or is_arrival_experiment_version(experiment_version)):
        contract['controller_configuration'] = v6_controller_configuration()
    if is_arrival_experiment_version(experiment_version):
        budgets = experiment_execution_budgets(experiment_version)
        for name in ('recording_sec', 'case_timeout_sec', 'suite_timeout_sec',
                     'cleanup_reserve_sec', 'science_budget_sec', 'shutdown_grace_sec'):
            contract['execution'][name] = budgets[name]
        for name in ('labels_sec', 'references_sec', 'summary_sec', 'freeze_report_sec'):
            contract['science'][name] = budgets[name]
        contract.update(development_release_policy=experiment_release_policy(experiment_version),
                        runtime_binding=_runtime_binding(experiment_version))
    if experiment_version == V12_EXPERIMENT_VERSION:
        contract['component_response_prerequisite'] = _v12_component_response_binding()
    if experiment_version == V13_EXPERIMENT_VERSION:
        contract['trapping_integrated_prerequisite'] = _v13_trapping_integrated_binding()
    if retained is not None:
        contract['retained_development'] = {key: deepcopy(retained[key])
            for key in ('policy', 'source_contract', 'source_slots')}
        contract['retained_development']['reuse_receipt'] = receipt(preflight/'retained_development.json')
    check_receipts(sources)
    atomic_exclusive_json(preflight/'contract.json', contract)
    verify_frozen(contract)
    atomic_exclusive_json(preflight/'prepared.json', {
        'status': 'PREPARED', 'contract': receipt(preflight/'contract.json'),
        'elapsed_sec': time.monotonic()-started, 'acquisition_started': False,
        'geometry_names': list(geometry), 'topology_conditions': list(topology_receipts),
        'limits': ['static model topology; noise margin3sigma',
                   'delay receipts do not qualify delayed dynamics'],
    })
    return receipt(preflight/'contract.json')


def _verify_cases(contract, rows, expected_slots):
    if [row['slot'] for row in rows] != list(expected_slots):
        raise ValueError('M4 science population differs from reserved slots')
    reuse = (_load_v14_reuse(contract)
        if is_retained_development_experiment_version(contract['version'])
        and any(row['slot'] <= 4 for row in rows) else None)
    for row in rows:
        planned = slot_spec(contract, row['slot'])
        retained = is_retained_development_experiment_version(contract['version']) and row['slot'] <= 4
        expected_version = planned['experiment_version'] if retained else contract['version']
        if contract['version'] != VERSION and row.get('experiment_version') != expected_version:
            raise ValueError('M4 acquisition belongs to a different experiment')
        if (row.get('status') != 'COMPLETE' or row.get('integrity_passed') is not True
                or any(row.get(key) != planned[key] for key in
                       ('run_id', 'case_id', 'seed', 'arm', 'partition', 'condition', 'block',
                        'geometry', 'visible'))):
            raise ValueError('M4 science input is not an exact complete acquisition')
        if retained:
            if row['receipt'] != reuse['source_acquisitions'][row['slot']-1]:
                raise ValueError('V14 retained acquisition is not its declared source receipt')
            _check_v14_receipts(contract, [row['receipt'], *row['input_files']])
        else:
            check_receipts([row['receipt'], *row['input_files']])
        recorded = read_json(row['receipt']['path'])
        if recorded != {key: value for key, value in row.items() if key != 'receipt'}:
            raise ValueError('M4 in-memory acquisition differs from immutable receipt')


def _verify_science_rows(contract, rows, acquired):
    if [row.get('slot') for row in rows] != [row['slot'] for row in acquired]:
        raise ValueError('M4 scientific rows do not preserve exact slot order')
    for row, original in zip(rows, acquired):
        planned = slot_spec(contract, row['slot'])
        retained = is_retained_development_experiment_version(contract['version']) and row['slot'] <= 4
        expected_version = planned['experiment_version'] if retained else contract['version']
        if contract['version'] != VERSION and row.get('experiment_version') != expected_version:
            raise ValueError('M4 scientific row belongs to a different experiment')
        if (any(row.get(key) != planned[key] for key in
                ('slot', 'run_id', 'case_id', 'seed', 'arm', 'partition', 'condition', 'block',
                 'geometry', 'visible'))
                or row.get('status') != original['status']
                or row.get('integrity_passed') != original['integrity_passed']
                or any(row.get(key) != original[key] for key in
                       ('run_directory', 'behavior_passed') if key in original)
                or any(row[key] != original[key] for key in row.keys() & original.keys()
                       if key != 'receipt')):
            raise ValueError('M4 scientific output changes an acquisition identity or integrity')


def _science_unavailable(rows, reason):
    """Complete the outcome ledger without certifying unperformed analysis."""
    results = []
    for acquired in rows:
        row = {key: deepcopy(acquired[key]) for key in (
            'slot', 'block', 'run_id', 'case_id', 'seed', 'arm', 'partition',
            'geometry', 'condition', 'visible', 'experiment_version', 'status', 'integrity_passed',
            'run_directory', 'behavior_passed') if key in acquired}
        row.update(science_status='EVIDENCE_UNAVAILABLE', science_reason=reason,
                   latency={'status': 'EVIDENCE_UNAVAILABLE', 'reason': reason,
                            'observed': False, 'independently_eligible': False},
                   wrong_fills=None, wrong_goals=None, direction_rows=[],
                   direction_analysis_complete=False, combined_sequence_passed=None,
                   mandatory_stopped_acquisitions=None)
        if is_arrival_experiment_version(acquired.get('experiment_version')):
            row.update(method_version=experiment_method_version(acquired['experiment_version']),
                       scientific_analysis_complete=False,
                       scientific_analysis_checks={'analysis_available': False})
        results.append(row)
    return results


def analyze_block(contract, block, four_case_receipts, suite_end):
    """Attempt each finite science stage once; preserve partial/failed output."""
    from m4_science_job import finite_science_job
    began = time.monotonic()
    science = contract['science']
    end = min(suite_end, began + science['labels_sec'] +
              2*science['references_sec'] + science['summary_sec'])
    output = Path(contract['root'])/'analysis'/f'block_{block}'
    output.mkdir(parents=True, exist_ok=False)
    atomic_exclusive_json(output/'started.json', {
        'status': 'INCOMPLETE', 'block': block, 'started_monotonic': began,
        'absolute_deadline': end, 'cases': [row['receipt'] for row in four_case_receipts],
    })
    verify_frozen(contract)
    _verify_cases(contract, four_case_receipts, range(block*4+1, block*4+5))
    jobs = []

    def job(stage, selector, number, cap, *, stage_start=None):
        start = time.monotonic() if stage_start is None else stage_start
        remaining_cap = min(cap-(time.monotonic()-start), end-time.monotonic())
        if remaining_cap <= 0:
            raise TimeoutError('M4 science stage budget exhausted before dispatch')
        name = stage if stage != 'references' else f'references_{number}'
        argv = [sys.executable, str(TOOLS/'evaluate_m4.py'), stage,
                '--contract', contract['contract_path'], selector, str(number)]
        ownership = ({'process_ownership_mode': experiment_identity(contract['version'])['process_ownership_mode']}
                     if contract['version'] != DEFAULT_EXPERIMENT_VERSION else {})
        result = finite_science_job(argv, output/(name+'.log'), output/(name+'_job.json'),
                                   cap_sec=remaining_cap, suite_end=end, **ownership)
        if is_arrival_experiment_version(contract['version']):
            result = {**result, 'receipt': receipt(output/(name+'_job.json'))}
        jobs.append(result)
        if result.get('integrity_passed') is not True:
            raise ValueError('M4 science process/source integrity failed: ' + name)
        return result

    labels = job('labels', '--block', block, science['labels_sec'], stage_start=began)
    if labels.get('complete') is True:
        labeled = read_json(output/'labels.json')
        if labeled.get('complete') is not True or labeled.get('integrity_passed') is not True:
            raise ValueError('M4 label result has incomplete source/input integrity')
        _verify_science_rows(contract, labeled.get('runs', []), four_case_receipts)
        for acquired in four_case_receipts:
            if acquired['arm'] in ('C', 'D'):
                job('references', '--slot', acquired['slot'], science['references_sec'])
        summary = job('summary', '--block', block, science['summary_sec'])
        if summary.get('complete') is True:
            result = read_json(output/'result.json')
        else:
            result = dict(complete=True, integrity_passed=True,
                runs=_science_unavailable(four_case_receipts, 'summary_analysis_timeout'),
                scientific_analysis_complete=False)
            atomic_exclusive_json(output/'unavailable_result.json', result)
    else:
        result = dict(complete=True, integrity_passed=True,
            runs=_science_unavailable(four_case_receipts, 'labels_analysis_timeout'),
            scientific_analysis_complete=False,
            references_skipped='no_complete_frozen_label_inputs',
            summary_skipped='no_complete_frozen_label_inputs')
        atomic_exclusive_json(output/'unavailable_result.json', result)
    if (result.get('complete') is not True or result.get('integrity_passed') is not True
            or [row['slot'] for row in result.get('runs', [])] != list(range(block*4+1, block*4+5))):
        raise ValueError('M4 block result does not retain all four exact slots')
    _verify_science_rows(contract, result['runs'], four_case_receipts)
    verify_frozen(contract)
    if time.monotonic() > end:
        raise TimeoutError('M4 inclusive block analysis deadline exceeded')
    summary_path = output/('result.json' if (output/'result.json').exists()
                           and jobs[-1].get('complete') is True else 'unavailable_result.json')
    complete = dict(complete=True, integrity_passed=True, block=block,
                    result=receipt(summary_path), jobs=jobs,
                    elapsed_sec=time.monotonic()-began, absolute_deadline=end,
                    cases=[row['receipt'] for row in four_case_receipts])
    if is_arrival_experiment_version(contract['version']):
        complete['scientific_analysis_complete'] = result.get('scientific_analysis_complete') is True
    atomic_exclusive_json(output/'block_receipt.json', complete)
    return {**complete, 'receipt': receipt(output/'block_receipt.json')}


def _verify_v10_development_science(contract, acquired, block, development):
    """Certify retained analysis products, not statistical success or new work."""
    from ros_esc.plotting_scripts.m4_pilot import (
        validate_experiment_document, direction_product_complete, development_latency_feasibility,
        arrival_sequence_required_keys,
    )
    output = Path(contract['root']) / 'analysis/block_0'
    nested = []

    def require(condition, reason):
        if not condition:
            raise ValueError(f"M4 {contract['version'].removeprefix('m4-pilot-')} usable development analysis: " + reason)

    def document(reference, path):
        require(reference.get('path') == str(path.resolve()), 'artifact path differs: ' + str(path))
        check_receipts([reference])
        nested.append(reference)
        return read_json(path)

    row_checks = {'acquisition_complete', 'position_labels_complete',
        'confirmation_attribution_complete', 'selected_authority_complete',
        'error_attribution_complete', 'arrival_measurement_complete',
        'path_length_complete', 'motion_measurement_complete', 'direction_inputs_complete'}
    summary_checks = {'four_arm_analysis_complete', 'both_reference_products_complete'}
    sequence_keys = ('local_recovery_stage_passed', 'fill_cardinality_passed',
                     'required_state_path_passed', 'escape_command_ownership_passed',
                     'required_events_passed', 'required_event_sequence_passed',
                     'forbidden_states_absent', 'forbidden_events_absent',
                     'post_recovery_global_proximity_passed')

    def completed_checks(value, expected):
        checks = value.get('scientific_analysis_checks')
        return (value.get('scientific_analysis_complete') is True
                and isinstance(checks, dict) and set(checks) == expected
                and all(flag is True for flag in checks.values()))

    require(contract.get('development_release_policy') == experiment_release_policy(contract['version']), 'policy differs')
    require(block.get('scientific_analysis_complete') is True, 'block science incomplete')
    require(completed_checks(development, summary_checks), 'summary science or required measurements incomplete')
    if is_integrated_arrival_experiment_version(contract['version']):
        require(development.get('scientific_scope') == 'integrated_arrival_direction_v1'
            and development.get('secondary_endpoint') == 'independent_basin_entry_latency',
            'V12 primary/secondary scientific scope differs')
    validate_experiment_document(development, contract['version'])
    require(development.get('contract') == receipt(contract['contract_path']), 'summary contract differs')
    require(block['result']['path'] == str((output / 'result.json').resolve()), 'summary result path differs')
    jobs = block.get('jobs', [])
    expected_jobs = [('labels', '--block', 0, contract['science']['labels_sec']),
                     ('references', '--slot', 3, contract['science']['references_sec']),
                     ('references', '--slot', 4, contract['science']['references_sec']),
                     ('summary', '--block', 0, contract['science']['summary_sec'])]
    require(len(jobs) == len(expected_jobs), 'four completed science jobs required')
    for job, (stage, selector, number, cap) in zip(jobs, expected_jobs):
        name = stage if stage != 'references' else f'references_{number}'
        saved = document(job.get('receipt', {}), output / (name + '_job.json'))
        require(saved == {key: value for key, value in job.items() if key != 'receipt'},
                'science job differs from retained receipt')
        require(job.get('argv') == [sys.executable, str(TOOLS / 'evaluate_m4.py'), stage,
            '--contract', contract['contract_path'], selector, str(number)], 'science job invocation differs')
        require(job.get('complete') is True and job.get('integrity_passed') is True
            and job.get('launched') is True and job.get('return_code') == 0
            and job.get('timed_out') is False and job.get('clean_termination') is True
            and job.get('process_ownership_mode') == 'subreaper_group_v3', 'science job did not complete safely')
        require(type(job.get('cap_sec')) in (int, float) and 0 < job['cap_sec'] <= cap
            and type(job.get('elapsed_wall_sec')) in (int, float)
            and 0 <= job['elapsed_wall_sec'] <= job['cap_sec'], 'science job exceeded its finite cap')
        script = receipt(TOOLS / 'evaluate_m4.py')
        require(job.get('source') == {'kind': 'script', **script}, 'science executable source differs')
        log_ref = {'path': job.get('log_path'), 'sha256': job.get('log_sha256')}
        require(log_ref['path'] == str((output / (name + '.log')).resolve()), 'science log path differs')
        check_receipts([log_ref]); nested.append(log_ref)

    labels = document(development.get('labels', {}), output / 'labels.json')
    validate_experiment_document(labels, contract['version'])
    require(labels.get('block') == 0 and labels.get('complete') is True
        and labels.get('integrity_passed') is True
        and labels.get('contract') == receipt(contract['contract_path'])
        and labels.get('input_files') == [row['receipt'] for row in acquired], 'labels binding differs')
    _verify_science_rows(contract, labels.get('runs', []), acquired)
    reference_receipts = []
    for row, labeled, original in zip(development['runs'], labels['runs'], acquired):
        require(completed_checks(row, row_checks), 'slot analysis/authority incomplete: ' + str(row['slot']))
        summary_fields = {'direction_rows', 'direction_analysis_complete', 'direction_summary',
                          'direction_supplemental', 'scientific_analysis_complete', 'scientific_analysis_checks'}
        require(all(row.get(key) == value for key, value in labeled.items() if key not in summary_fields),
                'summary changed the retained per-run analysis')
        actual = original.get('runner_result', {}).get('outcomes', {})
        components = row.get('combined_sequence_components', {})
        require(all(components.get(key) == actual.get(key) for key in sequence_keys)
            and components.get('arrival_criterion') == 'post_recovery_arrival_v1'
            and components.get('arrival_measurement_complete') is True
            and row.get('arrival_criterion') == 'post_recovery_arrival_v1'
            and row.get('arrival_measurement_complete') is True
            and row.get('arrival_passed') == actual.get('post_recovery_global_proximity_passed'),
            'arrival/sequence analysis differs from actual acquisition outcomes')
        if contract['version'] == V13_EXPERIMENT_VERSION:
            from ros_esc.plotting_scripts.m4_pilot import RECORDED_ARRIVAL_BINDING
            require(row.get('arrival_binding_method') == RECORDED_ARRIVAL_BINDING
                    and row.get('arrival_binding_error') is None,
                    'V13 recorded arrival binding differs or failed')
        required_sequence = arrival_sequence_required_keys(contract['version'])
        if is_integrated_arrival_experiment_version(contract['version']):
            require(row.get('combined_sequence_required_keys') == list(required_sequence)
                and row.get('combined_sequence_diagnostic_keys') == ['required_state_path_passed'],
                'V12 primary sequence and first-path diagnostic binding differ')
        sequence = [actual.get(key) for key in required_sequence]
        expected_sequence = all(sequence) if all(type(flag) is bool for flag in sequence) else None
        require(row.get('combined_sequence_passed') is expected_sequence,
                'combined sequence claim differs from actual acquisition outcomes')
        require(row.get('acquisition_receipt') == original['receipt']
            and labeled.get('acquisition_receipt') == original['receipt'], 'slot acquisition receipt differs')
        require(row.get('labels') == labeled.get('labels'), 'slot label receipt differs')
        spatial = document(row.get('labels', {}), output / f'slot_{row["slot"]}_labels.json')
        validate_experiment_document(spatial, contract['version'])
        require(spatial.get('spatial_labels_precede_event_join') is True, 'independent labels unavailable')
        if row['arm'] not in ('C', 'D'):
            continue
        normalized = row.get('normalized_inputs', {})
        require(normalized == labeled.get('normalized_inputs') and normalized.get('path') ==
            str((output / f'slot_{row["slot"]}_normalized.json').resolve()), 'normalized binding differs')
        # The completed numerical owner validates anchors against this hashed
        # input. Do not parse/copy its large observation array a second time.
        check_receipts([normalized]); nested.append(normalized)
        ref = receipt(output / f'slot_{row["slot"]}_references.json')
        reference_receipts.append(ref)
        references = document(ref, Path(ref['path']))
        validate_experiment_document(references, contract['version'])
        require(references.get('contract') == receipt(contract['contract_path'])
            and references.get('slot') == row['slot'] and references.get('run_id') == row['run_id']
            and references.get('normalized_inputs') == normalized
            and references.get('complete') is True and references.get('integrity_passed') is True
            and references.get('direction_analysis_complete') is True
            and row.get('direction_analysis_complete') is True
            and row.get('direction_rows') == references.get('rows'), 'reference result differs or is incomplete')
        targets = references.get('rows', [])
        require(direction_product_complete(targets, row), 'exact usable 24 reference targets required')
    require(development.get('references') == reference_receipts, 'both bound C/D references required')
    enabled = [row['slot'] for row in development['runs'] if row['arm'] in ('B', 'D')
               and row.get('combined_sequence_passed') is True]
    d = next(row for row in development['runs'] if row['arm'] == 'D')
    require(enabled, 'no enabled B/D local fill through global arrival')
    if contract['version'] == V13_EXPERIMENT_VERSION:
        require(enabled == [2, 4], 'both B and D recovery through global arrival are required')
    require(type(d.get('mandatory_stopped_acquisitions')) is int
        and d['mandatory_stopped_acquisitions'] == 0
        and d.get('mandatory_stop_evidence', {}).get('status') == 'OBSERVED_CONTINUOUS_ACQUISITION'
        and d['mandatory_stop_evidence'].get('analysis_complete') is True
        and d['mandatory_stop_evidence'].get('command_pairing_complete') is True
        and d['mandatory_stop_evidence'].get('authority_complete') is True,
        'D continuous verification/design is not established')
    evidence = dict(policy=experiment_release_policy(contract['version']), scientific_analysis_complete=True,
                    enabled_arrival_slots=enabled, continuous_development_slot=d['slot'],
                    nested_receipts=nested)
    if contract['version'] == V11_EXPERIMENT_VERSION:
        feasibility = development_latency_feasibility(
            development['runs'], experiment_version=contract['version'])
        require(development.get('development_latency_feasibility') == feasibility,
                'development latency feasibility differs from retained first-opportunity endpoints')
        require(feasibility['feasible'] is True, feasibility['reason'])
        evidence['development_latency_feasibility'] = feasibility
    if contract['version'] == V12_EXPERIMENT_VERSION:
        prerequisite = _v12_component_response_binding()
        require(contract.get('component_response_prerequisite') == prerequisite,
                'R10 prerequisite differs from frozen contract')
        evidence['component_response_prerequisite'] = prerequisite
        nested.extend(prerequisite['receipts'])
    if contract['version'] == V13_EXPERIMENT_VERSION:
        from ros_esc.plotting_scripts.m4_pilot import integrated_method_run_checks
        checks = integrated_method_run_checks(d)
        require(checks['status'] == 'PASS'
                and d.get('direction_summary') == checks['direction_summary'],
                'D integrated arrival/continuous/direction gates failed or unavailable')
        prerequisite = _v13_trapping_integrated_binding()
        require(contract.get('trapping_integrated_prerequisite') == prerequisite,
                'R21/D02 prerequisite differs from frozen contract')
        evidence.update(trapping_integrated_prerequisite=prerequisite, integrated_D_checks=checks)
        nested.extend(prerequisite['receipts'])
    return evidence


def release_holdouts(contract, development_receipts, analysis_receipt, suite_end):
    """Freeze the one development outcome once without tuning or replacements."""
    began = time.monotonic()
    end = min(suite_end, began+contract['science']['freeze_report_sec']/2)
    verify_frozen(contract)
    _verify_cases(contract, development_receipts, range(1, 5))
    if (analysis_receipt.get('block') != 0 or analysis_receipt.get('complete') is not True
            or analysis_receipt.get('integrity_passed') is not True):
        raise ValueError('M4 release requires a complete development outcome ledger')
    check_receipts([analysis_receipt['receipt'], analysis_receipt['result']])
    if (read_json(analysis_receipt['receipt']['path']) !=
            {key: value for key, value in analysis_receipt.items() if key != 'receipt'}
            or analysis_receipt.get('cases') != [row['receipt'] for row in development_receipts]):
        raise ValueError('M4 development analysis differs from its immutable acquisition binding')
    development = read_json(analysis_receipt['result']['path'])
    if development.get('complete') is not True or development.get('integrity_passed') is not True:
        raise ValueError('M4 development result integrity is unavailable')
    _verify_science_rows(contract, development.get('runs', []), development_receipts)
    v10_evidence = None
    if is_arrival_experiment_version(contract['version']):
        verify_development = (_verify_v14_development_science
            if is_retained_development_experiment_version(contract['version']) else _verify_v10_development_science)
        v10_evidence = verify_development(
            contract, development_receipts, analysis_receipt, development)
    for row in contract['runs'][4:]:
        if (Path(row['summary_path']).exists()
                or list((Path(contract['root'])/'runs').glob('*/'+row['run_id']))
                or (Path(contract['root'])/'acquisition'/f'slot_{row["slot"]}.json').exists()):
            raise ValueError('M4 holdout population is no longer sealed')
    if v10_evidence is not None:
        # Recheck after reading all nested products; no cached source/input
        # admission can release a population whose evidence changed meanwhile.
        _verify_cases(contract, development_receipts, range(1, 5))
        verify_frozen(contract)
        check_receipts([analysis_receipt['receipt'], analysis_receipt['result'],
                        *v10_evidence['nested_receipts']])
    if time.monotonic() >= end:
        raise TimeoutError('M4 one-time freeze budget exhausted')
    result = dict(status='RELEASED', contract=receipt(contract['contract_path']),
        development=[row['receipt'] for row in development_receipts],
        analysis=analysis_receipt['receipt'],
        source_files=contract['source_files'], holdouts=contract['runs'][4:],
        tuning_performed=False, replacements_allowed=False,
        scientific_pass_required=False, elapsed_sec=time.monotonic()-began)
    if v10_evidence is not None:
        result.update(development_release_policy=experiment_release_policy(contract['version']),
                      scientific_completion_required=True, development_evidence=v10_evidence)
    path = Path(contract['root'])/'preflight'/'holdout_release.json'
    atomic_exclusive_json(path, result)
    return {**result, 'receipt': receipt(path)}


def render_report(result, contract):
    """A local immutable evidence report; unavailable denominators stay visible."""
    latency, direction = result['latency'], result['direction']
    v10 = is_arrival_experiment_version(contract['version'])
    final_population = 'confirmation' if v10 else 'holdout'
    sequence_target = 'global arrival' if v10 else 'stronger candidate'
    text = [
        '# V2 M4 simulation comparison', '',
        *([f"Experiment: `{contract['version']}`; scientific method: `{experiment_method_version(contract['version'])}`.", '']
          if contract['version'] != DEFAULT_EXPERIMENT_VERSION else []),
        'This selected-condition pilot tests faster trapping detection and better '
        'GESC direction estimates while moving. Source validation is separate '
        'from the empirical acceptance targets below.', '',
        '| Target | Result | Evidence |', '|---|---|---|',
        f'| Confirmation latency: >=30% reduction, no additional wrong fills/goals | {latency["status"]} | '
        f'{latency["observed_endpoint_count"]}/12 observed endpoints; {latency["observed_pair_count"]}/6 pairs |',
        f'| Direction: median <=30 deg, p90 <=60 deg, availability >=80% | {direction["status"]} | '
        f'{direction["counts"]["eligible_informative"]} informative eligible /144 scheduled {final_population} targets |',
        f'| Zero mandatory stopped acquisition | {result["mandatory_stopped_acquisition"]["status"]} | '
        'C/D counts require attributable recorded evidence |',
        f'| Combined fill -> escape -> SEARCH -> {sequence_target} | {result["combined_sequence"]["status"]} | '
        f'Each of the three {final_population} conditions is evaluated separately |', '',
        f'Control/enabled confirmation medians (seconds): {latency["control_median_sec"]} / '
        f'{latency["enabled_median_sec"]}; descriptive fractional reduction: '
        f'{latency["descriptive_fraction_reduction"]}.', '',
        f'Direction median/p90 (degrees): {direction["median_error_deg"]} / '
        f'{direction["p90_error_deg"]}; averaging availability: {direction["averaging_availability"]}. '
        f'All {result["direction_scheduled_total"]} development/{final_population} direction slots are retained.', '',
        '| Slot | Arm | Partition / condition | Acquisition | Behavior | Science |',
        '|---:|---|---|---|---|---|',
    ]
    if is_integrated_arrival_experiment_version(contract['version']):
        primary = result['primary_outcomes']
        confirmation = primary['confirmation']
        counts = confirmation['arrival_counts']
        text = ['# V2 M4 integrated arrival and direction comparison', '',
            f"Experiment: `{contract['version']}`; scientific method: `{experiment_method_version(contract['version'])}`.", '',
            'Primary outcomes are post-recovery global arrival, completed local recovery, '
            'continuous acquisition and observed-phase GESC direction error/availability. '
            'Divergent integrated trajectories do not isolate detector response speed.', '',
            '| Primary outcome | Result | Evidence |', '|---|---|---|',
            f'| Global arrival | {counts["observed_arrival"]}/12 observed arrivals | '
            f'{counts["observed_nonarrival"]} observed nonarrivals; {counts["unavailable"]} unavailable |',
            f'| Direction: median <=30 deg, p90 <=60 deg, availability >=80% | {direction["status"]} | '
            f'{direction["counts"]["eligible_informative"]} informative eligible /144 scheduled confirmation targets |',
            f'| Zero mandatory stopped acquisition | {result["mandatory_stopped_acquisition"]["status"]} | '
            'Actual attributable C/D evidence |',
            f'| Completed fill -> escape -> SEARCH -> global arrival | {result["combined_sequence"]["status"]} | '
            'All three confirmation conditions retained |', '',
            f'Direction median/P90: {direction["median_error_deg"]}/{direction["p90_error_deg"]} degrees; '
            f'averaging availability: {direction["averaging_availability"]}.', '',
            'Development (4 runs, 48 direction targets) and confirmation (12 runs, 144 direction targets) '
            'are reported separately. Every planned run remains in its population denominator.', '',
            '| Population | Arm | Planned | Arrival / nonarrival / unavailable | Local recovery passed / failed / unavailable | Direction targets |',
            '|---|---|---:|---|---|---:|']
        for population, summary in primary.items():
            for arm in summary['by_arm']:
                arrived, local = arm['arrival_counts'], arm['local_recovery_counts']
                text.append(f'| {population} | {arm["arm"]} | {arm["planned_run_count"]} | '
                    f'{arrived["observed_arrival"]} / {arrived["observed_nonarrival"]} / {arrived["unavailable"]} | '
                    f'{local["passed"]} / {local["failed"]} / {local["unavailable"]} | '
                    f'{arm["direction"]["counts"]["scheduled"]} |')
        text.extend(['', 'The first-verification path remains a diagnostic. A later completed '
            f"recovery and valid arrival can satisfy {'V12' if contract['version'] == V12_EXPERIMENT_VERSION else 'V13'}; all other primary recovery/integrity predicates remain mandatory.", '',
            '| Slot | Arm | Partition / condition | Acquisition | Behavior | Science |',
            '|---:|---|---|---|---|---|'])
    for row in result['slots']:
        partition = 'confirmation' if v10 and row['partition'] == 'holdout' else row['partition']
        text.append(f'| {row["slot"]} | {row["arm"]} | {row["partition"]} / '
            f'{row["condition"]} | {row.get("status", "UNKNOWN")} | '
            f'{row.get("behavior_passed", "unavailable")} | '
            f'{row.get("science_status", "see result.json; missing metrics remain unavailable")} |')
        if v10:
            text[-1] = text[-1].replace(f'| {row["partition"]} / ', f'| {partition} / ')
    text.extend(['', '| Slot | Time to goal, s | Path, m | Fallback, s | '
        'Eligible duration, s | Jitter, deg | Relative lag, s | Mandatory stopped acquisitions |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|'])
    def value(number):
        return f'{number:.6g}' if type(number) in (int, float) and math.isfinite(number) else 'unavailable'
    for row in result['slots']:
        supplemental = row.get('direction_supplemental') or {}
        path = row.get('path_length') or {}
        text.append(f'| {row["slot"]} | {value(row.get("time_to_goal_sec"))} | '
            f'{value(path.get("value"))} | {value(supplemental.get("fallback_duration_sec"))} | '
            f'{value(supplemental.get("eligible_source_duration_sec"))} | '
            f'{value(supplemental.get("heading_jitter_median_deg"))} | '
            f'{value(supplemental.get("relative_smoothing_lag_median_sec"))} | '
            f'{value(row.get("mandatory_stopped_acquisitions"))} |')
    if v10:
        text.extend(['', 'Global arrival is evaluated separately from optional controller goal recognition.', '',
            '| Slot | Arrival observed | Time to arrival, s | Science completed |',
            '|---:|---|---:|---|'])
        for row in result['slots']:
            text.append(f'| {row["slot"]} | {row.get("arrival_passed", "unavailable")} | '
                f'{value(row.get("time_to_arrival_sec"))} | {row.get("scientific_analysis_complete", False)} |')
        text.extend(['', f'Development release: {result.get("development_release", {}).get("status", "WITHHELD")}. '
            f'Completed scientific blocks: {result.get("analysis_completion", {}).get("complete_blocks", 0)}/4. '
            'Complete baseline failures and censored endpoints remain results; incomplete science does not release confirmation.', '',
            'Confirmation uses fresh seeds on previously exposed conditions. The retained internal partition name is '
            '`holdout`; it does not establish unseen-condition validation.'])
    if contract['version'] == V11_EXPERIMENT_VERSION:
        feasibility = result['development_latency_feasibility']
        text.extend(['', f"Development latency measurement feasibility: {feasibility['status']}; "
            f"{feasibility['observed_pair_count']}/2 independently eligible observed pairs, "
            f"{feasibility['observed_endpoint_count']}/4 endpoints. "
            'This release condition does not require development latency improvement.'])
        if feasibility['reason']:
            text.extend(['', feasibility['reason']])
    if is_integrated_arrival_experiment_version(contract['version']):
        text.extend(['', 'Secondary historical endpoint: independent basin-entry latency '
            '(>=30% reduction, no additional wrong fills/goals). Its unchanged result is '
            f'{latency["status"]}: {latency["observed_endpoint_count"]}/12 observed endpoints and '
            f'{latency["observed_pair_count"]}/6 pairs. Control/enabled medians: '
            f'{latency["control_median_sec"]}/{latency["enabled_median_sec"]} seconds. '
            'Censored or unavailable secondary latency does not establish that target and does not '
            'replace the primary development analysis gate.', '',
            f'R10 component prerequisite: {result["component_response_prerequisite"]["status"]}; '
            f'decision `{result["component_response_prerequisite"]["decision"]["sha256"]}`. '
            'The component response comparison is separate evidence; its times are never substituted into basin-entry latency.'])
    if contract['version'] in (V13_EXPERIMENT_VERSION, V14_EXPERIMENT_VERSION):
        check = result['combined_method_confirmation']
        text.extend(['', f"R21/D02 prerequisite: {result['trapping_integrated_prerequisite']['status']}. "
            'Development requires both B and D recovery/arrival, plus D continuous acquisition and direction PASS.',
            f"Combined D method across all three confirmation conditions: {check['status']}.", '',
            '| D condition | Arrival | Recovery | Continuous | Direction | Verdict |',
            '|---|---|---|---|---|---|'])
        for row in check['conditions']:
            text.append(f"| {row['condition']} | {row['arrival_passed']} | {row['combined_recovery_passed']} | "
                f"{row['continuous_acquisition_passed']} | {row['direction_passed']} | {row['status']} |")
        text.extend(['', 'D uses authenticated recurrent_trapping_v1; C retains angular_profiles_v1. '
            'This integrated package comparison is not an isolated detector main-effect estimate. '
            'The original 30% independent basin-entry latency target remains unachieved when unavailable.'])
    if is_retained_development_experiment_version(contract['version']):
        population = result['acquisition_population']
        retained = population['retained_development']
        fresh = population['fresh_confirmation']
        text.extend(['', 'Acquisition provenance: four original V13 development recordings '
            'are reused; only the twelve V14 confirmation slots are new acquisitions. '
            'Original IDs, failures and scientific products remain unchanged. The new '
            'development view replaces only the separately qualified R22 C/D motion measurements.',
            f"Complete retained development acquisitions: {retained['complete_acquisition_count']}/4; "
            f"complete fresh confirmations: {fresh['complete_acquisition_count']}/12.",
            'V13 remains closed incomplete with its original twelve confirmation slots unstarted.'])
    text.extend(['', 'Run failures and unavailable evidence:', ''])
    for row in result['slots']:
        reasons = [str(row[key]) for key in ('failure', 'reason', 'science_reason') if row.get(key)]
        if row.get('latency', {}).get('reason'):
            reasons.append('latency: '+str(row['latency']['reason']))
        if reasons:
            text.append(f'- Slot {row["slot"]}: '+ '; '.join(reasons))
    text.extend(['', 'Per-run time to goal, path length, jitter, relative smoothing lag, '
        'fallback durations, failures and their denominators are retained in `result.json` '
        'and the immutable block results. Missing values are unavailable, never zero.', '',
        ('B/D use recurrent_geometry_v3; A/C use inherited PDE detection. C/D use matched '
         'rolling GESC, moving-cycle coherence and centered verification; A/B use stationary verification. '
         'A/C compares the complete acquisition package, not averaging alone. ' if v10 else
         'B/D use centroid_two_block_v2 (6s windows, 0.18m threshold, 0.50m confinement); '
         'A/C use the inherited detector. C/D use the fixed moving-cycle coherence policy. ') +
        'Labels are independently derived finite-grid model-region residence, not certified '
        'attraction dynamics. Direction references are stationary periodic GESC responses '
        'under the recorded augmented objective, not spatial gradients. Noise topology uses '
        'a three-sigma static margin; the delay receipt does not qualify delayed dynamics.', '',
        'No physical experiment, broad robustness claim, replacement acquisition or '
        'post-freeze tuning belongs to this comparison. All earlier failed evidence is retained.', '',
        f'Frozen contract: `{contract["contract_path"]}`. Git: '
        f'`{result["git"]["branch"]}` at `{result["git"]["head"]}`, with saved uncommitted '
        'task changes; no commit or push was made.', ''])
    rendered = '\n'.join(text)
    if is_retained_development_experiment_version(contract['version']):
        rendered = rendered.replace('can satisfy V13;', 'can satisfy V14;')
    return rendered


def finalize(contract, slot_receipts, suite_end):
    from ros_esc.plotting_scripts.m4_pilot import aggregate_pilot, development_latency_feasibility
    began = time.monotonic()
    end = min(suite_end, began+contract['science']['freeze_report_sec']/2)
    verify_frozen(contract)
    if [row.get('slot') for row in slot_receipts] != list(range(1, 17)):
        raise ValueError('M4 final ledger requires all sixteen unique ordered slots')
    check_receipts([row['receipt'] for row in slot_receipts])
    for row in slot_receipts:
        planned = slot_spec(contract, row['slot'])
        if (read_json(row['receipt']['path']) !=
                {key: value for key, value in row.items() if key != 'receipt'}
                or any(row.get(key) != planned[key] for key in
                       ('run_id', 'case_id', 'seed', 'arm', 'partition', 'condition', 'block',
                        'geometry', 'visible'))):
            raise ValueError('M4 final acquisition differs from its immutable identity')
    merged = {row['slot']: deepcopy(row) for row in slot_receipts}
    blocks = []
    completed_science_blocks = []
    v10_nested = []
    for block in range(4):
        path = Path(contract['root'])/'analysis'/f'block_{block}'/'block_receipt.json'
        if not path.exists():
            continue
        record = read_json(path)
        check_receipts([record['result'], *record['cases']])
        data = read_json(record['result']['path'])
        acquired = slot_receipts[block*4:block*4+4]
        if (record.get('block') != block or record.get('complete') is not True
                or record.get('integrity_passed') is not True
                or record['cases'] != [row['receipt'] for row in acquired]
                or data.get('complete') is not True or data.get('integrity_passed') is not True):
            raise ValueError('M4 final block lacks complete exact acquisition binding')
        _verify_science_rows(contract, data.get('runs', []), acquired)
        if is_arrival_experiment_version(contract['version']):
            if data.get('scientific_analysis_complete') is True:
                completed_science_blocks.append(block)
            # Verify every retained nested receipt even when scientific coverage
            # or enabled behavior prevents release. Never demand a pass to report.
            def nested_receipts(value):
                if isinstance(value, dict):
                    if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
                        yield {'path': value['path'], 'sha256': value['sha256']}
                    for item in value.values():
                        yield from nested_receipts(item)
                elif isinstance(value, list):
                    for item in value:
                        yield from nested_receipts(item)
            v10_nested.extend(nested_receipts(record))
            v10_nested.extend(nested_receipts(data))
        if is_retained_development_experiment_version(contract['version']) and block == 0:
            reuse = _load_v14_reuse(contract)
            if (data != _v14_development_document(contract, reuse)
                    or record.get('source_block') != reuse['source_block']
                    or record.get('jobs') != []):
                raise ValueError('V14 final retained block changed its allowed composition')
        for row in data['runs']:
            if row['slot'] not in range(block*4+1, block*4+5):
                raise ValueError('M4 block output crosses frozen population')
            merged[row['slot']].update(row)
        blocks.append(receipt(path))
    result = aggregate_pilot(list(merged.values()), experiment_version=contract['version'])
    result['contract'] = receipt(contract['contract_path'])
    result['block_receipts'] = blocks
    if is_arrival_experiment_version(contract['version']):
        release_path = Path(contract['root']) / 'preflight/holdout_release.json'
        result['development_release'] = ({'status': 'RELEASED', 'receipt': receipt(release_path)}
            if release_path.exists() else {'status': 'WITHHELD', 'reasons': sorted({
                str(row.get('reason') or row.get('failure')) for row in slot_receipts
                if row.get('reason') or row.get('failure')})})
        result['analysis_completion'] = dict(complete_blocks=len(completed_science_blocks),
            complete_block_numbers=completed_science_blocks, required_blocks=4,
            scientific_analysis_complete=len(completed_science_blocks) == 4,
            completed_run_count=sum(row.get('scientific_analysis_complete') is True
                                    for row in merged.values()))
        result['confirmation_scope'] = 'fresh seeds on previously exposed conditions; internal partition name holdout'
    if contract['version'] == V12_EXPERIMENT_VERSION:
        result['component_response_prerequisite'] = contract['component_response_prerequisite']
    if contract['version'] == V13_EXPERIMENT_VERSION:
        result['trapping_integrated_prerequisite'] = contract['trapping_integrated_prerequisite']
        result['component_response_prerequisite'] = contract['trapping_integrated_prerequisite']['component_response']
    if is_retained_development_experiment_version(contract['version']):
        reuse = _load_v14_reuse(contract)
        result['retained_development'] = contract['retained_development']
        result['trapping_integrated_prerequisite'] = reuse['trapping_integrated_prerequisite']
        result['component_response_prerequisite'] = reuse['trapping_integrated_prerequisite']['component_response']
    if contract['version'] == V11_EXPERIMENT_VERSION:
        feasibility = development_latency_feasibility(
            result['slots'][:4], experiment_version=contract['version'])
        result['development_latency_feasibility'] = feasibility
        if (result['development_release']['status'] == 'WITHHELD'
                and feasibility['feasible'] is not True):
            result['development_release']['reasons'].append(feasibility['reason'])
    result['git'] = {
        'branch': subprocess.check_output(['git', 'branch', '--show-current'],
            cwd=REPOSITORY, text=True, timeout=max(.1, end-time.monotonic())).strip(),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
            cwd=REPOSITORY, text=True, timeout=max(.1, end-time.monotonic())).strip(),
        'status': subprocess.check_output(['git', 'status', '--short', '--branch'],
            cwd=REPOSITORY, text=True, timeout=max(.1, end-time.monotonic())),
    }
    output = Path(contract['root'])/'report'
    output.mkdir(parents=True, exist_ok=False)
    report = render_report(result, contract)
    if is_arrival_experiment_version(contract['version']):
        if is_retained_development_experiment_version(contract['version']):
            _check_v14_receipts(contract, v10_nested)
        else:
            check_receipts(v10_nested)
        check_receipts([row['receipt'] for row in slot_receipts])
        verify_frozen(contract)
    if time.monotonic() >= end:
        raise TimeoutError('M4 final report budget exhausted')
    atomic_exclusive_json(output/'result.json', result)
    with (output/'report.md').open('x') as stream:
        stream.write(report)
    final = dict(status='REPORTED', report=receipt(output/'report.md'),
                 result=receipt(output/'result.json'), elapsed_sec=time.monotonic()-began)
    atomic_exclusive_json(output/'report_receipt.json', final)
    return {**final, 'receipt': receipt(output/'report_receipt.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('prepare',))
    parser.add_argument('--version', '--experiment-version', dest='experiment_version',
                        choices=EXPERIMENT_VERSIONS, default=DEFAULT_EXPERIMENT_VERSION)
    args = parser.parse_args()
    print(json.dumps(prepare(args.experiment_version), indent=2))
