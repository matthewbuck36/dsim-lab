#!/usr/bin/env python3

"""ROS adapter for the robust GESC/Gaussian supervisor state machine."""

import math
import uuid

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import numpy as np
import rclpy
from rclpy.node import Node
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill,
    StampedFloat64MultiArray,
)
from std_msgs.msg import Bool

from ros_esc.supervisor_node.state_machine import (
    ROBUST_PROFILE,
    State,
    StateMachineConfig,
    SupervisorStateMachine,
    TransitionInputs,
)


class SupervisorNode(Node):
    """Own robust state, weights, fill requests, and zero motion contribution."""

    def __init__(self, parameter_overrides=None):
        super().__init__(
            "gesc_gaussian_supervisor",
            parameter_overrides=parameter_overrides,
        )
        self._declare_parameters()
        profile = str(self.get_parameter("algorithm_profile").value).strip()
        if profile != ROBUST_PROFILE:
            raise ValueError(
                "supervisor_node is only valid for algorithm_profile="
                f"{ROBUST_PROFILE}"
            )
        self.algorithm_profile = profile

        now_sec = self._now_sec()
        self.started_sec = now_sec
        self.machine = SupervisorStateMachine(
            now_sec=now_sec,
            config=StateMachineConfig(
                convergence_hold_sec=self._float("convergence_hold_sec"),
                goal_score_threshold=self._float("goal_score_threshold"),
                goal_hold_sec=self._float("goal_hold_sec"),
                undesired_score_hold_sec=self._float("undesired_score_hold_sec"),
                verification_max_sec=self._float("verification_max_sec"),
                fill_design_timeout_sec=self._float("fill_design_timeout_sec"),
                escape_max_sec=self._float("escape_max_sec"),
                recenter_after_escape=bool(
                    self.get_parameter("recenter_after_escape").value
                ),
                recenter_max_sec=self._float("recenter_max_sec"),
            ),
        )
        self.run_id = uuid.uuid4().hex
        self.latest_pose_receipt_sec = None
        self.latest_pose_valid = False
        self.latest_source_receipt_sec = None
        self.latest_source_valid = False
        self.latest_source_score = None
        self.latest_source_score_valid = False
        self.latest_source_timestamp = None
        self.latest_convergence = None
        self.latest_convergence_receipt_sec = None
        self.pending_fill_result = None
        self.stop_requested = False
        self.controller_fault = False
        self.graph_fault = self._graph_fault()

        self.state_publisher = self.create_publisher(
            AlgorithmState, self._string("algorithm_state_topic"), 10
        )
        self.event_publisher = self.create_publisher(
            AlgorithmEvent, self._string("algorithm_event_topic"), 10
        )
        self.fill_request_publisher = self.create_publisher(
            StampedFloat64MultiArray, self._string("fill_request_topic"), 10
        )
        self.command_publisher = self.create_publisher(
            Twist, self._string("supervisor_command_topic"), 10
        )

        self.pose_subscriber = self.create_subscription(
            Odometry, self._string("pose_topic"), self.pose_callback, 10
        )
        self.source_subscriber = self.create_subscription(
            CostBreakdown,
            self._string("source_cost_topic"),
            self.source_callback,
            10,
        )
        self.convergence_subscriber = self.create_subscription(
            StampedFloat64MultiArray,
            self._string("convergence_status_topic"),
            self.convergence_callback,
            10,
        )
        self.fill_subscriber = self.create_subscription(
            GaussianFill,
            self._string("gaussian_fill_diagnostics_topic"),
            self.fill_callback,
            10,
        )
        self.stop_subscriber = self.create_subscription(
            Bool, self._string("supervisor_stop_topic"), self.stop_callback, 10
        )
        self.event_subscriber = self.create_subscription(
            AlgorithmEvent,
            self._string("algorithm_event_topic"),
            self.event_callback,
            10,
        )

        publish_rate = max(1e-6, self._float("supervisor_publish_rate_hz"))
        self.timer = self.create_timer(1.0 / publish_rate, self.timer_callback)
        self._publish_state_and_zero(now_sec)

    def _declare_parameters(self):
        defaults = {
            "algorithm_profile": ROBUST_PROFILE,
            "supervisor_publish_rate_hz": 20.0,
            "startup_timeout_sec": 5.0,
            "convergence_hold_sec": 2.0,
            "goal_score_threshold": 0.95,
            "goal_hold_sec": 3.0,
            "undesired_score_hold_sec": 3.0,
            "verification_max_sec": 10.0,
            "fill_design_timeout_sec": 5.0,
            "escape_max_sec": 20.0,
            "recenter_after_escape": True,
            "recenter_max_sec": 30.0,
            "stale_pose_sec": 0.5,
            "stale_sensor_sec": 0.5,
            "pose_topic": "/odom",
            "source_cost_topic": "/gesc_gaussian/source_cost",
            "convergence_status_topic": "/gesc_gaussian/convergence_status",
            "fill_request_topic": "/gesc_gaussian/fill_requests",
            "supervisor_command_topic": "/gesc_gaussian/supervisor_command",
            "supervisor_stop_topic": "/gesc_gaussian/stop_requested",
            "algorithm_state_topic": "/gesc_gaussian/algorithm_state",
            "algorithm_event_topic": "/gesc_gaussian/algorithm_events",
            "gaussian_fill_diagnostics_topic": "/gesc_gaussian/gaussian_fills",
            "pde_extensions_enabled": True,
            "directional_controller_selected": True,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _float(self, name):
        return float(self.get_parameter(name).value)

    def _string(self, name):
        return str(self.get_parameter(name).value)

    def _now_sec(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _graph_fault(self):
        if not bool(self.get_parameter("pde_extensions_enabled").value):
            return "robust profile requires PDE/Gaussian extensions"
        if not bool(self.get_parameter("directional_controller_selected").value):
            return "robust profile requires Directional_Controller"
        return None

    def pose_callback(self, msg):
        values = np.array(
            [
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z,
                msg.pose.pose.orientation.x,
                msg.pose.pose.orientation.y,
                msg.pose.pose.orientation.z,
                msg.pose.pose.orientation.w,
            ],
            dtype=np.float64,
        )
        quat_norm = float(np.linalg.norm(values[3:]))
        self.latest_pose_valid = bool(
            np.all(np.isfinite(values)) and quat_norm > 1e-9
        )
        self.latest_pose_receipt_sec = self._now_sec()

    def source_callback(self, msg):
        raw = np.asarray(msg.raw_cost, dtype=np.float64)
        count_valid = int(msg.channel_count) == raw.size and raw.size > 0
        self.latest_source_valid = bool(
            msg.source_timestamp_valid
            and math.isfinite(msg.source_timestamp)
            and msg.raw_cost_valid
            and count_valid
            and np.all(np.isfinite(raw))
        )
        scores = np.asarray(msg.source_score, dtype=np.float64)
        self.latest_source_score_valid = bool(
            msg.source_score_valid
            and scores.size == raw.size
            and scores.size > 0
            and np.all(np.isfinite(scores))
        )
        self.latest_source_score = (
            float(np.max(scores)) if self.latest_source_score_valid else None
        )
        self.latest_source_timestamp = (
            float(msg.source_timestamp)
            if msg.source_timestamp_valid and math.isfinite(msg.source_timestamp)
            else None
        )
        self.latest_source_receipt_sec = self._now_sec()

    def convergence_callback(self, msg):
        data = np.asarray(msg.data, dtype=np.float64)
        if data.size != 8 or not np.all(np.isfinite(data)):
            self.latest_convergence = None
            self.latest_convergence_receipt_sec = self._now_sec()
            return
        copied = StampedFloat64MultiArray()
        copied.header = msg.header
        copied.timestamp = float(msg.timestamp)
        copied.data = [float(value) for value in data]
        self.latest_convergence = copied
        self.latest_convergence_receipt_sec = self._now_sec()

    def fill_callback(self, msg):
        if not msg.source_timestamp_valid:
            return
        required = np.array(
            [
                msg.center_x,
                msg.center_y,
                msg.amplitude,
                msg.sigma_major,
                msg.sigma_minor,
            ],
            dtype=np.float64,
        )
        valid = bool(
            msg.active
            and msg.fill_id > 0
            and msg.covariance_valid
            and msg.principal_widths_valid
            and np.all(np.isfinite(required))
            and msg.sigma_major > 0.0
            and msg.sigma_minor > 0.0
        )
        self.pending_fill_result = (
            "success" if valid else "rejected",
            float(msg.source_timestamp),
            int(msg.fill_id),
        )

    def stop_callback(self, msg):
        if bool(msg.data):
            self.stop_requested = True

    def event_callback(self, msg):
        if (
            msg.event_type == AlgorithmEvent.EVENT_FAILSAFE
            and msg.detail.startswith("controller watchdog:")
        ):
            self.controller_fault = True
        if (
            msg.event_type == AlgorithmEvent.EVENT_FILL_REJECTED
            and msg.source_timestamp_valid
        ):
            self.pending_fill_result = (
                "rejected",
                float(msg.source_timestamp),
                None,
            )

    def timer_callback(self):
        now_sec = self._now_sec()
        try:
            if self.graph_fault is not None:
                transition = self.machine.force_failsafe(now_sec, self.graph_fault)
                if transition is not None:
                    self._publish_transition(transition, now_sec)
                self.graph_fault = None
            transition = self.machine.step(now_sec, self._transition_inputs(now_sec))
            self.pending_fill_result = None
            if transition is not None:
                self._handle_transition(transition, now_sec)
        except Exception as exc:  # safety boundary at the ROS adapter
            transition = self.machine.force_failsafe(
                now_sec, f"supervisor exception: {type(exc).__name__}: {exc}"
            )
            if transition is not None:
                self._publish_transition(transition, now_sec)
                self._publish_failsafe_event(now_sec, transition.reason)
        self._publish_state_and_zero(now_sec)

    def _transition_inputs(self, now_sec):
        startup_grace = now_sec - self.started_sec < self._float("startup_timeout_sec")
        pose_valid = startup_grace or self._fresh(
            self.latest_pose_receipt_sec, self._float("stale_pose_sec"), now_sec
        ) and self.latest_pose_valid
        sensor_valid = startup_grace or self._fresh(
            self.latest_source_receipt_sec,
            self._float("stale_sensor_sec"),
            now_sec,
        ) and self.latest_source_valid
        convergence_fresh = self._fresh(
            self.latest_convergence_receipt_sec,
            self._float("stale_sensor_sec"),
            now_sec,
        )
        convergence = bool(
            convergence_fresh
            and self.latest_convergence is not None
            and float(self.latest_convergence.data[0]) <= 0.0
        )
        fill_result = self.pending_fill_result or (None, None, None)
        return TransitionInputs(
            convergence=convergence,
            source_score=self.latest_source_score,
            source_score_valid=self.latest_source_score_valid,
            pose_valid=pose_valid,
            sensor_valid=sensor_valid,
            explicit_stop=self.stop_requested,
            controller_fault=self.controller_fault,
            fill_result=fill_result[0],
            fill_source_timestamp=fill_result[1],
            fill_id=fill_result[2],
        )

    @staticmethod
    def _fresh(receipt_sec, limit_sec, now_sec):
        return bool(
            receipt_sec is not None
            and now_sec >= receipt_sec
            and now_sec - receipt_sec <= limit_sec
        )

    def _handle_transition(self, transition, now_sec):
        self._publish_transition(transition, now_sec)
        if transition.current == State.DESIGN_OR_MERGE_FILL:
            if self.latest_convergence is None:
                failure = self.machine.force_failsafe(
                    now_sec, "fill request has no convergence snapshot"
                )
                if failure is not None:
                    self._publish_transition(failure, now_sec)
                    self._publish_failsafe_event(now_sec, failure.reason)
                return
            self.machine.register_fill_request(self.latest_convergence.timestamp)
            self.fill_request_publisher.publish(self.latest_convergence)
        if transition.current == State.GOAL_HOLD:
            self._publish_event(
                AlgorithmEvent.EVENT_GOAL_REACHED,
                now_sec,
                "goal source-score dwell satisfied",
            )
        if transition.current == State.ESCAPE_REPULSE:
            self._publish_event(
                AlgorithmEvent.EVENT_ESCAPE_STARTED,
                now_sec,
                "Gaussian repulsion escape started",
            )
        if transition.current == State.RECENTER:
            self._publish_event(
                AlgorithmEvent.EVENT_RECENTER_STARTED,
                now_sec,
                "recenter interface selected; Phase 02 command remains zero",
            )
        if "timeout" in transition.reason:
            self._publish_event(
                AlgorithmEvent.EVENT_TIMEOUT, now_sec, transition.reason
            )
        if transition.current == State.FAILSAFE:
            self._publish_failsafe_event(now_sec, transition.reason)

    def _publish_transition(self, transition, now_sec):
        self._publish_event(
            AlgorithmEvent.EVENT_STATE_TRANSITION,
            now_sec,
            f"{transition.previous.name}->{transition.current.name}: {transition.reason}",
        )

    def _publish_failsafe_event(self, now_sec, reason):
        self._publish_event(AlgorithmEvent.EVENT_FAILSAFE, now_sec, reason)

    def _publish_event(self, event_type, source_timestamp, detail):
        del source_timestamp
        event = AlgorithmEvent()
        event.stamp = self.get_clock().now().to_msg()
        event.source_timestamp = float(self.latest_source_timestamp or 0.0)
        event.source_timestamp_valid = self.latest_source_timestamp is not None
        event.event_type = event_type
        event.state = int(self.machine.state)
        event.state_name = self.machine.state.name
        event.state_valid = True
        event.fill_id = int(self.machine.active_escape_fill_id or 0)
        event.fill_id_valid = self.machine.active_escape_fill_id is not None
        event.reason_code = 0
        event.detail = detail
        event.value_names = []
        event.values = []
        self.event_publisher.publish(event)

    def _publish_state_and_zero(self, now_sec):
        state = AlgorithmState()
        state.stamp = self.get_clock().now().to_msg()
        state.source_timestamp = float(self.latest_source_timestamp or 0.0)
        state.source_timestamp_valid = self.latest_source_timestamp is not None
        state.run_id = self.run_id
        state.run_id_valid = True
        state.algorithm_profile = self.algorithm_profile
        state.state = int(self.machine.state)
        state.state_name = self.machine.state.name
        state.state_valid = True
        state.previous_state = int(self.machine.previous_state or 0)
        state.previous_state_name = (
            self.machine.previous_state.name
            if self.machine.previous_state is not None
            else "UNAVAILABLE"
        )
        state.previous_state_valid = self.machine.previous_state is not None
        state.transition_reason = self.machine.transition_reason
        state.transition_reason_valid = True
        state.state_elapsed_sec = self.machine.elapsed(now_sec)
        state.state_elapsed_valid = True
        state.active_fill_count = self.machine.active_fill_count
        state.active_fill_count_valid = True
        state.active_escape_fill_id = int(self.machine.active_escape_fill_id or 0)
        state.active_escape_fill_id_valid = self.machine.active_escape_fill_id is not None
        weights = self.machine.weights
        state.sensor_weight = weights[0]
        state.gaussian_weight = weights[1]
        state.affine_weight = weights[2]
        state.weights_valid = True
        state.failsafe = self.machine.state == State.FAILSAFE
        state.failsafe_valid = True
        self.state_publisher.publish(state)
        self.command_publisher.publish(Twist())

    def destroy_node(self):
        self.command_publisher.publish(Twist())
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SupervisorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
