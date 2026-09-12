# Direction-policy diagnostic handoff

The finite diagnostic is CLOSED COMPLETE_DIAGNOSTIC. Its predeclared rule
nominates **75% recorded one-cycle mean plus 25% instantaneous vector**, with
current-cycle coherence at least 0.25 and three covered warmup cycles. All 24
original targets pass that hypothetical eligibility rule. Median/P90 error
is 20.526919/34.946685 degrees; 23 improve on recorded output and one worsens.
Weights 0.5 and 1 fail the unchanged P90 requirement. Exact evidence and
limitations are in `validation/q1_direction_policy_result.md`.

This is selection on two repeatedly studied saved trajectories. It establishes
neither actual runtime behavior nor independent qualification. The original
Q1 failure, D1/D2 results, confirmation seal and unreleased M4 remain intact.
The 79 synthetic tests and 10.18-second arithmetic job complete this diagnostic
only. No existing frozen source owner changed; the evaluator and its tests
remain external under `qualification/q1_direction_policy_diagnostic_v1/`.

Before modifying runtime, close the material source/evidence boundary and save
an implementation amendment. Extend the existing rolling/filter owners with
an explicitly named selectable coherence policy and fixed nominated weight;
preserve old default semantics, source/reset clocks, controller speed ceilings,
fallback and all previously recorded flags. Match the diagnostic's original
piecewise-linear norm definition. Include component and transport checks for
DC/reset transients, noise/interference, moving means, zero/weak mixtures and
identity/clock faults. Then declare fresh closed-loop qualification inputs;
the old confirmation data may not serve as fresh evidence for this development.

Detector/neighborhood qualification and the unchanged 16-run M4 comparison
remain outstanding. Keep the full approved V2 goal active. Branch is
`feature/gesc-gaussian-robustness-v2` at HEAD/origin3369cfc; task-owned dirty
changes are retained. No new commit/push, V1 change or physical action occurred.
