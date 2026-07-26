# Phase 08 v1 Failure Closeout

Verified: `2026-07-25T16:58:42-07:00`

Disposition: **CLOSED / FAILED / HISTORICAL EVIDENCE ONLY**

Phase 08 v1 did not establish simulation readiness. Its training, holdout,
partial full-pass, frozen profile, workflow state, and diagnostic attempts are
retained as immutable historical evidence. They must not be resumed,
overwritten, relabeled, or counted toward the staged Phase 08 v2 activation,
tuning, holdout, validation, or reproducibility gates.

## Immutable evidence boundary

Historical v1 evidence root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08
```

The separate v2 root was absent at closeout:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
```

The historical root occupied approximately `50 GiB`; the containing filesystem
had `329 GiB` available at closeout. No v1 file or bag was modified by this
inventory.

The retained v1 repository freeze is:

```text
commit: 386221efd581a445f9d0f29edd7da12628a693b2
tree:   6f3dbaebb6d96c4804f8703367120378173769e2
profile: robust_gaussian_v1_phase08_frozen
candidate: C8
frozen parameter sha256:
  b1531988de3eb650fbced657555532baf1eb66056c0203dd21908c4def8f093e
```

That profile and candidate selection are v1-only. In particular, v2 must not
reuse the exposed v1 holdout, accept the historical C8 tie-break as a v2
selection result, or refer to v1 full-pass directories from a v2 manifest.

## Executed v1 evidence

### Training

- `81/81` declared training runs executed.
- Candidates C0-C5, C7, and C8 were infrastructure-eligible.
- C6 was ineligible because one required Gazebo parameter snapshot exhausted
  its bounded attempts.
- Every candidate had `0%` end-to-end success.
- Every candidate had zero observed escape attempts.
- C8 was selected only by the declared final tie-break, lowest median path
  length (`13.228608734409306 m`), not by a behavioral pass.

### Exposed holdout

- `12/12` v1 holdout runs recorded and analyzed.
- Controller goal success: `0/12`.
- Simulation ground-truth success: `5/12`.
- Failsafe observed: `2/12`.
- Collision observed: `0/12`.
- Timeout observed: `0/12`.

This is a Level C behavioral failure. The exposed holdout is not eligible for
v2 selection or acceptance.

### Partial full pass

- Declared pass-1 size: `519`.
- Retained pass-1 run directories: `203`.
- Recording completeness passed: `200`.
- Recording completeness failed: `3`.
- `pass_1.json` is absent because pass 1 did not complete.
- Passes 2 and 3 were never started.

The partial pass was stopped safely. The final active recorder was allowed to
flush and finalize; no validator, continuation guard, recorder, rosbag,
Gazebo, or scenario node remained. The retained v1 interim status records the
exact shutdown evidence.

## Read-only integrity inventory

The historical stop record reports:

- JSON parse: `548/548` passed.
- YAML parse: `2242/2242` passed.
- SQLite `PRAGMA quick_check`: `320/320` returned `ok`.
- Current inventory: `320` `.db3` files and `320` `completeness.json` files.

Closeout rechecked these representative immutable SHA-256 values:

| Artifact | SHA-256 |
|---|---|
| `phase_08_interim_failure_status_20260725.md` | `ca37a67e48596c96b71d75606a1048754a278ff75af0ef07e155a0b07484453c` |
| `workflow_state/sweep.json` | `f7dbfae1e2d793cee7b1ae147f1ca2a128c7ffb4c79c78d954cadd6687f0daab` |
| `workflow_state/frozen_snapshot.json` | `8264adcce7274eb151a3ad8de198f7d74ce884bfd8c2a787e244e60d3418a177` |
| `workflow_state/holdout.json` | `d17f0ef96b9a34227fd0e6387ec70161e17797389e7fe6df9964cdfc41a7b752` |
| `holdout/records.json` | `95a6ba34870e3aad4c110a48b50582d5095da7d176e5423b9edb1cc719bad20c` |
| `phase_08_parameter_selection.json` | `f7dbfae1e2d793cee7b1ae147f1ca2a128c7ffb4c79c78d954cadd6687f0daab` |
| `phase08_parameter_candidates.yaml` | `e2b1db60cccb570653b629de85d9916e6a6b6700a37944434018d3fdfd1175a9` |
| `phase08_training.yaml` | `9ac9c47e3bc76097d97396da3bd2868cf5986f0c25de42e36c13847019014fce` |
| `phase08_holdout.yaml` | `f6d9a627f0157ad62f12279f8bde40fef815b0ebdaa487398f0d3641c5172b83` |
| `phase08_full_matrix.yaml` | `2786ba6aa58ab1e2eeb49b995b1c4abd68c71c1fe3f1eea13b6a993c5ef000e0` |
| `phase08_frozen_parameters.yaml` | `549594512147199556999941b87edc720d95b9c6ceaf312c3ff7cc3ae980efc9` |

The v1 parameter-selection document and retained `workflow_state/sweep.json`
intentionally have the same hash because the committed selection document was
copied from that authoritative workflow result.

## Failure cause and v2 boundary

V1 exposed two blocking behavioral-contract defects:

1. The convergence detector emitted a confirmed event after its counter reached
   zero, while the supervisor required an uninterrupted positive continuous
   convergence status. Real detector-to-supervisor activation was therefore
   unreachable in the executed sweep.
2. Goal verification used instantaneous orientation-dependent source score, so
   the rotating sensor could not sustain the configured dwell even at a valid
   source.

These defects explain the absence of fill/escape activation and the controller
holdout failure. They do not authorize weakening any v2 gate. Phase 08 v2 must
repair the contracts in the existing owners, prove all ten activation cases,
select again from three declared candidates using new training evidence, seal a
new selection-blind holdout, and use only the separate v2 evidence root.

## Final v1 disposition

- Simulation-ready gate: **failed**.
- Simulation-ready tag: **not present and not permitted from v1 evidence**.
- Physical progression: **not authorized**.
- Smallest approved next action: execute the staged Phase 08 v2 workflow from
  its ten-run activation gate.
