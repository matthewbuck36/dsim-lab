# M4v14 preparation and execution

Plan: [M4v14](../m4_v14_retained_development_comparison_plan.md).
Source validation COMPLETE:776passing cases,1170stable pins,21entrypoints;
independent review PASS and681-member source archive verified. See
[m4_v14_source.md](m4_v14_source.md).

External work: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v14_source_v1/`.
Exclusive pilot: `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v14/`.

Sole preparation session70240 terminal/reaped0 in50.523521829s under600s inclusive.
Root command: timeout --signal=INT --kill-after=5s 595s; env -u PYTHONPATH
-u RMW_IMPLEMENTATION, PYTHONDONTWRITEBYTECODE=1, OPENBLAS_NUM_THREADS=1,
OMP_NUM_THREADS=1, MKL_NUM_THREADS=1, MPLBACKEND=Agg, ROS_DOMAIN_ID=201,
ROS_LOCALHOST_ONLY=1, DISPLAY=:0; bash --noprofile --norc sources the retained
R21 `runtime_environment.sh`, then exec /usr/bin/python3 -B V14 `prepare_once.py`.
Actual preparation receipts: `preparation_v1/{started,receipt}.json` and pilot
`preflight/{started,retained_development,contract,prepared}.json`.
Contract SHA256 `f34a2740cda331f2dbb6f363e0364db988f2d2c5928b3f376fae4a6bea289cf9`.
All1170validation pins remained unchanged;1157pins are bound by the new contract.
Root cached audit confirms exact first4original full plans, equal qualified
topology JSONs,12fresh plans andseeds26091152/53/54. No acquisition directory.
Independent preparation review pending; no new simulation or dispatch.

Sole cached development session51764 RUNNING under60s inclusive (55sINT+5skill).
Same runtime environment, exec V14 `cached_development_once.py`; calls the
existing `prepare_retained_development` once with absolute55s deadline. It
retains original4measurements and composes only the declared C/D motion fields.
No bag/model/reference/labels replay or dispatch release. Receipts will be at
`cached_development_v1/{started,receipt}.json` and pilot `analysis/block_0/`.

## Cached development QUALIFIED

Sole51764 terminal/reaped0 in11.635228834s inclusive; existing composition
owner4.359544728s. All1175source/input pins stable, before/after exact.
Execution receipt SHA256 `6f74ab75c2acb72c1d34064dea361f9626a9b337453d6527a3dd67b2b47681c1`.
Qualification SHA256 `21058f11685b30d28ba4d9e827b5c0dc4152b91bdf9f041d744431aa60d494e0`.
Block receipt SHA256 `a044a07233bbf49828b3713f115f06791de02721fc2968923387d7f3599c47f8`.
Reuse receipt SHA256 `ba7c5d7a8acca428dfd3a4a138ca1c00bbc5b71d9d4fc3b248deb935596e22b0`.
All four scientific measurements complete; both B/D valid recovery and arrival;
D continuous acquisition/zero mandatory stops and direction PASS (median12.519443,
P9025.224003,4/4eligible; all24scheduled targets preserved). No new acquisition,
scientific replay, jobs or dispatch release. Independent preparation and retained
qualification reviews are pending; require exact contract/qualification references
before public release. All jobs are terminal. Twelve new configurations are frozen
but unattempted. Full goal and original independently labelled latency target open.

## Independent review and launch readiness

Preparation review PASS50checks in0.566416s:
`preparation_review_v1.json`, SHA256
`6d0c512d3bc57c169b6533e72ee0ef6b159c39dae792831f289b80da649e0de6`.
Retained development review PASS107checks in0.692s:
`retained_development_review_v1.json`, SHA256
`342fde49875f97a6370c1b1aa7ba58e408511ef59b2c7888d4d98ce7529cc424`.
All1175 cached source/input pins stable; original plans/acquisitions and48targets
preserved; exactly permitted motion substitutions; required B/D arrival and D
continuous/direction gates PASS; original failure and fresh12 unattempted verified.
No tests/science/bags/models were rerun by either review.

The existing V13 external helpers are adapted for one V14 dispatch:
`archive_preparation.py`, `release_dispatch.py`, `acquire_once.py`. Root reviews
actual code and provenance before use. The public release binds both reviews,
qualified cached block and exact acquisition driver; initial slots5through16.
The acquisition wrapper retains exclusive owner/console/execution receipts and
strict driver/version/slot checks. Same GNU timeout SIGINT15680s+120skill grace,
15800s maximum, no retries or substitutions. No runtime/analysis owner edits.
After the preparation archive this document is frozen; live execution updates
belong in `m4_v14_runtime.md`, status and fresh handoff.
