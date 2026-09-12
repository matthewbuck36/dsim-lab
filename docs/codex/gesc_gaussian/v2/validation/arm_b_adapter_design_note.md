# Arm B compatibility design provenance

Historical pre-implementation diagnosis, retained below. The adopted exact
contract and active implementation are now in ../q5_stationary_centroid_adapter_plan.md
and q5_stationary_centroid_adapter.md; the prospective wording below describes
the original source boundary. Arm B selects centroid_windows_v2 plus stationary_v1. The detector
emits authoritative CentroidConvergenceDiagnostics, while its AlgorithmEvent
has no valid relative source timestamp. Stationary SupervisorNode expects the
legacy eight PDE values and therefore never accepts that centroid confirmation.
Launch also lacks a detector-mode/typed-topic selector for the supervisor.

The bounded future correction should add a B-only typed confirmation adapter
inside the existing supervisor, validating run/frame/topic/epoch, full support,
original source/publication/receipt times, score/radius and once-only identity.
Retain the typed center separately and reuse the existing transition input and
stopped VERIFY/DESIGN, raw RotationCostWindow, counted ranking and timeout. A
neutral candidate-center accessor can serve typed B or the inherited PDE path.
Do not enable MovingSupervisor to make B work, synthesize PDE values, or write a
metre-valued score into r_mean_m2.

The stationary fill hop needs an explicit typed request carrying the original
centroid diagnostic, request stamp, actual selected Timekeeper origin,
CREATE/targeted-REDESIGN identity and existing candidate-cost evidence fields.
The existing GaussianFillNode can normalize this into its common robust request
context, sharing synchronization, frozen sample window, estimator, designer and
registry. Preserve the original stationary receipt-ended fit window. This is
an interface adapter, not another moving pipeline or new fill algorithm.

Keep original absolute source/history times. After verification, the accepted
historical confirmation is not re-timestamped or required to remain a fresh
0.5s acquisition. Derive any legacy relative fill/result correlation time from
the actual Timekeeper origin once; never assume zero origin. Preserve targeted
redesign and old fill/result correlation. Extend existing launch, IDL, recorder,
validator and analyzer owners only as needed for the selected B request.

Before implementation declare the exact schema and owner boundaries. Required
focused evidence: A unchanged legacy stationary; B actual typed confirmation
through stopped verification and a provenance-correct fill; C/D unchanged
moving typed/transaction routes. Include parser/launch four-mode checks,
bounded actual DDS B transport, adversarial run/frame/topic/epoch/order/time/
full-support/origin cases, timeout/redesign/final-zero and focused C/D regressions.
Source clock admission must pass first; same-clock synthetic fixtures alone
would conceal the known leading-header/state behavior.

## Source routing details for the prospective implementation

The current stationary supervisor generates its own run_id; the detector learns
that identity from AlgorithmState. A B adapter can bind to that same existing
run without pretending to have the rolling stream contract. The stationary
supervisor currently has no Timekeeper subscription, so actual-origin ownership
must be explicit in the new selected adapter. GaussianFillNode already receives
AlgorithmState in robust mode; trace its stored fields and the selected
Timekeeper before accepting a typed request.

`convergence_snapshot_from_confirmation` requires the legacy valid relative
timestamp and eight named PDE values. Keep it unchanged for A, and prevent the
B path from accepting a legacy event as a substitute for its typed diagnostic.
`_candidate_associated_with_active_fill` currently reads data[3:5]; this is the
small center accessor boundary. `_handle_transition` creates the stationary
request and registers its relative timestamp. The existing `_transition_inputs`
consumes a fresh pending confirmation then keeps verification/ranking ownership
in SupervisorStateMachine. An already accepted historical confirmation remains
the candidate reference throughout verification/design and targeted redesign.

The new once-per-epoch typed confirmation itself can arrive ahead of the
supervisor clock. Its selected adapter therefore needs bounded original-receipt
admission, not immediate future-stamp rejection or a restamped retry. Bind the
current SEARCH epoch/entry, selected pose topic/frame, full six-window support,
source/publication/receipt ordering and freshness, score/radius and confirmation
sequence. Reject later replays or delayed old-epoch flags. Reuse existing bounded
admission semantics where appropriate and preserve actual steady receipts.

GaussianFillNode._robust_trigger_cb needs the legacy header/timestamp and
decoded CandidateFillEvidence for its request-specific inputs. It does not read
data[3:5]: robust estimation/design derives its center from synchronized samples.
The centroid center belongs to supervisor association and request provenance,
not a new estimator constraint. The later legacy trigger path owns event-center
extraction; preserve that distinction. Its remaining sample synchronization, receipt-ended freeze, estimator,
designer, association, active registry and events can share a normalized internal
request context. Normalize the legacy array into that context at its existing
entry, and the B typed request at its selected entry; never manufacture eight
PDE values for B. Rebuild the same request diagnostics and retain existing
candidate-informed enable/disable and targeted-redesign checks.

The prospective typed schema should carry the untouched diagnostic, actual
Timekeeper origin, new request publication/sequence, CREATE or targeted REDESIGN,
and explicit CandidateFillEvidence scalar fields/validity. Declare exact schema,
identity/idempotence and request/result correlation tests before implementation;
this note does not yet select or implement those fields. Reuse canonical topic,
launch, recorder and validator owners, including the original relative result
timestamp conversion. Confirmed history age and live request authority have
different roles and must not share a new0.5s historical-data expiry.
