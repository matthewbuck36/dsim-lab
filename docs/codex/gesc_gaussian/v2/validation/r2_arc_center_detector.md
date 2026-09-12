# R2 v3 arc-center/static finite development result

2026-09-10 UTC. The single prospective job completed terminal0 in3.411497242s
(3.367837136s work), within120s. **Finite component nomination PASS:** all32
circle/static positives detected, zero detections on58 declared negatives.
Artifact integrity PASS. Eight oscillations remain unsupported with no trigger;
one .005m/s drift remains a separate gray diagnostic. This is development
feasibility, not full V2 or general robustness qualification.

Method: [r2_arc_center_detector_plan.md](../r2_arc_center_detector_plan.md).
External directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/arc_center_detector_v1/`.
All previous detector/geometric failures and their inputs remain unchanged.
No production source, simulation, bag, field model or holdout was used/modified.

## Measured outcomes

Two independently fitted15s or18s arcs estimate circle-center drift. The fixed
.006m/s center-drift, .08m radius-change, .02m per-arc radial residual, pi/3 net
angle and .50m whole-confinement guards, followed by three consecutive same-
width6s endpoint passes, yield the following complete fixed-control results:

- All original/new constant-speed circle positives, periods12–72s and prescribed
  phase/noise variants, first detect at42s through30s total support plus12s
  persistence. No empirical speed improvement against an independent detector
  latency reference is inferred from this synthetic observation floor.
- Six variable-speed circle positives detect at42/42/48/48/84/72s in their
  declared order. The slowest phase-modulated circles need more support to
  satisfy per-arc coverage repeatedly; they are retained, not replaced.
- Static first detections are12s without noise/.002m noise and30s with .01m
  noise, through the separate12s nearstatic branch.
- All58 negatives, including the new four translating ellipses, the previously
  failed off-grid translating circle, larger loops and directed drift, reject.

All99 controls remain in `control_contract.json` and `control_results.json`;
there are no positive misses or declared-negative triggers. The eight
oscillations are not claimed as validated positives of this circle/static
component. The old false-positive two-block rule is not used as a fallback.

| Development input | First source-time candidate | Time after readiness | Candidate endpoints | Candidate pairs |
|---|---:|---:|---:|---:|
| V5 B | 153.8s | 150s | 10 | 12 |
| V9 B, changed shared translation gain | 104.8s | 102s | 6 | 7 |

Both first candidates use36s total arc support. V5 B has32 passing pairs before
persistence and V9 B24; complete failure/reset histories remain saved. Neither
trace has an independent settling-entry label in this study. These times are
relative to recording readiness, not qualified trap-detection latencies. Replay
cannot establish the motion after an earlier intervention. There was no
stopped acquisition or new closed-loop experiment.

## Command, complete artifacts and integrity

The saved plan/helper/command preceded the sole execution:

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/arc_center_detector_v1/run.py
```

`execution_receipt.json` retains exact argv, returncode0, elapsed time and log
hash. A single30s read-only artifact audit verifies12 published files, all12
selected input/source/helper/plan pins, and the complete99-control population.
`audit.json` saves these checks; no model replay was repeated to audit them.
Phase-context validation and `git diff --check` passed before dispatch.

- `decisions.jsonl`:1997 endpoint rows, including116 combined B endpoints;
  every old/new arc fit, exact drift/radius/confinement margin, consecutive-pass
  counter and reset reason is retained.
- `new_control_samples.jsonl`:12010 prescribed additional samples.
- `control_contract.json`, `control_results.json`, `b_results.json`, `result.json`.
- `prepared.json`, `pins_{before,after}.json`, `receipt.json`,
  `execution_receipt.json`, `execution.log`, `audit.json`.

Result SHA256:
`0a2e4b8aca320af82f8f0d4791722421a0958d174329c227c25c4b0860838600`.
Receipt SHA256:
`9d8a49e18db2ad24b2407b96150e5e5b5221d39a4cd98b2e64855dd09c520d43`.
Exact reusable helper/plan/input pins are in the verified before/after maps.
There is no whole-tree source-stability claim during unrelated agent work.

## Runtime boundary

This is the first passing finite circle/static prototype in this sequence.
Prospective runtime integration should extend the existing convergence owner,
preserve selectable legacy modes and source-time/SEARCH reset behavior, and
combine only with a separately justified oscillation component. Full original
sample/segment confinement must survive any numerical resampling. Meaningful
runtime cost, fault/reset, shared-clock, recorded diagnostic and integrated
behavior checks remain required; this result releases no full comparison.
