# R2 oscillation detector prototype

V1 completed offline in2.872096s, terminal0, under118s interrupt+2s kill.
[Prospective method](../r2_oscillation_detector_plan.md). The fixed92 controls
produce21/21 oscillation detections and0/65 negative detections. The other six
stationary/circle positives are outside this component's scope. All repeated
support decisions and control identities are retained; no runtime source changed.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/oscillation_detector_v1/`.
Exact command:

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/oscillation_detector_v1/run.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/oscillation_detector_v1/execution.log 2>&1
```

`run.py`, `pins_before.json`, `controls.json`, `supports.jsonl`, `result.json`,
`receipt.json` and `execution.log` retain the exact computation and hashes.
This is prescribed development evidence, not untouched confirmation or a
closed-loop latency result. A circle/static component remains necessary.

Pre-integration inspection identified a representation limitation: the harmonic
fit and geometric guards both use the declared .2s interpolated representation.
An off-grid original-pose spike could be omitted by those guards. Before runtime
nomination, a separately versioned correction will retain the efficient harmonic
grid but compute confinement and line geometry from every original support
vertex, with exact bracketed boundaries. Preserve v1 and explicitly test spikes
and irregular samples; no old measurement is reclassified.

## V2 all-source geometry correction result

V2 completed terminal0 in3.397128157s under120s. All22 oscillation positives
detect and all68 negatives reject; six circle/static positives remain outside
this branch. The unchanged92 controls plus four new representation fixtures
are fully retained. All54 spiked supports reject actual confinement. Exact
boundaries and every original vertex govern geometry; the harmonic fit alone
uses .2s interpolation. The fitted intercept plus weighted mean supplies the
model center at the support midpoint; endpoint center adds half the fitted
support drift displacement. No threshold changed.

Exact command:

```bash
timeout 120s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/oscillation_detector_v2/run.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/oscillation_detector_v2/execution.log 2>&1
```

External `oscillation_detector_v2/` beside v1 retains `run.py`, controls, every
support, result, pins, receipt, log and read-only `audit.json`. All published
receipt hashes were verified without model replay. This releases finite runtime
integration, not closed-loop or broad qualification. V1 remains unchanged.
