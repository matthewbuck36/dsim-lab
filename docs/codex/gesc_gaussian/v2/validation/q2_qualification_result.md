# Fresh Q2 qualification evidence

Status: ACQUISITION INCOMPLETE after one case; no scientific evaluation occurred.
Authority: `../q2_qualification_plan.md`; source evidence is recorded in
`q2_qualification_source.md`. Existing Q1 and D1/D2/D3 results stay closed.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v1/`.
Frozen contract SHA256
`a1b3b0b1d76e373e7a340a8749c898724d1f731a51eb90cd536e48f96b1fb7a3`.
Dispatch release SHA256
`a76f33cc216bdea3235efa1a995ffd602752f7c4e0a1ccc9aa658417234faeca`.
Source checkpoint SHA256
`bb853c7b8dd549d106ee885f1b369d5e38c84a7019acbf7a570ff5ffd7793d24`.

## Acquisition contract and command

Exactly four fresh simulation cases, seeds26090921–24,125 simulated seconds
after readiness each. First visible, remaining batch cases. Live direction uses
the frozen75% mean/25% instantaneous policy. Existing observation-only supervisor
prevents candidate interventions. The command is:

```bash
timeout --signal=INT --kill-after=60s 1140s python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/acquire_q1.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v1/preflight/contract.json
```

The pinned wrapper, exact sourced Humble/Q2 overlay environment and retained
source/build/audit receipts are in `preflight/dispatch_release.json`. Console
output is `preflight/acquisition.log`; the wrapper preserves exit/time in
`preflight/dispatch_completion.json`. The existing acquisition owner saves
per-case integrity/spawn receipts and final `acquisition/acquisition.json`.
It creates `study_manifest.json` only if all four inputs pass. No retry or
replacement is authorized by an incomplete acquisition.

## Retained acquisition failure

The single job exited1 after167.246393s including wrapper overhead; acquisition
reported164.732646s. Exactly one case dispatched, zero imports and zero accepted
study inputs. The first recording itself completed125.0 simulated seconds with
no clock error and passed recording completeness, no forbidden events, final
commands zero and cleanup. Spawn errors were0.0000266755m and0.0000385463rad;
no coordinate offset was fitted. No second case started.

Failure: `ValueError: Q2 run directory differs from its reserved identity before
input reads`. The unchanged recorder creates `runs_root/YYYY-MM-DD/run_id`;
the new analyzer guard incorrectly required `runs_root/run_id`. The actual
directory is `runs/2026-09-09/q2-primary-shadow-v1-discovery-residence-26090921/`.
The fixture duplicated that incorrect layout, so the synthetic test pass did
not establish recorder/analyzer path compatibility. Preserve this failure and
its source/data unchanged. The separately declared correction is
`../q2_acquisition_path_correction_plan.md`.

`acquisition/acquisition.json` SHA256
`77c879c357eb3add8845149796c7e1319603f7875aa9aba7ff4bfd177e3d6fb0`.
The failed guard ran after the existing acquisition integrity checks and before
publishing an accepted input receipt. No study manifest, labels, nomination,
direction reference, confirmation scientific output or M4 release exists for
this attempt. Its scientific stages below are withheld, not pending dispatch.

Immutable `acquisition_closed.json` SHA256
`672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02`,
status CLOSED_INCOMPLETE. It binds all20 retained files and confirms570 frozen
source receipts unchanged at closure. Only integrity metadata was interpreted;
bag content was byte-hashed for retention. The failed version is closed.

## Withheld scientific stages

The original plan would run the existing `evaluate_q1.py labels`
owner once under600s after acquisition integrity. It freezes input-only discovery labels/targets and nine
detector/neighborhood settings. A passing nomination alone permits held
confirmation evaluation; missing exposure preserves EVIDENCE_UNAVAILABLE.

Its `evaluate_q1.py references` job would run once under300s only with a completed,
integrity-valid label job. Its declared branch evaluates48 fixed targets after
nomination, or24 discovery targets diagnostically while24 confirmation slots
remain SEALED. Missing/incomplete/invalid authority never permits fallback.
No target replacements, numerical retuning, latent blends or old-controller
trajectory replay. Detector, direction and combined qualification stay separate.

Neither recording completeness nor this selected primary-field study establishes
the M4 latency, false-decision or fill/escape/SEARCH/stronger-candidate targets.
The16-run pilot and final V2 acceptance remain pending.
