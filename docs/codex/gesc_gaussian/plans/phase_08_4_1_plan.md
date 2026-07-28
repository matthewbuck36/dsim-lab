# Phase 08.4.1 Plan — bounded activation-runner correction and fresh restart

Status: **APPROVED FOR IMPLEMENTATION AND EXECUTION**

Authority: the user directed Codex on 2026-07-28 to plan and execute V4 and
to make any bounded simulation correction needed to reach the 120-run test.
This amendment remains inside that authority. It does not authorize physical
hardware, Phase 09, a readiness tag, weakened acceptance gates, or deletion
of failed evidence.

Parent Plan:
`docs/codex/gesc_gaussian/plans/phase_08_4_plan.md`.

## Why this amendment exists

The original V4 activation root passed qualification and dispatched two real
visible-Gazebo cases. Case 1 passed. Case 2 reached its declared fill and
escape branch with clean Gazebo cleanup, but the outer boundary runner sent
SIGTERM while the recorder was still performing offline completeness
validation. The runner used the same `30 s` allowance for both child-process
shutdown and complete recorder finalization; the observed 240-second bag
needed about `39 s` for validation after roughly `7 s` of shutdown.

The same retained bag exposed a separate named-scope evaluation defect:
`CONVERGENCE_CONFIRMED` causally precedes the
`SEARCH -> VERIFY_EXTREMUM` state transition, while the offline
`activation_window` began event collection at the later state timestamp and
applied the untrimmed state path beginning in `SEARCH`.

These are Level B runner/evidence-contract defects. They do not change the
controller, supervisor, Gaussian-fill algorithm, cost sign or units,
canonical topics, physical/simulation parity, formal population, or any
acceptance threshold.

## Immutable failed evidence

The following root is retained and never resumed, relabeled, repaired in
place, or counted:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
```

Its activation result is `FAILED / INFRASTRUCTURE STOP`: one passing case,
one recorder-finalization failure, and eight not-run cases. Neither attempt
enters a development, holdout, validation, reproducibility, or 120-run
numerator or denominator. They are not replacement attempts in the corrected
activation gate.

## Bounded corrections

Extend only the existing `run_scenario.py` owner:

1. Preserve the declared `shutdown_grace_sec=30.0` child-cleanup allowance.
2. For an observed graceful branch boundary only, add a separate bounded
   `120.0 s` recorder-finalization allowance before outer escalation.
3. Do not add that allowance to a wall-timeout or exception path.
4. Once the recorder leader exits, immediately escalate any retained
   nested-session survivors rather than waiting through the finalization
   allowance.
5. Let the live boundary observer retain the causal event immediately before
   the named state anchor.
6. Let offline scope evaluation include events from the state transition
   leading into the anchor and clip state requirements to the named anchor.
7. Add focused tests for the timeout hierarchy, causal pre-anchor event,
   state-path clipping, and nested-session cleanup.

No duplicate runner, recorder, validator, launch graph, controller, or
simulation fork is allowed.

## Fresh corrected activation identity

Create `phase08_v4r2_activation.yaml` before any corrected Gazebo execution:

- retain all ten V4 activation geometries, responsibilities, and contracts;
- use suite identity `phase08_v4r2_activation`;
- use case prefix `v4r2a_`;
- use new deterministic seeds `10601..10610`;
- retain visible Gazebo, serial execution, `240 s` run windows, and all
  integrity/behavior predicates;
- retain the original V4 activation YAML and failed evidence unchanged.

This is a complete fresh development gate, not a per-slot replacement.
Changing only identity and seed prevents the observed V4 attempts from being
redispatched while avoiding behavior-driven geometry selection.

## Fresh root and gates

The corrected pass-eligible root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2
```

Before creation:

- commit the correction, amendment, fresh activation input, tests, status,
  and checkpoint;
- require clean Git and no active ROS/Gazebo processes;
- re-run strict Phase 08 implementation context validation;
- re-prove the adopted formal 70+10 population has zero prior execution;
- pass the complete functional suite, isolated build, installed resource and
  launch checks, dry runs, and a process-level boundary-finalization smoke.

Execution remains:

1. 10 fresh visible-Gazebo corrected activation cases;
2. 30 headless development cases over the three V4 candidates;
3. freeze and seal exactly one eligible winner;
4. 20 headless holdout cases;
5. 50 headless validation cases;
6. 10 headless preselected reproducibility repeats.

Thus the formal test remains exactly 120 Gazebo runs:
`30 + 20 + 50 + 10 + 10 activation = 120` under the parent Plan's counting
convention. The activation runs are development evidence and do not enter the
70-case formal denominator.

## Unchanged scientific gates

Every numerical, family, lifecycle, escape, orbit, revisit, collision,
recording, completeness, cleanup, reproducibility, hash, and zero-tolerance
gate in the parent V4 Plan remains binding. The exact formal suite bytes stay:

```text
d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e
```

No GPG, encryption key, or encrypted artifact is required.

## Stop conditions

- A valid corrected activation behavior miss closes V4.1 before development.
- A hard integrity, collision, cleanup, hash, ownership, or orphan-process
  failure stops immediately.
- Only the parent Plan's predeclared infrastructure-invalid replacement
  policy applies inside the fresh corrected root.
- A corrected-root failure is retained honestly; do not modify the formal
  suite, weaken a gate, or silently create V5.

