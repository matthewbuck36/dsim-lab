# R1 development direction diagnostic

## V1: retained publication failure

Status: CLOSED_FAILED_PUBLICATION, 2026-09-10 UTC. Adopted input/reference scope:
[R1 direction plan](../r1_direction_diagnostic_plan.md). V9 remains closed
incomplete; no historical science result is reclassified.

The single attempt used saved development C normalized inputs, never a bag or
labels pipeline. All 10 prepared numerical/helper/plan source pins, two metadata
receipts and eight input/configuration receipts passed before work and in the
postfailure closure audit. Actual imported numerical owners resolved to current
repository source. Both helper AST checks and the existing V2 implement context
validator passed before execution.

Exact command from repository root:

```bash
timeout --signal=INT --kill-after=2s 88s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/direction_c_v1/run_once.py
```

External root is that `direction_c_v1/` directory. `command.json` retains exact
child argv and clean Humble -> Q2 -> Q5 environment. The wrapper returned 1 in
7.079849011 seconds of its 90-second inclusive cap; child PID 6551 is terminal
and reaped. Input preparation took 1.633654279 seconds. The first result could
not be published because its result row contains a NumPy `bool_`, which plain
JSON serialization rejects: `TypeError: Object of type bool_ is not JSON
serializable`. No target file was created. This is orchestration publication
failure, not a direction-accuracy or reference-informativeness verdict.

Evidence: `prepared.json`, `started.json`, `console.log`, `worker_receipt.json`,
`execution_receipt.json` and `closure.json`. Execution receipt SHA256:
`f3f62e5ab5ecdf79c31e2d53e57f6d6cbf02b23fb63f8d3a8440477968e1d2e3`.
The closure audit verifies all 20 source/input receipts remain unchanged.

Static diagnosis: existing Q1 evaluation explicitly converts numerical scalar
types through `gesc_gaussian_bag_analysis._q1_plain`; the independent M4 result
owner does not apply that conversion before calling its publication callback.
The existing `atomic_exclusive_json` writer also uses plain `json.dumps`, so
substituting that writer alone would not repair this boundary. A separately
saved correction must preserve native scalar values, all numerical owners and
the original input/target population. V1 remains failed and is not retried.

## V2: usable development measurement

Status: DIAGNOSTIC_ONLY_COMPLETE. The separately adopted
[publication/denominator correction](../r1_direction_export_correction.md)
preserves v1 and the failed historical V9 analysis. The passing result below is
one repeatedly available development trajectory, not independent qualification.

The external root is
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/direction_c_v2/`.
The existing `_q1_plain` owner converts numerical scalars, and the existing
atomic exclusive writer publishes them. A source-only fixture passed six
checks for nested native types, exact values, file content, exclusive output
and nonfinite rejection within a 15-second outer ceiling. Exact argv/result
are in `fixture_command.json`, `fixture_stdout.log` and `fixture_result.json`.

Before dispatch, D3's actual numerical fixture found a nested cycle boolean in
addition to the reference-result publication concern. Its corrected existing
M4 owner converts the complete result row before retaining, publishing or
counting it. `scalar_focused_v2` passed 43/43; the pinned `m4_pilot.py` SHA256 is
`dbc88df919dd8ee969693e7cd7640c1dd05368b33ea3262d38a37b17aa76706d`.
The initial v2 preparation is retained as unstarted, superseded by
`prepared_v2.json`, SHA256
`547733e83ea5476ee4fc650b2a025ab400944b6e972939a423d8302e5104e62b`.
No numeric job ran before these corrected source pins were saved.

Exact single numerical command from repository root:

```bash
timeout --signal=INT --kill-after=2s 88s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/direction_c_v2/run_once.py
```

The wrapper returned 0 in **11.944061794 seconds**, including startup and child
exit, within 90 seconds. Child PID 7766 is terminal/reaped; no timeout or forced
exit occurred. Input preparation took 2.129602698 seconds and the existing
direction evaluator 8.897300829 seconds. All 13 prepared source pins, two
metadata receipts and eight input/configuration receipts matched before and
after evaluation. The separately pinned `_q1_plain` function hash is
`12a4976bc2f1cf3b9b1952de40fe336faf73cab6376c9d48dcd6cb208f4acd68`.
Neither the D3 adapter nor any bag/labels acquisition was executed.

### Result and denominators

All **24 original targets** are retained. Twelve targets at offsets 15 through
345 seconds are exposed, input-qualified, reference-qualified, informative,
eligible, usable outputs and paired comparisons. All twelve use the recorded
.75 moving-cycle average. The remaining twelve targets are explicitly
unexposed; they never contribute fabricated references or angular errors.

| Measure | Recorded moving output | Recorded instantaneous output |
|---|---:|---:|
| Median angular error | 27.506842 degrees | 48.505983 degrees |
| P90 angular error | 31.614203 degrees | 53.348200 degrees |
| Sampled averaging availability | 12/12, 100% | Not applicable |

Every one of the twelve paired outputs improves; median paired improvement is
20.831181 degrees. Moving-output error ranges from 0.331298 to 31.837393 degrees.
The existing <=30-degree median, <=60-degree P90 and >=0.8 averaging-availability
diagnostic rule reports PASS. This provides usable direction-error evidence and
supports retaining the current moving blend while investigating the independently
observed detector/verification failures. It does not show that every continuously
published output is averaged or that performance generalizes to other trajectories.

The independent reference remains the complete recorded objective at the
anchor's fixed base position with periodic repetition of the actual observed
phase-time waveform. It is stationary-position GESC response, not a spatial
gradient, physical field measurement or proof of successful closed-loop seeking.

### Retained evidence

- `result.json`: all targets, existing summary/supplemental metrics and bound
  source/input context; SHA256
  `7fbf25090295797f1dad708325a039ab7bfdec77af8ab53ae2424ee3d585d7d9`.
- `target_01.json` through `target_24.json`: incremental complete rows, each
  bound by `result.json`; rejected/unexposed rows remain present.
- `execution_receipt.json`: SHA256
  `35d5c90f44fb3b872953381725458c63dce81704b441ae2fa451100167c9b504`.
- `worker_receipt.json`: SHA256
  `f19ff43a51db3918dc55113000ac5cc87dd8ec6f12a636a63b4500a1ef5be609`.
- `saved_result_audit.json`: separately verified all 24 target-file hashes and
  exact row equality, 96 native boolean fields, and instantaneous quantiles from
  saved rows; no model or reference recomputation.
- `command.json`, `console.log`, both preparations, initial helper/plan copies,
  the conversion-function source copy and fixture records preserve execution.

Source/measurement ownership was released after terminal/reaped completion.
Parent owns status/handoff and the material R1 checkpoint. Both original research
goals remain in progress; this result does not release the expensive comparison.
