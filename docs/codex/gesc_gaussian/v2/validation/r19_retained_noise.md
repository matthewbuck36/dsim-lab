# R19 retained-noise diagnostic validation

[Prospective plan](../r19_retained_noise_plan.md) adopted after R18 reviewed
archive and before any fits. Independent conceptual review PASS: exact additive
residual transfer,48-fit accounting and original support/reference populations.
Failure is a bounded development decision for this noise realization and method;
it does not prove every nonzero travel contraction would fail.

No numerical owner or runtime source changes are planned. The current harmonic
owner SHA256 remains
`449f4403edef7867b11a22f1715d346158f5ff8d719ec949fde084ac18604b1a`.
Helper preparation/static review, scientific execution and independent cached
arithmetic review are complete. No runtime is active.

## Separate verification-purpose audit

A read-only source/method review finds that the current angular-information
rule is not a spatial-minimum certificate. Runtime `moving_evidence.py:302`
checks repeatability of the whole demeaned angular profile plus negative cost
and rotation-minimum summaries; R15/R17's diagnostic projection requires H1.
An ideal isotropic spatial minimum can have constant cost around a sensor circle;
an anisotropic minimum can have H2 without H1, while a slope can produce H1.
The real directional sensor complicates that ideal example but does not turn
angular amplitude into positive spatial-curvature evidence.

The stationary counted path (`supervisor_node/state_machine.py:1002`) compares
repeated rotation-minimum intervals; it does not certify a Hessian. The existing
`basin_estimator.py:394` checks quadratic rank/conditioning, then clips negative
Hessian eigenvalues for fill design and floors basin depth. Those modified
quantities are not measured positive-curvature evidence. Cost consistency alone
would also accept a negative flat field and is not a justified replacement.

A future local-well verifier would need phase-comparable measurements at multiple
spatial offsets, an interior stationary point and positive curvature/outward cost
rise distinguished from noise. Reuse the existing quadratic basis and evidence
owner, but inspect the unclipped Hessian/unfloored depth and spatial excitation.
Flat, sloping and saddle controls must remain negative; missing excitation stays
unavailable. This is a proposed direction for method work, not an implemented
verifier or a reason to change the frozen R19 information decision. SEARCH
direction and verification of a local well remain separate research questions.

## Execution and reviewed outcome

Exact sole scientific command:

```json
[
  "timeout",
  "--signal=INT",
  "--kill-after=5s",
  "35s",
  "env",
  "-u",
  "PYTHONPATH",
  "OPENBLAS_NUM_THREADS=1",
  "OMP_NUM_THREADS=1",
  "MKL_NUM_THREADS=1",
  "PYTHONDONTWRITEBYTECODE=1",
  "ROS_DOMAIN_ID=201",
  "ROS_LOCALHOST_ONLY=1",
  "DISPLAY=:0",
  "bash",
  "--noprofile",
  "--norc",
  "-c",
  "source \"$1\" || exit; exec /usr/bin/python3 -B \"$2\" --prepared \"$3\"",
  "r19-retained-noise",
  "/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh",
  "/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r19_retained_noise_v1/run.py",
  "/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r19_retained_noise_v1/prepared.json"
]
```

Session51515 terminal/reaped0:3.070531238s outer,2.353673327s helper.
48 valid fits,58 stable pins,152 partials,zero model/reference/map/bag/subprocess calls.
A root wrapper KeyError reading ready.command occurred before execution;
prelaunch_wrapper_failure.json preserves it. Exact argv lives in prepared.command.
The corrected wrapper launched the scientific job once.

Independent cached review PASS in0.944264504s outer,214 stable selectedinputs.
All11,702 residual-transfer rows,48 gates,40 q/Cq/error compositions,720 cached
diagonal comparisons and original144/46/40+8 populations checked without refits.
Review SHA256 be3738c589f31926d904e2d46e85daca474dba13049af082e6149b8cfb617f3b;
receipt SHA2566253cbea2ec13d50945e267d470e4e229a8ccc1d4216c7ac2d23f44c2e42fa4a.

Both noisy all-supported direction gates pass. Frozen admission22/46 and
verification2/8 leave the motion-only decision FAILED. Full figures, limits,
source hashes and next method question are in the [handoff](../r19_retained_noise_handoff.md).
No numerical-owner/runtime source changed; no new source tests were needed.


R19 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r19_retained_noise_v1/`:634 verified source members
in0.902510378s; manifest SHA256
`f7dd55bf5acb4eddcce25e51400f72b6ee865de5aa332228679364e4a015212a`.
This live receipt postdates the immutable archive. Sole scientificsession51515
is terminal/reaped0; independent cached review PASS. No estimator/runtime source,
physical/Pi/snapshot/V1, commit or push changes. Full goal remains incomplete.
