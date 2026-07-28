# Phase 08.5 Handoff

## Terminal disposition

**PHASE 08.5 / V5 CLOSED — FAILED VISIBLE-GAZEBO ACTIVATION; NOT
SIMULATION-READY.**

V5 implemented the user's narrower scientific objective: every case has
exactly two or three lights, a weaker local aggregate-field basin is
precommitted directly between the start and stronger global basin, and direct
safe convergence is never an accepted substitute for Gaussian-fill recovery.

The committed population and isolated runtime qualified. Eight visible-Gazebo
activation runs then completed with eight valid recordings and eight clean
shutdowns. In all eight, the actual GESC trajectory bypassed the intended
blocking basin. First fills occurred `1.2624-1.5782 m` from that basin instead
of within the required `0.35 m`; the blocker-encounter contract passed `0/8`.

Activation failed, so none of the headless development or formal 120-run
stages was authorized.

## Git lineage

- Branch: `feature/gesc-gaussian-robustness-v1`
- `8b1fd77` — plan obstructing-local-minimum V5
- `166e72c` — add route-basin proof and runtime predicate
- `a17518d` — precommit the V5 population/workflow
- `9a7d547` — checkpoint initial V5 qualification
- `e6a21aa` — permit fresh V5 activation lineage
- `034338d` — preserve V5B recorder infrastructure stop
- Tested V5C commit:
  `034338d1dd87e306bb390c44027791f449f8d7f8`
- No tag was created or moved.
- No physical hardware or Phase 09 action occurred.

## Population and qualification

The precommitted V5 population contains:

```text
10 visible activation cases
10 development cases x 3 candidates = 30 runs
20 holdout cases
50 additional validation cases
10 fixed repeats
120 declared runs total
```

Every case has exactly two or three lights and passes the V5 static
route-barrier proof. There are no direct-convergence control cases.

```text
suite sha256
  b91d99405a29dc04688a8b6bac66f3344b09a564832077930ed62329587c4515
commitment sha256
  3c9ea5c6679ba2547a643fe3dc394a308cd25fee7f4ffdedd19476a3259670cd
V5C qualification
  495 passed, 2 skipped in 92.10 s
```

## Preserved roots

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5
  prepare and qualification passed
  activation stopped before dispatch on an inherited recovery-lineage check
  0 Gazebo cases

/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5b
  prepare and qualification passed
  activation failed before Gazebo because the shell resolved a stale recorder
  0 behavioral Gazebo cases

/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5c
  prepare and qualification passed from its own isolated install
  8 pass-eligible visible-Gazebo cases
  terminal failed evidence root
```

All three roots are immutable historical evidence. Do not resume, overwrite,
relabel, or merge their counts.

## Visible-Gazebo result

| Seed | Family | Terminal | First fill to blocker | Controller/global truth | Blocker contract |
| ---: | --- | --- | ---: | --- | --- |
| 15001 | 2-light collinear | `GOAL_HOLD` | 1.4980 m | pass/pass | fail |
| 15002 | 2-light offset | `GOAL_HOLD` | 1.5732 m | pass/pass | fail |
| 15003 | 3-light lateral | `SEARCH` | 1.5684 m | fail/pass | fail |
| 15004 | 3-light sequential | `FAILSAFE` | 1.2624 m | fail/fail | fail |
| 15005 | 2-light wall/corner | `VERIFY_EXTREMUM` | 1.5150 m | fail/pass | fail |
| 15006 | 2-light noise/delay | `GOAL_HOLD` | 1.5626 m | pass/pass | fail |
| 15007 | 2-light collinear | `SEARCH` | 1.5096 m | fail/fail | fail |
| 15008 | 2-light offset | `GOAL_HOLD` | 1.5782 m | pass/pass | fail |

Cases 15001, 15002, 15006, and 15008 observed the exact intended state path:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
-> RECENTER -> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

That proves the mechanism can execute in Gazebo, but the fill centers show
that it did not execute at the predeclared obstructing local minimum.

Case 15008's recording, cleanup, lifecycle, and goal outcomes were present,
but its analysis was partial because `state_durations` was invalid. That hard
integrity condition stopped cases 15009 and 15010.

The workflow should have stopped at the first case's failed blocker predicate,
as the V5 Plan required. It instead continued until the case-8 integrity hard
stop. This is a retained orchestration-policy defect and does not change the
scientific failure. A successor must fix first-contract-miss dispatch before
running Gazebo.

## Terminal counts

- Gazebo: `8 executed / 120 declared`
- Activation: `8 executed`, `2 not_run`
- Development: `0 executed`, `30 not_run`
- Holdout: `0 executed`, `20 not_run`
- Validation: `0 executed`, `50 not_run`
- Repeats: `0 executed`, `10 not_run`
- Total: `8 executed`, `112 not_run`
- Formal unique denominator: `0/70`
- Formal repeat denominator: `0/10`

## Terminal source artifacts

```text
phase_08_v5_gate_results.json
  93fc28695e10fa3288ec9d7374b743a5c401e31f2593f474d92883ef365cdde9
phase_08_v5_run_manifest.json
  d4e4e29271371e24293cccf7b77f0f0dc633905cff65079dc62cce00339acd03
phase_08_v5_validation_report.md
  26842cfa829b972d6090efdb9c6260df4bd66278f3678618d66f0e842f750566
phase_08_v5_failure_report.md
  d34acac5d97d44a466ec066f192af9462bf6ac6ed5a1764d21cc9af3ca52cf1b
```

## Scientific conclusion and boundary

V5 shows that a static straight-line route projection is not sufficient to
force the live GESC trajectory into a selected local basin. The path curves
around the blocker and triggers Gaussian fill much later, near another
extremum.

A separately planned successor would need to predeclare geometry against the
observed GESC trajectory/envelope or otherwise build a deeper unavoidable
local basin while retaining the two-/three-light cap. It must not tune V5
after observing these results or accept recovery at the wrong basin.

Do not resume V5, run its headless stages, count its activation runs as
acceptance successes, create a readiness tag, start Phase 09, or run physical
hardware.
