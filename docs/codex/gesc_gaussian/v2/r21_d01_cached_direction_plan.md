# R21 D01: cached direction diagnostic after partial analysis

ADOPTED prospectively before cached binding recovery or reference execution.
The original D01 acquisition remains incomplete. The first separate diagnostic
analysis remains PARTIAL_DIAGNOSTIC_RETAINED: two native scans completed in
58.945868518 outer seconds, with stable inputs and exact recorded arrival at
151.897 seconds. Preserve all original files and verdicts. No new bag scan,
native analysis, simulation, motion recomputation or matrix is released.

Two issues prevent the original diagnostic helper from completing. First, it
tries to hash the deleted temporary noisy configuration named in launch argv.
The runner already retained the exact bytes and SHA256 in
`resolved_cost_function.json` and `captured_cost_configuration`. The existing
`m4_recorded_binding(..., expected_cost_configuration=...)` owner verifies this
strict capture, actual argv, metadata, selected filter and captured geometry.
Use that existing path in a separate helper; do not recreate the temporary file.

Second, the native `state_durations` metric rejects two bag receipt intervals
of 0.156291035 and 0.153656145 seconds against its unchanged 0.15-second limit.
Each is a 0.1-second source-time step. These recorded receipt gaps remain real
failures of that duration metric. Keep it invalid, and keep the original motion
result EVIDENCE_UNAVAILABLE. Its authority flag inherited the helper's failed
all-metrics check. Do not change timing tolerances or recompute motion here.

Direction has separately retained qualified synchronized inputs: 4,467 unique
observations, exact typed provenance, no integrity errors, and all 24 original
scheduled targets. Native source/lifecycle validation, applicability integrity,
critical inputs and analysis-failure checks pass. The sole fresh recording check
failure remains the fixed-duration shutdown metadata. The duration integral is
not an input to direction normalization, geometry binding or reference evaluation.
This supports a separate direction diagnostic, without qualifying the original
acquisition, native analysis or integrated motion acceptance.

## Finite execution and checks

1. One cached binding helper, at most 20 seconds inclusive (14-second internal
   work, 15-second SIGINT plus 5-second kill). Freeze exact helper/source/input
   hashes before execution. Require the original run identity, source stability,
   two completed native scans, sole reference-binding error, exact sole invalid
   metric `state_durations`, all other native diagnostic checks, native lifecycle
   validity and normalized-input qualification. Verify all 588 original pins.
   Exclude raw bag bytes from new reads; their original acquisition/native scan
   hashes remain in retained receipts. Read only cached JSON/YAML and source/config
   files. Call the existing binding owner with the exact captured cost receipt.
   Save a fresh bundle containing a byte-identical normalized file and its new
   binding, plus a receipt explicitly preserving all partial/incomplete verdicts.
2. Only if that binding completes, run the unchanged prepared direction wrapper
   once, at most 45 seconds inclusive (38-second internal work, 40-second SIGINT
   plus 5-second kill). Reuse the existing model/reference owners. Keep every
   target at 15+30k seconds for k=0..23, including unexposed/ineligible targets.
   No alternative targets, reference, estimator, thresholds or source model.
   Retain median and P90 angular error, instantaneous comparison and all
   availability denominators. Original numerical limits remain median <=30
   degrees, P90 <=60 degrees, usable averaging fraction >=0.8 among eligible
   informative targets; an empty eligible set cannot pass.
3. Independent cached review checks binding provenance, source stability, exact
   24-target population, summaries and preserved evidence limits. No numerical
   rerun to recover context. Record commands, elapsed times, failures and paths,
   update live handoff/status and create the material evidence checkpoint.

The case remains exposed development evidence with seed 260921001, separate
from the closed V12 comparison. A direction diagnostic can inform subsequent
method work but cannot turn D01 into a fully qualified integrated run. Future
acquisition must resolve the duration/arrival configuration conflict in a fresh
prospectively specified version. No hardware, Pi, snapshot, V1, commit or push.

## Cached preparation correction v2

Binding v1 stopped before the binding owner in3.221427558outer seconds because
its prepared list omitted the required sensor URDF geometry pin. No binding,
model, reference or bag call occurred. Preserve v1 unchanged. Allow one v2
cached preparation with the byte-identical helper in a fresh sibling directory,
adding only the exact geometry hash already frozen by diagnostic started.json.
Keep the20-second inclusive limit and every original native/input gate. The
reference remains withheld until binding succeeds. This is a preparation fix;
no model, scientific threshold, target or evidence verdict changes.
