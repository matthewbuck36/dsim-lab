# Q2v2 recorded detector gate extraction

Status: ADOPTED bounded read-only continuation of the completed motion/timing
diagnostic. Read plan.md, status.md and q2_discovery_motion_diagnostic_plan.md.
The motion report found repeated local loops with124.882s uninterrupted
qualified SEARCH history per discovery run, no original pose faults and no
source gap above0.034s. Its JSON lacks continuous detector scores/radii.
The Q2v2 experiment remains closed and no qualification result is changed.

## Exact scope

Read only the two existing discovery recordings26090931/26090932 via the existing
`plotting_scripts.bag_reader.read_run_bag` owner, selecting alias
`centroid_convergence_diagnostics` plus the reader's automatic readiness alias.
The actual topic is `/gesc_gaussian/v2/convergence_diagnostics`, type
`ros_esc_interfaces/msg/CentroidConvergenceDiagnostics`. Source receipt, resolved
topics, metadata and bag integrity hashes must match the closed acquisition.
Never open a confirmation bag, dispatch ROS/Gazebo, replay the detector, alter
parameters/labels, calculate a reference or inspect another topic population.

One60s extraction/report job, exclusive external output
`qualification/q2_primary_shadow_v2/diagnostics/recorded_detector_v1/`.
Freeze the small extraction script, source/type/reader and allowed input hashes
before execution. Use the installed Humble/Q2 interfaces without ROS node
initialization. Recheck input hashes after execution; preserve failures.

## Saved fields and arithmetic

Export all selected typed diagnostic messages with original bag timestamp,
publication/source/receipt stamps, readiness membership, epoch/reset reason,
window bounds, score, displacement components, radius, configured thresholds,
validity, eligibility and confirmation fields. Keep startup/invalid/terminal
rows separately visible; invalid values never become zero evidence.

For the summary retain the first publication for every distinct complete
six-window `(run_id,search_epoch,reset_sequence,history_start,history_end)`
snapshot inside the original readiness interval. Choose the first publication
before checking its validity, so no later favorable replacement is possible.
Report invalid/missing snapshots. For valid snapshots report score/radius
minima/maxima and count score>=epsilon, radius>maximum, both, or neither.
Check the declared live W6/epsilon.30/R.75 configuration and score equality to
the sum of its five recorded displacement components. This checks saved wire
arithmetic only; do not recreate windows or execute detector logic.

Report source/history/readiness support and actual observed confirmations.
Do not infer that a different radius/epsilon/window would have passed, select
a new setting, or promote a confined trajectory into Q2 annular truth. If a
numerical gate consistently rejects supported local looping, that supplies
the cause for one prospective detector-development amendment. If wire/timing
data are invalid, report the specific missing observable or bounded defect.

## Boundary

Save JSON, message/window CSVs and a concise receipt. No new figure is needed.
Do not add a node, recorder, reference model or replacement analysis pipeline;
this is a projection of an existing recorded diagnostic through the canonical
reader. Stop after this extraction and report the identified gate/mechanism.
Runtime source remains held. The full implementation goal and16-run M4 remain
incomplete, and all confirmation scientific outputs stay sealed.
