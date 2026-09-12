# R3 recurrent moving startup selector correction

ADOPTED, 2026-09-10, simulation-only bounded source correction. Visible attempt
01 remains INCOMPLETE: both GaussianFill and SupervisorNode rejected
`recurrent_geometry_v3` in the common `stationary_centroid_selected` helper,
before reaching their moving adapters. No recording readiness or motion occurred;
retained case cleanup and source integrity passed. Do not retry attempt 01.

Extend that existing helper with one explicit recurrent branch. It accepts only
`rolling_gesc_v2`, `robust_gaussian_v1`, and actual boolean simulation time True,
then returns False because the stationary centroid adapter is not selected.
Reject recurrent+stationary, physical time, nonrobust profile and unknown mode.
Keep old centroid/PDE defaults and all existing wire layouts unchanged; do not
put recurrent mode in the centroid tuple or stationary request envelope.

Retain exact selected node ROS parameter arguments from the failed attempt's
console process-exit command receipts as a compact fixture with source hash.
Instantiate the actual GaussianFill and SupervisorNode classes independently
using these recorded arguments in an isolated ROS domain, without spinning,
publishing readiness, launching Gazebo or invoking any command consumer. Require
both moving adapters active and stationary adapters absent. Include physical,
stationary and legacy rejection cases plus the existing stationary selector/
protocol regressions. Inspect the remaining selected consumers for equivalent
allowlist omissions; change no numerical method or unrelated owner.

Save exact commands, source/fixture pins, logs and outcomes under
`development/20260910/recurrent_startup_correction_v1/`. One focused/protocol
invocation has a 90-second timeout, preserving any failure before a separately
identified correction. Existing generated schema-2 overlay is sufficient; no
interface rebuild. Parent owns attempt-01 closure, checkpoint/status/handoff and
the prospectively fresh attempt-02 release. No new simulation dispatch by this
source owner.
