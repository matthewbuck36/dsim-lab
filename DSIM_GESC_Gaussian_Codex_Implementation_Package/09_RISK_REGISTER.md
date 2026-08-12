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

## Phase 10 V1 closeout disposition

The principal unresolved research risk is generalization beyond the selected
two-source evidence. Broad simulation and physical readiness failed; v8.10
primary `11/11`, v8.11 secondary `6/6`, and v8.12 visible `14/14` remain scoped
successes, while the first varied v8.12 case was `13/14` and the other three
were withheld. The eighth physical run demonstrated selected two-basin
behavior but ended before a second convergence or `GOAL_HOLD`; its `61/62`
completeness also retains one cross-topic shutdown-ordering false negative.

These outcomes keep the unbounded-claim, evidence-ordering, sensor-cycle,
runtime scheduling, storage, calibration, and arbitrary-layout risks open for
future work. Phase 10 mitigates reporting risk through
the LaTeX-typeset
[`FINAL_PROJECT_REPORT_V1.pdf`](../docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf)
and its `.tex`/`.md` sources
and does not authorize a hardware rerun or implement a V2 correction.
