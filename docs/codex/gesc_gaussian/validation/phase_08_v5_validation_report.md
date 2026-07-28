# Phase 08.5 V5 Validation Report

## Outcome

**FAILED VISIBLE-GAZEBO ACTIVATION — NOT SIMULATION-READY.**

V5 qualified a fresh, precommitted population in which every case used
exactly two or three lights and statically placed a local aggregate-field
minimum in the direct start-to-global route. The pass-eligible V5C activation
then executed eight actual visible-Gazebo runs.

All eight recordings and cleanups completed. Zero of eight runs created its
first Gaussian fill within the required `0.35 m` of the predeclared blocking
basin. The observed first-fill distances were `1.2624-1.5782 m`. The robot's
curved GESC trajectory therefore bypassed the statically proven route basin
and first converged near a different location, generally close to the global
source.

This is a behavioral/scenario-reachability failure, not a claim that Gaussian
fill, escape, or recenter is absent. Four runs reached `GOAL_HOLD`, and four
runs observed the exact fill, escape, recenter, resumed-search, and global-goal
state path. They still failed V5 because those fills were not at the intended
local basin.

## Authority and population

- Plan: `docs/codex/gesc_gaussian/plans/phase_08_5_plan.md`
- Tested implementation commit:
  `034338d1dd87e306bb390c44027791f449f8d7f8`
- Pass-eligible evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5c`
- Formal suite SHA-256:
  `b91d99405a29dc04688a8b6bac66f3344b09a564832077930ed62329587c4515`
- Suite commitment SHA-256:
  `3c9ea5c6679ba2547a643fe3dc394a308cd25fee7f4ffdedd19476a3259670cd`
- Direct-convergence control cases: `0`
- Light count: exactly `2` or `3` in every activation, development, formal,
  and repeat case.

The static route proof was deterministic and passed before runtime. Runtime
acceptance separately required the first active fill to be no farther than
`0.35 m` from the committed blocker basin.

## Qualification

V5C preparation and qualification passed from its own isolated install:

```text
495 passed, 2 skipped in 92.10 s
```

The two skips are explicit opt-in Gazebo integration tests. Gazebo was then
run through the visible activation workflow itself. Installed resources,
entrypoints, launch/dry-run contracts, process cleanliness, and disk bounds
passed.

## Activation observations

| Case | Lights/family | Analysis | Terminal | First fill to blocker | Controller/global truth | Required blocker encounter |
| --- | --- | --- | --- | ---: | --- | --- |
| `15001` | 2 / collinear | complete | `GOAL_HOLD` | 1.4980 m | pass/pass | fail |
| `15002` | 2 / offset | complete | `GOAL_HOLD` | 1.5732 m | pass/pass | fail |
| `15003` | 3 / lateral | complete | `SEARCH` | 1.5684 m | fail/pass | fail |
| `15004` | 3 / sequential | complete | `FAILSAFE` | 1.2624 m | fail/fail | fail |
| `15005` | 2 / wall-corner family | complete | `VERIFY_EXTREMUM` | 1.5150 m | fail/pass | fail |
| `15006` | 2 / noise-delay family | complete | `GOAL_HOLD` | 1.5626 m | pass/pass | fail |
| `15007` | 2 / collinear | complete | `SEARCH` | 1.5096 m | fail/fail | fail |
| `15008` | 2 / offset | partial | `GOAL_HOLD` | 1.5782 m | pass/pass | fail |

Cases `15001`, `15002`, `15006`, and `15008` observed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Cases `15003` and `15007` performed repeated fill/escape/recenter cycles but
did not reach the goal. Case `15004` entered `FAILSAFE` on its third recovery
cycle. Case `15005` completed one recovery cycle and ended in
`VERIFY_EXTREMUM`.

Case `15008` retained a complete recording, clean shutdown, full state path,
and passed controller/global outcomes. Its overall analysis status was
`partial` because `state_durations` was invalid. That integrity condition
triggered the workflow hard stop before activation cases `15009` and `15010`.
The route-blocker result remains directly observed and false.

## Execution-policy variance

The V5 Plan says the first valid activation behavior miss closes activation.
The workflow recorded case `15001` as a contract failure but continued until
the case `15008` integrity hard stop. This is an orchestration-policy defect:
eight cases ran where one should have been sufficient. It does not convert any
failed result into a pass, and none of the extra runs enters an acceptance
numerator. All eight are retained and reported.

Any future experiment version must make a failed
`route_blocker_encountered` predicate stop activation immediately.

## Terminal counts

- Actual Gazebo runs: `8/120`
- Visible activation: `8 executed`, `2 not_run`
- Headless development: `0 executed`, `30 not_run`
- Headless holdout: `0 executed`, `20 not_run`
- Headless validation: `0 executed`, `50 not_run`
- Headless reproducibility: `0 executed`, `10 not_run`
- Total not run: `112`
- Formal unique denominator entered: `0/70`
- Formal repeats entered: `0/10`

The headless stages were not authorized because activation was not `10/10`.

## Retained evidence

```text
workflow_state/v5_prepare.json
  file sha256 2cad5a7d794d71368f7e5efd9d3b8abdd6900991390a4cc1cc517997c5b6f055
workflow_state/v5_qualification.json
  file sha256 b36d724bee58f64948b8217651cec3a92f317f6f97a68b18879e3e4d93e9b028
workflow_state/v5_activation.json
  file sha256 de32653fc22239b723dc6d11807f4bdd47464b97c995a58df2533300bf3ab0bc
activation/records.json
  sha256 035eb1507f591585f686a0e899b029eb7721c6430e17259c30131db6ea800114
activation/scenario_summary.yaml
  sha256 61e1eea723cf739b9f1c9f6841de4a5ff92806e08850c1e9fcd7af3ea15712b8
```

The earlier `/phase08_v5` prelaunch-only root and `/phase08_v5b` recorder
infrastructure failure remain historical failed evidence. Neither contributes
behavioral runs or acceptance counts.

## Scientific conclusion

V5 disproves the sufficiency of a straight route-projection constraint for
forcing the live GESC trajectory into a chosen local basin. The controller's
curved trajectory can bypass that basin even when the basin is mathematically
on the start-to-global line.

The evidence does support a narrower result: Gaussian fill creation,
repulsive escape, recenter, resumed search, and subsequent global convergence
can execute in Gazebo. V5 does not establish that this recovery happened at
the obstructing local minimum, so it cannot support the requested robustness
claim or the 120-run acceptance test.
