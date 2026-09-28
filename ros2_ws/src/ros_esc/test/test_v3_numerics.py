"""Portable golden parity from pre-refactor e726774 selected numerical owners.

Fixture values were captured before removal of those owners. Tests import only
active V3 helpers; no ROS, archived module, build/install tree, or hardware.
"""
from dataclasses import asdict, replace
import json
import math
from pathlib import Path

import numpy as np
import pytest

from ros_esc.gesc_v3.numerics import (
    basin, coherence, escape, evidence, fill, fill_design, gesc, objective,
    recurrent, registry, rolling, verification,
)

FIXTURE = Path(__file__).parent/'fixtures/test_v3_numerics_golden.json'


def assert_tree(actual, expected):
    if isinstance(expected, dict):
        assert set(actual) == set(expected)
        for key, value in expected.items():
            assert_tree(actual[key], value)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for a, b in zip(actual, expected):
            assert_tree(a, b)
    elif expected is None:
        assert actual is None or (isinstance(actual, float) and math.isnan(actual))
    elif isinstance(expected, float):
        assert float(actual) == pytest.approx(expected, rel=2e-11, abs=2e-12)
    else:
        assert actual == expected


def rolling_inputs():
    for i in range(61):
        stamp = 1_000_000_000+i*200_000_000
        phase = 2*math.pi*i/15
        yaw = .01*i
        world = (1+.2*math.cos(phase), .3+.1*math.sin(phase))
        body = (math.cos(yaw)*world[0]+math.sin(yaw)*world[1],
                -math.sin(yaw)*world[0]+math.cos(yaw)*world[1])
        yield i, stamp, phase, yaw, body


def rolling_row(result):
    fields = ('instant_world', 'mean_world', 'final_body', 'final_magnitude',
              'rolling_duration_ns', 'sector_counts', 'completed_cycle_count',
              'actual_blend_weight', 'coverage_valid', 'warmup_valid',
              'qualified', 'fallback_used', 'output_valid', 'coherence',
              'coherence_lower', 'coherence_upper', 'norm_denominator', 'norm_error')
    return {name: getattr(result, name) for name in fields}


def samples(sample_type=basin.BasinSample):
    result = []
    for i in range(80):
        t = i*.2
        radius = .05+.03*math.sin(.7*t)
        x, y = .1+radius*math.cos(.7*t), -.2+.7*radius*math.sin(.7*t)
        result.append(sample_type(t,x,y,.2*t,math.nan,False,
            -2+2*(x-.1)**2+3*(y+.2)**2,math.nan,False,1))
    return tuple(result)


def raw_inputs():
    for i in range(61):
        stamp = i*200_000_000
        phase = 2*math.pi*i/15
        yield dict(observation_id=i+1,source_sequence=i+1,source_stamp_ns=stamp,
            base_x_m=.02*math.cos(.3*i*.2),base_y_m=.02*math.sin(.3*i*.2),
            raw_cost=-2+.1*math.cos(phase),sensor_world_phase_rad=phase)


def evidence_row(result):
    return dict(ready=result.ready,reason=result.reason,
        summary=asdict(result.summary),amplitude=result.amplitude,
        disagreement=result.disagreement,information_floor=result.information_floor,
        informative=result.informative,sample_ranges=result.sample_ranges,
        cycles=[dict(start_ns=c.start_ns,end_ns=c.end_ns,centroid=c.centroid,
                     sector_counts=c.sector_counts,minimum=c.minimum,qualified=c.qualified)
                for c in result.cycles])


def detector_rows(detector_class):
    rows = {}
    for kind in ('static','circle','oscillation','drift'):
        detector = detector_class(); detector.start_epoch('one',0)
        evaluations = []
        for i in range(421):
            t = i*.2
            xy = ((.01*math.cos(t),.01*math.sin(t)) if kind=='static' else
                  (.2*math.cos(.3*t),.2*math.sin(.3*t)) if kind=='circle' else
                  (.2*math.cos(2*math.pi*t/12),.001*math.sin(t)) if kind=='oscillation' else
                  (.02*t,.01*math.sin(t)))
            for r in detector.update(i*200_000_000,xy,'odom'):
                if r.confirmed_event or (r.window_completed and i==420):
                    evaluations.append(dict(stamp_ns=r.stamp_ns,branch=r.branch,
                        eligible=r.eligible,confirmed_event=r.confirmed_event,
                        persistence_count=r.persistence_count,mean_xy=r.mean_xy,
                        radius_m=r.radius_m,score_m=r.score_m))
        rows[kind] = evaluations
    return rows


@pytest.fixture(scope='module')
def golden():
    return json.loads(FIXTURE.read_text())['results']


def test_golden_measured_phase_filter(golden):
    filt = gesc.InstantaneousGesc()
    rows=[]
    for i in range(12):
        result=filt.update(1_000_000_000+i*200_000_000,-2+.1*math.cos(i*.4),i*.4)
        rows.append(asdict(result))
    assert_tree(rows,golden['gesc'])


def test_golden_rolling_mean_coherence_and_frame_rotation(golden):
    owner=rolling.RollingGesc();rows=[]
    for i,stamp,phase,yaw,body in rolling_inputs():
        obs=rolling.DirectionObservation(i+1,stamp,stamp,yaw,phase)
        owner.update(rolling.DemodulatedSample(obs,body))
        job=owner.coherence_job()
        if job is not None:
            assert owner.apply_coherence(rolling.compute_coherence(job))
        if i in (0,15,45,60):
            rows.append(rolling_row(owner.evaluate(stamp,yaw,stamp)))
    assert_tree(rows,golden['rolling'])


def test_golden_recurrent_geometry_model_nomination(golden):
    assert_tree(detector_rows(recurrent.RecurrentGeometryDetector),golden['recurrent'])


def test_golden_moving_three_revolution_raw_evidence(golden):
    owner=evidence.MovingRawEvidence();owner.start_epoch(1,0)
    for values in raw_inputs():
        obs=evidence.RawObservation(**values)
        assert owner.add(obs,1,obs.source_stamp_ns)
    result=owner.evaluate((0.,0.),.5,.072,6_000_000_000)
    assert_tree(evidence_row(result),golden['evidence'])


def proposal():
    owner=registry.FillRegistry()
    inp=fill.PreparationInput(samples(),owner.snapshot(),basin.EstimatorConfig(),
        fill_design.FillDesignConfig(),owner.config,15.8,-2.1,1.,True,20)
    return owner,inp,fill.compute_fill_proposal(inp)


def test_golden_basin_fill_preparation_and_registry(golden):
    owner,inp,prepared=proposal()
    assert_tree(dict(prepared.version_values),golden['fill'])
    assert_tree(dict(prepared.rejection_counts),golden['fill_rejections'])
    staged=owner.stage_commit(dict(prepared.version_values),prepared.samples,
        expected_generation=prepared.registry_generation,strict=True)
    assert owner.active_count==0
    old,active=owner.commit_staged(staged)
    assert old is None and (active.fill_id,active.cluster_id,active.revision)==(1,1,1)
    with pytest.raises(ValueError,match='generation'):
        owner.commit_staged(staged)
    assert owner.active_count==1 and owner.generation==1
    assert active.center.flags.writeable is False
    assert active.covariance.flags.writeable is False
    value=objective.compose_cost(-2.,(.13,-.18),20.,fills=(active,),
        affine_terms=(objective.AffineTerm((.1,-.2),(.2,-.1),15.),))
    assert_tree(asdict(value),golden['objective'])


def make_controller():
    # Original public controller math is separately retained by this refactor.
    from ros_esc.config_parsing import parse_object_config  # initialize legacy circular import
    from ros_esc.controller_node.controller_objects.turtlebot_vehicle import Directional_Controller
    return Directional_Controller({'k_vx':.5,'k_wz':5.},dict(
        wheel_radius=.033,wheel_distance=.16,wheel_max_rpm=77.,set_max_vx=.1,set_max_wz=.5))


def tracking_rows(command):
    controller=make_controller()
    return [command(controller,(.1,-.2),(.02,-.1),yaw,t,approach=approach).tolist()
            for yaw,t,approach in ((0.,0.,True),(.4,1.,False),(-1.,5.,False),(2.,11.,False))]


def test_golden_centered_tracking_and_escape_progress(golden):
    assert_tree(tracking_rows(verification.tracking_command),golden['tracking'])
    geometry=escape.EscapeGeometry(1,0.,0.,.5,0.,1.,0.)
    tracker=escape.EscapeProgressTracker(geometry)
    rows=[]
    for i in range(31):
        r=tracker.update(escape.Pose2D(i*.2,.02*i,0.,0.))
        if i in (15,25,30):rows.append(asdict(r))
    # Unavailable diagnostics use JSON null in the golden fixture.
    rows=json.loads(json.dumps(rows,default=float).replace('NaN','null'))
    assert_tree(rows,golden['escape_progress'])
    assert_tree([escape.recenter_command((1.,.2),yaw,1.) for yaw in (0.,.5,2.)],golden['escape_command'])


def test_rejected_sample_and_new_objective_do_not_reuse_rolling_history():
    owner=rolling.RollingGesc()
    obs=rolling.DirectionObservation(1,1_000_000_000,1_000_000_000,0.,0.)
    owner.update(rolling.DemodulatedSample(obs,(1.,0.)))
    assert owner.evaluate(obs.source_stamp_ns,0.,obs.source_stamp_ns).output_valid
    assert not owner.evaluate(obs.source_stamp_ns+500_000_001,0.,obs.source_stamp_ns+500_000_001).output_valid
    changed=replace(obs,observation_id=2,source_stamp_ns=1_200_000_000,
                    receipt_stamp_ns=1_200_000_000,objective_revision=1)
    result=owner.update(rolling.DemodulatedSample(changed,(1.,0.)))
    assert result.reset_reason=='objective_changed' and result.completed_cycle_count==0
    assert owner.evaluate(changed.source_stamp_ns,0.,changed.source_stamp_ns).output_valid


def test_old_worker_result_cannot_change_new_direction():
    owner=rolling.RollingGesc();last=None
    for i,stamp,phase,yaw,body in rolling_inputs():
        obs=rolling.DirectionObservation(i+1,stamp,stamp,yaw,phase)
        owner.update(rolling.DemodulatedSample(obs,body))
        if i==45:last=owner.coherence_job()
    assert last is not None
    assert not owner.apply_coherence(rolling.compute_coherence(last))
    owner.invalidate('objective_changed')
    assert not owner.apply_coherence(rolling.compute_coherence(last))


def test_coherence_budget_is_bounded_and_returns_unavailable():
    budget=coherence.EvaluationBudget(max_calls=1)
    result=coherence.linear_norm_integral((1.,0.),(0.,1.),budget=budget)
    assert not result['available'] and result['reason']=='norm_evaluation_budget'
    assert budget.calls==1


def test_slow_full_cycle_uses_window_budget_in_worker():
    owner=rolling.RollingGesc()
    for i in range(451):
        stamp=1_000_000_000+i*200_000_000
        obs=rolling.DirectionObservation(i+1,stamp,stamp,0.,2*math.pi*i/150)
        owner.update(rolling.DemodulatedSample(obs,(1.,.3)))
    job=owner.coherence_job()
    assert job is not None
    response=rolling.compute_coherence(job)
    assert owner.apply_coherence(response)
    result=owner.evaluate(stamp,0.,stamp)
    assert result.qualified and result.output_valid
    assert 2048 < result.norm_new_evaluations <= coherence.MAX_NORM_CALLS


def test_duplicate_raw_sample_does_not_refresh_state_or_receipt():
    owner=evidence.MovingRawEvidence();owner.start_epoch(1,0)
    obs=evidence.RawObservation(**next(raw_inputs()))
    assert owner.add(obs,1,0)
    assert not owner.add(obs,99,100)
    assert owner.records[0].filter_state==1 and owner.records[0].filter_stamp_ns==0
    assert not owner.add(replace(obs,raw_cost=-5.),1,100)
    assert owner.reason=='conflicting_observation' and not owner.records


def test_source_gap_resets_filter_and_new_sample_can_recover():
    filt=gesc.InstantaneousGesc()
    filt.update(1_000_000_000,-2.,0.)
    filt.update(1_200_000_000,-2.,.2)
    result=filt.update(2_000_000_000,-2.,.4)
    assert result.dt_sec==0 and result.state_before==0
    with pytest.raises(ValueError,match='strictly increase'):
        filt.update(2_000_000_000,-2.,.4)


def test_pure_numerics_do_not_import_archived_or_ros_owners():
    import ast
    root=Path(rolling.__file__).parent
    for path in root.glob('*.py'):
        for item in ast.walk(ast.parse(path.read_text())):
            if isinstance(item,ast.ImportFrom):
                assert not (item.module or '').startswith(('rclpy','ros_esc_interfaces','ros_esc.'))
            if isinstance(item,ast.Import):
                assert not any(n.name.startswith(('rclpy','ros_esc_interfaces','ros_esc.')) for n in item.names)
