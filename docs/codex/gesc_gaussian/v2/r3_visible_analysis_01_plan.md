# R3 visible attempt01: bounded existing-owner analysis preparation

PROSPECTIVE 2026-09-10; preparation only until root provides the terminal run
path. Production source is held during visible acquisition. All artifacts are
DEVELOPMENT_ONLY for `v2_method_development_D_20260910_01`, with no historical
M4 membership, holdout claim, forced acceptance or repeated acquisition.

## Corrected ownership and finite scope

Call existing `gesc_gaussian_bag_analysis.analyze_run` with a new exclusive
`visible_integrated_01/analysis/analyzer/` destination. Instrument only its
`read_run_bag` call to retain the returned BagData, and wrap the existing
validator `_read_bag` solely to count/time its unchanged call. The actual
existing analyzer makes **two physical scans**: first the full BagData reader,
then its own fresh completeness validation reader. Root explicitly adopted
this ownership correction before dispatch. Neither reader or validator is
replaced, bypassed or given invented success. All supplementary work reuses
the first in-memory BagData; no third bag scan is permitted.

One118s SIGINT timeout,2s kill-after,110s internal work alarm, leaving time for
failure/receipt publication within120s. Output root is existing prepared
`development/20260910/visible_integrated_01/analysis/`; all result files and
analyzer destination must be absent. Exact run path comes from root after
terminal cleanup. Reject nonmatching metadata/run identity. Capture selected
source, resolved settings/metadata, scenario and original bag file hashes before
analysis and verify afterward. The existing analyzer separately preserves its
own raw-hash and completeness checks. Source identity comes from the actual
imported owners, not a fabricated historical checkpoint.

The capture callback saves useful evidence as soon as the first physical scan
returns: full recurrent and VerificationGuidance typed timelines, supporting
state/clock/command/event/confirmation/candidate/fill streams, then normalized
input-only direction artifacts. Only after these outputs exist does the
unchanged analyzer continue through its fresh validation, tables and plots.
This ordering preserves diagnosis if the second scan or later analysis exceeds
the budget. Record scan/phase timing so added work is not confused with native
analyzer cost. A timeout does not release a new unchanged job. Existing analyzer
private temporary cleanup remains unchanged; wrapper artifacts and exact errors
remain retained even when that owner removes its failed private temporary tree.

## Supplementary outputs, no parallel analysis owner

Use canonical `v2_lifecycle.message_payload` for every typed field; the wrapper
schema declares ROS Times as integer nanoseconds and inapplicable nonfinite
scalars as null. Bag receipt/source/readiness metadata, alias and exact ROS type
accompany each row. Export all recurrent/guidance messages, not only passing or
confirming rows. Existing analyzer owns lifecycle joins, event tables and
scientific summary; reference these actual outputs/status in the wrapper result.

For each readiness `/cmd_vel` record retain all6 actual components and exact
all-zero classification. Group descriptively by the latest causal valid
AlgorithmState bag receipt within.5 wall seconds, otherwise UNKNOWN. Report
counts and zero fractions by state, not inferred motor actuation or duration.
Full command rows retain state skew/identity and clocks for later inspection.
Do not use commanded proposals or controller intent as actual final output.
Recorded transition reasons, AlgorithmEvent detail, invalid guidance reasons
and recurrent reset/fit rejection reasons are retained verbatim with timestamps.
Unknown missing reasons stay unavailable; no counterfactual guard is asserted.

Call existing `prepare_m4_direction_inputs(captured_bag, metadata,
run_spec={'run_id': actual_id}, maximum_observations=40000)` once. This preserves
complete recorded augmented objectives and strict input qualification; an
integrity/capacity failure remains unavailable with its full error denominator.
Call existing `m4_pilot.normalize_direction_targets` with actual run ID, armD,
partition development, condition nominal and unchanged24 offsets15+30k seconds.
Keep its returned `version=m4-pilot-v1` honestly as the reused normalization/
reference protocol. Wrap it in a new schema1 `DEVELOPMENT_ONLY` document with
actual experiment identity `v2-method-development-v1`,
`historical_experiment_membership=false`, and explicit protocol_version. Do not
rewrite its version to a nonexistent experiment version or claim a historical
M4 result. Last retained input source stamp is exposure end; first observed
GOAL_HOLD ROS publication, if any, is an explicit terminal censor.

Use existing `m4_recorded_binding` with actual selected configuration receipts
and captured robot geometry for a future reference job. Geometry/configuration
binding performs no field calculation. Save receipts, sources from actual
resolved scenario, and selected settings. If binding fails, retain normalized
inputs and the precise reason; reference evaluation remains unavailable.

## Later reference-only job (prepared, not released)

A separate exclusive `analysis/direction_reference/` job can consume the saved
normalized wrapper and binding, verify their exact hashes plus all actual
selected cost/sensor/geometry owners, and call existing
`m4_pilot.evaluate_direction_targets`. Construct the evaluation-only raw model
through `aggregate_field_truth._model` using the actual selected cost JSON,
actual captured sensor binding and declared sources. No truth enters runtime or
changes normalized inputs/anchors. Save every target immediately through the
existing `on_result` callback, all24 outcomes/denominators, units and failures.
Limit43s SIGINT+2s kill-after and38s internal work. This job is not dispatched by
preparation or the120s analyzer job; root must explicitly release it after input
qualification and bounded analysis results are visible.

## Preparation amendment after attempt01 startup failure

Attempt01 ended before readiness; root does not release its bag for behavioral
analysis. Preserve its acquisition and all historical inputs. The same prepared
helper is now parameterized by required `--run-directory`, `--output-root` and
`--expected-run-id`; root supplies an explicit fresh development attempt after
terminal cleanup. The output root must not exist and is created exclusively.
The identifier must use the fresh `v2_method_development_` namespace and exactly
match recorded metadata. This prepares attempt02 without rewriting attempt01
source or pretending its early startup failure produced behavior. The analysis
method, two-native-scan count,120s budget, wrappers, thresholds and later
reference-only hold remain unchanged. Helper location is preparation lineage;
actual data/output identity is the explicit new run/output path in its receipt.
