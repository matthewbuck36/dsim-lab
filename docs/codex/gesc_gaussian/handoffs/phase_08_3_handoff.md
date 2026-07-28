# Phase 08.3 Handoff

## Terminal outcome

**FAILED / NOT SIMULATION-READY.**

Phase 08.3 implemented and qualified the fresh v3 robustness workflow, but it
did not reach acceptance. V3A stopped on contact-control contamination. V3B
retained one valid direct-path behavioral failure. V3C failed before Gazebo
because the boundary observer used the wrong ROS executor context. The bounded
V3D correction passed qualification and then ran one real GUI Gazebo
simulation before an unchanged recorder-completeness hard stop ended
activation.

The terminal rule was followed: evidence was preserved, thresholds were not
weakened, no replacement was run, the remaining stages are `NOT RUN`, and no
v4 began automatically.

## Authoritative Git boundary

- Branch: `feature/gesc-gaussian-robustness-v1`.
- Phase 08.3 implementation opened at:
  `da44ec1` (`phase 08.3: open v3 acceptance workflow`).
- Cleartext v3 adoption and precommit:
  `9837b7f` and `d69407b`.
- V3A-to-V3B contact correction:
  `e9e1d50` and `23c2b9b`.
- V3B behavioral failure/routing correction:
  `1e3bd0c` and `7cb7b44`.
- V3C qualification and retained prelaunch failure:
  `6af523f`.
- V3D executor correction:
  `7a0db9533491eaed7eaed29fe4f6a26ee038913a`.
- V3D qualification evidence:
  `a21671e858d504c81761c258cea18e407924c2e2`.
- Terminal closeout follows this handoff/checkpoint commit.

No encryption or GPG key is part of the v3 workflow. The suite, commitment,
Git state, and evidence are protected by cleartext SHA-256 commitments and
retained immutable paths.

## Preserved lineages

```text
V3A: /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3
V3B: /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b
V3C: /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
V3D: /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
```

- V3A is failed instrumentation-contaminated evidence.
- V3B is a valid direct-path behavioral miss and remains the one immutable
  carried record.
- V3C is failed prelaunch infrastructure evidence with zero new Gazebo
  executions.
- V3D is failed recorder-infrastructure evidence with one new GUI Gazebo
  execution.

None may be resumed, overwritten, relabeled, or counted as a future fresh
acceptance run.

## Implemented workflow and compatibility

The existing `validate_robustness`, scenario runner, recorder, analyzer,
supervisor, fill manager, controller, and launch owners were extended. No
parallel controller, recorder, validator, analyzer, simulation fork, physical
fork, topic, message, package, or public hardware interface was added.

V3 retains:

- the 120-slot `10/30/20/50/10` design;
- a researcher-visible cleartext precommitted 70-unique-case population;
- deterministic aggregate-field ground truth;
- fixed activation/development scenario identities and seeds;
- bounded serial dispatch, evidence manifests, and stage-order checks;
- collision, cleanup, recording, final-zero, timestamp, causality,
  applicability, family-floor, Wilson-interval, and reproducibility gates;
- no-replacement treatment of valid behavior and any executed
  non-replacement-eligible slot;
- selectable legacy behavior, cost sign/units, canonical topics, controller
  ownership, and simulation/physical algorithm parity.

The full post-correction functional gate passed `475 passed, 2 skipped`; the
skips were only explicit Gazebo opt-in integration tests. The standard
three-package and isolated three-package builds passed. Installed entrypoint,
resource, launch-argument, supervisor/fill instantiation, dry-run, and
real-ROS no-Gazebo boundary smokes passed before activation.

## V3D GUI Gazebo evidence

V3D qualification passed against commit
`7a0db9533491eaed7eaed29fe4f6a26ee038913a`. Activation then launched
Gazebo server and client on display `:0` with `gazebo_gui:=True`.

Exactly one new case ran:

```text
v3a_below_target_fill
seed 9302
attempt_index 1
```

It reached motion readiness and traversed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> FAILSAFE
```

The SQLite bag is healthy and contains `400131` messages over
`190.097876649 s`, but the recorder returned `2` during the requested boundary
shutdown:

```text
RCLError: Failed to publish: publisher's context is invalid
```

Default rclpy SIGINT handling invalidated the recorder context before
readiness-false and stop-true publication. Final-zero observation, orderly
recorder-owned target/bag shutdown, metadata finalization, and the final
completeness validator did not finish. Therefore `recording_complete=false`
and the case is infrastructure-invalid, not a behavioral result.

Outer cleanup passed and the final process set was empty.

## Activation and stage results

| Stage | Result |
|---|---|
| Prepare/adoption | PASS |
| Qualification | PASS |
| Activation | FAIL at first new V3D execution |
| Development/tuning, 30 runs | NOT RUN |
| Freeze and acceptance-contract seal | NOT RUN |
| Selection-blind holdout, 20 runs | NOT RUN |
| Additional unique validation, 50 runs | NOT RUN |
| Reproducibility, 10 repeats | NOT RUN |
| Simulation readiness | FALSE |

Activation provenance:

```text
carried V3B records: 1
new V3D executions: 1
attempts: 1
replacements: 0
ambiguous attempts: 0
not_run V3D cases: 8
integrity passes: 0
behavior-contract passes: 0
```

Because readiness became true and non-`SEARCH` behavior executed, the V3D slot
cannot be retried or replaced. The eight remaining cases stay `not_run`.

## Durable evidence

Detailed failure diagnosis:

- `docs/codex/gesc_gaussian/validation/phase_08_v3d_failure_report.md`

Workflow terminal artifacts:

- `docs/codex/gesc_gaussian/validation/phase_08_v3_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_failure_report.md`
- `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d/workflow_state/v3_terminal.json`

Key hashes:

```text
V3D activation state internal
  24ea143a452ecf28b5cd8a2c54d91444932de49334862038bbe47f29c898adcb
V3D terminal state internal
  e29c501868ea7f1a03fd678d78ca56f07bbf3eca8d4ea2688d6766c087370d74
new V3D run manifest, 33 files
  cfe30977ac51d11b04c35125a277c8eac0538c018f8ccb2faadc4a73c67ab6cd
new V3D bag
  c2c526bf0f969276a6c6c987517cc2da2d77484e7a20e33e27865f0caba274bd
complete terminal V3D root, 1576 files
  94161e4ec08512d844c43949da4a7ff0883031b4ea536aafad79390c66f261c9
gate results
  3d9835ff504a9a87af4a752a77c30a9a1ac9f47ee143968b2d7912309ee83fce
run manifest
  81a721f5cbb815f85db11c946f0f7099969e09a05e845356a4baf6f9f1d319b3
validation report
  cb88420088dd71899806c496029e2e9c8b4e081fe4233537d36f204382b323e3
generic failure report
  0b7ac933655c27a124b4251b046e69225ade15ec6e20a01b1f79ab04e80ac5cc
```

No Wilson confidence intervals exist because the 70-unique-case denominator
did not run. No selected candidate, frozen profile, acceptance contract, or
readiness tag exists.

## Smallest justified next work

The recorder needs a bounded signal-safe shutdown correction:

1. use `SignalHandlerOptions.NO` and the existing
   `DeferredSignalShutdown`;
2. preserve the ROS context through readiness-false, stop-true, final-zero,
   target stop, and bag stop;
3. boundedly stop the executor and join its spin thread before destroying the
   node/context;
4. retain the primary cleanup error while completing every remaining
   finalization step;
5. add focused lifecycle/race/error tests plus an installed real-ROS,
   no-Gazebo SIGINT smoke.

The current Plan does not authorize an automatic V3E or v4. A separately
authorized diagnostic V3E could preserve both the V3B and V3D failed slots and
execute only the remaining eight once while remaining failed and
acceptance-ineligible. A pass-eligible claim requires a separately planned
fresh v4/full activation after the recorder correction.

## Prohibitions and final state

- Do not rerun V3A, V3B, V3C, or V3D.
- Do not count partial V3D analysis as behavioral acceptance.
- Do not begin development, freeze, holdout, validation, reproducibility, or
  Phase 09 from this evidence.
- Do not create the simulation-ready tag.
- Do not run physical hardware.

No physical hardware ran during Phase 08.3.
