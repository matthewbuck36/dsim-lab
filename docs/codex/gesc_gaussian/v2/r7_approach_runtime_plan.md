# R7 fixed-center approach runtime integration

ADOPTED prospectively2026-09-10 after the
[paired prototype nomination](r7_approach_feasibility_handoff.md).
Prototype archive558 members verified0.996201s; manifest SHA256
`90170528009905ea0781231b563473afe767fea52ccad1fbcaf6def80c86812c`.
Both laws passed63 required cases; the prototype additionally passed both
previously failed hard cases. C01 modeled approach gained4.525s margin. The
baseline model did not reproduce actual C01's failure; this remains a testable
margin-improvement hypothesis, not an established physical diagnosis.

## Bounded implementation

Extend `centered_verification.tracking_command` with an explicit optional
approach-phase argument. Its default preserves the existing circular law for
current direct callers. During approach use only frozen-center position error,
rotated into the current body frame, through the same selected
Directional_Controller gains and saturation. After collection admission retain
the existing0.03m circular target, derivative and original acceptance-clock
phase exactly.

In the existing MovingSupervisor guidance publisher, select fixed-center
approach only for centered VERIFY while its current candidate has no immutable
collection admission. Actual first admission switches to the existing collection
law; re-entry does not restart it. DESIGN retains circular tracking and R5's
bounded activated-fill exemption. No extra controller, node, selector, topic,
interface, recorder or analysis owner is introduced. Stationary and legacy
rolling modes and direct-call circular defaults remain selectable/unchanged.

Preserve0.08m admission,8/12/20s budgets,5s preparation lease, candidate identity,
pose/freshness, raw-history eligibility, existing command-sweep/boundary/fill
checks, R6 expiry authorization, all ACK/state ownership and original speeds.
Do not add stopping, increase thresholds/timeouts, change detector/estimator
weights, reset controller phase, use evaluator coordinates or weaken a gate.
This source change does not resolve the separate recorded direction outlier.

## Validation and next empirical boundary

The unchanged-source/prototype comparison is already retained; no second
138-trajectory run is needed. Add actual owner/generated-guidance/controller
fixtures that bind the C01 anchor's nominated first command, verify pre-admission
phase selection, original circular behavior after immutable admission, no phase
reset on re-entry, unchanged direct-call/legacy behavior and intact bounds/fill/
freshness rejection. Verify the existing source owners rather than duplicating
the numerical implementation in a new simulator.

Run one named focused bundle covering the new phase tests, centered runtime/
guidance, controller/supervisor, R5 and R6 regressions:240s work within260s total.
Use the exact verified runtime environment and21 installed bindings; preserve
source/test/helper hashes before/after and all failed attempts. Independent
review, exact validation record and source checkpoint precede a new visible case.
No numerical job, Gazebo or bag read belongs to this source bundle.

Prepare materials for a prospective visible C02 separately, with exact same
exposed nominal seed26091011 and all prior C01 scenario settings/budgets. Its
acquisition is conditional on source validation and adoption of its own plan.
Require real approach/admission, fill/escape/SEARCH/global arrival within0.5m,
complete recording/cleanup and full continuous VERIFY/DESIGN evidence, followed
by usable native analysis and all24 direction-reference target outcomes. Preserve
C01 and V10 failures. No full comparison or V11 release follows from source tests.
Simulation only; no physical/Pi/snapshot/V1 changes or commit/push.
