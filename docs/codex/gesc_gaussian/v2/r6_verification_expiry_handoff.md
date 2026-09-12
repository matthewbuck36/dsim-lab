# R6 verification expiry handoff

2026-09-10: SOURCE_VALIDATED. The unchanged-controller baseline reproduced the
C01 failure in1.757365s with128 stable pins and21 installed bindings; session25015
terminated in isolated fixture domain218. Its exact pre-edit controller, fixture,
helper, command and receipt remain under `r6_verification_expiry_v1/baseline_v1/`.

The one final9-module bundle passed312 unique cases in50.074988s, with762 source
pins and21 installed bindings unchanged. Session10905 is terminal/reaped.
Independent static review found no blockers. See
[exact validation](validation/r6_verification_expiry.md).

Only the existing controller authorization owner changed. Otherwise valid centered
VERIFY expiry now immediately forces zero while waiting within original freshness
limits for new supervisor authority. It does not emit an erroneous hard fault
during that bounded wait. Other faults remain effective; missing authority still
faults. Original acceptance and expired collection admission cannot be renewed.
The legal once-only approach-to-collection phase change remains available with
the original admission/deadline rules, including delayed message delivery.
Stationary/legacy and initial DESIGN deadline policies remain unchanged.

Controller SHA256:
`521d33e75696e71657e80394f117715304aed11b1e48081fa22adf62d7701759`.
The source-only regressions do not establish new runtime or direction quality.
C01's approach failure, direction failure and partial native applicability result
remain unchanged. R5's activated-fill exemption still lacks new C01 empirical
exercise. No new Gazebo has run after C01.

Next: adopt the bounded [R7 approach feasibility draft](r7_approach_feasibility_draft.md),
freeze its paired model inputs, and evaluate the fixed-center approach proposal
through the existing controller/collector/unicycle owners. Keep all original
0.08m admission and8/12/20s bounds. A passing prototype requires a separately
validated runtime correction and new visible case before comparison release.
V11 remains NOT_ADOPTED. Branch V2 at3369cfc; changes uncommitted, no push or
physical/Pi/snapshot/V1 work. Current status records the source archive boundary.
