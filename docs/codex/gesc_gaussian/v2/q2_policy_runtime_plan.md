# Q2 moving-cycle policy runtime amendment

Status: SOURCE/TEST VALIDATED; material closure recorded in status/handoff.
This milestone is under the approved simulation-only V2
implementation goal. Read `plan.md`, `status.md`, the completed
`q1_direction_policy_handoff.md`, and this amendment before editing. This
selects one nominated policy for implementation; it does not release Gazebo,
open old confirmation or alter the frozen 16-run M4 pilot.

The preceding diagnostic is closed at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q1_direction_policy_closed_v1/manifest.json`,
SHA256 `995d9547ef5ce1096e012c9e4741c193e675c02ae29f3dfa1c2e42b2d8603fbf`:
232 files, 972158-byte archive, 351 retained artifact hashes. Its 24-target
result nominates weight0.75 with median20.526919/P9034.946685 degrees and
hypothetical averaging24/24. The independent 607-file audit agrees. These
are saved-trajectory development findings, not actual policy qualification.

This amendment adopts the bounded implementation and validation designs in
`q2_policy_math_design.md` (SHA256
`c1f562a9921caaefb5aa51d9273831c2ad44cef97aa3a70a28e36ff390a53349`)
and `q2_policy_owner_audit.md` (SHA256
`53a296e635d2ff5ee8f09a5c9658516be8e1811a435fc3258d177a1f6cc44209`).
The concrete decisions below resolve their remaining alternatives.

## Fixed runtime behavior

Add startup selector `v2_direction_policy`: default `three_cycle_v1` names
the current policy; opt-in `moving_cycle_coherence_v1` selects the new rule.
The new selector requires robust rolling simulation. Reject unknown selectors
and new-policy stationary/physical combinations before node startup. Do not
add user-facing weight or coherence tuning controls. Existing default modes,
old source acquisition schema2 and filter matrices remain unchanged.

The new rule uses the existing complete signed world-phase cycle, 12 sectors
with at least two actual samples, three completed covered cycles after a real
reset, current mean norm>1e-6 cost/metre and coherence lower bound>=0.25.
Three-cycle angle/variability remain recorded controls, not new-policy gates.
Blend `0.25*q_instant_world + 0.75*q_mean_world` and rotate into the current
admitted body frame. Preserve original source/objective/clock/pose freshness,
current state authorization, speed ceilings, controller ownership, source-gap
and reset behavior. Recorder readiness does not reset filter warmup.

Explicit edge clarification: a fresh finite zero instantaneous vector may
still contribute to an informative eligible mixture. This preserves the
existing `test_zero_instantaneous_value_does_not_suppress_mean` behavior.
The frozen diagnostic was conservative at this edge; all its 24 anchors had
meaningful instants, and its result is unchanged. Only instantaneous fallback
requires norm>1e-6. Weak/nonfinite mixture or unavailable mean uses that valid
fallback; if neither direction is meaningful, output is invalid with a reason.
Invalid/stale underlying input never becomes a fresh fallback. Keep the old
policy's numerical and zero/weak semantics unchanged.

## Cached calculation and bounded work

Implement the reviewed piecewise-linear norm definition inside the existing
rolling owner, using a private sibling helper as needed. Never import an
external experiment directory at runtime. Reuse the exact clipping vectors,
phase fraction, rounded source timestamps and normalized `math.fsum` mean
support. Cache each full adjacent source segment's bounded quadrature receipt
once, precomputing during warmup. Compute only new full support and a changed
clipped boundary segment at each accepted input. Repeated publications and
duplicate observations perform no integration. Prune with retained source
points; clear caches on actual history/context resets. Cache failed receipts
so unchanged timer publications cannot retry them.

Use split-at-norm-minimum quadrature with epsabs1e-12, epsrel1e-10, limit64;
at most 2048 new integrand calls per update and 20000 represented by the
current window. Normalize denominator/error by original cycle duration.
Require denominator error<=1e-10 cost/metre and a positive resolved denominator.
Keep the diagnostic's numerator margin sqrt(2)*(1e-10+1e-8*norm(mean)),
triangle check and lower/upper propagation exactly as specified in the math
design. Admit only the lower bound>=0.25. Failures are explicit unavailability,
not a relaxed threshold. No analytic-antiderivative replacement is included.
Use the existing installed SciPy dependency through the selected-policy path;
default policy performs no added norm work.

## Policy identity and compatible evidence

Retain the binary layouts of `GescDirectionDiagnostics` and all nested existing
messages. Publish one additive `GescDirectionPolicyDiagnostics` companion from
the same filter callback/publication, carrying policy schema/version, policy
name and canonical config SHA256; run/stream/source-schema/origin/frame;
diagnostic/reset/source/observation identity and publication/source stamps;
objective identity; fixed weight, norm/error/coherence/bounds/threshold;
coverage/warmup/selected qualification and numerical/fallback reasons.
The companion must join exactly to its direction diagnostic and preserve its
original publication identity. It is evidence, not a new control owner.

For new declared runs, existing `qualified` means qualification by the selected
policy. `cycles_valid` and old inter-cycle statistics retain their old control
meaning. For omitted/default policy every prior qualification/0.5 assertion
remains strict. Companion/metadata dispatch must precede new interpretations;
missing, conflicting, wrong-policy or unbound companions invalidate new-policy
evidence. Never infer new policy merely from a favorable vector or weight.

Add a shared small `ros_esc/v2_direction_policy.py` identity/descriptor owner
used by core, adapter and evidence consumers. Canonical sorted compact JSON
must identify policy version, fixed numerical parameters/units/integration
rule/budgets and its SHA256. Record the descriptor/hash in scenario/recorder
metadata and selected diagnostic. Source stream schema2 describes acquisition
and is unchanged by this filter policy.

Extend the existing CLI/launch/scenario, recorder, validator, bag reader and
analyzer owners. Require the companion only for selected new-policy runs;
old bags stay readable and old topic startup minima unchanged. Keep old Q1,
D1/D2/D3 frozen evaluations/results intact; add explicit new-policy handling
inside existing analysis ownership. Preserve first diagnostic selection and
raw M3 observation semantics. No new node, recorder, model, analysis pipeline,
physical source edits or controller retuning is included.

## Validation and source closeout

Work in four coordinated divisions: core/cache; adapter/interface/launch;
shared descriptor and scenario/recording/analysis evidence; independent source
and real-node checks. Give each file one active editing owner. Preserve failed
checks and meaningful review corrections. Build the interfaces and ros_esc
into isolated `builds/q2_policy_runtime_v1/` under the external V2 root; retain
the earlier installed overlay and its evidence. Bound builds/tests explicitly.

Required checks include synthetic agreement with the immutable external norm
oracle; exact clipping/signed phase/scaling, warmup/caches/budgets/reset/failure
reuse, moving means, finite-zero continuity, weak mixtures and source faults.
Use finite DC/reset/harmonic/noise/interference fixtures to document limits
without fitting another gate. Run one fixed 1000-update synthetic performance
check under60s; report p50/p99/max and norm calls, checking headroom against
the selected approximately30Hz source period. No freshness relaxation is a
performance remedy.

Verify old/default compatibility, policy identity/IDL decoding, conditional
recording, exact companion joins, false numerical claims and output algebra.
Build and resolve the real Humble launch graph. Use bounded actual-node DDS
tests for both policies, current output pose/source, new averaging despite
changing old cycle means, objective resets, stale/future source/state/pose,
moving VERIFY/DESIGN and existing controller limits/final zero. Run focused
legacy/source-clock/expiry regressions and the relevant integrated suite after
all owners are held stable. Record exact commands, logs, hashes and skips.

This milestone closes only when implementation, tests, evidence routing and
performance are reviewable and their material checkpoint/handoff are saved.
No scientific target is claimed from source tests. The next separately frozen
study must acquire fresh closed-loop development/confirmation evidence for
actual accuracy/availability and detector/neighborhood qualification before
the unchanged M4 pilot. Old confirmation remains sealed throughout this source
milestone. The full V2 goal remains active.
