# Risk Register

| Risk | Failure effect | Required mitigation |
|---|---|---|
| Raw cost sign is misunderstood | Gaussian attracts instead of repels | Audit sign; add gradient-sign unit test; never silently flip |
| Raw cost scale changes | Fixed amplitude becomes meaningless | Calibrated normalization and logged raw values |
| True source is treated as local | Robot fills and leaves desired source | Source-score threshold and dwell verification |
| Center estimate is biased by partial orbit | Miscentered fill creates residual minima | Kernel/cost weighted estimator, outlier rejection, confidence |
| Fill too narrow | Secondary local minima remain | Covariance-based width and local-grid validation |
| Fill too wide but too weak | Original basin remains | Couple amplitude to width and curvature |
| Overlapping fills ripple the field | Robot is trapped among fill shoulders | Hard-gated soft association and fill merging |
| Repulsion gradient is zero at center | Robot does not leave | Stall detection and assisted escape |
| Affine direction points into wall | Collision | Boundary-aware direction selection and recentering |
| Recenter command crosses old basin | Revisit | Keep all prior fills active |
| Endless circling | Long, unusable trials | Escape timeout, orbit metric, failsafe |
| Simulation and physical algorithms diverge | Gazebo success does not transfer | Canonical topics and one shared algorithm graph |
| Terminal logs are incomplete | Failures cannot be diagnosed | Structured messages and rosbag2 |
| Missing topic in a physical run | Irrecoverable experiment | Preflight manifest validation |
| Mixed ROS clocks | Signals cannot be aligned | Clock audit and run completeness checks |
| Command saturation is hidden | Controller blamed incorrectly | Log before/after saturation and flags |
| Bag grows too large | Storage/run failure | Explicit manifest, disk preflight, run duration limits |
| Codex creates duplicate nodes | Wiring becomes inconsistent | Phase 00 map and explicit reuse rule |
| Large Codex change or fresh chat loses context | Regressions and unfinished work | One phase per chat, Phase 00 audits, saved phase plans, validated handoffs, and commits |
| New dependencies unavailable on TurtleBot | Physical launch fails | Prefer current ROS/Humble dependencies; audit first |
| Unbounded robustness claim | Thesis claim is indefensible | Declare tested robustness envelope |
