# R2: extract current-gain V9 development detector inputs

Status: ADOPTED, 2026-09-10 UTC, under
[the revised development strategy](method_development_20260910.md).
This diagnostic is simulation-only and reads existing development data.

## Question and fixed population

Earlier V5 detector/verification diagnoses describe a different gain and cannot
establish V9 causes. Obtain the actual current-gain V9 development B and D
timelines before nominating a runtime detector. This extraction describes
recorded values only; it performs no new detector replay or label/reference work.

Exactly one selected read of each closed run under the external V2 root:

- `pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot02-B-26090801/`.
- `pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot04-D-26090801/`.

Original files and closed bags must match their receipts in
`checkpoints/m4_v9_closed_incomplete_v1/manifest.json`, whose SHA256 is
`fc818ab0a7831dedeee25876fc65faa3b2142b1daf99b091f351ea16250ad759`.
Inspect only the selected run receipts/metadata, not other trial data.
No V9 holdout or Q1/Q2 confirmation input is accessed. Historical outcomes,
including the shortened D observation and failed V9 comparison, are unchanged.

## Existing owners and exact exports

Use `bag_reader.read_run_bag` once per run with selected aliases only, then
`records_for_alias`. Reuse the complete serializer, tagged-nonfinite converter,
compressed exclusive row writer, metadata checks and descriptive summary helpers
from retained `builds/m4_v6_development_diagnostic_v1/extract_v1.py`, importing
without invoking its old V5 extraction function. Do not fork an analyzer.

Both runs select pose, centroid diagnostics, algorithm events/state, readiness,
clock and timekeeper. D additionally selects search epoch and typed detector
confirmation, which includes candidate centers; direction diagnostics are not
needed. Preserve B's manifest-proven absent epoch route explicitly, rather than
inventing epoch observations. All selected nonempty counts must match immutable
bag metadata exactly; cap each stream at 40,000 and each run at 160,000 records.
Abort instead of truncating a stream or omitting nested message payloads.

Each compressed JSONL row retains full generated-message payload, topic/type,
bag timestamp, source timestamp/value/validity, ROS/header timestamp, readiness
membership and motion-relative time. NaN/Infinity remain explicit
`__nonfinite_float__` tags. Save full events, state transitions, centroid score/
reset/confinement counts/ranges and existing-owner publication-gap description.
Recorded bag order never establishes exact callback order or runtime causality.

## Finite execution and integrity

New exclusive output root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/v9_detector_inputs_v1/`.
Save orchestration source, exact command/environment and source/input manifest
before reading either bag. Pin the existing bag reader, serializer helper and
selected coverage-owner source plus orchestration/plan. Imports use clean
Humble -> Q2 -> Q5 and the existing extremum-seeking source path, without ROS
initialization. Existing numerical/detector runtime owners are unchanged.

One sequential B then D batch has a 150-second inclusive ceiling. Each run has
at most 60 seconds including startup, bag read, export, input/source hash checks
and reaping; send SIGINT at 50 seconds, force group termination at 57 seconds
if necessary and reap by 59 seconds. Preserve failed/partial output; no retry.
Stop subsequent dispatch if input/source integrity or cleanup fails. Complete
all declared selected-file hashes before and after each read. Save exact counts,
elapsed times, original-file unchanged receipts and output hashes. No original
file is rewritten/reindexed and no simulator is started.

Exact execution command from repository root:

```bash
timeout --signal=INT --kill-after=2s 148s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/v9_detector_inputs_v1/run_batch.py
```

## Decision and handoff

Success means both complete selected exports with exact counts, source/input
integrity and terminal/reaped children. Report actual B/D score/confinement/
reset/confirmation findings without borrowing V5 causes. Failed or incomplete
input stops dependent detector nomination. A later explicitly scoped replay may
use these exports and independent negative controls; no fresh simulation or
expensive comparison is released by extraction alone. Record outcomes in
`validation/r2_v9_detector_inputs.md`; parent owns status/handoff/checkpoint.
