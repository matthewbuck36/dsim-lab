# R21 D02: qualify the unchanged method with corrected recording and analysis clocks

ADOPTED prospectively before source edits, retained metric execution or a fresh
simulation. The previous goal turn was progress: exact D01 arrival, qualified
direction inputs, a passing numerical reference, independent reviews and a
material source/evidence checkpoint were completed. The full research goal is
still open. Preserve D01 and V12 as recorded; neither is a replacement slot.

## Bounded corrections

The method remains exactly the R21 recurrent trapping policy with the existing
recurrent detector, rolling GESC, moving-cycle coherence, centered verification,
raw-cost ranking, Gaussian design, controller gains and escape lifecycle. D01
demonstrated a fill, escape and arrival at151.897s, and separately passed direction
error limits on4 eligible targets. This fresh case tests whether the same method
has a complete acquisition and analysis under another declared noise seed.

1. Omit `execution.simulation_duration_sec`. The existing recorder defaults that
   optional fixed-window requirement to zero and permits graceful arrival stop
   after readiness. Keep all independent finite stage/wall deadlines. No recorder,
   runner, shutdown, ownership or safety behavior changes.
2. Correct the state-duration clock comparison through the existing analyzer.
   Add an explicit `state_duration_basis='simulation_publication_v1'` option to
   `analyze_run` and `_state_intervals`; preserve the default bag-receipt behavior
   exactly. The selected supervisor uses `use_sim_time=True`,20Hz timer and
   AlgorithmState.stamp from its ROS clock. A3/rate heartbeat limit belongs to
   that publication clock. D01's two invalid bag intervals each span0.1s in this
   clock; changing the scientific gap limit is unnecessary and prohibited.
   Use `ros_timestamp_ns`/AlgorithmState.stamp, never the cost-source timestamp.
   Retain bag-based readiness selection, both timestamp domains in interval
   outputs, and explicit first-to-last selected publication support. Do not
   convert un-stamped readiness Bool messages into invented ROS timestamps or
   extrapolate durations into unmeasured boundary slivers. Reject missing,
   negative, backward or conflicting publication stamps, invalid states and
   true publication gaps above the unchanged3/rate limit. Equal publication
   stamps can represent simulation-clock quantization and must be handled
   without fabricating elapsed time. Require captured simulation-clock/rate
   selection for the opt-in; incompatible/missing clock metadata fails closed.
   Keep generic analysis completeness and every other metric gate unchanged.
3. In the fresh analysis wrapper, select that explicit basis and reuse
   `m4_recorded_binding(..., expected_cost_configuration=...)` with the runner's
   captured noisy JSON and exact argv witness. Pin the actual sensor geometry,
   filter and transform before analysis. Preserve the exact recorded-pose arrival
   join, native validation, motion owner and unchanged direction-reference owner.

## Evidence before dispatch

Keep the old analyzer bytes and hashes, then validate only the bounded analyzer
change plus relevant bag-analysis regressions, at most120s inclusive. Cover legacy
parity, slow/fast/bursty bag receipt versus a fixed publication timeline, genuine
publication gaps, absent/invalid/negative/regressing stamps, clock quantization,
invalid states, readiness filtering/support boundaries and explicit selected
simulation/rate metadata. Verify actual `analyze_run` forwarding and output
provenance, including rejection of incompatible selection. No algorithm source,
IDL, numerical estimator, acceptance threshold or physical behavior may change.

Allow one cached D01 state-interval component, at most20s inclusive, using its
already exported AlgorithmState records and original metadata. No bag read,
full native analysis, motion recomputation, model or direction reference. Retain
the old two-gap invalid verdict alongside the new explicitly scoped metric;
require exact source support and show that a separate true source-gap control is
still rejected. This diagnostic never promotes D01 completeness.

Fresh preparation must bridge the exact single analyzer source change and new
tests to the validated R21/D01 source receipts; every other frozen production
source remains identical. Reuse the existing21 installed entry-point checks and
new interface overlay. Freeze the exact preparation/acquisition/analysis helpers,
scenario, current source hashes and successful validation receipts. Before any
simulation, statically assert actual recorder argv omits `--sim-duration-sec`,
retains its600s wall limit, and all eleven primary recovery/arrival predicates
and selected source/lifecycle topics remain required.

## One fresh visible development case

External root: `development/20260911/r21_recurrent_trapping_v1/visible_integrated_D_02/`.
Run ID `v2_method_development_D_20260911_r21_02`; seed260921002. Copy D01's
secondary two-light geometry, start,0.015V Gaussian noise, zero delays and all
method parameters. Named schema14 development suite and recurrent_trapping_v1
remain selected; only identity/seed, omitted fixed recording window and declared
offline analysis basis differ. No new full comparison is released here.

Use the same sourced environment, interface overlay, domain201,localhost and
visible Gazebo GUI. Preparation90s inclusive. Acquisition: preflight45s,
local recovery300 plus post-recovery300 simulation seconds, recorder600 wall
seconds, runner650 wall seconds plus30s grace, root720s inclusive with the same
strict independent cleanup reserve. Retain every failure; no automatic retry.

After complete acquisition and both cleanup checks, one native analysis captures
one BagData read and the native validator's second read within120s inclusive.
No third read. Select the explicit simulation publication-duration basis and
retain its support bounds and original bag timestamps. Require native analysis
complete, native lifecycle/source integrity, complete motion and exact arrival
measurements. A measured nonarrival or stop remains a failed behavior, not
missing data. Permit one unchanged reference execution within45s inclusive only
after qualified normalized inputs and exact captured binding are retained.

Keep all24 direction targets at15+30k seconds, k=0..23, and every eligibility,
availability and exposure denominator. Direction thresholds remain median<=30
degrees, P90<=60 degrees and usable averaging>=0.8 among eligible informative
targets, with at least one eligible target. Required integrated behavior is
authentic continuous verification, a bounded committed fill, owned escape and
return to SEARCH, global arrival within0.5m, zero mandatory stopped acquisitions,
and complete evidence/final-zero/cleanup. GOAL_HOLD is optional. Direction error
remains the observed-phase stationary GESC response comparison, not a universal
spatial-gradient guarantee.

Review cached outputs independently, record exact commands/results/limits and
materially checkpoint the evidence. This case is exposed development. A future
16-run protocol must be separately frozen and keep development separate from
confirmation. No hardware, Pi, physical snapshot, V1, commit or push action.
