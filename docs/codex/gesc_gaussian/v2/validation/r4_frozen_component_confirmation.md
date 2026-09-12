# Frozen 96-trace recurrent component confirmation

FROZEN_FINITE_COMPONENT_PASS, 2026-09-10:36/36 newly generated positives
detected,0/48 negative confirmations and0 repeated confirmations. All36 first
confirmations used the generating motion's matching branch. Twelve gray or
unsupported histories remain excluded from acceptance. No threshold, input,
label or production source changed after results.

The [prospective plan](../r4_frozen_component_confirmation_plan.md) fixes every
case, equation, seed, phase, heading, source interval and decision before input
generation. This finite component evidence follows model selection; it is not
an IID reliability estimate, full qualification or release of the16-run study.

## Exact execution and ownership

External directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/frozen_component_confirmation_v1/`.

Context validator `timeout --signal=INT --kill-after=2s 28s
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
v2 implement` exited0. Preparation ran once, exited0 in.669476473s, generated
96 identities/114560 points and pinned all inputs before any detector call:

```bash
timeout --signal=INT --kill-after=2s 28s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/frozen_component_confirmation_v1/prepare.py
```

After D3's single-C profile was terminal/reaped and released its source/CPU hold,
the sole numerical job was:

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/frozen_component_confirmation_v1/run.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/frozen_component_confirmation_v1/execution.log 2>&1
```

PTY98146 exited0 and was reaped. Internal numerical/output time9.582620131s;
complete receipt9.612701952s, within110s internal and118+2s outer limits. There
was no retry or bag/model/Gazebo read. Root received terminal/source release
before dispatching visible03.

The helper extracts and executes the unchanged actual per-case update loop
from `combined_runtime_replay_v2/run.py`. It calls the production
RecurrentGeometryDetector on every original point and continues after the first
event, preserving all five branches and the actual OR/latch. It does not execute
that old helper's fixture construction or historical D replay. Production core,
contract and dependencies remain unchanged.

## Results and actual source timing

| Positive class |Detected / total|First model endpoint min / median / p90 / max|
| --- | ---: | --- |
|Circle|16/16|42 /42 /42 /42s|
|Oscillation|16/16|48 /48 /66 /66s|
|Static|4/4|30 /30 /38.4 /42s|

The sigma.009m static case035 first qualifies at42s (actual source42.024s), with
observed support radius.035881782m; its earlier nonqualifying supports are retained
without changing the noisy positive label. The other three static histories
qualify at30s. Integer-nanosecond endpoints are authoritative; JSON's
30.000000000000004s representation is floating conversion only.

| Negative class |Confirmed / total|
| --- | ---: |
|Translated circles, .023/.037m/s|0/16|
|Translated oscillations, .023/.037m/s|0/16|
|Straight drift, .021-.057m/s|0/4|
|Large loops, radius1.1/1.3m|0/8|
|Repeated2m source spikes|0/4|

The four A=.31m translated oscillations all reject. This is expanded empirical
coverage; the earlier cancellation bound assumed A<=.25m and does not prove this
result. The 16 positive oscillations also include four A=.31m cases, all detected.

All32 irregular histories retain their exact71/113/127/97ms source intervals.
The largest difference between an accepted model endpoint and the actual source
sample that makes it available is.096s. This is causal numerical source timing,
not reconstruction of ROS callback receipt or publication latency.

The source population has114560 points and9600 retained completed-branch rows;
the latter includes2496 incomplete-support evaluations. Other recorded reasons
are3928 model_guard,1112 model_pass,1909 not_confined_line_geometry and155
invalid_model_fit. All four spike cases together have296 fully represented
branch rows; their minimum actual confinement radius is2.000861911m and none
confirms. Original spike points are present even if interpolation for the
harmonic fit would miss a short spike.

## Gray and unsupported outcomes remain separate

Five of12 excluded cases confirm:

- circle drift.003m/s:42s;
- oscillation drift.003m/s:48s and.005m/s:66s;
- zero-drift circle P107s:48s;
- zero-drift oscillation P91s:66s.

Seven do not confirm: circle drifts.005/.008/.012m/s; oscillation drifts
.008/.012m/s; the A=.04m oscillation; straight drift.005m/s. These labels were
frozen before execution and remain excluded regardless of outcome. In
particular, the P91 oscillation's acceptance does not establish its correct
period identification or generalize the supported period range.

## Integrity and recoverable artifacts

`control_contract.json` contains all96 unique new identities, exact parameters,
sample hashes and source-spike timestamps. `control_samples.jsonl` retains every
original integer timestamp and XY point. `supports.jsonl` contains every model
row; `result.json` contains all outcomes, first candidates, strata and rejection
counts. `prepared.json` pins inputs and selected source before evaluation;
`started.json`, `receipt.json`, helpers and `execution.log` retain the execution.

An independent post-job SHA256 check verified8/8 retained artifact hashes and
10/10 source/input pins, with zero errors. Execution/integrity COMPLETE and
scientific PASS are separate findings. Key hashes:

- result: `2a1261747f3bbfa7df711203d646e41d893c6419e5f84d91e8d70fa8319f68e8`
- receipt: `66f448dbbd2d79dd3716d3677d916b39d5909c2ca026cbfa768658b92612f5b8`
- core: `b10fa55d49373493327369385f1b5964d0fae8a7461111724745c5d9cf5c7920`
- recurrent contract: `d41ec642ede342d53e89e01d043a90f2710468ef437cac7dda922d73cda4ae78`

No prior retained development populations are added to these denominators.
Stationary Arm B still needs the separately audited typed request envelope;
this detector check does not implement that integration. Full comparative and
broader closed-loop behavior remain pending. Root owns status/handoff/checkpoint.
