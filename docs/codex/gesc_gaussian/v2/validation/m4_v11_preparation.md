# M4v11 frozen preparation

PREPARED and independently reviewed; dispatch release pending.
Authority: [V11 plan](../m4_v11_draft_plan.md). Source validation676 unique
checks PASS160.293120s,806 stable pins/21 entries; source archive580 members
verified0.942779s,manifest SHA256
`1772d7d15c749e4d9c4ed724a901f137a34f56f4339a43918212ba63415c0dbf`.

Sole preparation command from repository root:

```sh
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 595s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/prepare_once.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/preparation_outer_v1.log 2>&1'
```

Session66863 terminal/reaped0. Preparation PASS54.797725867s under600s total;
all806 source/test/helper/input pins stable. Source-selection receipts797;
21 installed entry bindings. No acquisition. Receipt
`development/20260910/m4_v11_source_v1/preparation_v1/receipt.json` SHA256
`df2471dc87effdbf1d98d3a564b149a0a379985dfb384ad8a92ea13fea84a81e`.
Paths are relative to `/home/mattb/Experiments/GESC-Gaussian/v2/`.

Frozen `pilot/m4_pilot_v11/preflight/contract.json` SHA256
`3b1a4b5de2ee1eb5a9352561732cb349788f46f14dc8a4b7b0a776f5175b18ba`.
Identity m4-pilot-v11/methodrecurrent_arrival_v11;16slots A/B/C/D eachblock;
fresh seeds26091021..24, four visibleprimary development then12secondary
confirmation slots on exposed geometries. Existing startup recovery selected
for everyarm. Existing V6controller and detector/direction methods preserved.

720s recorder/900s case/45s shutdown/30s cleanup;240s labels+2x45sreference+
10ssummary perblock,40sfreeze/report.1400sscience and15800ssuite maximum.
`usable_four_arm_analysis_v1` plus V11 both independently eligible observed
development latency pairs must release12confirmation slots once. Arrival0.5m
sufficient; GOAL_HOLDoptional. All earlier failed attempts/versions retained.

Independent scenario/workflow audits will be saved externally and pinned in
preparation archive before dispatch. Filesystem has246GiB available; no ROS/
Gazebo/test application was active after preparation. Shared domain201 daemon
is not experiment-owned and is preserved. No commit/push/physical/Pi/snapshot/V1.

## Frozen scenario review

Independent scenario review PASS193checks,820current/stable input hashes.
Canonical `scenario_frozen_audit_v1.json` has audit_revision2,SHA256
`ef9ab5bc3e6cd0c712ecf1db459e9640795d81e806b57966fb25a378e029155e`.
Initial comparison produced8failures because the audit omitted the authorized
moving `v2_run_id` difference from V10 parity normalization. Every actual value
matched its independently constructed V11run ID. No scenario/helper/source fix
was required. Exact initial bytes remain at
`scenario_frozen_audit_initial_failure.json`,SHA256
`a8bf767cd13e8a786531e7971ba7abdb06e0767c74de87aa152093c79c4e29ae`;
canonical revision2 explicitly links that receipt and records all8failures/cause.
Root independently checked all8moving run-ID arguments. This was an unfrozen
comparison-audit correction; no historical scientific verdict was changed.
Workflow audit still pending at this record boundary; no dispatch yet.

Independent workflow review PASS17checks;canonical
`workflow_frozen_audit_v1.json`SHA256
`288e1f8f39bbd8e1acc9e4bc3df451559e0ebfe5594a539955fa41b9e88dd451`.
Verified797source pins coveredby806validation/preparation pins and allcurrent
late hashes,21installedbindings,48runtimefiles,heldhelpers/testlist,16commands,
12untouchedconfirmations,exactsciencecaps,strictcleanup/shareddaemon andV11
recomputedpaired-feasibility release. Hash parser0.388s;no project execution.
Both frozen audits PASS. Preparation archive and dispatch release follow.
