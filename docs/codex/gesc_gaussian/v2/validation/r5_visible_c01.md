# R5 visible C development01

Prospective protocol: [r5_visible_c01_plan.md](../r5_visible_c01_plan.md).
Current boundary: helper/scenario preparation; no acquisition or analysis yet.
This new exposed development case does not replace failed M4v10 slot C.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/`.
Run identity: `v2_method_development_C_20260910_01`, exposed seed26091011.
R5 validated source760 hashes still match before preparation. The existing
scenario/recording/analysis owners remain authoritative.

## Exact execution commands

All commands run from `/home/mattb/dsim-lab`, with logs retained externally.
Preparation is exclusive and will only run after helper/scenario review:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 85s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/prepare_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/preparation_outer.log 2>&1'
```

Once prepared identity, source/runtime bindings and checkpoint pass:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 415s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/run_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/acquisition_outer.log 2>&1'
```

Actual sessions, outcomes, elapsed times, analysis commands and artifact hashes
will be added after each terminal receipt. `ATTEMPT_RETAINED` means evidence was
saved; behavioral success requires all declared predicates, recording and
cleanup. Global arrival uses the existing evaluator-only0.5m region; GOAL_HOLD
is optional. Continuous acquisition requires the existing measured-motion rule.

## Static admission review

Scenario review PASS18 checks,16 disclosed leaf differences, no blockers:
`scenario_review_v1.json`, SHA256
`82c25418021022731a4982203f0d8c1c9600c33ed6bdeed529cc66e5dab26545`.
All algorithm, controller, geometry, topology, seed, disturbances and arrival
predicates match V10 C. The one-case suite also sets stop_on_run_failure true;
this stricter policy has no subsequent slot to affect.

The point-in-time procfs audit found no selected runtime active and all five
old V10 owners absent. Audit `r5_validation_v1/c01_pre_runtime_audit_v1.json`
and its `c01_pre_runtime_audit_v1_correction.json` retain the exact evidence.
The correction only removes the audit shell from a broad daemon label; actual
shared daemon PID24080/domain201 is separate from run ownership. Discovery and
readiness will still be checked by the existing runner before motion.

## Preparation outcome

C01 preparation PASS3.754784s, session98659 terminal/reaped;767 source pins
including all760 validated R5 pins and21 installed entries stable. Prepared SHA256
`e0d71e22461082dd6eaa3ed9b8d657b5242cb2dc2ecde127e7dd30c30b87a024`.
Root resolved selector/topic/identity review PASS. Acquisition may proceed once
this material checkpoint is saved; source/helpers stay held.

Preparation and root review verified exact seed26091011, Arm C, arrival-only
contract, all18 required algorithm topic aliases and no source hash changes.
Native analysis helper SHA256 `f3c8906dac585275128e0f04ee125c08fba6e8d9e8e445f6e8a446ae93d29e07`;
reference helper is byte-identical to the previously used development owner,
SHA256 `dff06e87ed23f630f6c9c5b9ed91114bbc3e1bb5d7ca45b780f0ea0b68e5a7ae`.

## Acquisition release

Material checkpoint and diff check PASS. Prepared archive9 verified files in
0.019669s, manifest SHA256
`1c81b85722e7213c264203b1d64fe75af9594b30fc6a0ed0e2ba9690e7879b3f`
at external `checkpoints/r5_c01_prepared_v1/manifest.json`.
Single acquisition session97648 started with the exact command above.
Recording preflight passed and motion readiness became true at
2026-09-10T22:57:13.212661Z. No behavioral result is asserted at this point.

## Prospective analysis commands

Use only after terminal acquisition receipts demonstrate complete recording,
source integrity and inner/outer cleanup:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 115s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/analysis/run_analysis.py --run-directory /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/runs/2026-09-10/v2_method_development_C_20260910_01 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/analysis_v1 --expected-run-id v2_method_development_C_20260910_01 > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/analysis_outer_v1.log 2>&1'

env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 40s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/analysis/run_direction_reference.py --analysis-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/analysis_v1 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/direction_reference_v1 > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/reference_outer_v1.log 2>&1'
```

## Terminal acquisition

C01 acquisition terminal/reaped, session97648,229.426403s. Recording and inner/
outer cleanup PASS,767 source pins stable; behavior FAIL. PDE confirmed71.1s,
but no fill/escape and Stage A expired at180.333s; final robot stayed near local.
Attempt receipt SHA256 `2156dd608365f4bb8cab0ba8826b758106e3be2f7a1970a5eaf5c4b5178a20ab`.
Native analysis is active once, session19870, under120s maximum; no raw reread
outside this existing two-scan job. Read `visible_integrated_C_01/analysis_v1/`.
No new runtime or source correction released; V11 draft remains NOT_ADOPTED.

Only recording_complete and cleanup_complete pass; the other10 required
predicates fail. The global-arrival relaxation is not the cause of this failure.
The new case did not reach a fill/escape handoff, so it cannot empirically
validate the R5 post-activation exemption. Native analysis proceeds because
recording/source/cleanup evidence is complete; behavioral failure is retained.

## Terminal analysis/reference and diagnosis

C01 closed with behavioral failure before DESIGN/fill/escape. Sessions97648,
19870 and90322 terminal/reaped; acquisition229.426403s, nativeanalysis64.377794s,
reference6.283701s. [Current handoff](r5_visible_c01_handoff.md) records the distinct
approach failure and ordinary deadline fault race. Native analysis PARTIAL from
missing required escape applicability, while freshrecording/lifecycle and measured
motion/arrival evidence are valid. Reference executes but scientific summary FAIL
(median22.061854deg,P9073.223806deg,3eligible/24scheduled). No runtime active.
Source remains held. Next prospectively plan bounded deadline handoff correction
and approach-law diagnosis. V11 draft NOT_ADOPTED; fullgoal remains IN_PROGRESS.

Native receipt SHA256 `c55a6ddc334a9cd04c68e512b3ada7665ee612643ce1985e9ed2f0c027b396ff`;
motion/arrival SHA256 `2c33ed1d96a7895509f1aae7d28c105ff76b4e425b75f6e6cc7a897aa9b41f10`;
reference receipt SHA256 `cb4f56c95ccf36862614a219258d59c86e59e743890890ebf07ceddd337207a5`;
reference result SHA256 `611a63bed3d1e94e580ab01b7cc92490160634c0858f7f74320416f29f3761f8`;
cached diagnosis SHA256 `0232a4714f9ec44e24fc2a490959c8c584090b1fb03c560064275db2016f2a6d`.
Native execution exit1 corresponds to PARTIAL_RETAINED, not a timeout or lost
recording. Both raw scans completed, no execution errors or changed pins. The
reference's exit0 preserves its scientific FAIL and all24 scheduled outcomes.

## Retained direction failure location

Read-only inspection of the completed reference result identifies target3
(offset75s, actual source77.619s) as the large error: averaged output86.014295deg
versus instantaneous4.227476deg, paired change-81.786819deg. Targets1/2 averaged
errors are3.540097/22.061854deg and improve17.746399/3.282330deg respectively.
Later exposed targets4–6 have uninformative references;18 targets are unexposed.
This locates a direction-quality failure during approach; it does not establish
a cause or authorize retuning from ground truth. No source/model/bag job ran.
This note postdates the immutable C01 closure source archive.
