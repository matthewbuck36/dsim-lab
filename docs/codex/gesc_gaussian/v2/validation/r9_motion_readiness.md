# R9 motion readiness validation

Material checkpoint saved after completed source/component/review validation:
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r9_motion_readiness_v1/manifest.json`,
SHA256 `bb07b5d61fc546b4a34fcecd64a6d208391a0ea51be3471e2b09df0823ea86ee`.
589 members individually verified,34 evidence receipts,source stable,0.842456s.
Exact command: `timeout --signal=INT --kill-after=5s 50s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r9_motion_readiness_v1/save_closed_checkpoint.py`.
This receipt postdates the archive. No bags/tests/runtime were repeated.

COMPLETE: source, selected C component and independent review PASS, 2026-09-11UTC.
[Adopted plan](../r9_motion_readiness_plan.md). No runtime behavior or scientific
threshold changed. All frozen V11 products and confirmation decisions remain intact.

The existing `evaluate_m4.py::_v10_motion_metrics` now requires usable integer
readiness bounds and checks that both streams' reader flags agree with them.
It pairs only rows within that same interval. Nonempty/equal counts, exact vectors,
finite/valid outputs, inclusive0.5s bag-time bound and source monotonicity remain
required. Full/pre/within/post counts are retained. The non-arrival owner is unchanged.

New focused tests cover startup/shutdown count differences, missing/extra/mismatched
interior rows, boundary crossings, inconsistent flags, invalid bounds, nonfinite
commands and source regression. Four existing projection fixtures now declare
readiness bounds consistent with their represented rows; assertions are unchanged.

## Source validation

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r9_motion_readiness_v1/`.
Source before copies, exact `source.patch`, selection and `source_ready.json` retained.
Owner SHA256 `137aa45d33b04e69b687ecd6cb03d790be55b451b47934e69b5e84d7beedaea1`.

Exact command, repository root:

```sh
timeout --signal=INT --kill-after=5s 95s env -u PYTHONPATH bash --noprofile --norc -c 'source "$1" || exit; exec /usr/bin/python3 -B "$2"' r9-source-validation /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r9_motion_readiness_v1/validate_source.py
```

One bundle: `test_r9_motion_readiness.py`, `test_m4_v10_motion.py`,
`test_m4_evaluation_cli.py`. Session54276 terminal/reaped0;59PASS, no skips/failures,
2.099730s wrapper work (pytest1.55s),304 source/test/helper pins unchanged.
`source_validation.json`SHA256
`0114f61e3f5aa8b9506ca6eac4455def89b1e6d1f0f6ddfef49e2ebd2857d81b`.
No ROS/Gazebo or numerical model was run by this focused bundle.

## Separate C reassessment

Prepared after source validation, `prepared_C.json`SHA256
`2281ab7eda991e999df51a6c0df1d1ff8af73c3986a412caef39e036198c3951`.
It binds the passing validation population, exact frozen C contract/metrics,
unchanged intervention evidence, run metadata and bag, active source/interfaces.
Exact saved argv:

```sh
timeout --signal=INT --kill-after=5s 55s env -u PYTHONPATH bash --noprofile --norc -c 'source "$1" || exit; exec /usr/bin/python3 -B "$2"' r9-C-component /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r9_motion_readiness_v1/reassess_C.py
```

Root dispatched saved argv once, with exclusive `console_C.log` and
`execution_C.json`. Session69875 terminal/reaped0, outer6.018183s; helper5.489169s,
one filtered read2.968616s and one existing motion-owner call0.145981s. All334
prepared/source/input/bag hashes remained unchanged. No full native, label,
reference, behavior or report rerun occurred.

New component: OBSERVED_CONTINUOUS_ACQUISITION, complete authority and motion,
11493/11493 exact pairs during readiness; no pairing errors. Outside-window
counts remain311/312 diagnostics/commands before readiness and314/314 afterward.
Three fully covered uncensored acquisition segments have positive measured motion:

| Segment | Source interval, s | Path, m |
| --- | --- | ---: |
| First VERIFY | 71.1–89.2 | 0.581199 |
| Second VERIFY | 156.5–171.0 | 0.515245 |
| Initial DESIGN | 171.0–171.6 | 0.013849 |

No sustained zero-command or stationary interval was observed.405 readiness-scoped
zero publications retain their recorded bag durations; zero ROS duration does not
claim zero physical pulse duration. All existing motion thresholds are unchanged.

- `reassessment_C.json`SHA256
  `cb4a32bbbe84aaf38e8c5c1b3452676a403ac660734f808077d5d48dcbc4448f`.
- `motion_component_C.json`SHA256
  `372bebaaf0ae21860058d857386d9fcca6f1823f6db33908911c8c985e62eebd`.
- `comparison_C.json`SHA256
  `1f9f93bb6644a093a5f05705522014eca99d6437d1a7b2b8af29f8c1288198e6`.

This is selected component evidence under corrected source. C's original V11
motion-unavailable verdict, prescribed-path failure, successful arrival and all
withheld confirmation/latency results remain separately retained. R9 does not
qualify a new comparison or establish the original detector-speed target.

Independent review PASS:13 checks,59 stable source/receipt/output hashes; no bag
read/hash or new test. `independent_review.json`SHA256
`3fac5a3e542d31a298f83a4689de4a0246f3178047f749bbb0bf2f17fe9c3039`.
The owner AST outside the motion function is unchanged. All34 original V11
closure inputs, old C metrics and intervention remain unchanged.395 zero
publications within acquisition segments have positive bag gaps1.124–13.529ms
to later nonzero publications at the same source tick; these are retained.
