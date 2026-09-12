# R1 detector measurements from retained B and fixed controls

2026-09-10 UTC. All planned numerical outputs are complete and their independent
artifact audit passes. The original command exited1 only after writing its final
result and hash receipt: stdout JSON serialization rejected a NumPy int64.
That failure is retained; the numerical job was not rerun. No runtime source,
bag, field model, holdout, V1, physical source or simulation was accessed/changed.
This is development evidence; research qualification and empirical B latency
remain unavailable.

Prospective method: [R1 plan](../r1_detector_diagnostic_plan.md).
External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/`.
Measurement directory: `detector_b_v1/`; separate read-only artifact audit:
`detector_b_v1_audit/`. Root owns status, handoff and material checkpoint updates.

## Main findings

The selected W6 two-block rule fails this independent finite control set in
both directions: it misses two confined stationary-center circles and detects
one translating circle. Shortening W to3s worsens both counts. The unchanged
strict threshold and radius checks were used through `CentroidWindowDetector`;
no threshold was fitted to B or the controls.

| Configuration | Positive detections | Negative detections | Control-set result |
|---|---:|---:|---|
| W6, epsilon .18 m, radius .50 m | 9/11 | 1/17 | FAIL |
| W3 sensitivity, same thresholds | 7/11 | 7/17 | FAIL |

All stationary and projected oscillation positives are detected by both
configurations. For radius .25 m circles, W6 misses P36 and P48, whose recorded
replay scores are respectively .318301806 and .362254137 m. W3 misses P18,
P24, P36 and P48. The full control population, every generated sample and all
completed supports are retained; neither these misses nor later detections were
discarded by favorable phase/support selection.

W6 incorrectly detects the .02 m/s translating P48 circle at78s. W3 incorrectly
detects .02/P12 at24s, .04/P24 at39s, .02/P36 and .04/P36 at18s, .02/P48 and
.04/P48 at18s, plus straight .02 m/s at24s. The straight-drift sensitivity case
lies exactly on the analytic .18 m strict boundary: floating-point replay scores
range .17999999999999927–.18000000000000038 m. It remains a recorded false
detection, with this numerical-boundary limitation stated explicitly. No
rounding tolerance or retrospective outcome correction was introduced.
All five radius1 m loops and both .04 m/s straight-drift cases are rejected.

Sixteen independent arithmetic checks pass within the same measured job:
stationary/linear block-score identities and the prospective circle
piecewise-linear interpolation error bounds. For ideal fixed circles the exact
two-block response
`2*r*P/(pi*L)*sin(pi*L/P)^2`, L=3W, explains the finite-period sensitivity.
It does not establish the cause of every recorded B/V9 observation.

## Retained B timeline and geometry

The five already decoded B streams contain36040 publications; all are retained
with full original payloads and stream row identities in
`detector_b_v1/all_publications.jsonl`. The readiness interval is
bag1789025232366848044–1789025592086283487ns; associated recorded clock is
3.8–360.9s. Its10501 admitted pose rows span source3.893–360.893s without an
invalid/regressing/conflicting/gapped pose. Recorder-relative `t_motion_sec`
was not substituted for source time.

The10718 detector publications comprise217 outside-readiness,1059 invalid-
history,1236 valid-score-and-radius failures and8206 radius-pass/score-fail rows.
Deduplication by run/epoch/reset/support identifies **54 distinct complete
supports**:47 radius-pass/score-fail and7 both-fail. There is no candidate.
The recorded score range .289676733–1.020874251m is therefore supported by
actual computed histories, rather than explained by unavailable pose history.
The217 reset-timeline rows preserve162 recording-not-ready and55 outside-SEARCH
reason publications; no detector cause is assigned to unrecorded callbacks.

Fixed readiness-origin36/72s bins produced11 complete fits and4 partial bins.
The initial/final bins lack exact full boundary support or full duration and
remain explicit partials. All complete36s bins represent less than one fitted
cycle. Complete72s-bin estimates are:

| Source interval, s | Harmonic period, s | Explicit center drift, m/s | Positional RMS, m | Axis ratio | Cycles represented |
|---|---:|---:|---:|---:|---:|
| 75.8–147.8 | 66.50 | .004117961 | .035795405 | .823273 | 1.082707 |
| 147.8–219.8 | 62.25 | .001429369 | .036160173 | .929277 | 1.156627 |
| 219.8–291.8 | 54.75 | .000781224 | .033951657 | .962047 | 1.315068 |

The separate algebraic circle fits for these bins have radii
.285431/.250915/.243627m, radial RMS .053730/.031815/.019159m, and descriptive
bearing-slope periods63.218871/61.110628/55.117051s. All parameters and residuals
for every bin are in `b_fixed_bin_geometry.json`.

The preset circle-like rule requires1.5 represented cycles, so **zero bins pass
that descriptive reliability screen**, despite the observed recurring loops.
The estimates suggest slower orbital motion than the12–48s synthetic-positive
range; this is a development hypothesis, not a qualified period/drift result.
The circle-plus-translation fit can absorb unmodelled shape; a small fitted
drift is not a calibrated rejection of translating motion. B remains without
an independent entry label, and replay cannot establish earlier-intervention
closed-loop behavior. These V5 observations do not explain all V9 failures;
later V6–V9 also changed the shared translation gain from1.0 to.5.

## Exact commands, failures, integrity and outputs

Pre-edit context check:
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
PASS. The original exact numerical command is saved in `command.json`:

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/detector_b_v1/run.py
```

Work7.056438418s; inclusive command7.295145371s, terminal1. The final stdout
TypeError is preserved in `execution.log`; all computation, exclusive artifact
publication, before/after pin equality and `receipt.json` preceded it.

The separately saved `detector_b_v1_audit/plan.md` preceded this read-only audit:

```bash
timeout 30s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/detector_b_v1_audit/audit.py
```

Terminal0, .221841836s internal elapsed. It verifies19 originally published
file hashes, all9 selected source/input/plan/helper pins, the complete28-control/
56-result population,16 arithmetic checks, all timeline/support rows and15 fit
bins. It preserves original_command_exit1 and explicitly records
measurements_complete=true, artifact_integrity=PASS, measurements_recomputed=false.
No whole-tree source-stability claim is made while independent agents work on
other owners.

Important artifacts within `detector_b_v1/`:

- `detector_publications.jsonl` (10718), `completed_supports.jsonl` (54),
  `reset_timeline.jsonl` (217), `state_transitions.json` (2).
- `readiness_poses.jsonl` (10501), `b_fixed_bin_geometry.json` (15).
- `control_contract.json`, `control_samples.jsonl` (33628),
  `control_supports.jsonl` (1680), `controls.json` (56), `arithmetic_checks.json`.
- `prepared.json`, `input_source_pins_{before,after}.json`, `result.json`,
  `receipt.json`, `execution_receipt.json`, `execution.log`.

`result.json` SHA256:
`8d66e36c7c783dd2dd51650b1a093724124c9304bc26357c78fe25e648df3294`.
Original measurement `receipt.json` SHA256:
`49ddb2d0cfba26b107a02bee1be9f8103f4c003b9089fb80158fa56e07cb5d1e`.
The separate audit receipt binds these exact artifacts and its own plan/helper.

The selected numerical source SHA256 pins, unchanged before/after and at audit:

- `centroid_windows.py`:
  `ddae313fb385a97b0dead39fc86a0d0b3280c57c8832b8799f0780bf745788ee`.
- `centroid_contract.py`:
  `1f024053b56e386a8a2faeca7270a31eaa22c5c625f0209814173dfdde67848a`.
- External `run.py`:
  `8037085a9e2f67ff571a7d6b1048742f54c3b7c9e7b4c6f7b419582fa37029a4`.
- Prospective R1 plan:
  `e285bc6cc0b580be8574cb3f67f5e6b0f861bccf36f024741ffa5f17b51a4f04`.
  The five complete compressed input hashes remain in the referenced pin maps.

## Next method decision

The measured controls reject a threshold-only or shorter-window nomination.
An explicit recurring-shape/center-translation model is a justified development
candidate, especially for partial slow circles; any such method must retain
independent translating/large-loop/straight-progress negatives, account for
partial-arc identifiability and include oscillation/static handling. The failed
1.5-cycle descriptive screen is not a new runtime requirement. A prospective
bounded R2 prototype can examine another well-defined identification rule while
preserving every R1 outcome and keeping field truth evaluator-only.
