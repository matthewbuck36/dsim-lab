# M1 geometry diagnosis — 2026-09-08

Status: **diagnostic only; no basin labels qualified and no frozen criterion changed**.
The bounded input-only calculation diagnoses the primary geometry from
`m1_labels_v1a/geometry_1.json`. It reads no detector outputs, recorded flags,
or calibration results and performs no new optimization. Existing label and
calibration versions remain unchanged.

The 72-angle quadrature substantially exaggerates the retained minima. Finer
quadrature does not rescue the existing radius-0.50 m, depth-0.025 basin test:
the local ring barrier remains too small, and the global ring contains a point
with lower cycle-mean cost than its retained center.

## Numerical evidence

The existing evaluator and cost owner were evaluated at both retained centers,
nine fixed offsets `{−0.05, 0, +0.05} m` in x/y, the original 36-point 0.50 m
rings, and the two declared source coordinates. Nested uniform quadratures use
72/144/288/576/1152 angles. Center-only adaptive integration uses 72 initial
panels, `epsabs=1e-9`, `epsrel=1e-8`, and `limit=400`; both calls returned without
a warning. Its estimated errors below are numerical estimates, not proofs.

| Center / quantity | 72 | 144 | 288 | 576 | 1152 | Adaptive center |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Local mean raw cost | -0.0662993 | -0.0540403 | -0.0505539 | -0.0497204 | -0.0495309 | -0.0494838 |
| Global mean raw cost | -0.1272620 | -0.1193390 | -0.1175427 | -0.1171131 | -0.1170069 | -0.1169716 |
| Local minimum ring cost minus center | 0.0024382 | 0.0021539 | 0.0019771 | 0.0018667 | 0.0018130 | — |
| Global minimum ring cost minus center | 0.0046942 | 0.0021708 | 0.0005012 | -0.0000443 | -0.0001974 | — |

Local center: `(1.2459541179, 1.2816497451) m`; global center:
`(3.4999999984, 3.1785876065) m`. Absolute 1152-angle errors against adaptive
center integration are `4.7121e-5` and `3.5294e-5` raw-cost units. Adaptive
estimated errors are `4.8363e-10` and `8.0099e-10`, respectively.

Four phase offsets of the 72-angle grid change its mean by ranges `0.0245180`
(local) and `0.0158460` (global). These ranges are comparable to the old
`0.025` barrier criterion. The finer center differences decrease consistently;
ring values are sampled diagnostics and have not received adaptive error
bounds or continuous spatial-ring certification.

At 1152 angles, all eight nearby local grid points are higher than the local
center, although the smallest difference is only `5.4249e-5`. For the global
center, offsets `(-0.05, 0)` and `(+0.05, 0)` lower the mean by `2.0854e-4`
and `1.2040e-4`. This fixed grid does not establish an isolated local minimum.

## Why the coarse calculation is unstable

The unchanged cost owner computes angular error in **degrees**, fits resistance
as approximately `8280.82*r² + 7.90425*beta² + 442.13*r*beta`, clips resistance
to `[100, 337260]` ohms, combines source conductance contributions, and converts
to negative divider voltage. ADC quantization is disabled. See
`cost_function_objects.py:457-568` and `aggregate_field_truth.py:479-521`.

At these centers, the nearby-source conductance peaks have sampled half-peak
support widths of only `1.25°` and `1.5625°`. The 72-angle spacing is `5°`,
and its phase happens to hit the peaks at `230°` and `90°`. Center raw cost
therefore varies from approximately `-2.8454` to `-0.00850` locally and
`-3.8061` to `-0.00778` globally during a revolution. Angular alignment cusps,
resistance clipping and these narrow peaks make a coarse finite-angle objective
poorly suited to tiny-step gradient optimization. This explains the phase
sensitivity and plausibly contributes to scattered optimizer endpoints and
line-search failures; optimizer convergence was not rerun here.

The verified sensor is **0.18 m in front of its rotation joint**. When the base
is exactly at a source coordinate, the rotating sensor points away from that
source throughout the turn. Its cycle mean there is consequently much higher:
`-0.0095520` local and `-0.0078555` global at 1152 angles. Lower cycle means
occur around the source instead. This geometry explains the annular structure
and why a 0.50 m ring around one apparent minimum can intersect another equally
good or better part of the same structure. The global sign reversal demonstrates
that tightening quadrature alone cannot certify the old retained center.

## Suggested independent follow-up

After retaining the failed fixed version, freeze a separate geometry procedure
before examining new detector outputs. First make evaluator integration
error-controlled across every spatial point used for labeling: include phase
checks and adaptive integration or sufficiently refined quadrature, with an
explicit numerical error budget small compared with the proposed barrier.

Then investigate a **connected low-cost region**, including its annular
structure, instead of requiring point-optimizer agreement despite near-angular
symmetry. Keep the same stationary-cycle **mean raw-cost objective** and source-
seeking research target; a minimum-over-angle envelope would be a different
objective and is not justified by this diagnosis. Source positions seed a
bounded polar/grid exploration; they do not supply final truth centers.

A candidate criterion would require a bounded connected sublevel component
and a higher enclosing outer boundary whose cost gap exceeds a prospectively
chosen numerical-error-scaled margin, including spatial sampling uncertainty.
The current primary bounds are `[-1, 5] × [-1, 5] m`; a source-centered 0.75 m
exploration fits both declared sources (nearest boundary distances are
`2.06066 m` local and `1.5 m` global). Those facts do not authorize assuming the
same clearance in other geometries: intersect every proposed grid with its
recorded bounds and leave a boundary-truncated/unresolved well uncertified.

Freeze the finite radial/angular grid, integration checks, component rule,
barrier margin and resulting residence region before evaluating new detector
outputs. Leave uncertified/intersecting regions and ambiguous trajectory
intervals unknown. Do not simply lower `0.025` until the existing rings pass,
or label a source-coordinate disk as a proven minimum.

This diagnosis establishes neither a new region nor a replacement threshold;
additional independently specified spatial qualification is necessary.

## Reproduction and retained artifacts

Command, from `/home/mattb/dsim-lab`:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
timeout 180s python3 /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_geometry_diagnostic_v1/diagnose_geometry.py > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_geometry_diagnostic_v1/diagnostic.log 2>&1
```

Exit **0**, numerical job **8.680235 s**. Python 3.10.12, NumPy 1.24.4,
SciPy 1.8.0. No ROS graph or Gazebo was launched.

All files are under
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_geometry_diagnostic_v1/`:
`inputs.json`, `summary.json`, `local_diagnostic.json`,
`global_diagnostic.json`, two `*_angular_profile.csv` files, the exact script,
and `diagnostic.log`. JSON artifacts use exclusive creation.

| Input/artifact | SHA-256 |
| --- | --- |
| Frozen geometry receipt | `1c8894470340bc1118ff94a9d417de44d8a4efef828729dd4af936a6fec25666` |
| Frozen seed-19801 scenario | `9c4a56e7793780124c2384b00a18a7706d0be256fc372a3aaf39783b91cae05a` |
| Cost JSON | `7a5f883e901070707bc37dc673bf27af6387fe650720fc0c84dca11767632741` |
| Evaluator owner | `b9b0e8b483dc4d7ac2fd392b7ef7ed57a8cb95ebb600124dc5d964b4cf0190c5` |
| Cost owner | `b54cf0baa3e068c471c424b2f629d3fa896c30187040769ca27808d5c7f77886` |
| Sensor URDF | `6a49d4ea96315e9d81cfddd30ad2ab9e1210c809af1e301f188f861760ebf425` |
| Sensor transform JSON | `8fcfb1e2c9e7a8d1463936ab525c2a1533b60bc0548391ca8cf3b3941ffc99b5` |
| Diagnostic script | `51ef1ef07faa565e9aa31dac2aea97a48fc785e8647bc92a7af103dd38e84271` |
| Complete diagnostic summary | `509818ecc208d0a58a678e2e9ed6cb72ac4fc3ebf34931dd3eb6efee8e82b05d` |

`inputs.json` records the exact paths and all input hashes. Model configuration,
evaluator, geometry and transform hashes were asserted equal to the retained
receipt before calculation; the scenario hash was checked against the frozen
inventory. The source locations and source intensities came from that scenario,
not the generic light-source defaults in the cost JSON.
