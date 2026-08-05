"""Preserve explicit ROS clock selection across shared runtime owners."""

from rclpy.parameter import Parameter


def apply_legacy_sim_time_default(node):
    """Select legacy simulation time only when startup supplied no override.

    Humble's :class:`rclpy.node.Node` records command-line, parameter-file, and
    constructor overrides before attaching its ``TimeSource``. The public
    parameter value alone cannot distinguish an explicit physical ``False``
    from rclpy's absent-override default, so this startup-only helper consults
    that recorded override map before any executor begins spinning.

    Returns ``True`` when the legacy default was applied and ``False`` when an
    explicit startup selection was preserved.
    """

    # MBuck 2026-08-04: Never replace an explicit Phase 09 wall-time choice;
    # avoiding a live True -> False switch also avoids destroying /clock while
    # a multithreaded executor owns its QoS waitable.
    overrides = getattr(node, "_parameter_overrides", None)
    if overrides is None:
        raise RuntimeError(
            "rclpy startup parameter overrides are unavailable; refusing to "
            "guess the use_sim_time selection"
        )
    if "use_sim_time" in overrides:
        return False

    results = node.set_parameters([
        Parameter(
            "use_sim_time",
            Parameter.Type.BOOL,
            True,
        )
    ])
    if len(results) != 1 or not results[0].successful:
        reason = results[0].reason if results else "no result"
        raise RuntimeError(
            f"failed to apply legacy use_sim_time default: {reason}"
        )
    return True
