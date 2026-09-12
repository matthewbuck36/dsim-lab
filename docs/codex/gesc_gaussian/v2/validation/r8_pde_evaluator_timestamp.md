# R8 private moving-PDE evaluator validation

Status: SOURCE_VALIDATED; C03_CACHED_COMPONENT_REASSESSMENT_PASS.
Authority: [R8 plan](../r8_pde_evaluator_timestamp_plan.md). Simulation only.

## Source scope and review

Only existing `run_scenario.py` adds a selected private moving-PDE timestamp
bridge, live monitor collection/latch and final reader/error integration.
Exactly V10/current development moving-PDE cases select it; older/stationary
and existing centroid/recurrent paths are preserved. Canonical public event,
legacy payload and detector decision clock stay unchanged. Exact eight-value
mirror/typed binding validates run, stream, frame, immutable origin, schema,
epoch/sequence and support/publication bounds; ambiguous/missing joins fail.
Main actual C03 fixtures exercise baseline rejection, corrected StageA, live
cross-topic pending and actual final CDR reader. Independent adversarial tests
exercise identity, bounds, ambiguity, malformed values and legacy pass-through.
Root exact-diff/main review and independent source review PASS. Root cached
helper review corrections before execution bind preparation to native/attempt
receipts and fail closed on late input/source mismatch.

External owner:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r8_pde_evaluator_v1/`.
Before source, actual C03 join, exact patch and review hashes are retained there.

## Exact commands and outcomes

Both commands use this prefix, from repository root:

```sh
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; <COMMAND>'
```

Source COMMAND:

```sh
timeout --signal=INT --kill-after=5s 135s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r8_pde_evaluator_v1/validate_source.py --version focused_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r8_pde_evaluator_v1/tests_v1.json > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r8_pde_evaluator_v1/focused_outer_v1.log 2>&1
```

Session8141 terminal/reaped0:147 unique checks PASS,16.709488452s inclusive
(pytest14.52s),770 source/helper/input pins stable,21 installed entries stable.
Internal120s pytest; outer135s SIGINT+5s kill,140s maximum. Six exact modules
are in `tests_v1.json`; no broad suite rerun. Receipt
`focused_v1/source_validation.json` SHA256
`a3bef7666b99b325e8f3ceb3f5ca095104193eafdec84fe4c9a8f45c777d2309`.

Cached COMMAND:

```sh
timeout --signal=INT --kill-after=5s 35s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r8_pde_evaluator_v1/reassess_c03.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r8_pde_evaluator_v1/cached_c03_outer.log 2>&1
```

Session39012 terminal/reaped0:REASSESSMENT_RETAINED,component_pass=True,
source_inputs_stable=True,1.751833033s. Internal30s/outer40s maximum.
Receipt `cached_c03_v1/receipt.json` SHA256
`ccf40d117f20a631d54159224d9ea6f564c2fe9fc378f863ce34bd60f26c3305`;
result `cached_c03_v1/result.json` SHA256
`e3f5bd8f4a1a7376f6acbe966a6115500b630ac4b92fa8125450e39ad0bddbe1`.

## Retained actual measurements and evidence boundary

Public85.0s binds uniquely to typed support84.927s; no changed public payload.
Original StageA/cardinality/arrival=False; corrected all=True through the same
existing evaluator owners. Readiness-filtered cached evidence:3253 states,
13 events,1 fill,1 typed confirmation,237 legacy records,1805 Timekeeper
heartbeats and4781 odometry samples. No raw bag scan, native analysis or
reference solve; exact message_payload roundtrip and seven native artifact
hashes verified, alongside inherited preparation/acquisition/analysis receipts.

First actual noninterpolated arrival:ROS152.519s,CSVline4484,readiness sample3965,
bag1789084783064317222ns,position(3.5418254989964746,3.002261019816568),
distance0.49949320792213703m to global(3.5,3.5),within existing0.5m radius.
Closest:0.21830030887061383m at159.965s,CSVline4703.
Final:0.25642404278213304m at180.229s,CSVline5299.

Original frozen C03 classification remains FAIL8/12. Original live arrival stop
was False and StageA timeout True. Missing cached supervisor-command/contact
streams prevent a full `_bag_outcomes` rerun; original passing safety/ownership,
recording, cleanup and native proofs are inherited explicitly. This is a separate
cached component reassessment of exposed development data. Selected C03 direction
and continuous-acquisition evidence are in [C03 handoff](../r7_visible_c03_handoff.md).
No claim of untouched confirmation, broad qualification or paired30% target.

Context validator and `git diff --check` PASS. Material checkpoint/source archive
follows this evidence record; no source/test/helper edits during either job.
