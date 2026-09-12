# R3 support-coordinate correction and explicit arrival acceptance

PROSPECTIVE 2026-09-10, before implementation. Authority is the user's
[global-arrival amendment](global_arrival_acceptance_20260910.md). Attempt02,
its source snapshot, original scenario and failed historical verdict remain
unchanged. This is a bounded correction of existing evaluator/scenario owners;
no algorithm, numerical threshold, message, launch graph or physical change.

## Recorded trigger

Attempt02 confirmed one recurrent support ending at 78.0 simulated seconds.
Its latest actual input pose was stamped 78.008. The typed candidate/fill binds
78.0, but `_centroid_convergence_evaluation_events` privately assigns the input
pose stamp to the public convergence event's evaluator copy. The inherited
`_staged_recovery_evidence` therefore rejects the fill as preceding confirmation.
The actual lifecycle independently validates: acceptance78.1, admission84.7,
snapshot92.3, commit92.7, assisted escape and resumed SEARCH112.8. The user now
accepts recorded post-recovery global arrival within the existing 0.5 m radius,
without a second verification, ranked GOAL_REACHED event or GOAL_HOLD.

## Exact selected scope

1. In `scenario_runner/run_scenario.py`, retain the diagnostic's actual input
   source stamp, history endpoint and publication stamp in the private binding
   audit. For `recurrent_geometry_v3` only, use `history_end` minus the immutable
   observed Timekeeper origin as the convergence/fill support coordinate.
   Preserve all identity, geometry, run/epoch, freshness and origin checks and
   leave old centroid/pde timestamp semantics and public messages untouched.
2. In `scenario_runner/scenario_schema.py`, add optional
   `success.criterion: post_recovery_arrival_v1`. Permit it only for the explicit
   `v2_method_development_v1` simulation suite, schema14+, development partition,
   robust counted two-source open-field case with the existing staged contract.
   Its recorded success still requires recording/cleanup, full local recovery,
   one unique committed fill, command ownership, required local states/events,
   forbidden-state/event checks and post-recovery recorded global proximity.
   Require the existing 0.5 m evaluator boundary, matching ground-truth settings.
   Bind the existing direct/assisted recovery paths ending in SEARCH, without
   a second VERIFY or GOAL_HOLD; no mandatory terminal-state predicate or
   GOAL_REACHED event. Unknown selectors and incompatible contracts fail closed.
   Omission retains all existing validation and normalized output shape.
3. Reuse `_run_record_to_global_proximity` and existing outcome predicates.
   Derive the ranked-goal prerequisite from the explicit criterion in both live
   and offline paths, rather than implicitly requiring it for every counted
   family. Continue observing/reporting any actual ranked goal independently;
   it cannot veto selected spatial arrival. Preserve live stage completion,
   current full-history validity, cardinality and before/after timing gates.
   Stop only at an actual post-recovery pose sample inside the declared radius;
   no interpolation, extra monitor or goal coordinates in the algorithm.

## Finite verification and release

Use generated messages in the current isolated schema2 interface overlay.
Extend focused tests beside the existing centroid-evaluator, monitor and
scenario fixtures: distinct input/support stamps and nonzero origin; actual
private join through staged recovery; unchanged legacy centroid mapping and
message payloads; selected schema/expansion/metadata roundtrip; rejection of
unknown/nondevelopment/physical/radius/path/predicate mismatches; live and
offline post-recovery arrival without ranked event; refusal before recovery or
with invalid current evidence/cardinality; omitted selector still requires
ranked goal and old complete paths. Exercise actual existing evaluation owners
using finite callback/bag-reader fixtures, with no ROS graph or Gazebo.

Retain source pins, exact commands, logs and result under exclusive external
`development/20260910/arrival_evaluator_correction_v1/`; each focused job <=90 s,
total test allowance180 s. Preserve any failed fixture version before repair.
Save validation in `validation/r3_arrival_evaluator_correction.md`. Parent owns
status/handoff, checkpoint and any separately frozen future scenario. No bag
reads, old-result rewrites or simulation dispatch are authorized by this plan.

D3's cached profiling hold has released. Coordinate a new source hold with D3
only after this correction's finite tests finish; his next retained-C timing
job must bind a stable runner.
