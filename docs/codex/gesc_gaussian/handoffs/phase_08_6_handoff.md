# Phase 08.6 Handoff

## Terminal state

V6 is closed **FAIL / NOT 120-RUN READY** at seven total Gazebo executions.

Tracked implementation commits:

```text
5e7cc46 phase 08.6: plan two-light Hue ratio demonstration
1482ff5 phase 08.6: qualify two-light Hue sweep
b63eb79 phase 08.6: select H25 for repeatability
```

The final closeout commit follows this handoff.

## What works

- exactly two lights in the `4 m x 4 m` room;
- unchanged zero-yaw/full-rotation GESC startup;
- no affine escape assist;
- local convergence near the declared lower-output source;
- typed Gaussian fill creation;
- `ESCAPE_REPULSE`, `RECENTER`, and resumed `SEARCH`;
- causal local/global fill evidence;
- complete bags, final-zero/readiness contracts, clean teardown, and collision
  evidence.

The full local-recovery mechanism occurred in four of seven runs: sweep H25,
sweep H85, repeat 17101, and repeat 17103.

## What failed

Only two of seven runs passed the full-record V6 case contract. The selected
H25 repeats passed `1/3`, not `2/3`:

- 17101 passed and later reached the global;
- 17102 converged/fill-designed at the global and failed recenter;
- 17103 completed the local recovery, then later rejected a second fill and
  entered failsafe.

## Retained evidence

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6
```

Size at closeout: approximately `1.8 GiB`. Do not rerun to recover context.
Read the two suite summaries and per-run `scenario_result.yaml` files.

Tracked reports:

```text
docs/codex/gesc_gaussian/validation/phase_08_v6_selection.json
docs/codex/gesc_gaussian/validation/phase_08_v6_validation_report.md
docs/codex/gesc_gaussian/validation/phase_08_v6_failure_report.md
```

## Successor decision

A successor must prospectively choose one of two claims:

1. first-episode Gaussian recovery through resumed `SEARCH`; or
2. stable multi-cycle behavior across the entire fixed recording window.

The first claim already produced `2/3` H25 repeat episodes. The second produced
`1/3` and requires diagnosis of global convergence/recenter and later
fill-rejection behavior before any 120-run campaign. Preserve V6 unchanged.

