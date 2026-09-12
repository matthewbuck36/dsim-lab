# R2 selected lifecycle source validation

The current source boundary is the later
[publication revision/static correction validation](r2_lifecycle_revision_validation.md).
This page retains the original guidance1/static12 source result.

SOURCE_VALIDATION_PASS, 2026-09-10. Implements the lifecycle portions of
[centered verification](../r2_centered_verification_runtime_plan.md) and
[recurrent detection](../r2_recurrent_detector_runtime_plan.md). No simulation,
ROS graph, bag read, reference/model job or empirical research acceptance.

The existing lifecycle validator retains its default initial snapshot deadline
of acceptance+12 seconds. Explicit `centered_tracking_v1` instead joins the
immutable type12 collection event to the candidate and SEARCH epoch, enforces
the 8/12/20-second approach/collection/absolute bounds, rejects conflicting
repeated admissions, and requires its selected guidance stream. Valid guidance
must match an exact recorded AlgorithmState, candidate/confirmation/center,
original acceptance, recorded first admission and fresh recorded pose. VERIFY
commands retain the verification deadline; initial DESIGN commands bind their
existing initial preparation expiry. Invalid startup/out-of-state guidance may
carry an unbound stream contract but must carry zero commands. Existing raw
support, cost, neighborhood, fill and redesign checks remain active.

The recurrent detector uses its separate typed diagnostic and shared model
contract. Confirmation joins require exact run/frame/epoch/sequence/support,
center and metre score, plus the declared recurrent history kind. It cannot
borrow a centroid diagnostic. Both the actual run report and analyzer consume
explicit selected metadata; historical duration never selects a new method.
The type12 producer is identified as the existing supervisor.

Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v1/lifecycle_validation_v1/`.
`source_before.json` and five `.before` copies retain scoped entry source.
`validation_summary.json` SHA256
`de3825d6a64d48061ca5838744606a90412d80788a2d767a153e4efd5c020960`.
The summary records exact commands, logs, JUnit files and source hashes.

- `focused_v1`:159 passed,29.385 seconds. Initial timing plus existing recording
  regressions in three named modules, before the guidance extension.
- `focused_v2`:111 passed,34.530 seconds. Complete lifecycle recording/analysis
  modules after guidance and actual report metadata coverage; new isolated
  interface overlay sourced through `centered_runtime_v1/environment.sh`.
- `focused_v3`:15 passed,111 deselected,4.980 seconds. Actual numerical static
  trajectory to generated recurrent diagnostic CDR roundtrip and lifecycle/
  analyzer joins; identity, quality, history and timestamp substitutions reject.

All three jobs used a178-second root timeout with2-second forced-cleanup grace,
finished normally and were reaped; scoped files were unchanged within each job.
The JUnit union is195 unique passing cases; overlapping module reruns are not
added again. Original test functions remain unchanged by AST comparison, and
`git diff --check` passes. Root owns the material checkpoint and integrated
release. Controller/supervisor source tests separately establish proposal
generation and final command authority; these recording checks do not claim
unrecorded callback receipt or real-field behavior.
