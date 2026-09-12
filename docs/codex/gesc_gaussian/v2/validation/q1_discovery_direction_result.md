# Discovery direction diagnostic result — 2026-09-09 UTC

Status: CLOSED COMPLETE_DIAGNOSTIC, qualification NOT_EVALUATED. The one
24-target job completed under its300s bound, exit0. No target was replaced,
no confirmation data opened and no source changed during evaluation. This
diagnostic does not qualify Q1 or release M4.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_discovery_direction_diagnostic_v1/`.
The exclusive `diagnostic_closed.json` binds57 artifacts and rechecks the exact
552-source analytical lineage and both actual recorded discovery bindings.
SHA256: `91188431df0160ca89da42c91d2785f7ff05cead0184cdeda265cbb787f913cc`.
Frozen source/validation/release evidence is in
`q1_discovery_direction_preflight.md` and `q1_discovery_direction_owner.md`.

Exact single invocation from repository root:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 300s python3 docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py evaluate > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_discovery_direction_diagnostic_v1/reference_console.log 2>&1
```

All24 causal anchors were present. All24 had complete input/sector coverage;
20 failed the unchanged stationary-reference world-rate CV<=0.10 condition.
Observed CV ranges0.0674268–0.1850267. The four surviving references were
numerically qualified and informative, all in the residence run. Approach
provided zero usable references. Rate variability is a limitation of this
reference's applicability; it is not automatically missing or corrupt input.

| Population | Fixed targets | Informative eligible references | Usable averaging |
| --- | ---: | ---: | ---: |
| Discovery residence26090911 |12 |4 |1/4 |
| Discovery approach26090912 |12 |0 |unavailable |
| Pooled |24 |4 |1/4 (25%) |

On those four eligible reference anchors, recorded rolling-output median error
is55.266605 degrees and p90 is76.574653 degrees. The aligned instantaneous
median is58.811482 degrees. All four output vectors are valid/nonweak, so no
angular output is missing within that already restricted population. Three
use instantaneous fallback; only one applies the blend:

| Residence target number | Instantaneous error (deg) | Actual output error (deg) | Averaging |
| --- | ---: | ---: | --- |
|1 |77.335955 |77.335955 |fallback |
|2 |42.824683 |21.478464 |blend |
|11 |35.734928 |35.734928 |fallback |
|12 |74.798282 |74.798282 |fallback |

The single blended eligible anchor improves its paired error. Four references,
all from one discovery trajectory, cannot establish overall quality or the
required confirmation coverage. Do not treat the small median difference as a
validated improvement. The three fallback comparisons are the same recorded
instantaneous vector, not independent alternative estimators.

Across all24 preselected anchors, irrespective of reference applicability,
runtime output is valid at every target. Four apply the blend,18 report
`weak_cycle_direction`, and two report `cycle_disagreement`. This descriptive
4/24 blend count is distinct from the original informative-reference denominator
1/4. The `weak_cycle_direction` flag comes from the unchanged cycle-variability
magnitude floor; by itself it does not prove the actual direction is wrong or
that the sensor data are noisy. Diagnose that distinction before tuning.

`analysis/references.json` SHA256:
`845a549849295082fe2d3b82f95ff81f788979898e52f47646f228704258a00c`.
`reference_console.log` SHA256:
`60b5d35db71d3c2a5910b0f39252237d26632d8df8c0f294d3061bb42ce6fe98`.
All24 per-anchor JSON receipts remain beside the final result. No repeated
numerical job, replacement target, changed rate cutoff or silent reclassification
occurred. No matched legacy detector latency, fill/goal outcome, causal origin
of the orbit or broad robustness is established.

Next work is bounded interpretation of the recorded phase-rate variation and
runtime fallback, then a prospective decision. A reference for a measured
nonuniform phase waveform would be a new declared numerical method requiring
analytic checks and its own evidence version; it cannot retrospectively make
the old constant-rate references valid. Runtime tuning, detector redesign and
new qualification remain separate future amendments.

## Completed recorded-data interpretation

The separate read-only `diagnostics/rate_and_fallback_v1/` audit completed once
under60s in0.581623s. All24 cycles retain exact34ms source cadence, consecutive
sequence numbers, full sector coverage, stable context/objective and readiness.
World phase equals yaw plus encoder within1.54e-8rad. Encoder mean stays
2.094024–2.094683rad/s, standard deviation<=0.003440rad/s. Yaw standard deviation
0.143068–0.408894rad/s accounts for the world-rate variation; their correlation
is>=0.9999329. This supports genuine recorded turning as the origin of the
variable rate, rather than a cadence/encoder-source defect. Result SHA256:
`4e5abc4033433cbd7d84e630ad981c5e5cab86c7ef83cd201f62b5b5d5aaa280`.

The `diagnostics/cycle_confidence_v1/` audit completed once under60s in5.749678s,
using the existing reader on direction diagnostics/readiness only. Every target
matches its exact first recorded diagnostic sequence, source/observation hash,
publication stamp, bag receipt, run/schema/frame/origin and readiness. Actual
three-cycle means, current rolling mean, variabilities and magnitude floors
are preserved. Result SHA256:
`4a2c39e84c1c6ada74b5b4cc193af83f928b9f49e8ea12be07f4e77a32293edf`;
manifest `58581ea042cd37e91eefed15bb349fe15cb967d0e16387a8a442225192227b6f`.

All24 magnitude floors are3 times recorded cycle variability. Among18 weak
cases, longitudinal variance dominates8 and transverse variance10; median
transverse fraction55.54%. The same three means have median maximum angular
separation54.743deg (26.821–96.117deg);15/18 exceed30deg. The recorded maximum
angle is unavailable in those weak cases because the implementation returns
before evaluating it. These separately derived descriptive angles do not
reconstruct a missing recorded decision or define a new gate. The two actual
disagreement values are30.061deg and32.620deg. Both magnitude and direction
change contribute; simple floor removal is not a supported remedy.

Exact extraction commands, scripts, all24 tables and before/after hashes are
in each adjacent README. Neither audit ran a field model, new reference,
alternative confidence policy, source change or confirmation read. These
completed diagnostics support prospectively evaluating a measured-phase
reference and a separately labeled algebraic blend sensitivity before runtime
tuning. They do not identify a causal correction to the orbit by themselves.
