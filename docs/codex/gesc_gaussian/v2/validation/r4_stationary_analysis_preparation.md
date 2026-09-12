# R4 stationary development01 analysis preparation

PREPARED, UNDISPATCHED, 2026-09-10 under the
[integrated plan](../r4_stationary_integrated_01_plan.md). No bag read, analyzer
execution, reference calculation or production change was performed here.

The retained helper is
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_01/analysis/run_analysis.py`,
SHA256 `199e5d5fefb87b7bb266cfc192c509b890a44e6c5d36bc5d4d578790ea0bcd45`.
Its sibling `preparation.json` records successful AST parsing and static checks:
one native `analyze_run` call, no moving normalization/reference or extra reader.
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
passed before preparation. The helper itself was not imported or executed.

Admission requires the exact declared B run, recorded recurrent stationary
selection, stored recording completeness, matching terminal acquisition receipt,
passed owned cleanup, stable acquisition source and root deadline compliance.
The helper pins selected loaded source, generated message/CDR bindings,
environment, acquisition receipts, recorded metadata/scenario and raw bag bytes.
It wraps the two existing readers only to count and time their unchanged calls.
The native analyzer keeps its independent fresh validation, late raw hashes and
atomic output publication. Helper late source/input hashes remain inside110s.

Success requires native complete analysis, stored and fresh complete recording,
valid `stationary_recurrent_pipeline` without errors, all four native stationary
tables, exactly one analyzer decode plus one validator decode, and stable pins.
Partial/invalid results retain their actual statuses and fail the helper exit.
Zero request counts remain zero; they are not behavioral acceptance. Recorded
arrival remains in `scenario_result.yaml`; native `convergence_time` retains its
GOAL_REACHED meaning. No moving exports or references are added.

After complete acquisition and terminal cleanup, use the actual retained run
directory from the scenario result. For the expected dated path, the exact
prospective command is:

```bash
timeout --signal=INT --kill-after=2s 118s env -u PYTHONPATH bash --noprofile --norc -c '
source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/environment.sh
exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_01/analysis/run_analysis.py \
  --run-directory /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_01/runs/2026-09-10/v2_method_development_B_20260910_01 \
  --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_01/analysis_v1
' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_01/analysis/analysis_v1.execution.log 2>&1
```

The output root must not already exist. The work alarm is110s; the outer bound
includes environment setup and final receipt handling, with SIGINT at118s and
forced termination two seconds later. Preserve the log and any partial artifacts
on timeout; no unchanged retry is authorized. A result validation record must
report actual scan counts, elapsed time, integrity and observed stationary events.
