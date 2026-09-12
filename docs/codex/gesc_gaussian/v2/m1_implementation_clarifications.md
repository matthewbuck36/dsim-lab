# M1 implementation clarifications — 2026-09-08

This elaborates the approved plan without changing its metric, finite grid,
research gates or simulation-only scope. M1 qualifies the detector and replay;
supervisor candidate binding and fill transactions remain M3 work. No Gazebo
arm may be described as implemented or qualified before that integration.

- The numerical core uses integer absolute ROS nanoseconds and a piecewise
  linear trajectory. Each complete window has a trapezoidal time integral;
  boundary positions are interpolated without extrapolation. Its six-window
  radius is the maximum distance of represented segment endpoints from the
  six-window mean. A norm is convex on each segment, so this also bounds its
  interior. This is a bound on the sampled/interpolated trajectory, not unseen
  motion between source samples.
- Initial maximum source gap and source/state freshness are 0.50 seconds,
  reusing the inherited stale-pose allowance. Invalid time/frame/source data
  discard history while preserving the once-confirmed latch within an epoch.
  Only a distinct SEARCH epoch permits another confirmation. A hard memory
  limit resets explicitly rather than silently dropping required support.
- Recording readiness is an existing operational authorization gate. When
  the launch requires it, only fresh true readiness permits accumulation.
  This prevents a stationary startup interval from producing a candidate
  before the recorder authorizes motion. It adds no convergence dwell;
  stationary data become eligible after six windows of authorized observation.
- The M1 typed diagnostic has detector-local SEARCH epoch and monotonic
  confirmation sequence within the supervisor run ID. The M3 supervisor will
  bind that identity to its own immutable candidate and lifecycle epoch. These
  local diagnostic epochs must not be treated as already synchronized global
  lifecycle identifiers. The common envelope in the M0 audit describes the
  later transaction contract, which remains pending.
- `source_stamp`, support bounds, receipt and publication times are explicit
  absolute ROS times. Optional inherited AlgorithmEvent mirrors name the new
  metre-valued fields and leave their inherited relative source timestamp
  invalid until a verified origin conversion is available. The typed message
  is the authoritative detector result. No legacy array receives the new score.
- `pde_mean_v1` remains the default. Centroid settings initially select the
  approved development W=3 s with epsilon=0.06 m and radius=0.50 m pending the
  frozen calibration. The scenario parser validates finite positive values
  and requires SEARCH gating for the new mode. Inherited counted-candidate
  profiles continue to require their qualified-dwell contract only for the
  inherited metric; the new metric does not acquire that extra persistence.
- The existing manifest records the typed stream only in simulation. It is
  optional for inherited runs. Selected V2 targets promote it to required,
  bind its source topic and observed supervisor run, and check authorized
  interval coverage against recorded simulation clock time. The maximum gap
  is the source-gap allowance plus source freshness (initially 1 second).
  Final resolved parameter/mode binding remains required before the pilot.
- Numerical eligibility and authorized publication have separate latches.
  If readiness expires after numerical evaluation, the node discards the
  unsupported history and can publish after fresh complete support. It only
  consumes its once-per-epoch publication after the typed publish succeeds.
  Incomplete-window status messages cannot publish a new confirmation. Replay
  reports its recorded-authority proxy explicitly; it cannot reconstruct every
  wall-time callback race from simulation stamps.

Exact commands and results are recorded in the M1 validation record after
integration. Frozen independent-label definitions and calibration outcomes
are separate artifacts and cannot be changed to fit detector outputs.
