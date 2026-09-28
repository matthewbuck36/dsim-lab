"""Selected continuously moving centered verification law."""
import math
import numpy as np

APPROACH_NS = 8_000_000_000
COLLECTION_NS = 12_000_000_000
TOTAL_NS = 20_000_000_000
ADMISSION_RADIUS_M = .08

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
