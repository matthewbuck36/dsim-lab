# R2 recurrent geometry runtime integration

ADOPTED 2026-09-10 after the retained arc-center v1 and oscillation v2 finite
development passes. This is source implementation and focused verification;
no Gazebo dispatch, bag/model read, confirmation set or holdout is released.
The failed geometric v1/v2 and two-block controls remain failed.

## Owners and selected behavior

Extend the existing convergence detector folder with a pure
`recurrent_geometry.py` core and `recurrent_contract.py` evidence contract.
The existing detector node and `v2_binding.py` select
`convergence_metric_mode=recurrent_geometry_v3`. Preserve PDE, five-shift and
two-block selectors and their original wire types. Do not add this mode to
`CENTROID_METRIC_MODES`: the six-centroid arithmetic is a different contract.
No extra node, pose reader or analyzer. Launch ownership remains with the
centered-verification agent; existing recorder/analyzer/supervisor owners adapt
explicitly through the contract below. Root coordinates their shared release.

The new optional topic is `/gesc_gaussian/v2/recurrent_convergence_diagnostics`,
parameter `recurrent_diagnostics_topic`, message
`ros_esc_interfaces/msg/RecurrentConvergenceDiagnostics`. System remains V2.
All method constants below are fixed, not independently launch-tunable. Reuse
existing selected pose/source-gap, frame, readiness, clock and state admission.

## Equations and finite computation

At source-time endpoints spaced6s from the SEARCH epoch origin, evaluate
static12s, circle30/36s and oscillation36/54s supports. Use original positions,
exact bracketed boundaries, trapezoidal time weights and no extrapolation.
Reject nonfinite, regressing, conflicting duplicate, frame-changing and gapped
source. Keep at most54s plus one bracketing source observation, with a100000
source-point cap that invalidates on overflow. All support geometry includes
every original vertex. Supports crossing the epoch/reset cannot qualify.

Static: weighted linear position trend, norm(v)<=.005m/s and actual maximum
distance from the time-weighted mean<=.03m. One completed support suffices.

Circle: independently fit two equal15/18s arcs using centered weighted
algebraic circle least squares `x²+y²=2cx*x+2cy*y+k`. Each must have rank3,
radius[.03,.5]m, radialRMS<=.02m and absolute net unwrapped bearing>=pi/3.
Center displacement/arc midpoint separation<=.006m/s, radius difference<=.08m,
whole-support actual confinement about its weighted mean<=.5m. Candidate center
is the average fitted arc centers, the estimate at the whole support midpoint.

Oscillation: weighted least squares
`p(t)=c+v*(t-t_mid)+a*cos(2*pi*(t-t_mid)/P)+b*sin(...)` on a bracketed uniform
.2s representation. Cache weighted pseudoinverses for P6..min(96,width/.75)s,
step.5s and widths36/54s. Select minimum residual fit. Before resampling require
full-original actual confinement<=.5m, principal perpendicularRMS<=.02m and
minor/major spatial variance ratio<=.1. Require fitted major harmonic amplitude
>=.05m, RMS<=.02m, design condition<=50 and norm(v)<=.006m/s. Model center is
weighted original mean plus fitted intercept at support midpoint.

Circle and oscillation require3 consecutive passing6s endpoints of the SAME
branch and support width. Failed/invalid evaluations reset that counter; no
pooling, fallback two-block route or accumulated-noise-angle substitute. Static
then circle30,circle36,oscillation36,oscillation54 is deterministic priority if
several qualify together. Evaluate and publish every branch at each endpoint;
only the first eligible branch may consume the SEARCH confirmation latch.
History faults never rearm; only a distinct explicit SEARCH epoch rearms.

## Typed shared contract (frozen before source edits)

Generic fields preserve units and source semantics: `stamp`, `receipt_stamp`,
`source_stamp`, `epoch_started_at`, `history_start`, `history_end` (ROS Time);
`run_id`, `frame_id`, `source_pose_topic`, `metric_mode`, `reset_reason` strings;
`search_epoch`, `confirmation_sequence`, `reset_sequence` uint64;
`source_valid`, `history_valid`, `metric_valid`, `confinement_valid`, `eligible`,
`confirmed` bool; `center_x_m`, `center_y_m`, `score_m`,
`confinement_radius_m`, `maximum_radius_m`, `represented_duration_sec`,
`maximum_source_gap_sec` float64; `sample_count` uint32.

New explicit model fields: `branch` string (`static`, `circle`, `oscillation`,
or empty invalid status); `support_duration_sec`, `evaluation_interval_sec=6`,
`score_scale_sec=12`, `score_threshold_m`, `drift_m_s`, `maximum_drift_m_s`,
`fit_residual_rms_m`, `radius_difference_m`, `period_sec`, `amplitude_m`,
`perpendicular_rms_m`, `axis_variance_ratio`, `design_condition` float64;
`persistence_start` ROS Time and `persistence_count`, `persistence_required`
uint32; `fit_rejection_reason` string. Circle-specific oldest-first arrays
`arc_center_x_m`, `arc_center_y_m`, `arc_radius_m`, `arc_radial_rms_m`,
`arc_net_angle_rad` float64[] have exactly2 elements for a valid circle fit,
and are empty for other branches. Inapplicable scalar fields are NaN.

`score_m=drift_m_s*12s`, with inclusive branch threshold .060m static or .072m
circle/oscillation; no quantity in m/s is labeled metres. `history_start/end`
is the current model-fit support. `persistence_start` is the earliest model
support start in the CURRENT passing streak (not silently collapsed into the
fit support); it is zero if the branch is failing. The counter is capped3,
with persistence_start tracking the most recent3 successful endpoints, so
full confirming support spans width+12s. `metric_valid` means finite model
score, not that model quality or threshold guards passed. `eligible` requires
all model guards, confinement and required persistence plus live authorization.

Existing DetectorConfirmation is unchanged: `metric_mode=recurrent_geometry_v3`,
`history_kind=recurrent_geometry`, `source_stamp_kind=pose_input`,
`convergence_score_valid=true`, `legacy_r_mean_valid=false`, empty
`legacy_snapshot`. Its history_start/end and source_stamp bind the selected
diagnostic model support (source_stamp equals history_end), score and center
match exactly, frame/run/epoch/sequence mirror existing authoritative binding.
Its distinct evidence lifetime and current source/clock freshness remain
enforced by existing adapters. CandidateSnapshot uses the same metric mode
and metre score; its existing schema is unchanged.

Shared API: `RECURRENT_GEOMETRY_V3`, `RECURRENT_HISTORY_KIND`,
`recurrent_diagnostic_errors(messages, expected_source_pose_topic=None,
supervisor_run_ids=None, maximum_source_gap_sec=None,
allow_clock_admission=False, expected_frame_id=None,
pose_freshness_sec=.5, expected_metric_mode=None)` returns string errors,
analogous to the existing centroid checker, validating explicit branch units,
support, quality, persistence and identity. Numerical trajectory truth still
requires replay. Confirmation joins remain in existing lifecycle validators.

## Validation and limits

Before edits retain this plan and read current owners. Run bounded focused
core tests for independent circle/oscillation/translation/large-loop/spike
controls, causal boundary timing, same-width persistence reset, source
faults/frame/epoch/latch and bounded history. Run existing positional transport,
clock, typed confirmation and legacy detector regressions. Add selected new
typed transport checks. Root performs isolated interface build and consumer
integration, then checks source-bound evidence. Retain commands/results and
source hashes in `validation/r2_recurrent_detector_runtime.md`.

Finite prototype passes establish feasibility on declared development inputs,
not a proof against arbitrary trajectories or closed-loop/source performance.
Runtime cost must remain bounded by cached finite fits; no rival optimization.
No threshold selection from additional B outcomes or broader campaign here.

## Measured static amendment (supersedes static12 above)

The combined-core independent P66 translating oscillation exposed transient
cancellation through static12. That failure remains retained. Under the saved
[r2_static_correction_plan.md](r2_static_correction_plan.md), the sole228-row
calibration (159 negatives,4 static-positive rows/3 unique fixtures) selected
**static30s, radius.04m, drift<=.005m/s, one support**. Radius.03 missed the
unchanged sigma.01m static control; radius.04 detected all static positives and
zero negatives. This is the only runtime/model-contract change: static allowed
support becomes30s and its actual radius guard .04m. Source gap, score units,
static persistence count1, circle/oscillation rules and other fixed limits stay
as saved. Evidence is retained under external `static_correction_v1/`.
Recurrent status heartbeat is mandatory through the existing watchdog; the old
centroid heartbeat parameter remains false and is rejected for this selector.
First integration requires selected rolling simulation and moving verification;
stationary request-envelope support is deliberately withheld.
