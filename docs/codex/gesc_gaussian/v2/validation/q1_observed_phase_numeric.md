# Observed-phase numerical owner validation — 2026-09-09

Status: IMPLEMENTED, focused numerical checks PASS. No recorded-data objective,
reference, confirmation or Gazebo job was run by this owner. This record does
not release the diagnostic or qualify Q1/M4. Parent integration/source freeze
is separate.

Changed owners only:

- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/v2_direction_reference.py`, SHA256
  `7138a5715899aed214d1b4e88f20b470d21a86bf39781318b4e884bba2a0c6d9`.
- New `ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py`, SHA256
  `d3c41f081cffe2a3972617ceef5c7bb70f33b93482574e898e39efa3246f5f8d`.

`observed_phase_cycle` retains the original clipped source knots, actual stamps
and phases, and old rate/coverage fields. CV0.10 applicability is explicitly
preserved under `constant_rate_qualified`/`constant_rate_reason`; readiness and
all other support requirements still apply. The new reference validates the
waveform against its actual count/sectors, complete signed revolution, phase
knots, source gaps and integer crossing boundary before objective access.

`observed_phase_reference` uses the exact periodic adjoint of the selected
alpha1/s washout and d0.18m demodulation. Both time-quadrature partitions retain
all source knots and mapped angular/source-bearing breakpoints. The25,000-call
objective cache, normalized1e-6 component-error ceiling, propagated error and
max(1e-6,20*error) informative floor are preserved. Kernel closure and normalized
DC residual/error must remain below1e-10. Kernel quadrature uses1e-11 tolerance,
objective quadrature1e-7; receipts retain both passes and estimated roundoff.
These estimates do not certify field/model or phase-interpolation accuracy.

The prior constant-rate reference and its public cycle outputs remain
unchanged. Read-only AST inspection against the verified closed source archive
found16 old functions and all prior constants identical. The shared extraction
body differs only in returning its extra internal support receipt; the old
public wrapper returns exactly the previous summary. The original old-owner
SHA256 is `614332ebbaa0d654b11b8f0c7304bf980ea3e7d693172e471dc999d703f51aed`.

## Exact focused commands

All four commands ran from `/home/mattb/dsim-lab`. Each command used this exact
environment prefix:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

The source package was not prepended to PYTHONPATH. Commands after that prefix:

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_numerical_v1.log 2>&1
```

Exit0:47 PASS in3.33s. Initial analytic boundary.

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py ros2_ws/src/ros_esc/test/test_v2_direction_reference.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_numerical_v2.log 2>&1
```

Exit1:131 PASS,1 FAIL in19.34s. The inherited Q1 `uninformative` fixture refused
the analyzer source hash after the parallel analyzer owner changed that file
during the run. This is an effective freshness guard, not a scientific failure
or an ignored check. All54 new numerical checks passed. Parent will run the
combined suite after all owners are stable; no source-hash check was waived.

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_numerical_v3.log 2>&1
```

Exit1:55 PASS,1 FAIL in3.59s. The added complete-receipt JSON check caught a
NumPy boolean produced by the roundoff comparison. Scalar normalization fixes
that publication bug; numerical values and limits are unchanged. The adjacent
finite-extreme-objective check also verifies that overflow produces a failed,
JSON-safe receipt with explicit unavailable fields.

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_numerical_v4.log 2>&1
```

Exit0:56 PASS in3.33s at the final held source hashes above. Tests include an
independent forward DOP853 periodic washout calculation for variable positive
and negative phase rates, with and without dwell; it uses neither the adjoint
nor the owner's quadrature. Signed uniform harmonics reproduce the old Hc
reference; DC/higher-harmonic, offset, rotation, cyclic-time-origin and Hd-limit
checks pass. Narrow analytic peaks, tiny segments and fractional boundaries
pass. Fault tests cover source/context/readiness, fabricated count/sector/phase
receipts, warnings, error/disagreement, budget, timeout, weak direction and
JSON-safe numerical overflow. No actual model values enter these tests.

## Retained log hashes

All paths below are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Log | SHA256 |
| --- | --- |
| `q1_observed_phase_numerical_v1.log` | `86a635a285afdac20def26e5ebda2482ba641a5233a34037d2bf7581ec5417e6` |
| `q1_observed_phase_numerical_v2.log` | `8e158a0608d307a5282f90a1f4792a586446710831f72b59bccafaac7fdf8672` |
| `q1_observed_phase_numerical_v3.log` | `8c9b0b9548f5fbee303d6631a9be933d79e48d78780f42e7c084fbda3af62737` |
| `q1_observed_phase_numerical_v4.log` | `09af70dd978ee337e7f7c72b0a6d8131e6257d38e76b1dcedfc4f809038cad2b` |

Supplementary read-only AST inspection receipts are
`q1_observed_phase_numerical_parity_v1.log` (an inspection-script TypeError from
passing a target list to ast.dump, after function/extraction checks) and
`q1_observed_phase_numerical_parity_v2.log` (corrected list traversal, PASS).
Their hashes are respectively
`db426f3d7c323d82cb1380f13d2266f7c4da60050c4899b01e810c056ddd4c09`
and `ce521a725ca461970c5c9233afa32e8ff8de478608a88a2f8fec3fff104d021f`.
No numerical evaluation occurred in that inspection.

Scoped whitespace inspection produced no findings. Both source files are held
stable for independent analyzer/latent and final parent integration checks.
This documentation was written afterward and is outside the source-freeze set.
