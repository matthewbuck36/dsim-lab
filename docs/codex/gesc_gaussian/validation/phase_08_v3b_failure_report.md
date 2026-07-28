# Phase 08.3 V3B activation failure report

## Disposition

V3B is **CLOSED / FAILED / NOT SIMULATION-READY**. Its evidence root
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b` is immutable.
Exactly one of ten GUI-visible activation cases ran. The other nine are
retained as `not_run`. V3B is not resumed, overwritten, relabeled, combined
with a successor, or counted as a passing activation.

This is not the earlier V3A contact-probe contamination. V3B used the corrected
launch contract with passive contact evidence enabled and the physical
positive-control probe disabled.

## Executed case

The workflow executed `v3a_goal_aggregate_direct`, seed `9301`, from the
qualified corrected runtime snapshot at commit
`e9e1d500116fe884d06574d316143da94e25d920`. The evidence-only execution
commit was `23c2b9b`. Gazebo ran with its GUI visible.

Retained run ID:

```text
20260728T064829892284Z_simulation_phase08_v3_activation-v3a_goal_aggregate_direct-robust_gaussian_v1-acd554565b_1b6fb3f5
```

The attempt passed the infrastructure and safety boundary:

- recorder exit `0`, complete readable sqlite3 bag, and full required topics;
- fresh Phase 05 validation passed;
- cleanup passed with no remaining descendants;
- all final-command representations were zero and final readiness was false;
- collision evidence was valid with zero non-ground contacts;
- no timeout or failsafe occurred;
- controller goal and aggregate-field ground truth both passed;
- terminal state was `GOAL_HOLD`;
- final distance to a global-equivalent aggregate target was
  `0.03908346942306904 m`.

## Behavioral miss

The direct-goal contract required:

```text
SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

and forbade fill, escape, and recenter behavior. The observed path was:

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

`FILL_CREATED`, `ESCAPE_STARTED`, `RECENTER_STARTED`, and
`RECENTER_COMPLETE` were observed. The robot recovered and ultimately reached
the goal, but that does not satisfy the predeclared direct-path contract.
The case remains a genuine behavioral failure.

## Premature hard-stop defect

The scenario predeclared escape metrics as not applicable. Because an
unexpected escape occurred, the analyzer correctly recorded:

```text
applicability_integrity.passed = false
analysis_status = partial
reason = "escape occurred in a case declared not applicable"
```

There was no analysis exception, missing critical input, invalid metric,
recording failure, collision, cleanup failure, or raw-bag drift. The outer V3
workflow nevertheless routed any non-`complete` analysis status through the
immediate evidence-integrity hard stop. That conflated a valid behavioral
contract miss with corrupt evidence and contradicted the Phase 08.3 rule that
ordinary activation misses must finish all ten cases before stopping
development.

The original final integrity and behavior verdicts remain failed. The bounded
correction changes only immediate dispatch routing: a partial status caused
solely by a predeclared metric-applicability violation is an ordinary
behavioral miss for early-stop purposes. Every real analysis error, missing
or invalid evidence, collision, cleanup failure, outer timeout, hash drift,
and ownership failure remains an immediate hard stop.

## Fresh successor boundary

A corrected successor must:

- use the absent root
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c`;
- preserve V3B byte-for-byte and prove all retained hashes;
- recursively re-prove V3B's adopted V3A contamination recovery;
- reuse the exact cleartext suite and commitment bytes without regeneration;
- qualify a fresh clean corrected repository snapshot;
- rerun all ten unchanged activation IDs, seeds, geometries, profile, and
  contracts from the beginning with `gazebo_gui=true`;
- keep the V3B direct-goal miss as historical failed evidence rather than
  using it as a replacement or passing result;
- still close before M4 if any V3C activation contract misses.

## Key retained hashes

```text
V3B activation internal state
  8d50df1cf6eed92a8829758357aacbc61503f816f65086a3f51120e1105c9a48
V3B activation state file
  e915d249e855d8b17c214bdd72efb378caa66636f9838c660ca327cd0c14a80e
progress file
  265d69ae8c4c806fadb5658cb41e88c04832738fc97b44817aa9d62e3e772e45
records and attempt-records files
  4d1edcddec10dbf5b529b0b46d4f1d8189ade380432838f1023cfa1e3c5544ec
attempt record
  d1cc6b4b2f73d5ad70031d3b74d7ac4b535894bdf5425100d3f72175d2593ad5
analysis summary
  fa6f06a7a3cd1e80d8405616c6955644e944097ad5f2fceb23579d467540cbd6
analysis completeness
  c3fc7196032469cb5d3d7966d15ed79706290e5ad506739d9c5ccdf5d300e43c
raw bag
  2d9b2813b2c15623f62fc44907dc391636e4cd53254d2d923ce13d71ac72453c
```

## Superseding diagnostic-completion clarification

Independent review completed before M3C source changes or V3C execution found
that rerunning all ten unchanged activation cases would retry a valid observed
behavioral failure. That would violate the no-replacement rule. The earlier
fresh-successor paragraph above is retained as superseded planning history;
it is not the binding recovery.

V3C instead carries the exact V3B direct-goal record by its original path and
SHA-256, executes only the nine cases retained as `not_run`, and reports one
carried failed record plus nine newly executed diagnostic records. The
carried record is never rerun, rewritten, reanalyzed, relabeled, or counted as
a V3C simulation. The composite result and Phase 08.3 are forced failed before
M4 regardless of the nine new outcomes.

Binding machine-readable policy:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_v3b_diagnostic_completion.json
```

Omission SHA-256:
`c7a8acb97755ee7d41b3bd7932e7d4181bc854b7ee310bf1d4325f365a385e8d`.
