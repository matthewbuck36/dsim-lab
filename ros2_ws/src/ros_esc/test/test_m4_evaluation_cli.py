"""Finite staged CLI fixtures; no bags, ROS graph or field models evaluated."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace as Obj

import pytest

from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from ros_esc_interfaces.msg import AlgorithmEvent, GaussianFill

ROOT = Path(__file__).resolve().parents[4]
TOOLS = ROOT/'docs/codex/gesc_gaussian/v2/tools'
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('m4_evaluation_test_cli', TOOLS/'evaluate_m4.py')
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def stamp(sec):
    return Obj(sec=int(sec), nanosec=round((sec-int(sec))*1e9))


def bag(messages):
    rows, aliases = {}, {}
    for alias, values in messages.items():
        topic = '/'+alias
        aliases[alias] = dict(alias=alias, topic=topic)
        rows[topic] = [BagRecord(topic, 'fixture', int(t*1e9), int(t*1e9), None, False, m, True)
                       for t, m in values]
    return BagData(Path('/unused'), {}, aliases, rows, 1_000_000_000, None)


def planned(arm='A', slot=1):
    block=(slot-1)//4
    return dict(slot=slot, block=block, run_id=f'run-{slot}', case_id=f'case-{slot}', seed=10+block,
                arm=arm, partition='development' if block == 0 else 'holdout',
                condition='nominal', geometry='primary',
                resolved_scenario={'algorithm': {'launch_overrides': {}}})


def event(kind, decision=20., source=15.):
    message=AlgorithmEvent()
    message.event_type=kind
    message.stamp.sec=int(decision)
    message.source_timestamp=source
    message.source_timestamp_valid=True
    return message


def test_legacy_primary_uses_decision_stamp_not_earlier_source_support():
    b=bag({'algorithm_events': [(22.,event(11, 20.,15.))],
           'timekeeper': [(1.,Obj(start_time=1.,mode='sim time'))]})
    confirmations, _, _, errors=cli._confirmation_inputs(b,planned())
    assert errors == []
    assert confirmations == [dict(decision_ns=20_000_000_000, source_ns=16_000_000_000)]
    b=bag({'algorithm_events': [(22.,event(11,20.,15.))]})
    assert cli._confirmation_inputs(b,planned())[3]


def test_centroid_primary_preserves_authoritative_typed_decision_and_support(monkeypatch):
    audit=[dict(diagnostic_publication_stamp_ns=20,diagnostic_source_stamp_ns=16)]
    monkeypatch.setattr(cli.runner,'_centroid_convergence_evaluation_events', lambda *a: ([],audit,None))
    values,_,actual,errors=cli._confirmation_inputs(bag({}),planned('D',4))
    assert values == [dict(decision_ns=20,source_ns=16)] and actual == audit and not errors


def test_moving_activation_uses_commit_owner_not_prepared_or_mirror(monkeypatch):
    b=bag({'algorithm_events':[],'algorithm_state':[],'gaussian_fills':[]})
    monkeypatch.setattr(cli.analysis,'_v2_lifecycle_analysis',lambda *a:
        ({'status':'valid','errors':[],'audit':{'commits':[{'committed_at_ns':30}]}},{},{}))
    result=cli._intervention_inputs(b,{},planned('C',3),[])
    assert result['complete'] is True and result['stamp_ns'] == 30
    monkeypatch.setattr(cli.analysis,'_v2_lifecycle_analysis',lambda *a:
        ({'status':'invalid','errors':['unbound commit'],'audit':{'commits':[{'committed_at_ns':30}]}},{},{}))
    assert cli._intervention_inputs(b,{},planned('C',3),[])['complete'] is False


def test_missing_event_aliases_or_terminal_event_never_become_zero_errors():
    result=cli._error_counts(bag({}),planned(),[],{})
    assert result['wrong_fills'] is result['wrong_goals'] is None
    b=bag({'algorithm_events':[], 'gaussian_fills':[],
           'algorithm_state':[(20.,Obj(state_valid=True,state=7))]})
    result=cli._error_counts(b,planned(),[],{})
    assert result['wrong_fills']==0 and result['wrong_goals'] is None


def test_ranked_goal_requires_external_global_region_evidence(monkeypatch):
    monkeypatch.setattr(cli.runner,'_ranked_goal_evidence',lambda *a:(True,{},None))
    b=bag({'algorithm_events':[], 'gaussian_fills':[], 'algorithm_state':[]})
    outcomes={'local_recovery_stage':{'stage_a_completion_stamp':10}}
    events=[(30,event(30))]
    assert cli._error_counts(b,planned(),events,outcomes)['wrong_goals'] is None
    outcomes['post_recovery_global_proximity_passed']=True
    outcomes['simulation_ground_truth']='passed'
    assert cli._error_counts(b,planned(),events,outcomes)['wrong_goals']==0


def test_stopped_acquisition_distinguishes_suppression_from_natural_zero():
    state=Obj(state_valid=True,state=2,previous_state=1)
    message=Obj(final_command=[0.]*6,gesc_command_unsaturated=[0.]*6,
                combined_command_unsaturated=[0.]*6,final_command_valid=True,
                gesc_command_unsaturated_valid=True,combined_command_unsaturated_valid=True)
    b=bag({'algorithm_state':[(2.,state)],'control_diagnostics':[(2.1,message)]})
    result=cli._motion_metrics(b,planned('C',3))
    assert result['mandatory_stopped_acquisitions'] is None and result['zero_command_samples']==1
    message.gesc_command_unsaturated[0]=.05
    result=cli._motion_metrics(b,planned('C',3))
    assert result['mandatory_stopped_acquisitions'] is None
    assert result['potentially_suppressed_command_samples']==1
    message.final_command[0]=.05
    state.state=1
    assert cli._motion_metrics(b,planned('C',3))['mandatory_stopped_acquisitions']==0
    state.state=7
    assert cli._motion_metrics(b,planned('C',3))['potentially_suppressed_command_samples']==0


def test_labels_are_durably_frozen_before_any_event_join_and_missing_goal_is_none(monkeypatch):
    calls=[]
    labels={'exposure_end_ns':None}
    monkeypatch.setattr(cli.metrics,'analyze_labels',lambda *a,**k: (calls.append('labels') or labels))
    monkeypatch.setattr(cli,'_confirmation_inputs',lambda *a: (calls.append('events') or ([],[],[],[])))
    monkeypatch.setattr(cli,'_intervention_inputs',lambda *a: dict(complete=True,stamp_ns=None,errors=[]))
    monkeypatch.setattr(cli,'_error_counts',lambda *a: dict(wrong_fills=None,wrong_goals=None))
    monkeypatch.setattr(cli.metrics,'join_first_opportunity',lambda *a,**k: dict(observed=False))
    row={**planned(), 'runner_result':{'outcomes':{}},'status':'COMPLETE','integrity_passed':True}
    result,normalized=cli.analyze_run_data(row,planned(),bag({}),{}, {},
        freeze_labels=lambda value: (calls.append('freeze') or {'path':'fixture','sha256':'fixture'}))
    assert calls==['labels','freeze','events'] and normalized is None
    assert result['time_to_goal_sec'] is None and result['combined_sequence_passed'] is None
    assert result['path_length']['status']=='unavailable'


def contract_fixture(tmp_path):
    contract=dict(version=cli.metrics.VERSION, root=str(tmp_path), contract_path=str(tmp_path/'contract.json'),
                  runs=[planned(arm,slot) for slot,arm in enumerate('ABCD',1)])
    atomic_exclusive_json(tmp_path/'contract.json',contract)
    return contract


def block_fixture(tmp_path):
    contract=contract_fixture(tmp_path)
    directory=tmp_path/'analysis/block_0'
    directory.mkdir(parents=True)
    rows=[]
    for p in contract['runs']:
        row={**p,'status':'COMPLETE','integrity_passed':True}
        if p['arm'] in ('C','D'):
            path=directory/f"slot_{p['slot']}_normalized.json"
            atomic_exclusive_json(path,{'run_id':p['run_id']})
            row['normalized_inputs']=cli.receipt(path)
        rows.append(row)
    labels=dict(version=cli.metrics.VERSION,block=0,complete=True,integrity_passed=True,
                runs=rows,input_files=[],contract=cli.receipt(contract['contract_path']))
    atomic_exclusive_json(directory/'labels.json',labels)
    return contract,directory,labels


def test_summary_retains_four_rows_when_reference_jobs_missing_and_reads_no_bag(tmp_path,monkeypatch):
    contract,directory,labels=block_fixture(tmp_path)
    monkeypatch.setattr(cli,'read_run_bag',lambda *a,**k:pytest.fail('summary reopened a bag'))
    result=cli.summary_stage(contract,0)
    assert len(result['runs'])==4
    assert [r['slot'] for r in result['runs']]==[1,2,3,4]
    for row in result['runs'][2:]:
        assert row['direction_analysis_complete'] is False
        assert row['direction_unavailable_reason']=='reference_job_no_complete_result'
    aggregate=cli.metrics.aggregate_pilot(result['runs'])
    assert aggregate['direction_scheduled_total']==192
    with pytest.raises(FileExistsError):
        cli.summary_stage(contract,0)


def test_summary_rejects_incomplete_reference_and_contract_tampering(tmp_path):
    contract,directory,labels=block_fixture(tmp_path)
    row=labels['runs'][2]
    partial=dict(slot=3,run_id=row['run_id'],normalized_inputs=row['normalized_inputs'],
                 contract=labels['contract'],complete=False)
    atomic_exclusive_json(directory/'slot_3_references.json',partial)
    with pytest.raises(ValueError,match='incomplete or mismatched'):
        cli.summary_stage(contract,0)
    (tmp_path/'contract.json').write_text('{}')
    with pytest.raises(ValueError,match='retained input changed'):
        cli.summary_stage(contract,0)


def test_labels_stage_reads_each_reserved_bag_once_and_preserves_exclusive_stage(tmp_path,monkeypatch):
    contract=contract_fixture(tmp_path)
    (tmp_path/'analysis/block_0').mkdir(parents=True) # existing outer hook owns directory
    geom=tmp_path/'geometry.json'; atomic_exclusive_json(geom,{'geometry':'fixture'})
    reads=[]
    for p in contract['runs']:
        p['geometry_receipt']=cli.receipt(geom)
    monkeypatch.setattr(cli,'_acquired',lambda c,p: ({**p,'run_directory':f"/run/{p['slot']}"}, {'path':'fixture','sha256':'fixture'}))
    def yaml(path):
        return {'algorithm':{'launch_overrides':{}}} if path.name=='resolved_scenario.yaml' else {}
    monkeypatch.setattr(cli,'load_yaml',yaml)
    monkeypatch.setattr(cli.metrics,'science_aliases',lambda *a,**k:('pose','events'))
    monkeypatch.setattr(cli.runner,'build_v2_stream_config',lambda *a:{})
    monkeypatch.setattr(cli,'read_run_bag',lambda path,**k: reads.append(str(path)))
    def analyze(acquired,planned,*a,freeze_labels):
        ref=freeze_labels({'positions_only':True})
        return {**acquired,'labels':ref},None
    monkeypatch.setattr(cli,'analyze_run_data',analyze)
    result=cli.labels_stage(contract,0)
    assert len(reads)==4 and len(set(reads))==4 and len(result['runs'])==4
    assert all(Path(r['labels']['path']).is_file() for r in result['runs'])
    with pytest.raises(FileExistsError): cli.labels_stage(contract,0)
    assert len(reads)==4


def test_reference_stage_consumes_exact_snapshot_without_bag_and_keeps_partial_receipts(tmp_path,monkeypatch):
    contract,directory,labels=block_fixture(tmp_path)
    row=labels['runs'][2]
    normalized={k:row[k] for k in ('run_id','arm','partition','condition')}
    path=Path(row['normalized_inputs']['path']); path.write_text(json.dumps(normalized))
    row['normalized_inputs']=cli.receipt(path)
    lab=directory/'pose-labels.json';atomic_exclusive_json(lab,{})
    row['labels']=cli.receipt(lab);row['acquisition_receipt']=cli.receipt(lab)
    model=directory/'model.json';atomic_exclusive_json(model,{})
    row['binding']={'binding':{'verified':'sensor'},'selected_configurations':{'cost_function_config_filepath':cli.receipt(model)}}
    labels_path=directory/'labels.json';labels_path.write_text(json.dumps(labels))
    contract['runs'][2]['resolved_scenario']['sources']=[]
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    called=[]
    monkeypatch.setattr(truth,'_model',lambda *a:(called.append(a) or (object(),model)))
    monkeypatch.setattr(cli,'read_run_bag',lambda *a,**k:pytest.fail('reference reopened bag'))
    def evaluate(inputs,**kwargs):
        kwargs['on_result']({'number':1})
        return {'rows':[{'number':i} for i in range(1,25)], 'summary':{},'supplemental':{}}
    monkeypatch.setattr(cli.metrics,'evaluate_direction_targets',evaluate)
    result=cli.references_stage(contract,3)
    assert result['complete'] is True and len(called)==1
    assert (directory/'slot_3_partial_references/target_1.json').is_file()
    assert (directory/'slot_3_references.json').is_file()


@pytest.mark.parametrize('law_errors', [[], ['missing objective component']])
def test_complete_nonempty_objective_censors_latency_at_composition_publication(monkeypatch,law_errors):
    observed=[]
    monkeypatch.setattr(cli.metrics,'analyze_labels',lambda *a,**k:{'exposure_end_ns':99})
    monkeypatch.setattr(cli,'_confirmation_inputs',lambda *a: ([],[],[],[]))
    monkeypatch.setattr(cli,'_intervention_inputs',lambda *a: dict(complete=True,stamp_ns=40,errors=[]))
    monkeypatch.setattr(cli,'_error_counts',lambda *a: dict(wrong_fills=None,wrong_goals=None))
    monkeypatch.setattr(cli,'_motion_metrics',lambda *a: dict(mandatory_stopped_acquisitions=None))
    observations=[{'objective': {'complete':True,'composition_stamp_ns':30,'weights':[1.,1.,1.],
                                'gaussian_fills':[],'affine_terms':[{'anchor':[0.,0.],'vector':[1.,0.]}]}}]
    qualification={'qualified':not law_errors,'integrity_errors':law_errors}
    monkeypatch.setattr(cli.analysis,'prepare_m4_direction_inputs',lambda *a,**k:(observations,qualification))
    monkeypatch.setattr(cli.metrics,'normalize_direction_targets',lambda *a,**k:{'supplemental':{},'qualification':qualification})
    monkeypatch.setattr(cli.metrics,'join_first_opportunity',lambda *a,**k: (observed.append(k) or {}))
    p=planned('C',3)
    result,_=cli.analyze_run_data({**p,'runner_result':{'outcomes':{}}},p,bag({}),{}, {},
                                 freeze_labels=lambda value: {'path':'fixture','sha256':'fixture'})
    assert observed[0]['intervention_ns']==30
    assert observed[0]['intervention_evidence_complete'] is (not bool(law_errors))
    assert result['intervention']['first_nonempty_recorded_law_ns']==30


def d3_labels_fixture(tmp_path, monkeypatch):
    """Exercise real stage writes/receipts with existing finite stage seams."""
    contract = contract_fixture(tmp_path)
    geometry = tmp_path/'geometry.json'
    model = tmp_path/'model.json'
    acquired = tmp_path/'acquired.json'
    for path in (geometry, model, acquired):
        atomic_exclusive_json(path, {})
    acquisition_ref, model_ref = cli.receipt(acquired), cli.receipt(model)
    for planned_run in contract['runs']:
        planned_run['geometry_receipt'] = cli.receipt(geometry)
        planned_run['resolved_scenario']['sources'] = []
    monkeypatch.setattr(cli, '_acquired', lambda c, p:
        ({**p, 'run_directory': f"/run/{p['slot']}"}, acquisition_ref))
    monkeypatch.setattr(cli, 'load_yaml', lambda path:
        contract['runs'][0]['resolved_scenario'] if path.name == 'resolved_scenario.yaml' else {})
    monkeypatch.setattr(cli.metrics, 'science_aliases', lambda *a, **k: ('pose', 'events'))
    monkeypatch.setattr(cli.runner, 'build_v2_stream_config', lambda *a: {})
    bag_reads = []
    monkeypatch.setattr(cli, 'read_run_bag', lambda path, **k: bag_reads.append(str(path)))
    def analyze(acquisition, planned_run, *args, freeze_labels):
        labels = freeze_labels({'positions_only': True, 'slot': planned_run['slot']})
        normalized = ({key: planned_run[key] for key in ('run_id', 'arm', 'partition', 'condition')}
                      if planned_run['arm'] in ('C', 'D') else None)
        return {**acquisition, 'labels': labels, 'binding': {
            'binding': {'verified': 'sensor'},
            'selected_configurations': {'cost_function_config_filepath': model_ref}}}, normalized
    monkeypatch.setattr(cli, 'analyze_run_data', analyze)
    return contract, bag_reads


@pytest.mark.parametrize('isolated', [False, True])
def test_d3_labels_writer_receipts_do_not_reread_published_artifacts(tmp_path, monkeypatch, isolated):
    contract, bag_reads = d3_labels_fixture(tmp_path, monkeypatch)
    directory = tmp_path/'diagnostic' if isolated else tmp_path/'analysis/block_0'
    kwargs = {'output_directory': directory} if isolated else {}
    actual_open = Path.open
    immediate_reads = []
    def opened(path, mode='r', *args, **kwargs):
        if ('r' in mode and path.parent == directory
                and path.name.endswith(('_labels.json', '_normalized.json'))):
            immediate_reads.append(path.name)
        return actual_open(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', opened)
    result = cli.labels_stage(contract, 0, **kwargs)
    assert bag_reads == [f'/run/{slot}' for slot in range(1, 5)]
    artifacts = [row[key] for row in result['runs']
                 for key in ('labels', 'normalized_inputs') if key in row]
    assert len(artifacts) == 6
    for ref in artifacts:
        path = Path(ref['path'])
        assert path.parent == directory.resolve()
        with actual_open(path, 'rb') as stream:
            assert ref['sha256'] == hashlib.sha256(stream.read()).hexdigest()
    assert json.loads((directory/'labels.json').read_text()) == result
    if isolated:
        assert not (tmp_path/'analysis').exists()
    with pytest.raises(FileExistsError):
        cli.labels_stage(contract, 0, **kwargs)
    assert len(bag_reads) == 4
    assert immediate_reads == []


@pytest.mark.parametrize('artifact', ['labels', 'normalized_inputs'])
def test_d3_references_consume_writer_receipts_and_reject_changed_bytes(tmp_path, monkeypatch, artifact):
    contract, bag_reads = d3_labels_fixture(tmp_path, monkeypatch)
    result = cli.labels_stage(contract, 0)
    row = result['runs'][2]
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    monkeypatch.setattr(truth, '_model', lambda *a: (object(), tmp_path/'model.json'))
    def evaluate(inputs, **kwargs):
        assert inputs == {key: row[key] for key in ('run_id', 'arm', 'partition', 'condition')}
        return {'rows': [{'number': number} for number in range(1, 25)],
                'summary': {}, 'supplemental': {}}
    monkeypatch.setattr(cli.metrics, 'evaluate_direction_targets', evaluate)
    assert cli.references_stage(contract, 3)['complete']
    path = Path(row[artifact]['path'])
    path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(ValueError, match='retained input changed'):
        cli.references_stage(contract, 3)
    assert len(bag_reads) == 4


def test_d3_isolated_labels_output_preserves_default_content_except_declared_paths(tmp_path, monkeypatch):
    contract, bag_reads = d3_labels_fixture(tmp_path, monkeypatch)
    default_directory = tmp_path/'analysis/block_0'
    isolated_directory = tmp_path/'diagnostic'
    default = cli.labels_stage(contract, 0)
    isolated = cli.labels_stage(contract, 0, output_directory=isolated_directory)
    assert json.loads(json.dumps(isolated).replace(str(isolated_directory), str(default_directory))) == default
    assert len(bag_reads) == 8
    assert {path.name for path in default_directory.iterdir()} == {path.name for path in isolated_directory.iterdir()}
    for original in default_directory.iterdir():
        actual = (isolated_directory/original.name).read_text()
        assert actual.replace(str(isolated_directory), str(default_directory)) == original.read_text()
