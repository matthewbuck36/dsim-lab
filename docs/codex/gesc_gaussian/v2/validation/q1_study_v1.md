# Q1 study v1 closeout — 2026-09-09 UTC

Status: CLOSED EVIDENCE_UNAVAILABLE. Acquisition is COMPLETE; scientific
qualification is unavailable. No detector/neighborhood pair was nominated,
confirmation remained SEALED_NOT_OPENED, and the direction-reference job and
M4 pilot were withheld. This closes the fixed Q1 version, not the full V2 goal.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery4/`.
The exclusive `study_closed.json` binds79 retained artifacts, including all
four accepted inputs, imported evidence, acquisition and frozen analysis.
SHA256: `090a5b11c803cb0bd0b69b740f02630dacc19f9b84af3172687ba6cf978f61b7`.
The complete source contract and normal analytical input validation passed
again before closure; no frozen source changed during acquisition/analysis.

## Acquisition evidence

The finite continuation imported exactly two accepted recovery3 discovery rows
and dispatched exactly two new confirmation cases. It finished in
321.26918041799945 wall seconds, exit0, below600s. All four inputs completed
125 simulated seconds after readiness and passed all60 recording checks,
spawn/configuration binding, safety/final-zero and cleanup. Both new runs
ended in SEARCH, with no forbidden events. These are shadow observations;
absence of fill/goal is the intended observation contract, not a behavioral
pilot result. All41 original recovery3 closure artifacts are unchanged.

Exact commands from repository root, after sourcing Humble and the isolated
overlay:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout --signal=INT --kill-after=60s 540s python3 docs/codex/gesc_gaussian/v2/tools/acquire_q1.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery4/preflight/contract.json > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery4/acquisition_console.log 2>&1
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout --signal=INT --kill-after=30s 600s python3 docs/codex/gesc_gaussian/v2/tools/evaluate_q1.py labels --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery4/preflight/contract.json > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery4/label_console.log 2>&1
```

Each command ran once and exited0. The label job completed within600s; no
elapsed-time measurement beyond that process bound is claimed. No reference
invocation occurred. `acquisition_integrity_review.md` records the independent
integrity-only review, including exact imports and all32 input-file hashes.

## Frozen discovery result

Both discovery inputs have qualified schema2 joins, no integrity errors and
no pose faults. Residence has3732 synchronized observations,3673 eligible
after readiness; approach has3732 and3676. Every one of the nine fixed
R/tolerance combinations produced zero detector events. Each approach row
passed its eligible negative-exposure requirement; every residence row was
EVIDENCE_UNAVAILABLE because there was no uncensored first42s positive.
There are no measured FAIL reasons, but zero required positives means neither
sensitivity nor moving-verification success can be estimated.

The independently frozen local-well intervals were:

| Discovery input | First positive | Later positive |
| --- | --- | --- |
| Residence26090911 |25.898–45.822s,19.924s |68.398–98.114s,29.716s |
| Approach26090912 |25.155–45.555s,20.400s |68.845–84.995s,16.150s |

Times are absolute simulation source time. The first intervals are too short;
later same-SEARCH intervals remain censored under the frozen first-opportunity
rule and are also shorter than42s. Eligible negative exposure is8.958s in the
residence run and19.890s in approach. Unknown trajectory remains unknown.
No old-detector latency,30% improvement, erroneous-fill rate, direction error
or averaging availability is inferred from these results.

| Relative artifact | SHA256 |
| --- | --- |
|`acquisition/acquisition.json`|`65c8e815eb9cb711b5eb3f84ab73fe9f1f17f2db989c7da71b625ebd9cf4c568`|
|`study_manifest.json`|`e3eab21ca5ea7724c11f20317e7bab5b6db383b5624c2ce36836d229f9032fd7`|
|`analysis/label_job.json`|`735948bb338c20af20f11a719f14b4d106584b89984e65cb08b635e04a8a0f1c`|
|`analysis/discovery_nomination/nomination.json`|`2406dc5de32ae2309a3d94af0989492b5f1a1411fe165288e8f1edb7bb4a2ea5`|
|`analysis/discovery_labels/labels_manifest.json`|`eeebf54c3e9299edc968d5a497e501fc1ab4d19113a43f5c71522fa143fde19e`|
|`analysis/discovery_targets/targets.json`|`b5d84cf2bb4f8900a940389ec16e5aa2608cbd76222907cdfeecb9a64cc4b1aa`|
|`label_console.log`|`6b3856da69e819ab8ee0cdbc6e794190ad006dc22cde65af3f3b109d367bbca8`|

Closure creation initially used a wrong administrative dictionary key
`input_artifacts` instead of `input_files`; it exited1 before creating the
closure. The retained `closure_creator_v1.py` records that failed helper.
Correcting only that key and idempotent comparison of the already copied
review allowed closure creation, exit0, under30s. No analytical computation,
acquisition or scientific output was retried or overwritten.

Next work is discovery-only diagnosis of actual motion, independent region
semantics and unchanged detector response. Any changed study needs a fresh
prospective amendment. Do not lower Q1's42s gate, enlarge its labels, reuse its
sealed confirmation for tuning, or treat complete recordings as qualification.
