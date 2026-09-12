# Direction-policy arithmetic diagnostic preflight

Status: SOURCE/PREFLIGHT VALIDATED. The prospective contract is
`../q1_direction_policy_diagnostic_plan.md`; its reasoning is retained in
`../q1_direction_policy_review.md`. No new recorded-data coherence or weight
values have been calculated. The completed observed-phase diagnostic remains
closed and all 556 frozen source files remain unchanged.

The external evaluator uses the existing strict lineage and first-diagnostic
join helpers, plus the existing scalar angular-error calculation. It integrates
the norm of the original piecewise-linear demodulation vector only. It does
not evaluate a field, replay a filter, read a bag, acquire a new trajectory or
open confirmation data. The fixed candidate set and nomination rule are in
the prospective plan; nomination would mean development selection only.

The helper reproduces the recorded rolling mean before calculating coherence.
Boundary vectors use the original phase fraction; their timestamps separately
use the original integer-nanosecond rounding. It checks current readiness and
context while preserving warmup cycles that preceded recorder readiness.
Warmup requires the original recorded cycle counts, bounds and sector receipts
to agree with causal source support. A readiness transition does not alone
justify ignoring a source discontinuity or objective change. Original receipt
times may precede a nonzero experiment origin under the existing clock
admission contract.

Review covers fixed populations, invalid-input handling, instantaneous fallback,
weak mixtures, magnitude changes, per-run ranking and exclusive publication.
All failures and missing values retain their original target slots. Coherence
is an observable consistency measure, not a noise probability or a guarantee
of spatial accuracy. The denominator quadrature error is a numerical estimate.

Final combined validation passed **79 tests in 29.91 seconds**, exit 0 under
60 seconds, with no warnings or skips. This comprises 35 mathematical/support
tests and 44 independent evaluator tests. The initial independent arithmetic
slice passed 23 tests in 1.29 seconds; the math-only run passed 35 in 0.61
seconds. No test failures occurred in this preparation. Exact combined command
from the repository root:

```bash
env -u PYTHONPATH bash -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && export ROS_DOMAIN_ID=192 && timeout 60s python3 -m pytest -q /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/preflight/test_policy_math.py /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/preflight/test_policy_diagnostic.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_policy_diagnostic_combined_v1.log 2>&1'
```

The math-only command, from the external preflight directory, was
`timeout 60s python3 -m pytest -q test_policy_math.py`, redirected to
`builds/initial/q1_policy_math_v1.log` under the external V2 root. Independent
source review verified the final held helper, including contiguous admitted
observation IDs, increasing source/diagnostic sequences and causal receipts.
Reconstruction and recorded cycle bounds/counts provide additional checks.

The sourced domain191 freeze command was:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/preflight/freeze.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_policy_freeze_v1.log 2>&1
```

Freeze PASSED: all 556 old source files unchanged, six new plan/review/evaluator/
test receipts, exactly 24 old targets and informative reference/first-diagnostic
joins. Frozen contract SHA256:
`917d10eb90effac6005593448ae324e2b63bfbb74d62dffef4fbecb0a5315a41`.
It verifies the completed D2 result, closure and material checkpoint. No new
weight/coherence values were evaluated by freeze.

Final combined log SHA256:
`427504c18ce4d7cadbb5511f2373d3c298c7c2fd0797cdf9b35f28416c6633ce`.
Math-only log SHA256:
`5a6a4553cb36b890e18f7d6fdd844fe39709300542094f94cc48697666d93cbf`.
All logs remain under `/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.
The contract records all six final source hashes, and the next material
checkpoint binds this record and the retained helpers/logs before release.

No existing runtime, analyzer, numerical-reference, launch or test owner changed
in this milestone. The existing context validator and `git diff --check` pass.
Material checkpoint and dispatch release precede the single 60-second job;
their receipts and eventual result belong in the separate result record.
Qualification remains NOT_EVALUATED, confirmation SEALED, and M4 unreleased.
