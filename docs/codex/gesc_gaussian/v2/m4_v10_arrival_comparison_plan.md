# M4v10 arrival comparison and usable development release

ADOPTED prospectively, 2026-09-10, after the
[R4 integrated boundary](r4_stationary_integrated_handoff.md). Simulation only.
The user authorizes a revised development sequence and substantial method
changes. This plan implements the next comparison through existing owners;
source validation and frozen preparation precede acquisition. No V1–V9 result,
source archive, failed run or original budget is rewritten.

## Hypothesis and population

Compare the frozen `recurrent_geometry_v3` detector with inherited PDE detection,
and the implemented continuous rolling/centered acquisition package with
stationary GESC verification. Recurrent numerical branches, persistence and
all current GESC/Gaussian/controller settings remain those already validated
in R2–R4. No method tuning is authorized inside this fixed experiment.

| Arm | Detector | Search and verification |
| --- | --- | --- |
| A | `pde_mean_v1` | `stationary_v1` |
| B | `recurrent_geometry_v3` | `stationary_v1`, full recurrent request |
| C | `pde_mean_v1` | `rolling_gesc_v2`, `moving_cycle_coherence_v1`, `centered_tracking_v1` |
| D | `recurrent_geometry_v3` | same continuous package as C |

C/D preserve the detector contrast. A/C measures the whole continuous package,
not the isolated effect of averaging. Keep matched V6 half-gain controller,
geometry, starts, speed limits, escape selection and disturbance settings.
Arrival within0.5 m after valid local recovery is success under
`post_recovery_arrival_v1`. Keep actual ownership, safety, local fill/cardinality,
escape and SEARCH handoff checks. GOAL_HOLD/second ranking and escape bearing
alignment remain separately reportable diagnostics.

Use a distinct `m4-pilot-v10` experiment and method identity (do not describe its
methods as unchanged M4v1). Reserve sixteen exclusive slots under
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v10/`:
four visible primary nominal development cases, seed26091011, then twelve
secondary confirmation cases, four each for nominal seed26091012, Gaussian
sensor noise std0.015 with seed26091013, and sensor/pose delay0.10 s with
seed26091014. Retain historical
internal `holdout` partition spelling for owner compatibility while reporting
these as fresh confirmation runs on previously exposed conditions. Fresh seeds
are not evidence of unseen geometry. Never replace or rerun an attempted slot.

## Finite budgets and environment

Keep720 s recorder,900 s inclusive case,45 s shutdown grace and30 s independent
cleanup reserve. Adopt a new240 s labels budget per four-run block from the
retained169–186 s estimate and working B/D single-run analyses. The old120 s
benchmark stays failed; this is a new experiment cap, not a changed old verdict.
Keep45 s per C/D reference job and10 s summary. Adopt40 s total freeze/report
reserve (20 s each) under the pre-validation amendment below. Science reservation
is4*(240+2*45+10)+40=1400 s. The consistent outer maximum is16*900+1400=15800 s
(4 h23 min20 s), eight minutes20 s above the original suite cap.
Every source, CLI, preparation and empirical job has its own explicit timeout.
Record actual elapsed time and preserve partial/failed results at each cap.

Use the verified external
`development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh`
with `env -u PYTHONPATH`, preserving Q5 installed metadata/canonical source and
both new interface schemas. Bind the actual runtime environment, callable
entry points, generated interfaces and canonical modules during preparation.
Do not use the original pairing test environment for installed console scripts.

## Existing owners and measurements

Extend `m4_scenario.py`, scenario schema/runner, `m4_workflow.py`, `run_m4.py`,
`m4_pilot.py` and `evaluate_m4.py`; keep existing acquisition, native decoder,
validation, numerical reference and process ownership implementations. Add no
parallel science pipeline. New version selection must explicitly bind the
recurrent stationary request and centered guidance science aliases.

Use selected full recurrent diagnostics for B/D confirmation support and B
stationary request authority. Keep exact source/publication/admission stamps,
original receipt leases and typed diagnostic/request/fill joins. Report actual
post-recovery global arrival from the retained scenario evaluator separately
from native controller-goal timing, which may be not applicable. Combined
success uses actual local fill -> escape -> SEARCH -> arrival.

Keep independently frozen spatial labels, first-opportunity residence/latency,
negative-control events, wrong fill/goal counts and all24 reference targets per
moving arm. Report the original30% paired detector-latency target honestly;
missing paired endpoints leave it unestablished. Do not substitute a new latency
estimand after seeing outcomes. Short residence and intervention censoring are
explicit results. Direction reference remains recorded-position/observed-phase
stationary GESC, not a claim of a general spatial gradient.

For continuous verification use actual state/guidance/command coverage and
measured motion. Retain zero publications, their timestamps/durations, missing
coverage and safety reasons. Same-stamp transient zero publications or absent
ordinary-GESC per-heartbeat diagnostics must not alone classify an observed
moving acquisition as a mandatory stopped sweep. Require sufficient positive
evidence; missing coverage stays unavailable. Stationary B remains the stopped
baseline. Preserve historical motion metric outputs for old versions.

The fixed motion audit segments actual VERIFY and its initial DESIGN by state
transitions. Require valid selected lifecycle/guidance and state/pose endpoint
and successive source gaps at most0.5 s. Pair the complete ordered actual
`/cmd_vel` six-vectors with `ControlDiagnostics.final_command`, with exact
equality, monotone diagnostic ROS stamps and at most0.5 s bag-receipt separation;
command-source coverage through each segment also has at most0.5 s gaps.
Each segment needs at least two finite measured poses, positive planar path
and observed speed with planar hypot(vx,vy)>=0.001 m/s or abs(wz)>=0.001 rad/s.
Retain low-motion and zero-command runs; a sustained interval is at least0.5 s
by actual source stamps. Continuous acquisition requires no sustained measured
stationary interval or zero-command interval. Same-tick zero/nonzero pulses
retain both ROS and bag timestamps and have zero observed ROS dwell. Missing
coverage/censored unbracketed segments are unavailable; no candidate is
`NO_ACQUISITION_OBSERVED`, a complete outcome if SEARCH/input coverage is valid.
Only `OBSERVED_CONTINUOUS_ACQUISITION` establishes zero mandatory stopped
acquisitions for the D release condition. A sustained stop is a measured outcome,
not an unsupported attribution to a mandatory sensor sweep.

## Development release policy

New contract selector: `development_release_policy: usable_four_arm_analysis_v1`.
Before any confirmation slot, require all of:

1. Four exact COMPLETE development acquisitions with valid source/configuration
   identity, recording completeness, actual process termination and cleanup.
2. A completed labels job, both completed C/D reference jobs, and completed
   summary, all within frozen caps and with process/source integrity. Successful
   summary explicitly derives `scientific_analysis_complete=True` from actual
   four-arm analysis products; clean timeout is not science completion.
3. Four valid selected analysis/label/authority products, the exact24 scheduled
   targets for each C/D arm with eligibility/exposure retained, immutable nested
   receipts and late source/input hash checks. Missing references, invalid
   authority or missing required measurements blocks release.
4. Credible integrated enabled-method development evidence: at least one of
   B/D must complete valid local fill, escape, restored SEARCH and global arrival;
   D must additionally establish actual continuous verification/design without
   a mandatory stationary acquisition. Retain the independently established R4
   component evidence; do not require every baseline or every metric to pass.
5. All twelve confirmation slots remain untouched. Freeze the development
   outcome and release once without tuning/replacements.

Complete baseline behavioral failure, finite negative counts, no candidate,
short residence, censored latency and unexposed scheduled reference targets are
valid scientific outcomes. Require their attribution/coverage, not manufactured
positive results. Preserve historical V9 clean-timeout release semantics and its
test; the stronger gate applies only to the new explicit selector. An incomplete
development science result closes this version with confirmation withheld.

## Validation and dispatch order

First source milestone: version/schema/selection, consistent budgets and
identities, actual selected analyzer/arrival/motion behavior, immutable release
evidence and historical compatibility. Focus tests on real owner routes, changed
nested receipts, missing references, timeout, invalid authority and already
started confirmation slots; explicitly accept complete failed/censored baseline
results. No additional numerical calibration or full historical matrix rerun.

After source review and one bounded focused regression bundle, save validation,
status, checkpoint and source archive. Then prepare the exclusive new contract
through existing topology/schema owners under a separately recorded preparation
invocation. Review resolved method/environment/arrival selection before four
visible development acquisitions. Obtain complete usable development analysis
before the release policy can authorize twelve headless confirmation runs.

Report all sixteen outcomes (including unstarted slots), actual analysis
completion, paired/censored denominators, arrival versus optional goal holding,
method limitations and exact retained paths. A failed fixed version remains
failed. Full V2 closure requires the declared evidence and final handoff; a
source pass or selected development success alone does not complete the phase.

## Source validation invocation amendment

Before any test or comparison, root will use the external
`development/20260910/m4_v10_source_v1/validate_source.py` with an explicit unique
module list: one230 s pytest work cap plus5 s termination allowance and260 s
inclusive wrapper cap. Capture the entire V10 preparation source set, selected
runtime/interface files, installed21 entry-point bindings, driver and test list
before/after. Retain every outcome, including failed versions, full log and JUnit
identities. Run actual console help checks only under separate30 s caps. Source
and helpers remain held during each job.

Also exercise the new motion owner once on the closed D02 first-read typed
exports and native odometry CSV under60 s via `check_retained_motion.py`.
Require exact canonical payload parity when restoring generated messages;
consume only recorded pose/time/frame/planar-twist CSV fields. Pin the prior
complete/valid lifecycle summary and retain its original scope: this invocation
checks the new motion measurement, not a repeat lifecycle validation or a new
comparison result. No bag decode, model, reference or simulation is performed.
Keep all source/input hashes and complete motion/zero-pulse results. A failure
remains retained and must be diagnosed before changing any source or invocation.

### Pre-validation release-budget amendment

Before source tests, preparation or freeze, adopt40 s total freeze/report reserve
instead of the initially proposed20 s; all historical versions retain20 s. The
retained V9 `preflight/holdout_release.json` reports4.065685725 s for its original
release. The new policy adds a second full acquisition/source verification and
nested-product checks/late hashes, plus stronger final-report checks. Twenty
seconds for each new release/report step provides justified headroom; it is not
a measured V10 runtime claim. Shared V10 constants, contract construction,
validation, source tests and total science/suite reservations must all use the
updated40/1400/15800 s values before source freeze. Other caps are unchanged.
