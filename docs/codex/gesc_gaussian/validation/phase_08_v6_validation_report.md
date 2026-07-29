# Phase 08.6 V6 Validation Report

## Result

V6 is **complete but failed its precommitted repeatability gate**. It is not
120-run ready.

The requested mechanism was nevertheless observed repeatedly with unchanged
GESC startup and no affine assist:

```text
local convergence -> typed Gaussian fill -> ESCAPE_REPULSE
-> RECENTER -> resumed SEARCH
```

That primary sequence occurred in H25 and H85 during the visible sweep, and in
repeat seeds 17101 and 17103. Two of those four later entered a failure during
a subsequent search/fill cycle, so only H25 and repeat 17101 passed the
precommitted full-record no-failure gate.

## Executed evidence

External root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6
```

Retained summaries:

```text
phase08_v6_hue_sweep_summary.yaml
phase08_v6_selected_repeats_summary.yaml
```

Seven Gazebo executions completed: four visible sweep cases and three headless
H25 repeats. All seven recordings, cleanup checks, and collision checks passed.
The evidence root occupies approximately `1.8 GiB`.

## Visible sweep

| Case | Ratio | Primary sequence | Full gate | Key outcome |
|---|---:|---:|---:|---|
| H25 | 0.25 | pass | pass | recovered, then reached global |
| H50 | 0.50 | fail | fail | escape stalled, fill rejected, failsafe |
| H70 | 0.70 | fail | fail | local convergence classified as goal; no fill |
| H85 | 0.85 | pass | fail | recovered, then later fill rejected/failsafe |

H25 corrected local evidence:

```text
convergence to local:  0.3701 m
convergence to global: 1.8836 m
fill to convergence:   0.0140 m
```

H25 was the only eligible ratio and was frozen for repeats.

## H25 repeats

| Seed | Primary sequence | Full gate | Local evidence |
|---:|---:|---:|---|
| 17101 | pass | pass | local 0.3276 m; global 1.9197 m; fill 0.0365 m |
| 17102 | fail | fail | converged at global: local 2.2753 m; global 0.0930 m |
| 17103 | pass | fail | local 0.3619 m; global 1.8942 m; fill 0.0252 m; later failsafe |

Precommitted repeatability result: `1/3`, below the required `2/3`.

Mechanism-only result through the first resumed `SEARCH`: `2/3`. This is
reported separately and does not overwrite the fixed full-run result.

## Bounded evidence correction

The initial `observed_local_recovery` implementation required an identical
source timestamp on convergence and fill design. Runtime evidence showed the
valid lifecycle is sequential: H25 convergence at `84.7 s`, followed by fill
design at `93.8 s`, with centers only `0.0140 m` apart.

The runner now selects the latest valid `CONVERGENCE_CONFIRMED` event preceding
the first active fill. No spatial threshold, scenario geometry, intensity,
algorithm setting, or result was loosened. Focused regression after correction:

```text
89 passed, 1 skipped
```

## Scientific boundary

Confirmed:

- the original zero-yaw/full-rotation GESC can encounter the intended local
  source without outcome-selected steering;
- Gaussian fill, escape, recenter, and resumed search work in Gazebo;
- the local/global evidence predicate rejects a fill produced at the global;
- the H25 behavior is not yet reliably repeatable under the full 300-second
  record contract.

Not confirmed:

- `2/3` full-record H25 repeatability;
- three-light robustness;
- physical Hue/lux calibration;
- 120-run readiness or simulation acceptance.

