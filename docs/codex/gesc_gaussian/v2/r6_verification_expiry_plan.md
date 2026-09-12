# R6 ordinary verification expiry handoff

ADOPTED prospectively2026-09-10 after [C01 closure](r5_visible_c01_handoff.md).
Closure archive549 source members verified in1.338651s, manifest SHA256
`ec3d42b4fc8556a65733f1b0f90358be5548e19c977c346ebfd01fc16981f634`.
This is a bounded simulation runtime correction, not a changed research gate.
C01 and V10 remain failed; R5's source correction remains intact.

## Confirmed mechanism and scope

C01's last valid exact-state VERIFY guidance at79.0s expired at79.1s. The
controller evaluated expiry and emitted a hard fault before the supervisor's
ordinary approach-deadline cancellation and SEARCH publication arrived. That
fault latched and forced FAILSAFE despite the valid cancellation transition.
The controller callback responsible cannot be identified from shared event text.
The eight-second approach itself failed legitimately and is a separate method
question; R6 does not change the approach law, admission radius or any deadline.

Extend the existing controller authorization owner only. For an otherwise fully
valid exact-state centered VERIFY companion whose original expected verification
deadline has just expired, immediately revoke motion and emit zero while waiting
for fresh supervisor authority. Classify this as a bounded normal transition,
not a hard fault. Require all existing schema, identity, stream, frame, candidate,
state, bounds, original source/receipt/steady freshness and lease-consistency
checks. VERIFY command_end must equal the original expected verification_end.
This applies to ordinary approach/collection expiry; initial DESIGN and all
other states retain their current deadline policy.

Preserve the existing once-only approach-to-collection transition: admission
at or before the original approach deadline may authorize its already-defined
collection lease when a newer valid exact-state companion arrives. Retain the
original acceptance/candidate identity and admission time; do not confuse that
valid phase change with shifting accepted_at or repeatedly renewing admission.
The expired old companion remains unauthorized. Test delayed delivery of this
legal phase change, including admission at the existing inclusive boundary.

The wait cannot extend the command lease or original verification deadline,
permit nonzero motion, fall back to GESC in VERIFY, reset candidate timing,
refresh duplicate receipts or suppress malformed/unsafe authority. It is bounded
by the existing500ms freshness limit measured from the original deadline and
all original state/pose/receipt/steady freshness limits; whichever fails first
ends the wait with the existing hard fault. A new valid SEARCH state restores
its existing authorization. Missing transition, stale inputs, changed identity,
future or inconsistent lease and invalid guidance still stop and fault.

Do not short-circuit other controller faults merely because this wait exists.
Both normal output and watchdog paths must use the same narrow wait policy;
final output authorization must still force zero. Preserve all recorder/readiness
guards, state fences, command ownership, stationary/legacy behavior and R5 DESIGN
handoff checks. Reordering publications is insufficient across independent nodes.
No new topic, interface, node, recorder or analysis owner is introduced.

## Bounded source evidence

First save a regression against the unchanged current controller, using actual
controller/generated-message fixtures and C01's original71.1/79.0/79.1 timing.
Retain the baseline's expected hard-fault reproduction under30s plus5s kill
grace within35s total; pin source/fixture/input receipts before and after.
Then implement the bounded correction and run one named focused controller,
guidance, supervisor and R5 handoff bundle,240s work within260s total. All test
and fixture processes must terminate. Retain failed attempts without unchanged
retry; no Gazebo, bag decode or numerical reference belongs to R6.

Require clock/filter/watchdog expiry before SEARCH and SEARCH-before-expiry
orders; zero output with no hard event during the valid bounded wait; normal
SEARCH resumption; no resumed expired VERIFY command. Negative checks cover
missing transition, ROS/steady/source/receipt freshness, duplicate/revised or
wrong identity, malformed/invalid guidance, bounds, preparation/DESIGN expiry,
readiness loss and unrelated controller faults. Reuse existing owner fixtures.
Record exact commands, hashes, outcomes and independent review, then checkpoint
the validated source before another milestone.

Next, separately plan the approach-law feasibility correction from C01's cached
trajectory. Do not relax0.08m admission or8/12/20s budgets on this evidence. A
fresh visible C case requires credible approach behavior and this handoff repair,
with new prospective identity and retained analysis. No acquisition or full
comparison is released by R6. Simulation only; no physical/Pi/snapshot/V1 work.
