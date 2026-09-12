# M4v13 execution

Current state: CLOSED_INCOMPLETE; sole dispatcher session9544 terminal/reaped1
after1559.393681570s outer. Four complete acquisitions, twelve confirmation
slots unstarted. D motion pairing is unavailable despite passing arrival and
direction; see [closeout](../m4_v13_handoff.md). Original start record: the
acquisition helper started at2026-09-11T11:26:07.040965UTC, PID148602.
At the starting boundary no V13 completed outcome was claimed. The four visible
development slots run first; the existing release gate controls the twelve
confirmation slots. Source, scenarios, helpers, tests and preparation inputs
remain frozen throughout. GOAL_HOLD is optional; valid recovery followed by
recorded arrival within0.5m is the behavioral endpoint.

Startup established for slot01/A: native console records preflight passed and
motion readiness true at2026-09-11T11:27:22.861175UTC. Run path:
`pilot/m4_pilot_v13/runs/2026-09-11/m4-pilot-v13-slot01-A-26091141/`.
This is readiness evidence only; await the native terminal slot, block-analysis
and release receipts before claiming a completed outcome. Poll session9544 and
the existing acquisition/slot_N.json, acquisition/summary_N.yaml,
analysis/block_K/block_receipt.json and result.json. Final native owners write
acquisition/acquisition.json and report/report_receipt.json.

## Preparation and release

The source bundle passed640/640 checks. Independent frozen scenario and workflow
audits passed207 and29 checks respectively. See
[source validation](m4_v13_source.md) and [frozen preparation](m4_v13_preparation.md).
The latter document is an archived input and must remain unchanged through
dispatch. Retained source-work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/`.

Prepared archive COMPLETE:24 verified files,0.152343736s, at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m4_v13_prepared_v1/manifest.json`.
Manifest SHA256:
`a726b8b32f30b6d40c60ddf44d1d2448dc80699907568546e2621ca0174b7e7f`.
Release session77791 is terminal/reaped0. Initial release is RELEASED at
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v13/preflight/dispatch_release.json`,
SHA256`ad89001d6fab7bc27f39ce7f3a091611f8bde27a1792cfd9103687128c92f4cc`.
It binds the16-row contract SHA256
`47fa4a8239d9a87f479461cba01790ce8aaa234a022a1cdeb206220152560efe`.

## Sole acquisition command

```bash
env -u PYTHONPATH -u RMW_IMPLEMENTATION \
  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 MPLBACKEND=Agg ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 \
  bash --noprofile --norc -c \
  'source "$1" || exit; exec /usr/bin/python3 -B "$2"' \
  m4-v13-acquire \
  /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/runtime_environment.sh \
  /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/acquire_once.py
```

The frozen helper verifies the release identity, environment and source pins,
then invokes the existing run_m4.py dispatcher once. The exact released command
uses GNU timeout:15680s to SIGINT plus120s to SIGKILL,15800s inclusive ceiling.
No retry, replacement, tuning or added scientific analysis is authorized within
this fixed version. The source root retains acquisition_owner_v1.json and
acquisition_console_v1.log; acquisition_execution_v1.json is written at terminal
completion. Native receipts are under pilot/m4_pilot_v13/acquisition/.

After context recovery, the phase-context validator passed before documentation
updates. Branch remains feature/gesc-gaussian-robustness-v2 at3369cfc, with retained
task changes. No physical/Pi/snapshot/V1 edits or commit/push. Full goal remains
open, including the separate unachieved/unavailable original30% onset endpoint.

## Completion audit while acquisition runs

Read-only detector audit confirms the original acceptance target in plan.md:
at least30% median latency reduction from independently labelled sustained basin
entry, without additional erroneous fills or terminal decisions. R10's response
from a fixed SEARCH origin and its synthetic controls are different estimands;
neither those results nor D02 arrival proves this endpoint. V13 preserves it as
secondary evidence. No source or scientific calculation changed in this audit.

The existing automatic analysis already produces the next required evidence.
Inspect confirmation block slot_N_labels.json for admission_ns,
observation_start_ns,residence_intervals,short_residences and pose_faults;
slot_N_metrics.json for latency status/reason/first_opportunity, eligibility,
observed/censored endpoints and attribution fields wrong_fills,wrong_goals,
attribution_errors. The final report/result.json latency object retains six
planned A/B and C/D pairs, twelve planned endpoints, observed counts, both
medians, descriptive_fraction_reduction,error_attribution_complete,
no_additional_errors,pairs and status. The existing aggregate requires all six
valid pairs, reduction>=0.30 and no additional errors for PASS.

Await those frozen outputs before any follow-on diagnostic. Do not substitute a
later residence, commanded verification motion or a different latency origin to
manufacture an endpoint. Existing labels describe sampled model-region residence,
with the limitations already recorded in m4_v11_measurement_diagnosis.md.

## First retained acquisition

Slot01/A COMPLETE,480.851330411s inclusive. Native slot_1.json and
summary_1.yaml retain the exact result and inputs. Recording/integrity, final
cleanup and independent inner/outer cleanup all PASS. Stage A did not complete:
no convergence/fill/escape events; observed state path SEARCH only. The live
360s bound stopped on source-time360.313s, elapsed360.026s from0.287s. No global
arrival or valid recovery is claimed. This measured baseline failure does not
block the planned development comparison. Scientific labels wait until all four
acquisitions finish. Slot02/B has started under the same dispatcher session9544.

## Second retained acquisition

Slot02/B COMPLETE,437.995454385s inclusive. Recording/integrity, all eleven
primary predicates and both cleanup owners PASS. Observed state path:
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE ->
ESCAPE_ASSIST -> SEARCH. Valid fill cardinality, local recovery and owned escape
pass. Global proximity is observed at distance0.499832657689m, recorded sample
index8723, bag stamp1789126839865512279, position(3.522849846286,3.000689905753).
The live post-recovery monitor ends at314.098 simulation seconds; Stage A
completed at277.14s. The block's exact recorded-pose arrival measurement remains
pending and is required before treating this monitor time as the analyzed time.
Controller-ranked goal was not observed and is optional under the adopted
arrival endpoint. No native predicate failed. Native receipts:slot_2.json and
summary_2.yaml. The dispatcher remains live; C/D and block analysis are pending.

Independent cached B review found no inconsistency: summary_2.runs[0] equals
the acquisition runner_result; scenario_result classification agrees. All52
completeness checks pass without failures/warnings. One confirmation/request
produced fill1/cluster1/revision1; request255.3s, active fill publication255.4s.
Native final-zero, process exits and strict cleanup pass. Absent GOAL_HOLD and
the failed optional controller-goal diagnostic remain preserved. No bag scan,
scientific recomputation or frozen-input edit occurred during this review.
Slot03/C has now started under the same live session9544.

## Third retained acquisition

Slot03/C COMPLETE,239.424210189s inclusive. Recording/integrity, all eleven
primary predicates and both cleanup owners PASS. Direct recovery path:
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE -> SEARCH.
Live arrival136.567s at0.498622480636m, position(3.705676516141,3.045773680965),
recorded sample3949/bag stamp1789127100476040467. Live and native recorded
proximity witnesses agree; the exact recorded-pose clock join remains pending
in the block analysis, as do direction quality and mandatory-stop measurements.
This run is a measured C-package success; it does not isolate a detector main
effect or establish D success. Native receipts:slot_3.json and summary_3.yaml.
Slot04/D is next, and the same finite dispatcher session9544 remains live.

Independent cached C review found exact summary/scenario/slot runner-result
agreement, all61 completeness checks PASS without failures/warnings, one
fill/cluster and one completed direct episode. Command ownership is supported
by1023 repulse controls;352 mature radial-progress samples all exceed0.18496m
against0.05m required. Return authority cleared at live recovery107.123s.
Final-zero, target/bag exits and strict cleanup pass. No scientific recomputation
or frozen-input edits occurred in this review.

## Fourth retained acquisition and automatic science

Slot04/D COMPLETE,258.978157089s inclusive. Recording/integrity, all eleven
primary predicates and both cleanup owners PASS. One qualified recovery follows
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE ->
ESCAPE_ASSIST -> SEARCH. Live arrival147.998s at0.497300517719m,
position(3.544424821743,3.004687734720); native recorded sample4288/bag
stamp1789127351846543429 agrees without interpolation. Exact analyzed timing,
motion/mandatory stops and direction gates still require the block products.
Native receipts:slot_4.json and summary_4.yaml.

All four development acquisitions are COMPLETE: A behavior FAIL, B/C/D behavior
PASS. The existing automatic analysis/block_0 job is running under session9544;
slot1/2 labels and metrics are already retained. No manual scientific rerun or
confirmation release was introduced. The existing release gate evaluates the
complete frozen block before any confirmation dispatch.

## Terminal development gate and retained science

Session9544 is terminal/reaped1, outer1559.393681570s, native1554.627737746s.
The source-hash checking driver reports error=null. Native terminal failure:
`ValueError: M4 v13 usable development analysis: block science incomplete`.
Four COMPLETE acquisitions, twelve UNSTARTED, no confirmation release and no
replacements. The report was generated successfully in5.033743823s.

All four science child jobs returned0 with complete/integrity/clean termination
true, no timeout or unexpected descendants. Elapsed127.474274578s for block0;
labels100.457599557s, C reference7.496080291s, D reference8.451591495s,
summary6.188649624s. All recorded_pose_arrival_v1 bindings pass: B314.098s,
C136.567s,D147.998s; A is a measured nonarrival. A/B/C science completeness
passes all nine checks. D fails only motion_measurement_complete.

C direction median16.839333255/P9021.180856594 degrees,3/3 eligible averaging;
D12.519442678/25.224003284,4/4. Both direction gates PASS. All48 development
targets retained:9 observed,39 unexposed. C motion is observed continuous with
zero mandatory stops. D authority and segment coverage pass, but positional
pairing fails:7398 commands versus7399 diagnostics inside readiness,8041 each
in the full streams. Pre-readiness counts312/311 and3233 positional mismatches
motivate a separate boundary diagnosis. D mandatory-stop count remains unknown.

Native block receipt SHA256
`d065a333cccc8f02b3cba4f1ad768cf6c0ca2f34f12004b51f3ff79dd94bc1e3`;
acquisition SHA256`af02254977aee7309406fd01fd433413f4a442616d2603cc7a848c1d945f64b6`.
No frozen receipt was rewritten, no science was rerun, and no confirmation was
unsealed. See closeout for final report hashes and the full evidence boundary.

Independent terminal cached review PASS:57 checks in0.312s, saved as
`v13_terminal_cached_review_v1.json` in the source-work root; SHA256
`3d0d70a850546639c4532660badf4d80fac70b45ddcf0ac51c7f2b0254590300`.
All963 validation pins remained unchanged through closure review;948 contract
sources are covered. Four native cleanup chains and science reaping proofs pass;
owned PIDs/sessions are absent. No release/replacements and all192 scheduled
direction targets, including144 unavailable confirmation targets, are retained.
This review validates the terminal ledger, not D motion or overall qualification.

Before post-terminal navigation updates, exact plan/status/fresh-handoff bytes
were saved under source-root closure_before/ with a manifest. The existing V12
closure archive helper is adapted only for V13 paths and truthful scope, with
origin/target hashes in closure_helper_origin.json. No source/measurement owner
changed. Context/diff checks and the existing checkpoint tool precede its one
finite material archive invocation.

Material closure archive COMPLETE:669 verified source members,0.956403317s,
`checkpoints/m4_v13_closed_v1/manifest.json`, SHA256
`f393c5ab1786127c84b17fa5a35b4d95e370b616b172b1a3c2e8e4d2d0b21e58`.
Exact command: `timeout --signal=INT --kill-after=5s 25s python3 -B
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v13_source_v1/save_closure_checkpoint.py`.
The unexecuted initial helper retained one V12 pilot-path literal; its assertion
caught it before archive execution. Initial bytes and origin hashes are retained;
the literal was corrected, AST checked, and the single archive job completed.
No source/science/runtime or frozen result was changed by that helper correction.
Context validator, diff check and existing material checkpoint tool PASS.
This receipt postdates the immutable archive.

Independent native D review also confirms all62 completeness checks, one
authenticated snapshot/fill/cluster and one owned assisted escape. Recovery
120.73s and arrival147.998s witnesses agree. Final-zero/clean exits and strict
cleanup pass. This native evidence does not replace the unavailable scientific
motion pairing measurement.
