# R2 final combined runtime replay

ADOPTED 2026-09-10 before execution. Read-only final production core; all model
constants and production owners remain held. One bounded replay checks the
actual static/circle/oscillation OR behavior and one-confirmation latch after
the selected static30/.04 amendment. No threshold or class changes follow from
these results. No bag, model, Gazebo or holdout access.

## Fixed source population and decision

Reuse all99 exact arc-center fixtures and96 exact oscillation-v2 fixtures plus
all33 cancellation controls from the static-correction job. The latter are the
new P66/.37 failure plus P54/60/66/72 at eight phases k*pi/4, all amplitude.25m
and translation.02m/s. No controls are generated adaptively. Same original
samples, deterministic noise seed and irregular/spike positions are retained.
The static-correction helper already freezes exact fixture generation; reuse
only its fixture-construction AST before any fit/evaluation statements.

There are228 original family rows. Deduplicate only shared declared fixture IDs
whose integer nanosecond timestamp and exact XY sample hash agree, retaining
all family aliases and class claims. A conflicting shared ID/hash is a failure,
not permission to combine. Expected shared R1 rows28, leaving200 trajectories:
142 negative,57 positive (3 static,29 circle,25 oscillation),1 gray drift. These
expected counts are verified against loaded contracts, not assumed results.
Prior arc oscillation labels described that component's unsupported scope;
explicitly adopt their already-declared bounded oscillation positives as
in-scope for this combined detector. Retain every original label alongside it.

For each unique120s source history, create the actual production
RecurrentGeometryDetector with fixed RecurrentConfig and start_epoch(id,0), then
call update on every original point in original order. Do not replace methods,
resample input, skip model branches, force eligibility or prefit trajectories.
Retain every completed support/branch, rejection/reset, persistence and emitted
confirmation; all later updates continue to test latch behavior. Count positive
misses and negative confirmations, stratified by declared class and first
accepting branch, alongside unsupported/gray outcomes. PASS requires no positive
miss, no negative confirmation and at most one confirmation per trace. The
static calibration's overlapping populations do not inflate distinct cases.

## Optional declared V9 D prefix (included)

Use only already extracted `v9_detector_inputs_v1/D/` pose, SearchEpochContext,
recording-ready and clock JSONL.gz plus their existing receipt/summary. Select
the first valid SEARCH epoch observed in recording readiness; preserve its
actual started_at origin. Replay readiness-admitted original poses only until
the first recorded exit/change of that epoch, or120s after first ready clock,
whichever occurs earlier. Keep all source resets and frame checks. Record
actual epoch bounds, original first/last pose, first candidate if supported,
and elapsed-from-ready/epoch values. This is a numerical positional
counterfactual within one observed SEARCH prefix, not reconstruction of live
receipt admission or evidence of behavior after a different intervention.
Missing/short support is reported as unavailable, never extended beyond exit.

## One finite job and retained evidence

Exclusive external directory: `development/20260910/combined_runtime_replay_v1/`.
Save plan/helper/selected production+fixture+input hashes before dispatch. One
118s SIGINT timeout with2s kill-after and110s internal deadline. No unchanged
numerical rerun. Retain exact argv, counts/aliases, all model supports, first
candidates, class denominators, terminal failures, elapsed time, and before/after
source/input hashes. Production core/contract/node remain unchanged during the
job and D3 benchmark. Final source pin stability is mandatory. Preserve all
prior failed jobs; any new failure blocks nomination and is reported to root.
