# M4 v5 typed fill authority and bounded escape selection

Status: ADOPTED FOR IMPLEMENTATION, 2026-09-10 UTC, under the user's active
full V2 goal and express authority for recommended algorithm corrections.
This prospective amendment releases the source work below after the immutable
M4v4 closure. It does not release preparation or acquisition before validation.

Active scenario prerequisite: `m4_v5_primary_topology_amendment.md` records
the unchanged schema's requirement for primary verified-trap topology before
selecting the bounded interior option. Read it before further source/preparation
work; only prospective v5 primary association/receipt is added, not new geometry.

## Recorded diagnosis and preserved boundary

M4v4 remains CLOSED_INCOMPLETE: A/B complete behavioral failures, C incomplete,
13 unstarted, no block science or holdouts. Its closure archive SHA256 is
`21243aa35a666896d59ec6bbb748985487aa0855d58d9bab765f80a017ab529b`.
The original one-shot diagnostic export failed on NaN serialization; preserve
it under `builds/m4_v5_moving_fill_v1/diagnostic/`. The separately amended
`m4_v5_diagnostic_export_correction.md` export completed in 4.424504 seconds,
with 1.119386 seconds in the existing read-only bag reader. Its receipt is
`builds/m4_v5_moving_fill_v1/diagnostic_export_v2/receipt_v1.json`, SHA256
`d1ac26282e4282dcfebab19e889e6c72c68f6d5c2605bcb0a36da745f4b4e8ef`.
All 11 original C artifacts and 618 source pins are unchanged before/after.
This extracted events/transition/transaction details only; no science was rerun.

The first recorded FAILSAFE at simulated 152.2 seconds is exactly:
`open-field escape approach continuity has no pose outside the frozen exit radius`.
The fill committed at 152.0 seconds and both consumers acknowledged at 152.1.
The shared transition attempted ESCAPE_REPULSE, then immediately failed that
guard; no escape interval or ESCAPE_STARTED was published. The retained fill
has exit radius 1.3667708293638696 m. The subsequent CANCEL received
ALREADY_ACTIVATED, preserving the committed fill. Later controller stale-input
events at 166.6/166.7 seconds are also retained; they are not the first stop.
Do not infer their detailed causal chain from this restricted diagnostic.

Separately, completeness checks legacy fill-request timestamps for every
Gaussian-owner event. Moving mode uses typed transactions and has zero legacy
requests. The recorded FILL_CREATED source time 151.41500000000002 is derived
from the candidate confirmation and immutable Timekeeper origin. Correct this
missing selected-route authority without bypassing request causality.

## Bounded source ownership and selected control change

1. Extend the existing recording validator/lifecycle owner for the selected
   moving route. Preserve the legacy helper/default behavior. Require the
   already validated original candidate snapshot, PREPARE, PREPARED, actual
   ACTIVATE, original ACTIVATED and committed GaussianFill chain. Bind exact
   run/stream/frame/origin/epoch/candidate/preparation/evidence/prepared hashes,
   fill/cluster/revision/generation, finite source time and publication order.
   Bind committed fill source time directly to the originating confirmation
   with the producer's exact relative-time expression. PREPARE, CANCEL,
   rejection or retry acknowledgements alone do not authorize owner events.
   Enforce exact event kind and redesign/supersession predecessor provenance;
   malformed, absent, conflicting or unbound authority remains failure. There
   is no generic accepted-timestamp list or moving-to-legacy fallback.

2. Select the existing v8.12 bounded interior-anchor alternative prospectively
   for **all four matched arms** in fresh `m4_pilot_v5` only:
   `open_field_escape_interior_anchor_fallback_enabled=True` and the unchanged
   minimum `open_field_escape_interior_anchor_min_displacement_m=0.50`.
   Keep approach continuity enabled. The shared owner prefers a retained pose
   outside the frozen exit radius; only if none exists may it use the farthest
   valid retained pose displaced at least 0.50 m from the accepted fill center.
   Missing/insufficient history remains FAILSAFE. Preserve hard-safe direction,
   collision/freshness checks, controller ownership and all escape limits.
   Reuse the existing helper; no moving-only bypass or copied physical tuning.
   `docs/environment_parameters.md` and the actual existing v8.12 owner were
   read. This is one matched simulation policy selection, not a change to
   shared defaults or a claim of successful escape in the retained C run.

3. Extend the existing exact version mapping/scenario/workflow owners with
   `m4_pilot_v5`, retaining `subreaper_group_v3` and method v1. Preserve exact
   v1-v4 generated behavior and source/evidence archives; make only the above
   v5 control overrides. No geometry, Gaussian shape, detector/verification
   tolerances, timing, direction blend or scientific thresholds change.

## Required source evidence before release

Retain a failing pre-correction fixture from the actual Gaussian-owner
AlgorithmEvent plus serialized typed transaction/fill publications and zero
legacy requests. Validate the selected recording integration, including wrong
origin/epoch/fill identity/source/hash, absent PREPARED, CANCEL masquerading as
ACTIVATE, conflicting retries and redesign predecessor rejection. Preserve
relevant legacy recording/lifecycle and actual transport regressions.

Exercise the actual moving candidate/commit/both-ACK/shared escape transition
with approach continuity enabled. Cover outside-anchor success, absent-anchor
FAILSAFE with retained committed fill and one-count ledger, no escape before
both ACKs, postcommit CANCEL returning ALREADY_ACTIVATED, selected bounded
interior success, and displacement below 0.50 m remaining FAILSAFE. Do not
alter the existing expected guard failure; retain it as legacy coverage.

Check all 16 exact v5 slots and matched control settings, legacy versions,
recorded binding, source pins and actual installed Q5 CLI owners. Retain exact
commands, logs, source copies and hashes externally. All tests/transport jobs
have explicit timeouts; no extra qualification-only Gazebo acquisition.
Review the combined diff, run focused regressions and one final integrated
suite with stable source pins, then material source checkpoint/archive.

## Unchanged comparison and release contract

The parent `m4_execution_evaluation_plan.md`, clarifications, prerequisite
audit and implementation/source gates remain binding except the explicit v5
control selection above. Keep B/D two-block W6 s, 0.18 m threshold, 0.50 m
confinement; C/D moving coherence with 0.75 mean and M3 0.75/0.15 m evidence
settings. Keep original seeds, maps, starts, gains, speed limits and all
matched disturbances. Keep 16 slots, 192 direction targets, all first-opportunity
latency denominators, no-error requirements and all research thresholds.

After source validation: one 600-second preparation, frozen audit and exact
release; four visible development slots before the one-time 12 holdout release.
Keep 720-second recording / 900-second case / 15300-second suite caps including
900 seconds science. Integrity failure aborts; complete behavioral failures
remain outcomes. No replacement, postfreeze tuning, old-slot import, weakened
gate or scientific budget renewal. Preserve all unavailable denominators and
failures in the all-slot report. Both original research goals remain open.

Simulation checkout only. No physical/Pi, V1, commit or push action.
