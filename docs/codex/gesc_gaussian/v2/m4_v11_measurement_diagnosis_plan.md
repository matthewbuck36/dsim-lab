# V11 measurement diagnosis, separate from the closed comparison

ADOPTED2026-09-11UTC under the user's simulation-development authorization.
Prerequisite: [V11 closure](m4_pilot_v11_handoff.md), no runtime active, source
archive583 members verified in0.997531s, manifest
`468bb21a08f13ae89014b372117833a987804c7152accc1616a0f7b84f89235f` at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m4_v11_closed_v1/`.

This is a bounded diagnosis of measurement coverage. Preserve all V11 artifacts,
classifications, censoring, first-opportunity estimand and withheld confirmations.
No algorithm change, new run, numerical reference, threshold selection or
scientific qualification is authorized by these diagnostic results alone.

## Job1: cached spatial residence and confinement

Hypothesis: finite-grid region boundaries/holes fragment local confined motion,
so uninterrupted model-region residence need not measure settling/trapping.
Use the four saved labels/poses, corresponding metrics/intervention/confirmation
coordinates, contract and already qualified geometry. Reuse existing region and
segment classification owners. No bag scan or field-model evaluation.

Restrict comparisons to readiness through first objective intervention. Record
every local residence and reason for each break: point/segment outside positive
mask, excluded/unknown mask, unqualified pose or gap. Report distance to the
fixed independently specified local source, path and displacement for each
residence and intervening excursion, with detector events as annotations only.
Retain existing negative travel intervals and unknown labels. Do not create a
new positive label or substitute a later opportunity. The result should distinguish
actual departure from fragmented mask membership; if available caches cannot
explain a break, report it unavailable.

One job maximum60s including termination; external GNUtimeout55s SIGINT+5s kill.
Exclusive output `development/20260910/m4_v11_residence_diagnosis_v1/` under the
external V2 root. Save helper, exact command/environment, input hashes before/after,
all derived rows, concise summary and elapsed outcome. Do not rerun a failed job.

## Job2: C command/diagnostic alignment

Hypothesis: an inserted/missing topic row shifts positional pairing. Counts alone
cannot distinguish one insertion from multiple loss/reorder events. The normalized
direction artifact lacks the required command vectors, so one filtered extraction
is necessary. Reuse `read_run_bag(aliases=...)` for only `command_final` and
`control_diagnostics` plus its automatic readiness stream. No new reader or live
ROS node. Extract alias index, bag timestamp, readiness membership, six-vector,
validity and diagnostic source stamp. Preserve every row and the original ordering.

Reproduce the recorded count/mismatch totals first. Inspect first mismatch and
tail neighborhoods; count every possible single-extra-command removal that would
give exact order-preserving vector matches with the unchanged0.5s bag-time bound.
Use linear prefix/suffix comparisons, not a quadratic alignment search. Retain
all unmatched rows and multiple equivalent candidates. If no candidate works,
report the hypothesis unsupported; do not fit a multi-edit repair. A nearest
timestamp or repeated vector alone cannot assign a source time to headerless Twist.

One extraction/diagnosis maximum120s including termination; external GNUtimeout
115s SIGINT+5s kill. Exclusive output `development/20260910/m4_v11_command_diagnosis_v1/`.
Bind existing source reader/evaluator, run metadata/resolved topics/completeness,
retained metrics and bag bytes before/after. Use the verified runtime environment
with clean PYTHONPATH. Save raw projection, helper, exact command, hashes and result.
No full native analysis, reference rerun or promotion of C's unavailable metric.

## Decision boundary

Both jobs may run independently after scripts are reviewable. Save results and
update status/handoff. An evidence-backed evaluator correction or independently
defined operational confinement endpoint requires its own prospective source/
method amendment and focused validation. Check any future operational endpoint
against retained translating, large-loop, straight-drift, spike and gray controls;
detector decisions and fitted branches cannot define its ground-truth labels.
No new matrix until analysis and endpoint meaning are established.
