# Q1 recovery1 acquisition — CLOSED INCOMPLETE

First case: `q1-primary-shadow-v1-recovery1-discovery-residence-26090911`.
The corrected console environment started the recorder and visible Gazebo.
Recording became operational, observed exactly125 simulated seconds after the
ready clock2.6s, and finished at127.6s. Final commands were zero; target and bag
exited0; shutdown/cleanup passed with no remaining new nodes or session processes.

The attempt nevertheless FAILS both recording completeness and the forbidden
event gate. Its state sequence is SEARCH -> FAILSAFE; the sole completeness
failure is a simulated publication coverage gap in centroid diagnostics.
The synchronized-source and typed lifecycle structural checks pass. Therefore
do not describe the whole recorded source stream as structurally invalid just
because it contains explicit rejected-input notices. First-safety-event diagnosis
must distinguish the cause of FAILSAFE from subsequent diagnostic gating.

The existing serial runner stopped after the first case, elapsed163.521097122s,
exit1 without timeout. Three later cases were not dispatched; zero Q1 inputs
qualified. No detector/neighborhood nomination or direction reference was
evaluated. Confirmation results remain unopened. The125s exposure is real but
does not establish scientific acceptance or permission to replace this outcome.

## Retained evidence

External V2 root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Acquisition root: `qualification/q1_primary_shadow_v1_recovery1/`.
Run directory below it:
`runs/2026-09-09/q1-primary-shadow-v1-recovery1-discovery-residence-26090911/`.

The immutable closure `acquisition_closed.json` hashes14 retained files,
including the76,824,576-byte bag, metadata, resolved topics/parameters/scenario,
completeness, scenario result, console and acquisition results. Closure SHA256:
`537932976096cc01a43b911b3103ceb0a4d4ce4d82fff6563a1b7acf0ab74fe6`.
Contract SHA256 `f4fca24e4e39f791396be76674d56eaa6c4ced4b6ba472ca0a7975da3b547b17`;
release SHA256 `516e4ad551b17491e268fb27abc8b5f650a478d72029cb04d9d8d05a0d86c72f`.
Source checkpoint `checkpoints/q1_preacquisition_recovery1/manifest.json`, SHA256
`85af0eca9eb2bc6d4c1a6f587a9d8b6a58e8f462cba771746c123fb06f17c963`.

Exact invocation, after sourcing base Humble and the isolated local overlay:

```bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout --signal=INT --kill-after=60s 1140s python3 docs/codex/gesc_gaussian/v2/tools/acquire_q1.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery1/preflight/contract.json > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery1/acquisition_console.log 2>&1
```

## Confirmed source-ordering issue

A bounded8s live `ros2 topic info /joint_states -v` recorded two publishers:
`/turtlebot3_joint_state` and `/joint_state_broadcaster`. The exact output is
`joint_states_graph.txt` in the acquisition root. Source confirms the Gazebo
joint-state plugin publishes the rotating joint at nominal30Hz while the active
controller-manager broadcaster reports the same joint at100Hz.

Read-only closed-bag inspection found16,486 joint messages. The two payload
shapes contain3,750 and12,736 samples with34ms and10ms source spacings respectively;
each shape has zero internal timestamp regressions. Attribution of those shapes
to the two named publishers follows the source/graph and payload conventions;
the bag does not retain DDS publisher GIDs.

The merged receipt stream has six timestamp regressions, matched by six encoder
regressions and six invalid-source notices. First pair: joint row20218 has source
9.011s; row20227 arrives afterward with source9.008s. Encoder row20323 forwards
the regressed key; provenance row20458 rejects model stamp9008000000ns,
sequence1066, with no prior valid raw publication for that key. No same-stamp
phase conflict or within-owner clock rollback was found. Unused broadcaster
effort NaN is not the trigger.

This demonstrates a merged-source ordering defect. It does not by itself identify
the first FAILSAFE cause; that diagnosis is still required. Preserve all recorded
failures and all strict source/safety rules before any new source correction.

## First FAILSAFE and diagnostic coverage diagnosis

The first controller FAILSAFE is earlier than the first joint-source regression.
At bag receipt1788948888654928817 its AlgorithmEvent is stamped2.7s and reports
`controller watchdog: V2 pose source missing, stale or future`. Its source stamp
is explicitly unavailable. The preceding recorded clock2.7s arrives at
1788948888624989400; odometry with header2.721s at1788948888652250784; the next
clock2.8s at1788948888728797846. Bag receipt order is not proof of internal callback
order, but the controller event's own clock and exact code branch support the
held-clock admission defect: `state_callback` immediately stores the incoming
pose stamp while `_robust_fault_reason` requires nonnegative source age.

Supervisor transition at2.8s, bag1788948888731197820, reports
`SEARCH->FAILSAFE: controller reported failsafe`; first FAILSAFE state is bag
1788948888731579265. No later SEARCH recovery occurs. Readiness began at bag
1788948888617727844 with ready clock2.6s.

Centroid diagnostic stamps are0,0.1,2.8,11.5,127.6s. In the ready interval the
two pre-shutdown messages report `outside_search` and
`stale_or_future_algorithm_state`, with invalid source/history. The116.1s gap
exceeds the unchanged1s coverage bound. The detector binding correctly rejects
FAILSAFE poses and its watchdog returns outside SEARCH. This is downstream of
the controller fault; do not infer poor settling detection or weaken the gap gate.
`../q1_simulation_source_plan.md` declares the bounded source corrections.
