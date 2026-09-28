"""Assemble measured support once, without access to a simulator's field truth."""

from collections import deque
import math

from .records import Observation, Pose


def angle_lerp(a, b, fraction):
    return a + math.atan2(math.sin(b - a), math.cos(b - a)) * fraction


class ObservationBuilder:
    """Bounded sensor support; a missing bracket rejects data, not the run.

    Interpolate when both nearby observations exist. Otherwise retain the
    nearest observed support within tolerance and explicitly report its age.
    This is an observed/estimated geometry contract, not exact ground truth.
    """

    def __init__(self, source_instance, radius=0.18, support_tolerance=0.05,
                 expiry=0.5, capacity=256):
        if radius <= 0 or support_tolerance <= 0 or expiry <= 0 or capacity < 2:
            raise ValueError('invalid observation bounds')
        self.source_instance = source_instance
        self.radius = radius
        self.tolerance = support_tolerance
        self.expiry = expiry
        self.poses = deque(maxlen=capacity)
        self.phases = deque(maxlen=capacity)
        self.sequence = 0
        self.pending = None
        self.reason = 'waiting_support'
        self.frame = None
        self.fault = None
        self.last_cost_stamp = None

    def add_pose(self, pose):
        if not pose.valid():
            return False
        if self.frame is not None and self.frame != pose.frame:
            self.fault = 'pose_frame_changed'
            return False
        self.frame = pose.frame
        if self.poses and pose.stamp <= self.poses[-1].stamp:
            return False
        self.poses.append(pose)
        return True

    def add_phase(self, stamp, phase):
        if not all(math.isfinite(v) for v in (stamp, phase)):
            return False
        if self.phases and stamp <= self.phases[-1][0]:
            return False
        self.phases.append((stamp, phase))
        return True

    def add_cost(self, stamp, cost, receipt_stamp, *, basis='receipt',
                 uncertainty=math.nan, device_sequence=None):
        if not all(math.isfinite(v) for v in (stamp, cost, receipt_stamp)):
            self.reason = 'invalid_cost'
            return False
        if self.last_cost_stamp is not None and stamp <= self.last_cost_stamp:
            self.reason = 'duplicate_or_old_cost'
            return False
        self.last_cost_stamp = stamp
        self.sequence += 1
        self.pending = (self.sequence, stamp, cost, receipt_stamp, basis,
                        uncertainty, device_sequence)
        return True

    def _support(self, records, stamp, get_stamp):
        before = next((p for p in reversed(records) if get_stamp(p) <= stamp), None)
        after = next((p for p in records if get_stamp(p) >= stamp), None)
        if before is not None and abs(get_stamp(before) - stamp) <= 1e-9:
            return before, before, 0.0, 0.0
        if (before is not None and after is not None
                and stamp - get_stamp(before) <= self.tolerance
                and get_stamp(after) - stamp <= self.tolerance):
            fraction = (stamp - get_stamp(before)) / (get_stamp(after) - get_stamp(before))
            return before, after, fraction, max(stamp-get_stamp(before), get_stamp(after)-stamp)
        nearby = [p for p in (before, after) if p is not None
                  and abs(get_stamp(p)-stamp) <= self.tolerance]
        if not nearby:
            return None
        nearest = min(nearby, key=lambda p: abs(get_stamp(p)-stamp))
        return nearest, nearest, 0.0, abs(get_stamp(nearest)-stamp)

    def take(self, now):
        if self.pending is None or self.fault:
            return None
        sequence, stamp, cost, receipt, basis, uncertainty, device_sequence = self.pending
        if not 0 <= now-receipt <= self.expiry or not 0 <= now-stamp <= self.expiry:
            self.pending = None
            self.reason = 'sample_expired_or_future'
            return None
        ps = self._support(self.poses, stamp, lambda p: p.stamp)
        es = self._support(self.phases, stamp, lambda p: p[0])
        if ps is None or es is None:
            self.reason = 'missing_pose_support' if ps is None else 'missing_phase_support'
            return None
        p, q, f, pose_age = ps
        a, b, g, phase_age = es
        pose = Pose(stamp, p.x+(q.x-p.x)*f, p.y+(q.y-p.y)*f,
                    angle_lerp(p.yaw, q.yaw, f), p.frame)
        phase = angle_lerp(a[1], b[1], g)
        world_phase = pose.yaw + phase
        self.pending = None
        result = Observation(self.source_instance, sequence, stamp, receipt, pose,
                             phase, cost, pose.x+self.radius*math.cos(world_phase),
                             pose.y+self.radius*math.sin(world_phase), basis,
                             uncertainty, pose_age, phase_age, device_sequence)
        self.reason = 'valid' if result.valid() else 'invalid_observation'
        return result if result.valid() else None
