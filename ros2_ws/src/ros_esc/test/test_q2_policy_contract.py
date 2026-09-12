"""Independent Q2 policy identity, compatibility and synthetic oracle checks.

The immutable external helper is a test oracle only. No retained observation,
field model, reference evaluation, bag or confirmation partition is opened.
"""
from copy import deepcopy
from dataclasses import replace
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import pytest

from ros_esc.v2_direction_policy import (
    DIRECTION_POLICIES, MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY,
    policy_descriptor, policy_config_sha256, policy_metadata,
    validate_policy, validate_policy_metadata,
)
from ros_esc.filter_node.rolling_gesc import (
    DemodulatedSample, ObjectiveIdentity, RollingGesc, RollingGescConfig,
)
from test_rolling_gesc import feed, observation, times, ns

PACKAGE=Path(__file__).parents[1]
REPO=PACKAGE.parents[2]
EXTERNAL=Path('/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1')
ORACLE=EXTERNAL/'preflight/policy_math.py'
ORACLE_SHA256='f3bdfb9c99f852c3f72df5e4c0922d2d5c044f7eb676a54d663ee1653d3e61a1'


@pytest.mark.parametrize('policy',DIRECTION_POLICIES)
def test_descriptor_hash_is_canonical_and_callers_cannot_mutate_owner(policy):
    descriptor=policy_descriptor(policy)
    expected=hashlib.sha256(json.dumps(descriptor,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    assert policy_config_sha256(policy)==expected
    assert validate_policy_metadata(policy_metadata(policy))==policy
    descriptor['configured_mean_weight']=99.
    assert policy_descriptor(policy)['configured_mean_weight']==(.75 if policy==MOVING_CYCLE_POLICY else .5)
    assert policy_config_sha256(policy)==expected


@pytest.mark.parametrize('value',[None,'','moving_cycle','three_cycle','MOVING_CYCLE_COHERENCE_V1',True,1])
def test_unknown_policy_never_falls_back_silently(value):
    with pytest.raises(ValueError):validate_policy(value)


@pytest.mark.parametrize('overrides',[
    {'continuous_search_mode':'stationary_v1'},
    {'algorithm_profile':'legacy'},
    {'use_sim_time':False},{'use_sim_time':'true'},{'use_sim_time':1},
])
def test_new_policy_requires_actual_rolling_robust_simulation(overrides):
    selected={'continuous_search_mode':'rolling_gesc_v2','algorithm_profile':'robust_gaussian_v1','use_sim_time':True}
    selected.update(overrides)
    with pytest.raises(ValueError):validate_policy(MOVING_CYCLE_POLICY,**selected)
    assert validate_policy(THREE_CYCLE_POLICY,**selected)==THREE_CYCLE_POLICY


@pytest.mark.parametrize('fault',['weight','threshold','units','hash','name','extra','missing'])
def test_policy_metadata_cannot_relabel_old_or_arbitrary_behavior(fault):
    value=policy_metadata(MOVING_CYCLE_POLICY)
    if fault=='weight':value['config']['configured_mean_weight']=.5
    elif fault=='threshold':value['config']['coherence_threshold']=.2
    elif fault=='units':value['config']['output_units']='untyped_vector'
    elif fault=='hash':value['config_sha256']='0'*64
    elif fault=='name':value['policy_name']=THREE_CYCLE_POLICY
    elif fault=='extra':value['extra']=True
    else:value.pop('config')
    with pytest.raises(ValueError):validate_policy_metadata(value)


def test_existing_nested_message_definitions_are_identical_to_closed_d3():
    contract=json.loads((EXTERNAL/'preflight/contract.json').read_text())
    frozen={item['path']:item['sha256'] for item in contract['source_files']}
    for name in ['GescDirectionDiagnostics','SynchronizedObservation','ObjectiveCostSample','SourceSampleProvenance']:
        path=REPO/'ros2_ws/src/ros_esc_interfaces/msg'/f'{name}.msg'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==frozen[str(path)]


@pytest.fixture(scope='module')
def oracle():
    assert ORACLE.is_file(), 'required immutable external oracle is unavailable'
    assert hashlib.sha256(ORACLE.read_bytes()).hexdigest()==ORACLE_SHA256
    spec=importlib.util.spec_from_file_location('q2_immutable_d3_math_oracle',ORACLE)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('a,b',[
    ((2.,-1.),(2.,-1.)),((1.,0.),(-1.,0.)),
    ((1.,0.),(0.,1.)),((1.,1.),(1.+1e-10,1.-1e-10)),
])
def test_runtime_segment_matches_immutable_external_oracle(oracle,a,b):
    from ros_esc.filter_node.cycle_coherence import linear_norm_integral
    expected=oracle.linear_norm_integral(a,b)
    actual=linear_norm_integral(a,b)
    assert expected['available'] and actual['available']
    assert actual['mean_norm']==pytest.approx(expected['mean_norm'],rel=1e-12,abs=1e-13)
    assert actual['mean_error']==pytest.approx(expected['mean_error'],rel=1e-10,abs=1e-15)


def test_moving_mean_qualifies_despite_unchanged_old_cycle_disagreement():
    moving=RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY))
    legacy=RollingGesc()
    vector=lambda t:(math.cos(.4*t),math.sin(.4*t))
    timeline=times(12.,40)
    new=feed(moving,timeline,vector=vector)[-1]
    old=feed(legacy,timeline,vector=vector)[-1]
    assert new.mean_full and new.coverage_valid and new.warmup_valid
    assert not new.cycles_valid and not old.qualified
    assert new.qualified and new.coherence_lower>=.25
    assert new.mean_world==pytest.approx(old.mean_world,abs=1e-12)
    snapshot=moving.evaluate(ns(12),.7,ns(12))
    expected_world=[.25*a+.75*b for a,b in zip(new.instant_world,new.mean_world)]
    expected_body=[math.cos(.7)*expected_world[0]+math.sin(.7)*expected_world[1],
                   -math.sin(.7)*expected_world[0]+math.cos(.7)*expected_world[1]]
    assert snapshot.output_valid and snapshot.actual_blend_weight==.75
    assert snapshot.final_body==pytest.approx(expected_body,abs=1e-12)
    assert snapshot.direction_policy==MOVING_CYCLE_POLICY
    assert snapshot.policy_config_sha256==policy_config_sha256(MOVING_CYCLE_POLICY)


def test_finite_zero_instant_preserves_informative_mean_and_timer_cache():
    core=RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY))
    feed(core,times(10.,40),vector=lambda t:(1.,0.))
    result=feed(core,[10.025],vector=lambda t:(0.,0.))[-1]
    assert result.qualified and result.instantaneous_magnitude==0.
    snapshot=core.evaluate(ns(10.025),0.,ns(10.025))
    assert snapshot.output_valid and not snapshot.fallback_used and snapshot.actual_blend_weight==.75
    assert snapshot.final_body==pytest.approx([.75*result.mean_world[0],0.],abs=1e-12)
    for _ in range(5):
        repeated=core.evaluate(ns(10.025),0.,ns(10.025))
        assert repeated.final_body==snapshot.final_body
        assert repeated.norm_window_evaluations==snapshot.norm_window_evaluations


def test_real_objective_reset_clears_new_policy_warmup_without_stale_fallback():
    core=RollingGesc(RollingGescConfig(direction_policy=MOVING_CYCLE_POLICY))
    before=feed(core,times(10.,40))[-1]
    assert before.qualified
    after=feed(core,[10.025],objective=ObjectiveIdentity(2))[-1]
    assert after.reset_sequence>before.reset_sequence
    assert not after.qualified and not after.warmup_valid and after.completed_cycle_count==0
    fresh=core.evaluate(ns(10.025),0.,ns(10.025))
    assert fresh.output_valid and fresh.fallback_used and fresh.actual_blend_weight==0.
    stale=core.evaluate(ns(10.526),0.,ns(10.526))
    assert not stale.output_valid and not stale.fallback_used
    assert stale.final_body is None


def test_default_zero_output_and_half_weight_semantics_remain_unchanged():
    core=RollingGesc()
    feed(core,times(10.,40))
    result=core.evaluate(ns(10.),0.,ns(10.))
    assert result.output_valid and result.actual_blend_weight==.5
    assert result.direction_policy==THREE_CYCLE_POLICY
    zero=RollingGesc()
    feed(zero,[0.],vector=lambda t:(0.,0.))
    value=zero.evaluate(0,0.,0)
    assert value.output_valid and value.final_body==(0.,0.)
