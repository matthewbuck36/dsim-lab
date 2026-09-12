# M4v11 execution record

CLOSED_INCOMPLETE; selected development evidence only. Sole dispatcher session59849; wrapperPID76969,
started2026-09-11T00:55:28.656467UTC.
[Adopted plan](../m4_v11_draft_plan.md),[source validation](m4_v11_source.md),
[frozen preparation](m4_v11_preparation.md). Keep frozen preparation validation
unchanged because its exact bytes are in the reviewed preparation archive.

Dispatchrelease session88425terminal0, externalrelease_outer_v1.log;
`pilot/m4_pilot_v11/preflight/dispatch_release.json`SHA256
`d6ebc1ceac5f16c23620bbb41d8884665402561f432190d7331a02cd2598c02e`.
Preparationarchive24filesverified0.156347s,manifestSHA256
`768eaa35553e66d56c8e1efba280c1ff8569abce097424624eae221ba17b2031`.

Exact outer invocation from repository root:

```sh
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/acquire_once.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/acquisition_outer_v1.log 2>&1'
```

Held helper executes saved command exactly once:
`timeout --signal=SIGINT --kill-after=120s 15680s /usr/bin/python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/run_m4.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v11/preflight/contract.json`.
Actual executable path/command/process owner are retained in
`development/20260910/m4_v11_source_v1/acquisition_owner_v1.json`.

15800s command maximum;4visibledevelopment before12 gatedconfirmation.
No replacements,tuning,duplicateinvocation,physical/Pi/snapshot/V1orcommit/push.
Preserve each actual failed/incomplete/unstarted slot andallunavailablemetrics.
GOAL_HOLDoptional;0.5marrivalcriterion remains evaluator-only.

Initial slot1/A active:run `m4-pilot-v11-slot01-A-26091021`,dated2026-09-11.
Gazebo GUI/server present; existing idempotent controller load/configure/activate
completed. Recorder readiness true at2026-09-11T00:56:42.079690Z. No terminal
slot result yet; initial completeness file is provisional during acquisition.

Slot1/A COMPLETE,behaviorPASS,412.728963s inclusive. Recording/outercleanup
PASS; full SEARCH->VERIFY->DESIGN->REPULSE->ASSIST->SEARCH path. Actual live
arrival298.959s atdistance0.499471724163m,noninterpolatedposition
(3.5553045214446324,3.0035995435676006),bag1789088500392818232ns.
Localrecovery/cardinality pass; optionalcontroller_goal diagnostic failed,
with successful arrival-only classification. Finalposition
(3.5602053586393176,3.0080023997023564). Independent readonlyslot receipt audit
pending; detectorcandidate publictime233.4s,independentlatencylabels pending.
Dispatcher59849 remainsactive; no source/helper change or secondinvocation.

Slot1readonlyauditPASS;fourinputhashesstable,all12predicates/recording/finalzero/
inneroutercleanupPASS;finaldistance0.495667554m. External
`slot_1_readonly_summary.json`SHA256
`4474c2d1806a832bddb0f964dfa134a11a05904f0d032fac9bde3bd80a5cc6fd`.
ESCAPE_STALLED preceded successfulassist; no completenesswarnings.

Slot2/B COMPLETEbehaviorPASS274.685528s;all12predicates,recording/outercleanup
PASS. Full SEARCH->VERIFY->DESIGN->REPULSE->ASSIST->SEARCH. Exactarrival167.367s
at0.498013615523m,position(3.5942581618348193,3.010987770936358),finalposition
(3.6097958143972906,3.0320972988030594),distance0.480612170722m.
Recurrent typedpublication96.1s,currentinput96.001s,confirmedhistoryend96.0s.
These are event coordinates, not independently labeled detectorlatency.
A/Bobservedarrivaltimes298.959/167.367s are selecteddevelopment outcomes;
first-opportunity pairlabels and scientificacceptance remainpending.
Dispatcher59849active;slot3/Cstarting,sourceandhelpersheld.

Recovery context validator PASS2026-09-11UTC; branch/HEAD unchanged and task-owned
working changes preserved. Slot2 independent readonly audit PASS, four stable
inputs, all12predicates/finalzero/cleanup; `slot_2_readonly_summary.json`SHA256
`6302b3c1e41ddd9ab951f9479e980acb8213c7afc04fcef19b1cfc2df20cecdc`.

Slot3/C COMPLETE348.778406s, integrity/recording/allcleanup PASS. Arrival SUCCESS
at226.755s, distance0.498397145018m, exactposition
(3.5434489861424674,3.003500352703781),bag1789089122033311266ns;
finaldistance0.491464225564m. Frozen behavior FAIL11/12 solely
`required_state_path`: observed SEARCH->VERIFY->SEARCH->VERIFY->DESIGN->REPULSE->
ASSIST->SEARCH. Local recovery, cardinality, ownership, safety, event sequence
and arrival all PASS; optional GOAL_HOLD absent. Do not recast this as arrival
failure or rewrite frozen classification. Independent receipt review pending.
Dispatcher59849 continues slot4/D; first4run scientific stage remains pending.

Slot4/D COMPLETE289.638050s,behaviorPASSall12predicates;recordingandallcleanup
PASS. Arrival179.946s at0.498044172140m,exactposition
(3.576618961176837,3.0078846352825352),finaldistance0.495698162092m.
Full SEARCH->VERIFY->DESIGN->REPULSE->ASSIST->SEARCH. Allfourdevelopment
arrivals succeeded; C retains the separate pathpredicatefailure.
Automatic block0science is ACTIVE under dispatcher59849. PreliminaryA/B
metrics have firstbasinresidences0.578/0.850s,independentlyeligibleFalse,
rightcensored/latencyunavailable; no pairlatency or30%claim follows from
arrivaltime differences. Frozen feasibility decision awaits completedscience.

Terminal closure2026-09-11UTC: session59849reapedexit1,1478.291230s wrapper,
1474.156589s acquisition. Completion receipt error=null means all806source/helper
pins passed the wrapper's final recheck. Block0fourjobs completeexit0, all strict
cleanup/integrity PASS,139.769499s. Frozen gate stops at C motion attribution
incomplete; final summary also retains0/2observablelatencypairs. All12confirmation
UNSTARTED; no replacements. Finalreport saved4.508961s. No application runtime
matched in post-terminal readonly/proc inspection. [Closure](../m4_pilot_v11_handoff.md)
records actual outcomes, directiondenominators and exact hashes.
C/D readonly summaries PASSstablefourinputs; SHA256respectively
`636a79485324a3fb2b007439afb951aabcd25f16040d6ceed142ed07feae42c0`,
`d9d679645d2075c5d77930a9a17bbbf49ee5ddabec658e053cc63acaaad04bd9`.
No rawbag reread or independent scientific rerun by these audits.

Material closure checkpoint and source archive PASS:583 verified members,
0.997531s, `checkpoints/m4_v11_closed_v1/manifest.json`SHA256
`468bb21a08f13ae89014b372117833a987804c7152accc1616a0f7b84f89235f`.
Independent closure audit PASS with34 stable immutable receipt/report inputs:
`m4_v11_source_v1/closure_audit_v1.json`SHA256
`6f996c464a0998c23c70aad8cb2d8e5c31c5eb6395b4f11e4af7a2b348cb5f6b`.
These live receipts postdate the immutable archive. The separately adopted
[measurement diagnosis plan](../m4_v11_measurement_diagnosis_plan.md) permits
bounded cached/filtered diagnoses; original comparison outputs remain held.
