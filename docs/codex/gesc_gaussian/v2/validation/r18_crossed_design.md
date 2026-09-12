# R18 crossed cost/design diagnosis validation

Prospective [plan](../r18_crossed_design_plan.md) adopted before fits.
Context validator and `git diff --check` PASS at preparation. Sole scientific
execution is now complete as recorded below. Original R14/R15/R17 candidate failures remain.

Pre-execution independent conceptual review confirms the factorial diagnosis
and 432-fit accounting. Fixed-XY point estimates should coincide; admissions
need not. Hybrid cost/design results cannot assign additive causal percentages
to physical motion, nuisance projection, truncation or conditioning.

A separate read-only ownership review finds a possible future direction-gate
issue: R15 gates raw H1 and R17 gates mapped raw response even after composing
the full augmented vector `q = raw_weight*M*beta + known_vector`. Thus known
Gaussian/affine information cannot rescue an otherwise accurate full direction.
This is a structural finding only, with no measured count or R18 gate change.
Any future full-direction uncertainty rule must include model error and possible
raw/known cancellation; current HAC noise covariance is not a complete error
bound. Verification must continue to require evidence about the raw field so
artificial fills cannot manufacture basin evidence. Relevant owners are
R15 external `retained_probe.py::mapped_response`, R17 external `gate` and the
runtime `supervisor_node/moving_evidence.py`. No new method is adopted here.

## Execution

Root and independent helper static reviews PASS before execution. Exact argv:

```json
[
  "timeout",
  "--signal=INT",
  "--kill-after=5s",
  "115s",
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
  "r18-crossed",
  "/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh",
  "/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r18_crossed_design_v1/run.py",
  "/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r18_crossed_design_v1/prepared.json"
]
```

Sole session43287 terminal/reaped0:6.579207011s outer,5.180053881s helper.
432/432 fits valid,49 stable pins,152 partials,zero subprocess/model/reference/map/bag calls.
All original144/46/40 populations and8 verification supports preserved.
No estimator/runtime source changed, so no new source tests were run.
Scientific outcomes and hashes are in the [handoff](../r18_crossed_design_handoff.md).
Independent cached review PASS; material archive receipt follows.

## Cached review

Independent cached review PASS in1.604015667s outer (1.597297682s helper):
360 target vector/covariance compositions,432 scores,288 fixed-design agreement
pairs and all original denominators/152 partials checked without refits. Narrative
measurements match cached results. Review SHA256
`5153d0c2a8d636588ff52aca8c4a75163226fd394a15555e8bcce44ab4a61f21`;
receipt SHA256
`94d2a0f7e26a755031aa47684ede243a90cfc505276571a0e00c0fd41feb5df7`.

The next bounded diagnostic should retain the actual additive residual noise:
`y_test = model_fixed_anchor + recorded_raw - model_provenance`, with copied XY
fixed at the original anchor and all source timing/support/reference identities
preserved. This asks whether suppressing motion would leave enough information
under the recorded noise, without new model evaluations. It is a limiting
control, not a proposed stopped acquisition or independent replication. If it
still fails badly, slowing motion alone lacks support. If promising, a single
prospectively selected nonzero travel contraction can test collection feasibility.
No R19 plan, fit or runtime correction is adopted by this R18 closeout.


R18 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r18_crossed_design_v1/`:631 verified source members
in0.944628473s; manifest SHA256
`ea96665137d8a66062afd3fb067441b386f705a14d3329f2da0d1d24fe2f985b`.
This live receipt postdates the immutable archive. Scientific session43287 is
terminal/reaped0; independent cached review PASS. No runtime or estimator source
changed, and no commit or push occurred. The full goal remains incomplete.
