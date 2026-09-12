# Visible03 analysis: reuse the prepared existing-owner job

PROSPECTIVE 2026-09-10 while root owns active visible03. Preparation only: no
active bag or run metadata read and no production source changes. Root must
supply terminal readiness/completeness/cleanup status and explicitly release
the job before dispatch. The finite component96 job is already terminal.

Reuse the unchanged helper
`development/20260910/visible_integrated_01/analysis/run_analysis.py` under the
[original generic analysis plan](r3_visible_analysis_01_plan.md). The fixed
new identity is `v2_method_development_D_20260910_03`; its input directory is
`development/20260910/visible_integrated_03/runs/2026-09-10/v2_method_development_D_20260910_03`.
The output is new exclusive `visible_integrated_03/analysis_v1/` and the log is
`visible_integrated_03/analysis_execution_v1.log`; both must be absent at dispatch.
The helper location records preparation lineage only; metadata/run IDs must
match03 exactly. Attempt01/02 data and results remain unchanged.

Keep118s SIGINT plus2s kill-after and110s internal deadline. Use the generated
`centered_runtime_v2/environment.sh` with inherited PYTHONPATH removed, prepend
the current repository Python package and set MPLBACKEND=Agg. The helper's two
unchanged native decoder scans remain mandatory: analysis.read_run_bag and the
analyzer-owned completeness validator read. All additional typed exports,
command-zero summaries, rejection reasons and direction normalization reuse
the captured first BagData. No third scan, alternate reader or validator bypass.

The source held by acquisition now includes the separately corrected recurrent
support-endpoint evaluator association and prospective arrival-only acceptance.
Use the current existing analyzer as frozen, with its exact source/config/input
pins and resulting status. Global arrival is the user's success criterion;
GOAL_HOLD is not required. Do not force an unavailable analyzer metric to pass
or reinterpret02's original fixed verdict. Report acquisition's arrival result,
native analysis integrity and typed lifecycle status separately.

Retain full canonical typed streams, all command zeros and explicit reasons.
The existing normalization still has24 fixed targets15+30k seconds, actual
source exposure, honest m4-pilot-v1 protocol reuse and DEVELOPMENT_ONLY wrapper.
Any observed GOAL_HOLD timestamp remains that normalizer's existing optional
terminal censor, not an added requirement for successful arrival.

Save helper/environment/plan hashes and literal command in
`visible_integrated_03/analysis_prepared_v1.json` before release. At dispatch
the unchanged helper additionally pins actual acquisition/source metadata and
raw bags before its readers run. Preserve errors and partial outputs, count
the two scans, verify hashes after completion and notify root/direction agent
when exports exist. No unchanged retry after timeout or failure.

The separate <=45s reference-only helper remains prepared but unreleased until
root reviews normalized input integrity. It uses the fixed24 target schedule,
actual selected sensor/cost configuration and unchanged evaluator-only model;
no runtime truth or retuning. Validation goes in
`validation/r3_visible_analysis_03.md` after the released job, with exact command,
timing, denominator, lifecycle and arrival limitations. Root owns status/handoff.
