"""Selected moving-collection law; numerical controller ownership is reused."""
import json
import math
from pathlib import Path

import numpy as np

from ros_esc.controller_node.controller_objects.turtlebot_vehicle import Directional_Controller

LEGACY_MODE = 'rolling_neighborhood_v1'
CENTERED_MODE = 'centered_tracking_v1'
MODES = (LEGACY_MODE, CENTERED_MODE)
GUIDANCE_TOPIC = '/gesc_gaussian/v2/verification_guidance'
ADMISSION_DETAIL = 'moving verification collection admitted'
ADMISSION_EVENT = 12
APPROACH_NS = 8_000_000_000
COLLECTION_NS = 12_000_000_000
TOTAL_NS = 20_000_000_000
ADMISSION_RADIUS_M = .08


def tracking_controller(filepath):
    """Bind the exact selected development controller instead of copying gains."""
    if not filepath:
        raise ValueError('centered verification requires the selected controller configuration')
    config = json.loads(Path(filepath).expanduser().read_text())
    if config.get('object_name') != 'Directional_Controller':
        raise ValueError('centered verification requires Directional_Controller')
    controller = Directional_Controller(config['gains'], config['params'])
    if (controller.k_vx, controller.k_wz, controller.max_vx, controller.max_wz) != (.5, 5., .1, .5):
        raise ValueError('centered verification requires validated .5/5 gains and .1/.5 limits')
    return controller


def tracking_command(controller, center, position, yaw, elapsed_sec, *, approach=False):
    """Selected fixed-center approach or the unchanged circular collection law."""
    if not all(math.isfinite(v) for v in (*center, *position, yaw, elapsed_sec)) or elapsed_sec < 0:
        raise ValueError('invalid centered tracking input')
    if approach:
        world = np.asarray(center)-np.asarray(position)
    else:
        angle = .3*elapsed_sec
        target = np.asarray(center)+.03*np.array([math.cos(angle), math.sin(angle)])
        derivative = .009*np.array([-math.sin(angle), math.cos(angle)])
        world = target-np.asarray(position)+derivative/.5
    body = np.array([[math.cos(yaw), math.sin(yaw)], [-math.sin(yaw), math.cos(yaw)]])@world
    return controller.controller_output(elapsed_sec,
        np.array([*position, 0., 0., 0., yaw]), body)


def attraction_probe_reference(center, theta0, elapsed_sec):
    """Pure 28-second probe geometry; no runtime mode or admission is selected.

    The frozen orientation is independent of sensor phase. The positive radius
    makes the returned tangent yaw continuous without angle unwrapping.
    """
    if (len(center) != 2 or not all(math.isfinite(v) for v in
            (*center, theta0, elapsed_sec)) or not 0. <= elapsed_sec <= 28.):
        raise ValueError('invalid attraction probe reference input')
    rate = 2. * math.pi / 28.
    u = rate * elapsed_sec
    radius = .14 - .025 * math.cos(2. * u)
    radial_derivative = .05 * math.sin(2. * u)
    radial_second = .1 * math.cos(2. * u)
    angle = theta0 + u
    radial = np.array([math.cos(angle), math.sin(angle)])
    tangent = np.array([-math.sin(angle), math.cos(angle)])
    position = np.asarray(center, dtype=float) + radius * radial
    velocity = rate * (radial_derivative * radial + radius * tangent)
    acceleration = rate**2 * ((radial_second - radius) * radial
                              + 2. * radial_derivative * tangent)
    speed_squared = float(velocity @ velocity)
    yaw_rate = float((velocity[0] * acceleration[1]
                      - velocity[1] * acceleration[0]) / speed_squared)
    return {'position': tuple(position), 'velocity': tuple(velocity),
            'acceleration': tuple(acceleration),
            'yaw': angle + math.atan2(radius, radial_derivative),
            'yaw_rate': yaw_rate, 'speed': math.sqrt(speed_squared)}


def attraction_probe_command(controller, center, position, yaw, elapsed_sec, *, theta0):
    """Opt-in component command using the existing gains and saturation owner."""
    reference = attraction_probe_reference(center, theta0, elapsed_sec)
    if (len(position) != 2 or not all(math.isfinite(v) for v in (*position, yaw))
            or (controller.k_vx, controller.k_wz,
                controller.max_vx, controller.max_wz) != (.5, 5., .1, .5)):
        raise ValueError('invalid attraction probe state or controller')
    world = (np.asarray(reference['position']) - np.asarray(position)
             + np.asarray(reference['velocity']) / controller.k_vx)
    body = np.array([[math.cos(yaw), math.sin(yaw)],
                     [-math.sin(yaw), math.cos(yaw)]]) @ world
    body[1] += reference['yaw_rate'] / controller.k_wz
    return controller.controller_output(elapsed_sec,
        np.array([*position, 0., 0., 0., yaw]), body)
