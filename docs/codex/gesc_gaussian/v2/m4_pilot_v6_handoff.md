# M4 v6 incomplete acquisition handoff

M4v6 is CLOSED_INCOMPLETE,2026-09-10 UTC. Full V2 remains IN_PROGRESS.
Read [the result/postmortem](validation/m4_pilot_v6_result.md), latest status
and any later prospective amendment before acting. Both research goals remain
open: faster settling/trapping detection and better GESC direction while moving
without mandatory stopped acquisition.

The one dispatcher, session87498, is terminal1 after818.281188141 s. Baseline
slot1 is INCOMPLETE because the outer work deadline interrupted the inner
runner while it awaited recorder cancellation. Fifteen slots remain UNSTARTED;
no block science or holdout release occurred. Never restart this version.

Recorder completeness48/48, final zero, clean target/bag exits and outer kernel
ownership/performed cleanup passed. The missing inner scenario result and
cleanup classification prevent a complete acquisition/behavior claim. The
source-supported collision is between synchronous recorder finalization
(~115.12 seconds from clean wall_end to completeness publication) and the
enclosing work deadline. The validator's expensive operation remains unmeasured;
see the result for exact source/timestamp boundaries. Preserve this uncertainty.

All16 outcome rows and192 scheduled direction rows remain in the existing
report with unavailable research metrics:0/12 latency endpoints,0/6 pairs and
0/144 eligible holdout targets. All631 source hashes match the frozen contract.
Do not infer behavioral acceptance from source tests, recorder counts or the
logged baseline detector event. No post-close bag replay/evaluation was run.

External root: /home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v6/.
Acquisition SHA25677af3981d1207fb9a6b8ada892ac5b66f50e3767f62a1a0e43f59380411086be;
contract815b2e3c0c832f296320471af118e59ba8d189b555d978d45de342b13664b4e0.
Material closure archive is next. Future correction requires a separate saved
scope/version and validation; all old evidence, limits and gates remain intact.

Git remains the V2 branch at3369cfc with saved uncommitted task changes.
No commit/push, physical/Pi or V1 work occurred.
