# R22 readiness command pairing validation

Current milestone ADOPTED in
[plan](../r22_readiness_command_pairing_plan.md), after verified
[V13 closure](../m4_v13_handoff.md). The single capture is COMPLETE and its
structural proof passed. The conditional evaluator correction is implemented;
91 focused tests and independent static source review pass. The cached component
is COMPLETE: D and C both have qualified continuous acquisition and zero mandatory
stopped acquisitions. Independent result review passes39 checks. Material closure
is COMPLETE; R22 is closed with the receipt below.

The first bounded job captures V13 D/slot4 then C/slot3 through the existing
five-alias reader union, once per bag, plus automatic readiness. It preserves
typed payloads for later cached evaluation.45s internal/55s SIGINT+5s kill,
60s inclusive. Subsequent opt-in correction, tests and cached component remain
conditional on exact full-stream pairing and boundary evidence.

Static owner review confirms ordinary publication and _publish_zero both emit
Twist before their diagnostic using the same final vector. Zero-publication
diagnostics deliberately have an invalid/NaN source_timestamp, while their ROS
stamp and final_command remain usable. Preserve the historical final-vector
validity rule; unrelated intentionally unavailable diagnostic fields must not
be mistaken for pairing failures. No common sequence identifier exists.

Existing R9 boundary-split tests must keep their historical unavailable verdict
under the default basis. New full_publication_order_v1 is opt-in and must validate
the entire ordered streams before admitting only pairs with both receipts inside
readiness. Capturing equal counts alone does not qualify this assumption.

Context validator and git diff --check PASS after adoption. Branch V2 at3369cfc,
task changes retained, no commits/push or physical/Pi/snapshot/V1 actions.
External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/`.

## Capture and independent proof

Sole session2295 terminal/reaped0;6.627779740s internal work. Exact command:

```bash
timeout --signal=INT --kill-after=5s 55s env -u PYTHONPATH OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 PYTHONDONTWRITEBYTECODE=1 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/runtime_environment.sh && exec /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/capture.py --prepared /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/prepared.json'
```

Exactly2 attempted/completed filtered reads: D1.960585298s, C1.721344365s.
All53,601 selected typed rows retained. Full streams contain8041 D and7319 C
ordinal pairs with exact finite vectors and valid monotone stamps/receipts;
no vector, gap, missing-record, stamp or order failures. Historical results
reproduce exactly: D7399/7398 inside,3233 mismatches; C6840/6840, no mismatch.
D global ordinal311 is the only boundary straddler, with matching all-zero
vectors: command receipt1789127204233268782, diagnostic1789127204234813533,
readiness start1789127204233578918. Separation1,544,751ns. Both-receipt admission
yields7398 D and6840 C pairs. No interior mismatch remains.

Helper SHA2569af34f898ce988ff0f6cb9b86cb50e4a885328a6e44acea3d764fb473c3e7e17;
prepared7773e53e6a2fe86d43b7a990d6b051aa9d27151734681358ac020586d325db6e.
Result115a266dea4813f542e6fc70ba8c330c1f05fcb88e1b8d965618313ecd1e5b74;
receipt3656cd5ad41e2bd985993595d9bcfc7b4ecd19601cd700640101537c20935544.
Independent capture_cached_review_v1.json PASS:23 checks, all143 prepared plus
prepared-self144 pins stable; SHA256
e6a6c4577325d7336c2d385b7b3b47a5174f6948367c2dcd4b2a65f1a2171997.
Initial review-only alias-population expectation was corrected from6 to55
resolved aliases, with6 selected record streams; initial audit remains saved.
No capture or scientific failure occurred. Native bag hashes are inherited
explicitly, with stable before/after raw file stats, not recomputed full hashes.
No model, motion-owner, subprocess or runtime calls occurred in the capture.

## Conditional source correction and focused tests

evaluate_m4.py now accepts keyword-only pairing_basis='full_publication_order_v1'
in _v10_motion_metrics. The historical default and all version/caller routing
remain unchanged. Exact full-stream validation precedes both-ready admission;
excluded boundary pairs, full/within/admitted counts, stamp validity and receipt
order remain explicit. All actual motion/coverage/authority limits are unchanged.
Original evaluator bytes are saved in evaluate_m4.before_r22.py, SHA256
fb5a85c0260788d92cc9d84781f2d16d04395f3e8298a6cb9dbc46b93f801987.
Selected source SHA256
f6369cdd6a3d659cab5f10997945945050e868140f91bfadd09aeb5f54f6765c.
Independent source review found no defect; all AST outside this function is
identical. Publication-order correspondence is conditional on the sole publisher;
the correction neither creates nor proves a missing shared sequence identifier.

Sole focused session47479 terminal/reaped0:91 passed in1.63s, including32 new
R22 cases and59 existing regressions. Seven selected source/test pins stable.
Exact command (console retained as focused_tests.log):

```bash
timeout --signal=INT --kill-after=5s 85s env -u PYTHONPATH OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 PYTHONDONTWRITEBYTECODE=1 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/runtime_environment.sh && exec /usr/bin/python3 -B -m pytest -q -p no:cacheprovider ros2_ws/src/ros_esc/test/test_r22_motion_pairing.py ros2_ws/src/ros_esc/test/test_r9_motion_readiness.py ros2_ws/src/ros_esc/test/test_m4_v10_motion.py ros2_ws/src/ros_esc/test/test_m4_evaluation_cli.py --junitxml=/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/focused_tests.xml'
```

focused_test_receipt.json binds source pins, JUnit and console. Tests exercise
both boundary edges/orientations, exact default/C field parity, full-stream
missing/extra/outside/interior faults, invalid/nonfinite vectors, source/receipt
rollback, the inclusive0.5s receipt limit, unchanged authority and real sustained
pose/command stops. No whole-workspace tests or new simulation were needed.
The previous user-question turn was explanatory, with no implementation progress;
this turn resumed the available source correction and completed its validation.

## Cached motion component

Sole session28620 terminal/reaped0, COMPLETE in6.045165063s. One job restored
53,601 captured records and made exactly four existing motion-owner calls:
historical default and selected basis for D, then C. No raw bag reads, model,
reference, native analysis, subprocess or runtime calls. All178 prepared plus
prepared-self179 execution pins remained unchanged. All11 component checks pass.
Exact command:

```bash
timeout --signal=INT --kill-after=5s 25s env -u PYTHONPATH OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 PYTHONDONTWRITEBYTECODE=1 bash --noprofile --norc -c 'source "$1" || exit; exec /usr/bin/python3 -B "$2" --prepared "$3"' r22-cached /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/runtime_environment.sh /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/cached_component.py /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/component_prepared.json
```

Helper SHA256e1b6d438edc41b5022beb6514bae54acaff46a69ed8b63c7d0db8a7856bad797;
prepared965419c6d1428e6a4e2683eafadd8baea3db9c32dcb2a4f6e7c9d33dbb5defd7.
The helper's unexecuted draft source-validation receipt schema was corrected to
the actual91-test/seven-pin receipt before final preparation; no failed execution.

Both historical results reproduce their original mandatory_stop_evidence exactly.
C preserves every original common result field except the explicitly selected
pairing-scope label. D now measures OBSERVED_CONTINUOUS_ACQUISITION, complete
authority, pairing and pose coverage, with zero mandatory stopped acquisitions.

| Arm and phase | Source interval (s) | Measured path (m) | Commands | Maximum zero-command overlap (s) |
| --- | --- | ---: | ---: | ---: |
| D VERIFY |84.2–98.8|0.515312808|891|0.0|
| D DESIGN |98.8–99.5|0.016482363|50|0.1|
| C VERIFY |69.9–85.8|0.476942843|976|0.0|
| C DESIGN |85.8–86.4|0.004111921|39|0.0|

All four segments have complete coverage and positive measured motion; none has
a sustained stationary interval. D's isolated0.1s zero overlap remains recorded,
below the unchanged0.5s sustained-stop threshold. D admits7398 complete pairs
and excludes only zero pair311; C admits6840 and excludes no boundary pair.
This is a new, separately retained R22 measurement. V13's original unavailable
verdict, failed release, reports and twelve unstarted slots remain unchanged.

Result SHA25602e07e19c34fdb97716c4570037e046f4cf7709bc5a1b700c3afd04205dc28af;
receipt7f2ae8a7d8077c9a6733918583aadc15702bdee13f302123b071141ddc76e09c.
See cached_component/slot_4_selected.json and slot_3_selected.json for complete
motion evidence; component_execution.json retains exact argv and terminal status.

## Independent result review and closure

cached_component_review.json PASS:39 checks, SHA256
26f04870988809a1160c550098fde24a1b370041b46be8ab5987bf2835b62a89.
The independent reviewer directly checked original D/C default objects against
the retained V13 metrics, all20 C common fields, D's two uncensored positive-motion
segments and complete authority/pairing/coverage,179 current execution pins and
eight output hashes. D's three DESIGN zero-publication reports overlap the same
98.8–98.9s interval; they are not additive durations. No owner, bag, model or
runtime was invoked by the review. Original V13 evidence remains unchanged.
Context validation and git diff --check pass. Material checkpoint follows.

Material checkpoint commands completed successfully:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
git diff --check
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2
timeout --signal=INT --kill-after=5s 25s /usr/bin/python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/save_closure_checkpoint.py
```

Archive COMPLETE in 0.961338 s, 673 verified source members, stable source,
retained staged/unstaged patches and external evidence hashes. Manifest
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r22_readiness_command_pairing_closed_v1/manifest.json`
SHA256 `21385d3af80c3818b581475cbc26db3cb7c381d35eaf488fc394558365a34049`.
The existing V13 closure helper changed only its exclusive archive destination
and scope text; origin and exact helper hashes are retained. Final archive-receipt
paragraphs postdate this snapshot. R22 is COMPLETE; full research goal remains open.
