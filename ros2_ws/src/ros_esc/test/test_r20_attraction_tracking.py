"""R20 pure probe checks and prospectively fixed midpoint-unicycle component.

Integration and perturbations are frozen in external tracking_integration_plan.
No ROS executor, Gazebo, field model, noise draw or estimator is used here.
"""
import json
import math
import os
from pathlib import Path

import numpy as np
import pytest

from ros_esc.supervisor_node.centered_verification import (
    APPROACH_NS, COLLECTION_NS, TOTAL_NS, MODES,
    attraction_probe_command, attraction_probe_reference,
    tracking_command, tracking_controller)

CONFIG = Path(__file__).parents[1]/'ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage_m4_v6_gain_half.json'
CENTER = (.23, -.41)
THETA0 = .37
CASES = ((0., 0.), (.02, .25), (-.02, -.25))


@pytest.mark.parametrize('time,expected_radius,radial_second', [(0., .115, .1), (7., .165, -.1), (14., .115, .1), (21., .165, -.1), (28., .115, .1)])
def test_reference_axis_extrema_have_independent_tangent_kinematics(time, expected_radius, radial_second):
    reference = attraction_probe_reference(CENTER, THETA0, time)
    omega = 2.*math.pi/28.
    assert math.dist(reference['position'], CENTER) == pytest.approx(expected_radius)
    assert reference['speed'] == pytest.approx(omega*expected_radius)
    assert reference['yaw_rate'] == pytest.approx(omega*(1.-radial_second/expected_radius))
    assert reference['yaw'] == pytest.approx(THETA0+omega*time+math.pi/2.)


@pytest.mark.parametrize('time', [.2, 3.7, 12.8, 27.7])
def test_analytic_velocity_acceleration_and_yaw_rate_match_local_geometry(time):
    dt = 1e-4
    left = attraction_probe_reference(CENTER, THETA0, time-dt)
    middle = attraction_probe_reference(CENTER, THETA0, time)
    right = attraction_probe_reference(CENTER, THETA0, time+dt)
    assert middle['velocity'] == pytest.approx((np.array(right['position'])-left['position'])/(2.*dt), abs=1e-9)
    assert middle['acceleration'] == pytest.approx((np.array(right['velocity'])-left['velocity'])/(2.*dt), abs=1e-9)
    assert middle['yaw_rate'] == pytest.approx((right['yaw']-left['yaw'])/(2.*dt), abs=1e-9)
    assert np.dot(middle['velocity'], (math.cos(middle['yaw']), math.sin(middle['yaw']))) == pytest.approx(middle['speed'])


def test_reference_is_closed_and_commands_are_exact_on_the_moving_tangent():
    controller = tracking_controller(CONFIG)
    first = attraction_probe_reference(CENTER, THETA0, 0.)
    final = attraction_probe_reference(CENTER, THETA0, 28.)
    assert final['position'] == pytest.approx(first['position'])
    assert final['velocity'] == pytest.approx(first['velocity'])
    assert final['yaw']-first['yaw'] == pytest.approx(2.*math.pi)
    for time in (0., 3.1, 7., 16.7, 21., 28.):
        reference = attraction_probe_reference(CENTER, THETA0, time)
        command = attraction_probe_command(controller, CENTER, reference['position'], reference['yaw'], time, theta0=THETA0)
        assert command[[0, 5]] == pytest.approx((reference['speed'], reference['yaw_rate']))
        assert command[1:5] == pytest.approx(np.zeros(4))


def test_command_is_rigid_transform_invariant_and_uses_existing_saturation():
    controller = tracking_controller(CONFIG)
    angle = -.81
    rotation = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
    shift = np.array([1.7, -.9])
    position, yaw, time = (.32, -.35), 1.21, 6.3
    original = attraction_probe_command(controller, CENTER, position, yaw, time, theta0=THETA0)
    transformed = attraction_probe_command(controller, rotation@CENTER+shift, rotation@position+shift, yaw+angle, time, theta0=THETA0+angle)
    assert transformed == pytest.approx(original, abs=1e-12)
    far = attraction_probe_command(controller, CENTER, (-100., -100.), 0., 0., theta0=THETA0)
    assert far[[0, 5]] == pytest.approx((.1, .5))
    assert controller.last_saturation_flags[[0, 5]].tolist() == [True, True]


@pytest.mark.parametrize('center,theta0,time', [((0., 0.), 0., -.001), ((0., 0.), 0., 28.001), ((0., 0.), math.nan, 1.), ((0., math.inf), 0., 1.), ((0.,), 0., 1.)])
def test_reference_rejects_invalid_support(center, theta0, time):
    with pytest.raises(ValueError, match='invalid attraction probe'):
        attraction_probe_reference(center, theta0, time)


def test_command_rejects_invalid_state_or_unselected_controller_limits():
    controller = tracking_controller(CONFIG)
    with pytest.raises(ValueError, match='invalid attraction probe'):
        attraction_probe_command(controller, CENTER, (math.nan, 0.), 0., 1., theta0=THETA0)
    controller.max_wz = .6
    with pytest.raises(ValueError, match='invalid attraction probe'):
        attraction_probe_command(controller, CENTER, (0., 0.), 0., 1., theta0=THETA0)


def test_existing_circle_and_runtime_timing_remain_unchanged():
    command = tracking_command(tracking_controller(CONFIG), (0., 0.), (.25, 0.), 0., 0.)
    assert command[[0, 5]] == pytest.approx((-.1, .09))
    assert (APPROACH_NS, COLLECTION_NS, TOTAL_NS) == (8_000_000_000, 12_000_000_000, 20_000_000_000)
    assert MODES == ('rolling_neighborhood_v1', 'centered_tracking_v1')


def integrate_case(lateral, heading):
    """Fixed .005s explicit midpoint; 30Hz state interpolation is descriptive."""
    controller = tracking_controller(CONFIG)
    initial = attraction_probe_reference(CENTER, THETA0, 0.)
    yaw0 = initial['yaw']
    xy = np.asarray(initial['position']) + lateral*np.array([-math.sin(yaw0), math.cos(yaw0)])
    state = np.array([*xy, yaw0+heading])
    dt = .005
    states = [state.copy()]
    error_max = math.dist(state[:2], initial['position'])
    max_v = max_w = stopped = longest_stopped = 0.
    min_v = math.inf
    def derivative(time, value):
        command = attraction_probe_command(controller, CENTER, value[:2], value[2], time, theta0=THETA0)
        assert np.isfinite(command).all()
        assert abs(command[0]) <= .1 and abs(command[5]) <= .5
        return np.array([command[0]*math.cos(value[2]), command[0]*math.sin(value[2]), command[5]]), command
    for i in range(5600):
        time = i*dt
        start_rate, start_command = derivative(time, state)
        middle_rate, command = derivative(time+dt/2., state+dt/2.*start_rate)
        state = state+dt*middle_rate
        states.append(state.copy())
        reference = attraction_probe_reference(CENTER, THETA0, (i+1)*dt)
        error_max = max(error_max, math.dist(state[:2], reference['position']))
        max_v = max(max_v, abs(command[0]), abs(start_command[0]))
        max_w = max(max_w, abs(command[5]), abs(start_command[5]))
        min_v = min(min_v, command[0], start_command[0])
        stopped = stopped+dt if abs(command[0]) <= 1e-4 else 0.
        longest_stopped = max(longest_stopped, stopped)
    states = np.asarray(states)
    sampled_times = np.arange(840)/30.
    grid_times = np.arange(5601)*dt
    sampled = np.column_stack([np.interp(sampled_times, grid_times, states[:,j]) for j in range(3)])
    phases = .83+2.*math.pi*sampled_times/3.+sampled[:,2]
    bearing = np.unwrap(np.arctan2(sampled[:,1]-CENTER[1], sampled[:,0]-CENTER[0]))
    radial = np.linalg.norm(sampled[:,:2]-np.asarray(CENTER), axis=1)
    phase_sectors = np.floor((phases % (2.*math.pi))/(2.*math.pi/12.)).astype(int)
    summary = dict(initial_lateral_m=lateral, initial_heading_error_rad=heading,
        max_error_m=error_max, final_error_m=math.dist(state[:2], initial['position']),
        max_linear_m_s=max_v, min_linear_m_s=min_v, max_yaw_rate_rad_s=max_w,
        longest_stopped_sec=longest_stopped, sample_count=840,
        radial_min_m=float(radial.min()), radial_max_m=float(radial.max()),
        sampled_bearing_span_rad=float(bearing[-1]-bearing[0]),
        sampled_world_phase_span_rad=float(phases[-1]-phases[0]),
        minimum_world_phase_step_rad=float(np.diff(phases).min()),
        phase_sector_counts=np.bincount(phase_sectors, minlength=12).tolist(),
        sampling='30Hz linear interpolation of fixed5ms midpoint states; final28s state separate')
    rows=np.column_stack([sampled_times, sampled, phases]).tolist()
    return dict(summary=summary, samples=rows, final_state=state.tolist())


@pytest.fixture(scope='module')
def component_results():
    results = [integrate_case(*case) for case in CASES]
    output = os.environ.get('R20_TRACKING_OUTPUT')
    if output:
        with Path(output).open('x') as stream:
            json.dump({'scope':'component kinematics, not runtime entry or Gazebo',
                       'sample_columns':['time_sec','x_m','y_m','unwrapped_yaw_rad','world_phase_rad'],
                       'cases':results}, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    for result in results:
        print('R20_KINEMATIC '+json.dumps(result['summary'], sort_keys=True))
    return results


@pytest.mark.parametrize('case_index', range(3))
def test_fixed_midpoint_component_tracks_without_sustained_stopping(component_results, case_index):
    result = component_results[case_index]
    summary = result['summary']
    assert summary['max_error_m'] <= .05
    assert summary['final_error_m'] <= .02
    assert summary['longest_stopped_sec'] < .5
    assert summary['max_linear_m_s'] <= .1
    assert summary['max_yaw_rate_rad_s'] <= .5
    assert summary['sample_count'] == 840
    assert summary['minimum_world_phase_step_rad'] > 0.
    assert min(summary['phase_sector_counts']) >= 4
    # These are observed kinematic coordinates, with the base yaw included.
    for t, x, y, yaw, phase in result['samples']:
        assert phase == pytest.approx(.83+2.*math.pi*t/3.+yaw)
