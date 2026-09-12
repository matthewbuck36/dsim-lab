# R22: retained command pairing across readiness boundaries

ADOPTED prospectively on2026-09-11UTC after [V13 closeout](m4_v13_handoff.md),
independent terminal review57checks PASS and material archive669members verified,
manifest f393c5ab1786127c84b17fa5a35b4d95e370b616b172b1a3c2e8e4d2d0b21e58.
The exclusive work root was absent at adoption:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/`.
V13 remains CLOSED_INCOMPLETE. Its four acquisitions, failed development gate,
reports and twelve unstarted confirmation slots must remain unchanged.

## Question and scope

D arrived at147.998s and passed direction accuracy, but its motion measurement
was unavailable. The existing evaluator independently cuts command and diagnostic
topics to readiness, then pairs by ordinal. D has8041 records in each full stream,
but7398 commands versus7399 diagnostics inside readiness. C passes with7319 full
records per stream and6840 per stream inside readiness. The publisher emits Twist
before its matching diagnostic from the same output, without a shared sequence.

Test whether a readiness boundary splitting an otherwise valid publication pair
alone explains D's3233 positional mismatches. Equal counts are not proof of
correspondence. Existing partial motion segments do not establish a qualified
zero-stop result. The direction-normalized cache lacks the complete command
records, so one targeted read is justified. No simulation, detector tuning,
controller change, new direction reference, native full-analysis rerun or new
comparison is part of R22.

## Capture and falsifiable diagnostic

Reuse the R9 filtered read route and R12 retained-input receipt pattern through
existing bag_reader.read_run_bag. Inputs are V13 development slot4/D and slot3/C,
in that fixed order. Maximum one scan per bag, alias union algorithm_state,
v2_verification_guidance,control_diagnostics,command_final and selected pose;
the existing reader adds readiness. One job:45s internal work,55s SIGINT plus5s
kill,60s inclusive. Same R21 runtime environment and single BLAS threads as V13.

Bind contract/acquisitions/original metrics, resolved topics/configuration,
source/interfaces and helper bytes before dispatch. Inherit the immutable native
acquisition bag hashes explicitly, with before/after raw size/mtime/inode/device
checks; hash all other selected inputs and new outputs. Preserve complete ordered
selected typed records, bag/source stamps, readiness flags, diagnostic validity,
exact command six-vectors and sufficient lossless payloads to reconstruct the
captured BagData. Use an experiment-local adapter over existing ROS serialization
and reader records, not a new general cache or analysis pipeline.

First reproduce historical counts, readiness bounds and positional mismatch
indices exactly for both cases. Then inspect full-stream ordinal pairs without
reordering, shifting or searching for a better fit. Require equal nonempty
counts, valid finite diagnostics/vectors, exact vector equality, receipt distance
<=0.5s and nondecreasing diagnostic source stamps. Retain every failure and every
pair crossing either readiness boundary. Explicitly test candidate D global
ordinal311 and whether any interior mismatch remains. Missing/extra records,
source rollback, vector/gap failure, ambiguous authority or changed inputs stop
this correction path. Preserve the failed diagnostic and choose further work
prospectively if falsified; do not coerce a pass.

## Conditional existing-owner correction

Only if the structural proof passes, extend evaluate_m4._v10_motion_metrics with
an opt-in pairing basis full_publication_order_v1. Preserve its historical default
and output exactly. Pair and validate full streams first, then admit only pairs
whose BOTH original bag receipts lie within readiness. Retain excluded boundary
pairs as evidence, without assigning an invented Twist source stamp. Every
interior mismatch remains fatal; no relaxed value/gap/order/authority conditions.
Document the inherited publication-order assumption and absence of a shared
sequence identifier. No runtime source, message type, topic or controller changes.

Keep existing0.5s pose-coverage and stationary-duration limits, typed guidance,
state segments, motion thresholds, command authority and safety/final-zero checks.
The correction only changes which corresponding recorded pairs are admitted.

## Focused validation and cached measurement

One focused bundle,90s inclusive maximum, through existing pytest selection and
the new bounded cases. Include left/right boundary splits, default parity, C
parity, missing/extra messages, interior mismatches, invalid/nonfinite commands,
source rollback, receipt-gap failure and genuine sustained-stop controls. Reuse
test_r9_motion_readiness.py,test_m4_v10_motion.py,test_m4_evaluation_cli.py where
relevant. Do not run a whole-workspace campaign. Preserve any failure before a
separately recorded correction.

One cached component job,25s SIGINT plus5s kill,30s inclusive: reconstruct the
captured BagData and invoke the existing motion owner using unchanged retained
intervention authority. No second bag scan. Save historical and selected results
for D/C with exact pair/exclusion/coverage/stop counts. Require historical results
to reproduce original retained measurements and C's qualified motion verdict to
remain unchanged. Report D complete, failed or unavailable as observed; a full
goal or comparison pass is not implied by this component.

Independent source/result review, exact validation record, context/diff checks,
material checkpoint and handoff close R22. Keep status/fresh handoff current.
Any later comparison needs its own prospective evidence/reuse contract; R22 does
not unseal V13 or release a matrix. Full research goal and original unavailable
30% basin-entry target remain open. No physical/Pi/snapshot/V1/commit/push.
