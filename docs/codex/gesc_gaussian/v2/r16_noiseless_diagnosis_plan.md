# R16: separate retained field approximation, geometry alignment and noise

ADOPTED prospectively,2026-09-11 UTC, after complete R15 review/material closure.
Both R15 candidates remain REJECTED. Their synthetic improvement does not
resolve the large unscreened errors on retained trajectories. This is a bounded
evaluator-only model diagnosis, not a new estimator or runtime experiment.

## Question and fixed inputs

Using exactly the six R15 normalized inputs,144 original targets/46 eligible,
40 supported eligible target matrices and eight original noisy verification
supports, distinguish the recorded signal and three model controls at each selected support:

1. recorded raw cost, already fitted in R15;
2. noise-free model cost at the original synchronized base position/world phase;
3. noise-free model cost at the actual recorded raw-cost sensor provenance
   position and world phase, represented as an equivalent base position solely
   for the existing model evaluation;
4. noise-free model cost with the base fixed at the original target/verification
   center throughout that support, preserving its original phase/time waveform.
   Only this explicitly stationary diagnostic also fixes copied fit-input XY
   at that center; it is not a new recorded trajectory or continuous-search run.

For signals2/3, fit-input base positions, phase, timestamps, cycle IDs, target
center/end, source admission and original references remain unchanged; only a
copied raw-cost column is replaced. Signal4 separately fixes model and copied
fit base XY at the same original center, preserving phase/time/cycle IDs. This
stationary control isolates angular approximation/nuisance-phase effects from
motion-driven profile change within the selected model; it is diagnostic only. Keep every unsupported/unexposed target in
its original denominator. Do not fit the recorded values again or regenerate
noise from its seed; missing preceding evaluations would change generator state.

Build six detached models through `scenario_runner.aggregate_field_truth._model`
using each frozen resolved scenario's sources, captured selected cost JSON and
acquisition geometry binding. The JSON light list alone is stale: runtime used
resolved-source overrides, and the existing owner applies the same override.
The model is negative voltage, mode Voltage/scale1/no ADC/reference1000lumens;
noise is a separate runtime owner and is not included by `_model`.

For signal2 use existing `evaluate_raw_cost`. For signal3 recover the original
wire sensor_x_m/sensor_y_m and original world phase. With checked zero joint XY
and zero mount yaw, subtract the existing `selected_sensor_xy((0,0),phase,binding)`
offset from sensor position and call `evaluate_raw_cost` with that equivalent
base. The estimator continues using original synchronized base positions.
Verify source-key, recorded raw value, phase and selected-sample identities
before evaluation; report any mismatch explicitly instead of joining approximately.

Use the existing R15 fit owner, both frozen spatial degrees and cutoffs. Reuse
cached R15 harmonic maps/known augmented contributions and existing mapping/error
owners. Never query new stationary references, solve geometry/field extrema or
modify original numerical qualification. This is a model-generated counterfactual;
its admission counts are descriptive and do not inherit a noise-calibration claim.

## Measurements and interpretation

Report per-run sensor-position discrepancy; model(provenance)-model(base);
recorded-model(provenance) residual mean/RMS/median absolute/P90/P99/max, with
sample counts and noise condition. Keep duplicates across supports explicit and
cache model evaluations by complete source identity; no cross-run identity reuse.

As a prospective reconstruction diagnostic, nominal provenance residual RMS
must be<=1e-4 voltage and P99 absolute<=1e-3 before treating the remaining noisy
residual as a useful isolated measurement-noise comparison. If this premise
fails, preserve the counterfactual but withhold a claim of pure-noise removal
from the actual recorded stream. Do not silently enlarge these tolerances.

For each of the three model controls and spatial variants, report all-supported direction
errors and frozen-admission errors/availability at original eligible anchors,
paired error changes against R15, covariance and predictive/score reasons.
Interpret accurate noise-free directions with poor recorded directions as
noise/alignment sensitivity only where reconstruction supports that attribution.
Persistent large noise-free moving error supports local-model/truncation or
trajectory-identifiability failure within this represented simulation field.
Compare it with the fixed-anchor control: large fixed-anchor error shows that
angular approximation/phase weighting alone is sufficient for error; good
fixed-anchor and poor moving fits instead locate a motion-related difference.
This still does not uniquely separate harmonic truncation from time-nuisance
projection or establish a corrected estimator.
Neither finding alone proves a unique causal mechanism or runtime correction.

Report the same raw-information diagnostics at all eight verification supports;
retain original geometry/minima/negative-cost guards and historical mismatches.
No projection becomes an accepted fill, escape, global arrival or modified old
experiment. Existing direction thresholds and all original populations remain.

## Ownership, bounds and next action

One root-owned job:120s inclusive,115s SIGINT+5s kill, internal108s cap;
BLAS threads1, exclusive retained partial outputs and exact source/input pins.
At most36000 scalar model evaluations covers three model interpretations of
9775 supported target samples plus1927 verification samples, before cache reuse.
At most288 fits (40targets+8verification times3signals times2variants).
No new production source, tests, bag reads, ROS/Gazebo, reference quadrature,
geometry preparation, hardware/Pi/snapshot/V1, commits or pushes. Independent
cached review follows without re-evaluating the field or fits.

Use findings to choose the next substantive method or moving-collection change.
Do not automatically relax prediction gates: R15 unscreened errors make that
unsupported. Promising corrected behavior still requires independent controls,
a bounded visible integrated case and a frozen full comparison.

Work root: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r16_noiseless_diagnosis_v1/`.

Pre-execution source-review amendment: the fixed-anchor control was added before
any R16 model evaluation or fit. The actual cost owner contains an absolute
bearing-angle polynomial with clipping/nonlinear aggregation, so three-harmonic
truncation may cause error even at fixed position. This extra control distinguishes
that possibility from moving-profile mismatch in the same finite job. All prior
R15 results remain unchanged; no numerical outcome motivated this amendment.
