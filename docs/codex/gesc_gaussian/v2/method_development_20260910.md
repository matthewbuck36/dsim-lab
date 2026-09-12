# V2 method and development amendment — 2026-09-10

Later user clarification adopts [global arrival acceptance](global_arrival_acceptance_20260910.md).
Reaching GOAL_HOLD is no longer a success requirement. Apply the existing
evaluator-only spatial arrival tolerance and preserve safety/holding behavior.

Status: ADOPTED from the user's attached continuation instruction. Simulation
only, on `feature/gesc-gaussian-robustness-v2`. The original two research goals
remain open. This amendment supersedes prospective method and sequencing
restrictions in `plan.md` and earlier amendments where they conflict below;
historical methods, contracts, failed attempts and results remain unchanged.

## Authority and verified entry

The user explicitly authorizes substantial detector, estimator, moving
verification and evidence-collection changes, including a spatial-gradient
model, and bounded development before qualification. Routine justified
simulation decisions do not require renewed permission. Preserve selectable
legacy GESC and GESC + Gaussian as working baselines, cost sign/units, existing
controller and safety ownership, ground truth exclusively in evaluation, and
final goal holding. No V1, physical snapshot, Pi, device or hardware work.

The email at `/home/mattb/Downloads/San Diego State University Mail - TurtleBot
Experiment Updates and Next Steps.pdf` was read directly. It identifies delayed
or missed circling detection and the desire for reliable direction during
continuous search. It supplies methodological context, not execution authority.

Entry HEAD is `3369cfc83a64ff5d8354827fd5310caaf0c8e945`, with the existing V2
work uncommitted. No active ROS/Gazebo/scenario/analysis/test process was found
on entry. Both `validate_phase_context.sh v2 plan` and `v2 implement` pass under
30-second timeouts. V9 remains ten complete behavioral failures, one incomplete
recording and five unstarted slots. D1 explained the missing recorded startup
prefix; D2 monitor progression is source-validated, awaiting fresh empirical
evidence. D3 has a saved pre-edit snapshot and unfinished source/test work.

## Development sequence and release gates

1. **R1: useful retained-development measurements.** Finish the two justified
   D3 redundant-work corrections through the existing analysis owners. In
   parallel inspect already extracted development records; analysis that does
   not depend on those changes need not wait for a full four-bag benchmark.
   Measure detector score, resets, confinement and candidate timing; reconstruct
   explicit moving-evidence rejection reasons where logged prerequisites allow.
   Obtain direction error and availability on fixed development inputs with an
   independently computed, appropriate reference. Save exact finite jobs before
   execution. Partial historical normalized inputs can support explicitly scoped
   new diagnostics; they never become completed V9 science results.
2. **R2: select a measured method correction.** Separate detector positives
   (real confined circling/oscillation) from independent negatives (translating
   circles, large loops, drift, transit, uninformative fields). Separate direction
   error, reference informativeness, estimate availability and latency. Choose
   tuning or redesign from these measurements; do not infer V9 causes from V5
   counts. Save equations, assumptions, parameters, relevant literature if needed,
   and decision rules before changing the runtime. Extend current owners.
3. **R3: bounded integrated development.** Before each experiment save hypothesis,
   scenario/settings, finite simulated/wall budget, measurements and decision
   rule. Use short informative cases, including a visible integrated case. A
   failed attempt remains failed; a changed hypothesis/source uses a new identity.
   Recording/startup/discovery corrections needed for trustworthy fresh data
   must be verified before that dispatch. Demonstrate continuous moving evidence,
   local detection/fill/escape and continued source seeking, with explicit
   rejection diagnostics and preserved stop/hold behavior.
4. **R4: freeze and confirm.** Another four-arm, 16-run comparison requires a
   completed end-to-end development analysis within its prospectively saved
   budget, credible component results and integrated behavior. Development
   analysis failure or unavailable primary measurements blocks holdout release.
   Freeze method/configuration/analysis before confirmation. Any data examined
   for tuning, including previously exposed pilot cases, is development evidence;
   define fresh untouched confirmation identities/conditions explicitly. Preserve
   historical four-arm comparisons and their denominators. No expensive matrix
   is released by this amendment alone.

## Practical evidence discipline

Prefer existing extracted records and cached evaluator geometry/reference inputs.
Use existing reader, analyzer, detector, filter, supervisor, recorder and runner
owners. Avoid new parallel pipelines, repeated whole-source test campaigns and
archives after every small edit. Run meaningful focused compatibility checks at
coherent implementation boundaries; record exact commands/results and checkpoint
at material evidence or runtime changes. Original D3 output semantics and late
receipt checks remain required; its full-block throughput benchmark is a later
release prerequisite, not a prerequisite to independent component diagnostics.

Use new exclusive directories under
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/` for new
measurements, preserving raw inputs and all failed/partial outputs. Use
`builds/m4_post_v9_analysis_v1/` for the already adopted D3 source work. Each job
records source/input identity, scope, elapsed time and failures without imposing
hundreds of unrelated tests. Never rewrite an old closed science job or claim
development observations are untouched holdout evidence.

## Current acceptance boundary

R1 also adopts a bounded observability correction in the existing
`MovingRawEvidence`, `MovingSupervisor`, and state-machine transition owners.
Retain the existing guard decisions, selected cycles and deadlines. Add
diagnostic guard margins/counts to the already computed evidence, retain the
last evaluated rejection separately from the cancellation cause, and append
both to the existing moving cancellation transition reason (already recorded
as AlgorithmEvent). Default/legacy reason text stays unchanged when no detail
is supplied. No new topic, message type, recorder or controller behavior.
Focused evidence/supervisor tests under 90 seconds must show distinct spatial,
signal and cost-bound rejection details and that the last detail survives the
deadline cancellation into the actual transition, with unchanged verdicts.
This repairs a future diagnostic blind spot; it cannot recover old callbacks.

R1 measured evidence is complete; current acceptance is R2 runtime integration
and then R3 fresh integrated development. See the live status for exact scope. Substantial method changes and fresh simulation are
authorized after their bounded prospective designs; no repeated user choice
is required. The live status and fresh-chat handoff track the latest result and
next exact action. Full V2 remains in progress until research criteria and the
final report are actually supported.
