# R2 selectable centered verification runtime

ADOPTED, 2026-09-10, simulation-only development. Authority is
[the revised method/development amendment](method_development_20260910.md).
The first centered-motion prototype failed 3/12 required cases; its separately
declared two-stage successor passed all 12 required starts under ideal kinematics
and an optimistic signal. Neither establishes real field repeatability or ranking.
This milestone implements that measured collection hypothesis before a separately
bounded visible simulation. No new comparison or hardware operation is released.

## Selected method and immutable timing

Add `v2_verification_motion_mode`: default `rolling_neighborhood_v1` preserves
the existing moving GESC behavior and 12-second acceptance deadline; opt-in
`centered_tracking_v1` changes candidate evidence-collection motion only.
The new mode requires rolling GESC, simulation time and the actual selected
Directional_Controller configuration (.5/5 gains, .1 m/s/.5 rad/s ceilings).

At confirmation admission freeze candidate identity, selected frame, SEARCH
epoch, original center and accepted ROS time. Approach must first reach <=.08 m
from that center using a fresh admitted algorithm pose no later than accepted
time+8 s. Freeze that first observed admission time; it never changes after
departure/re-entry. Evidence deadline is min(admission+12 s, accepted+20 s).
Missing approach/evidence cancels to SEARCH. Safety, readiness, origin/epoch,
frame/pose validity and .75 m candidate departure still cancel immediately.

The additional 12 seconds is observation allowance after spatial admission.
Retain the existing raw owner's latest-three eligible complete cycles, including
valid pretrigger/approach cycles. Do not reset filter/raw history at admission or
invent a new requirement that every cycle start after admission: that was not
the passing prototype. All existing sector/centroid comparison, amplitude/MAD,
negative-cost, minimum count, ranking and fill guards remain authoritative.

Track `z=c+.03*[cos(.3*t),sin(.3*t)]` and
`q_world=z-p+z_dot/.5`, with t from immutable candidate acceptance. Rotate q into
the admitted pose's body frame and evaluate the existing Directional_Controller
class with the exact selected controller JSON. Its output is a supervisor motion
proposal. There is no stopped-sensor state, new source gradient or cost-model use.
Natural velocity zero crossings and safety stops remain possible.

## Ownership, state boundaries and safety

Extend the current MovingSupervisor/normal supervisor publication owner.
Publish a new opt-in `VerificationGuidance` message on
`/gesc_gaussian/v2/verification_guidance`, with run/contract/frame, candidate and
epoch, exact AlgorithmState publication stamp, original pose stamp, accepted/
first-admission/expiry times, phase validity, fixed center and proposed velocities.
Existing AlgorithmState and CandidateSnapshot serialized fields remain unchanged
so old bags retain their generated-message decoder compatibility.

The existing controller consumes only a fresh exact-state guidance companion in
selected VERIFY and initial DESIGN entered from VERIFY. It remains the sole
cmd_vel publisher and final speed limiter; GESC continues to compute normally.
Ignore centered guidance in SEARCH, escape/redesign, RECENTER and GOAL_HOLD.
Missing, conflicting, stale, invalid, expired or wrong-state guidance cannot
authorize centered motion. Binding the proposal to the exact state publication
avoids leaking a prior-state unstamped Twist across asynchronous transitions.

Before publishing valid guidance, use the existing `command_sweep_is_safe` with
active fill avoidances and operating bounds for the existing command persistence
horizon. For reverse motion use equivalent yaw+pi and abs(v), preserving that
helper's nonnegative-speed contract. If unsafe, cancel the selected candidate
and publish invalid/zero guidance; no new unsafe fallback. Freshness checks run
at proposal and final controller publication. Initial fill preparation remains
bounded by its existing design timeout; verification itself never gains more
than 20 seconds. Escape redesign keeps its existing purpose and deadlines.

## Record actual admission and preserve historical validation

Add constant `AlgorithmEvent.EVENT_VERIFICATION_STAGE=12`; constants do not
change the existing serialized event fields. Publish exactly one event with
detail `moving verification collection admitted`, actual immutable admission
stamp, VERIFY state and values named `candidate_id`, `search_epoch`. Build the
event with that stored Time directly; the generic publish helper currently
restamps with callback-now and cannot establish the frozen admission itself.

Selected lifecycle validation joins that event to the candidate snapshot and
requires accepted<=admission<=accepted+8 s, snapshot<=admission+12 s and
snapshot<=accepted+20 s. Conflicting repeated admissions fail. The default
accepted+12 s rule remains unchanged. Explicit selected launch metadata flows
to recorder/validator/analyzer; never infer new semantics from an extended
snapshot duration in a historical run. The D3 agent owns lifecycle checks and
caller plumbing; this owner owns runtime, guidance interface and launch route.

The hardcoded MovingSupervisor deadline, moving state-machine timeout and
supervisor constructor's forced 12 seconds must all use the explicit selected
method. The state-machine total cap is 20 seconds only for centered mode;
the adapter enforces the earlier approach/collection deadlines. Old mode tests
must still exercise its exact 12-second behavior.

## Finite source validation and next boundary

Extend current owners, launch forwarding and manifest applicability. No duplicate
node/controller/recorder/analyzer or change to frozen old experiment definitions.
New guidance topic is required only for selected centered mode, with identity
and freshness/state companion checks. Record the new selector in resolved
scenario metadata and validate incompatible startup combinations explicitly.

Build changed message/package sources in a new isolated overlay under
`development/20260910/centered_runtime_v1/`, with a 240-second ceiling and saved
logs. Focused tests (<=180 s) cover immutable first admission; approach/collection/
absolute deadlines; center departure, stale/revoked inputs and cancellation;
exact prototype command parity including reverse sweep; guidance state/identity/
freshness conflicts and all stop states; source expiry; snapshot event joins;
legacy 12-second/default command behavior; and selected launch/metadata wiring.
Record exact commands, outcomes, output paths and source hashes. Relevant focused
regressions use one <=240-second ceiling; no repeated unrelated source campaign.
Finish context/diff review and a material source checkpoint before any separate
visible integration plan. Real raw-profile repeatability and successful fill/
escape/continued seeking remain empirical acceptance gates.
