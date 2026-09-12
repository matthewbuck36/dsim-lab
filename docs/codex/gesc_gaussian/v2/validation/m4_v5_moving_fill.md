# M4 v5 moving-fill source validation

Status: CLOSED_SOURCE_VALIDATION_PASS, 2026-09-10 UTC. Source checks passed;
source archive and preparation/audit/release still precede acquisition. Both original research goals remain
unproven. Active plans: `../m4_v5_moving_fill_plan.md` and
`../m4_v5_primary_topology_amendment.md`.

External evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v5_moving_fill_v1/`.

## Recorded diagnosis and old evidence

See `m4_v5_moving_fill_diagnostic.md` for the exact first safety-stop reason,
failed first export, separate corrected extraction and before/after hashes.
The original run remains CLOSED_INCOMPLETE. Under `timeout 30s python3`,
`retained_evidence_check_v1.py` independently verified all 242 v1–v4 pilot
files and four closure archives unchanged in 5.345019 seconds. Receipt
`retained_evidence_check_v1.json` SHA256
`ad88b5f43964392eb2b0bdaf031bb04cb98040780f92dab2564876380f137d8b`.
No bag decoding or scientific reevaluation occurred in that evidence check.

## Actual moving/shared-escape integration

The existing `test_v2_moving_pipeline_transport.py` fixture gains an optional
guarded case; its default path is preserved. New
`test_m4_v5_moving_escape.py` selects six cases. All eight production
supervisor/Gaussian/composer/escape owner files are unchanged.

The initial legacy-guard reproduction passed 1 check in 10.98 seconds,
confirming the recorded missing-outside-anchor reason after actual commit
and both acknowledgements. Its exact intermediate test bytes are retained
by documented inverse-extension reconstruction and receipt-hash verification;
see `moving_escape/legacy_guard_exact_source_v1/manifest.json`.

The focused bundle passed **78 checks in 86.25 seconds** (wrapper86.759909),
under an explicit235-second command cap. Exact command, log/JUnit and 11-file
stable before/after source/test pins are in
`moving_escape/guarded_pipeline_v1_receipt.json`, SHA256
`aa4648f39e9955adc34fcc8f6af71c6a441c1acdd5f916477f3b5f3bd972c8b1`.
Held scope receipt `moving_escape/held_scope_v1.json`, SHA256
`705efde142e8f0c2e73c899ad20909191bd884b8e4a5c98f149751f883754b75`.

Coverage: outside anchor with fallback off/on; missing legacy anchor FAILSAFE;
bounded interior success for PDE and two-block detector selectors; displacement
below0.50m rejected; each of the actual objective and direction acknowledgements
independently blocks escape when withheld; one retained committed fill and
one ledger count; postcommit CANCEL returns ALREADY_ACTIVATED. Existing moving
worker-cancellation, supervisor guard/interior and escape geometry regressions
also pass. Successful cases intentionally stop only after ESCAPE_STARTED.

These fixtures use declared synthetic pose/source/detector inputs and direction
diagnostics echoing actual objective publications. The worker, registry,
composer, supervisor transition/ledger, escape guard and cancellation paths are
actual owners. This does not qualify Gazebo behavior, controller motion or
direction estimation. Final held test hashes:

- `test_v2_moving_pipeline_transport.py`:
  `2b404af60042431524871853e3599ab8c48186c0e8cd4b6de682735d04d4af73`.
- `test_m4_v5_moving_escape.py`:
  `d2f380cd6b77e0750653164db0c3b5889663441580b4b44ae9def5ca1201722c`.

## Intermediate version routing

The initial route bundle retained one fixture failure plus290 passes: its
assertion looked for an inherited control in raw case overrides instead of
the resolved frozen-profile/case merge. Correcting that fixture, without
changing runtime controls, passed291 checks28.526seconds with nine stable
pins. `version_routes/focused_v2_receipt.json` SHA256
`b08e0c7331d7eb63298e14891b913f22f8d5c6e18686f3876039d0080e0c7054`.
Oldv1–v4 JSON output parity and exact preedit source copies are retained.

This is intermediate evidence only: subsequent read-only schema review found
the primary verified-trap prerequisite, now separately amended before edits.
No schema admission or numerical qualification is claimed by291 route checks.
Fresh prepared-only driver copies use domain186; none has run preparation or
acquisition. Final source validation will include the topology amendment.

## Strict selected typed-fill authority

The existing recording validator enables an explicit optional fill-event audit
inside its single lifecycle pass for selected moving runs. The legacy request
causality helper and the default standalone lifecycle audit remain unchanged.
Selected events require the admitted original candidate/PREPARE/PREPARED/
ACTIVATE/ACTIVATED chain, confirmation-derived exact fill source time,
identity/hashes/generation, the matching canonical fill published by the event
time, and ordered supersession/merge evidence where both are recorded.
Cancellation or retry replies cannot mint event authority. Missing/invalid
selected lifecycle processing fails closed. Existing conditional event
occurrence rules remain: the change validates recorded events and does not
introduce a blanket requirement that every committed fill have an owner event.

Final focused **172 checks passed in46.98seconds** under the declared240-second
cap, with stable source/test pins. They include45 new authority checks,
inherited lifecycle/recording tests and actual-worker Gaussian DDS regressions.
The retained producer baseline demonstrates the original mismatch: full
lifecycle passed but an actual owner FILL_CREATED with zero legacy requests
failed source causality. Preserve that1.17second expected failure, the initial
metadata-fixture failure1.01seconds, and the redesign state-fixture failures
6fails2.55seconds; neither fixture correction changed production gates.

`typed_authority/consumer_hold_receipt_v1.json`, SHA256
`cce3136e18b70b3751bbae7e37cd59b5f310881ec14282059acb586673c95a8a`,
binds exact commands/logs, intermediate results and final three-file scope:

- `experiment_recording/validate_run.py`:
  `71b1d3636f89f59b796806fdf66e6ae12ce2af33c56efd24ae844e5653678306`.
- `experiment_recording/v2_lifecycle_validation.py`:
  `277d3ed138fcf2dcd600a476c8601655898f6f0d4c164294fe44eda3ca74a405`.
- `test/test_m4_v5_typed_fill_authority.py`:
  `b5c0dba9be131644bb27c252190f6bec5c07af58bcb3c8ea2e77b65d1dd9e4ee`.

Actual Gaussian command/result/event/canonical-fill DDS tests use a controlled
pure worker to isolate publication authority; the unchanged actual-estimator
transport regression also passes. No old bag was decoded or reclassified.

## Remaining source boundary

The primary topology routes are now held after373 expanded checks58.90seconds
and173 final dedicated checks34.44seconds. Exact receipt
`version_routes/hold_receipt_v1.json`, SHA256
`bd54f8309c75db3014a94e3bec49e51c7573dd4021c543d38e4a26ca4b0de2ad`,
retains all prior route versions and failures. Source fixtures exercised real
schema loading/expansion for16 cases with numerical/geometry operations
explicitly mocked. They include missing/wrong/cross-arm primary records and
primary qualification failure preserving partial preparation and refusing retry.
No actual primary topology qualification occurred. Six prepared driver copies
are bound by `driver_provenance_v2.json`, SHA256
`646fec32754060ef9c55eb51c22aa8f7744babf20022e6a647aeb326cd3e15cc`.
Independent read-only review found no blocker and verified unchanged schema
and numerical-owner bytes against the retained v4 source pins.

The172PASS typed-authority hold above is **intermediate**: independent
review found selected repeated-generation reply validation did not distinguish
an original activation from contradictory retry result kinds/transaction
identities. The adopted conflicting-retry requirement covers the bounded fix.
Pre-correction failures are retained: three retry-kind cases2.37seconds,
one contradictory cached-CANCEL reply1.10seconds, and two earlier-sequence
replies1.96seconds. A distinct-source fixture setup failure reused a PDE
history sequence; it is retained separately and fixed to use a new sequence.
The final selected branch requires strictly newer command sequences for
ALREADY_ACTIVATED, exact original transaction/commit identity and stable
ACTIVATE/CANCEL reply kinds. Same-sequence exact retransmission, a newer
command published before commit but handled later, and PREPARE's legitimate
terminal updates remain valid. Default standalone lifecycle behavior is unchanged.

The renewed focused group passed184 checks56.85seconds. The subsequent
strict-sequence correction passed11 affected checks7.41seconds with48deselected;
the184 group was not repeated. `typed_authority/consumer_hold_receipt_v3.json`
SHA256 `20d375708160d25ca04c263027c9f1b8e770838071d10f03da4096ec13818f49`
links all previous holds, exact source copies and failures. Final production
`validate_run.py` is unchanged from the earlier hold; lifecycle SHA256 is
`fad7df763791506af549af7bd6b68b23d1d67986b76e1bb7bfbc8db7f777db5d`,
authority test SHA256
`7a10518bbb48827e75464ef6927beedd9a3f6b8362de39bc83d7f2cc2b68c3b3`.
The actual runtime redesign fixture uses distinct epochs/candidates and
confirmation source times6s/26s; emitted creation/supersession/merge source
times6s/6s/26s pass and swapped-source events fail.

Root scope audit v2 PASS:623 current pins,608 of618 prior files identical,
ten expected prior changes and five additions. `root_scope_review_v2.json`
SHA256 `24f0f2aa924a6ddf1fbb9bfcfd01918ad4d80b596e84c4e9924429e8c1c6a57d`.
The original scope audit remains retained. Actual installed `run_scenario`
and `record_run --help` checks pass under20-second caps; no nodes start.
`actual_entrypoints_v1.json` SHA256
`6adce21164ad0deae861b932a133450573df898cebb9af3f900e559b1b150797`.

## Final integrated validation

Session51864 terminated exit0. The final suite passed **1500 unique tests in
337.01 seconds**, with one existing Gazebo E2E deselected; wrapper elapsed
337.978001067 seconds. All623 source pins match before/after and current bytes.
The source receipt SHA256 is
`4d68036db37e934c43d1dedbcedc3dcc37e40ea927aa2037a82e1a66353ba210`;
JUnit SHA256 `6be001ddaa4d70afa0b0a6beafe3c10d124032387f2f0e4def03912e33399d1d`.
Exact test argv, per-test outcomes, environment,21 installed entrypoint bindings,
source pins and log receipt are in `root_final_v1_receipt.json`. The command was:

```bash
env -u PYTHONPATH bash --noprofile --norc -c '
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q5_stationary_centroid_adapter_v1/install/local_setup.bash
export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src"
export ROS_DOMAIN_ID=186 ROS_LOCALHOST_ONLY=1
exec timeout 520s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v5_moving_fill_v1/root_source_validation.py root_final_v1'
```

The helper enforces pytest480s plus10s kill allowance. This includes the final
strict retry correction, all59 typed-authority cases, actual moving/shared
escape fixtures, final topology routes, old version compatibility and focused
recording/scenario/science/process regressions. No additional Gazebo probe was
run; historical Q1/Q2 entrypoint tests retain their original package contexts,
while the actual selected Q5 owners and CLI were verified separately.

Next: material source checkpoint/archive, one600s preparation with the real
primary topology qualification, independent frozen audit and exact release.
Numerical/schema owners, original geometry receipts, scientific thresholds
and old results remain held. These source checks establish neither faster
empirical confirmation nor improved direction accuracy/continuous recovery.

Independent read-only reviews confirmed all623 current pins, all1500 unique
JUnit/receipt identities, all59 final typed-authority outcomes, all8 version
hold pins, six copied-driver hashes and current installed wrapper bytes.
No extra tests or numerical jobs were run by those reviews.

`git diff --check`, the30s context validator and30s checkpoint tool passed.
`timeout 60s /usr/bin/python3` running the external `archive_boundary.py
m4_v5_source_closed_v1` retained366 files,199 external evidence references and
a1434455-byte verified source tar. Manifest
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m4_v5_source_closed_v1/manifest.json`
SHA256
`35329d0a6fd68d813797a9e7328877581d8eadc5003efd2c42e3a2281844fe26`.
This receipt was appended after the immutable archive; no pinned source changed.

## Single preparation and frozen audit

Session98742 terminated0: the one preparation passed52.284768937s inclusive
wrapper (task50.917849472s) inside600s. Same clean environment as above;
outer `timeout 600s /usr/bin/python3` ran external `run_preparation_v1.py`.
The helper used SIGINT590s/kill-after5s for `m4_workflow.py prepare --version
m4-pilot-v5`. Exact command/log receipt is `preparation_v1_receipt.json`, SHA256
`fdcbb1400d34b0df5219c9e43d51ded2b58257ad0abb8629bbfd1194fc56aec8`.
No retry, separate geometry derivation or independent numeric rerun occurred.

Fresh `pilot/m4_pilot_v5/preflight/contract.json` SHA256
`42a7b57afcec26e8e4b643cacc0d71895e037c7b3129cb66cd37e26d0580f08e`;
`prepared.json` SHA256
`4f7bad4d9bdbb32a07c1e7af09083015ac754625c67706d8fcde287db818d695`.
The unchanged numerical/schema owner admitted all16 cases and four topology
records. Primary exact source hash30f4d514...a8c9, original start/bounds and
nominal disturbances bind `topology_primary_nominal.json`, SHA256
`a1e37d2cdf576bff2f93d6646fc4d365c1c9ba90ca091b562bfd6652505bab06`.
This is the existing finite static topology contract; the retained local
optimizer success flag is false for all four records. Admission follows the
unchanged finite numerical/geometry thresholds, not a claim of optimizer
convergence or certified attraction dynamics. The Gaussian noise margin remains
the3sigma simulation convention; delay receipts do not certify delayed dynamics.

Session25341 terminated0: one `timeout 60s /usr/bin/python3` invocation of
external `frozen_audit_v1.py` passed3.061765128s. It performs no load_suite,
field evaluation, bag decoding or ROS startup. All623 pins match final source
validation/current bytes; exact16 argv, shared controls, selectors, original
geometry/recovery receipts, four topology bindings, installed owners/wrapper
and all budgets match. `preflight/frozen_audit_v1.json` SHA256
`27ab78221405ffc61fb225694ba482aad99d7a770da4ef3c84d92f66f103f19e`.
Next: preparation checkpoint/archive and exact dispatcher release. No
acquisition has started; both research targets remain unestablished.

Preparation context/diff/checkpoint PASS. Material preparation archive SHA256
`557397cd2d94526c12139bd1c95b23a41ae19e46c28c2d4f374f2aa28700ddbb`
binds366 files/214 artifacts/1435978-byte verified tar. Independent read-only
preparation review verified all623 pins, four records and5730 original geometry
point-file hashes without numerical evaluation. Exact release passed the public
release validator (session91644 terminal0,30s cap), SHA256
`c4b5038975acc7b9c71b1eaab4731a17f24fd7c081b1edb748f09bed9eba3853`.
The single acquisition command, in the same clean environment, is:

```bash
timeout --signal=SIGINT --kill-after=120s 15180s /usr/bin/python3 /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/tools/run_m4.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v5/preflight/contract.json
```

Console is exclusively created at external
`builds/m4_v5_moving_fill_v1/acquisition_dispatch_console_v1.log`.
Read fresh started/slot/final receipts before recovery; never start another
dispatcher. Source remains held. Development science, the one-time holdout
release and research acceptance remain separate from source/preparation PASS.
