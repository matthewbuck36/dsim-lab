# M4v12 source validation

VALIDATED source boundary; V12 later closed incomplete on empirical execution.
See the accepted source boundary below and [closeout](../m4_v12_handoff.md).

Original prospective entry (historical): PENDING, 2026-09-11 UTC. Adopted scope: [plan](../m4_v12_integrated_comparison_plan.md).
Existing scenario/schema, science and workflow owners only; no algorithm tuning.
Evidence root `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v12_source_v1/`.
Before copies, exact owner patches/readiness receipts and adapted V11 orchestration
helpers are retained there. One explicit34-selection bundle is reserved in
`tests_v1.json`,230s work plus5s termination,260s inclusive. No source tests,
preparation or comparison have executed yet.

Context validator `timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement` PASS.
Branch `feature/gesc-gaussian-robustness-v2`,HEAD `3369cfc83a64ff5d8354827fd5310caaf0c8e945`;
task changes remain uncommitted. No physical/Pi/snapshot/V1/commit/push actions.

## First bundle and bounded test-selection correction

The sole full source bundle finished/reaped session80546 with exit1 in
179.030068s:784passed,2failed,0skips; all source pins and21 installed entrypoints
remained stable. Failures are exclusively the historical V2/V3 evaluator
allowlist fixtures expecting `m4_pilot_v12` to be rejected, now a supported
version. Their exact failure records remain in `focused_v1/source_validation.json`
and pytest logs/XML. No production failure occurred in this bundle.

Prospective bounded correction: change only those two fixture sentinels to
`m4_pilot_v13`; retain current production behavior. Re-run only their two
parameterized test functions under60s inclusive. Preserve first bundle and
bind its784passing cases plus the named correction into downstream preparation.
Adapt existing preparation/release/archive receipt paths to `focused_v2`; no
new numerical owner or complete-bundle repeat. Root orchestration copies and
source delta will be retained before the correction. No preparation/simulation
is authorized by a failed source receipt.

## Accepted source boundary

Correction session8562 terminal/reaped0:10/10parameterized checks passed in
2.876825184s;866source pins and21installed entrypoints stable. This
reruns the two corrected functions only;8cases overlap the original784passes.
The original2stale-sentinel failures remain preserved. The final786-case
selection is covered by the original unaffected passes and the10-case rerun.
No skips. Exact current source delta is the declared two test files and three
receipt-selector helpers; tests_v2.json is the only added pin. No production
source changed after the full bundle.

Corrected receipt `focused_v2/source_validation.json` SHA256
`f67c9721bc1deb647a0c9083cdcd96a76e737f7533c112949a5897dada1e1621`. Original receipt SHA256
`f4094dde77c05b2ba96754e6fbff8a04feb18174d2de955411e3d3e09f99ee1f`.
Preparation explicitly verifies that original receipt and exact delta before
using the corrected source pins. Owner cross-reviews and root workflow review
passed; fixture/orchestration correction review is retained separately.

Exact validation invocation: clean PYTHONPATH/RMW_IMPLEMENTATION, domain201,
localhost1,DISPLAY:0; source the selected stationary_recurrent_pairing_v1
`runtime_environment_v2.sh`, then `/usr/bin/python3 -B` on external
`validate_source.py --version focused_v1 --tests tests_v1.json` inside
`timeout --signal=INT --kill-after=5s 255s`; the correction uses
`--version focused_v2 --tests tests_v2.json` inside the same timeout with55s.
The driver receipts/logs retain exact pytest child argv and per-case outcomes.
No Gazebo acquisition, retained bag decode or numerical reference replay was
performed by source validation. Next:material archive then exclusive preparation.
