# M4 v6 closed-development diagnostic validation

Status: `DIAGNOSTIC_ONLY_COMPLETE`, 2026-09-10 UTC. The single authorized
extraction of each closed M4v5 B/C/D run completed successfully. This explains
B's recorded threshold failures and reproduces D's recorded publication-gap
failure. The specific last M3 evidence rejection in C/D remains unavailable.
M4v5 remains `CLOSED_INCOMPLETE`; both original research goals remain unproven.

Authority: [adopted diagnostic plan](../m4_v6_development_diagnostic_plan.md),
SHA256 `78521523d588e7721662f7754ed168aff7fc0769a279466a7fb1495ea4b701f0`.
All source and evidence remained held throughout the diagnostic. There were
no repository source edits, ROS initialization, simulator launches, numerical
evaluations, parameter sweeps, scientific endpoint jobs or retries.

## Inputs, aliases and preservation

External experiment root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Diagnostic directory, abbreviated `DROOT` below:
`builds/m4_v6_development_diagnostic_v1/` under that root.

Original closed runs are under `pilot/m4_pilot_v5/runs/2026-09-10/`:

| Arm | Exact run directory | Selected records |
| --- | --- | ---: |
| B | `m4-pilot-v5-slot02-B-26090801` | 39,661 |
| C | `m4-pilot-v5-slot03-C-26090801` | 64,473 |
| D | `m4-pilot-v5-slot04-D-26090801` | 72,711 |

The existing `read_run_bag` and `records_for_alias` owners decoded each run
once. Selection was checked against its closed resolved manifest and bag
metadata before reading; decoded counts matched metadata exactly. Every stream
was below 40,000 rows and every run below 160,000 rows. The 176,845 selected
records retain full generated-message payloads and original bag, publication
and source timestamps with validity flags. Compressed JSONL files preserve
explicit `__nonfinite_float__` tags for NaN, Infinity and negative Infinity;
no observation arrays were truncated.

Common aliases were `algorithm_events`, `algorithm_state`, `recording_ready`,
`clock`, `timekeeper` and `pose`. B/D additionally retained
`centroid_convergence_diagnostics`. C/D additionally retained
`v2_search_epoch`, `v2_detector_confirmation`, `v2_direction_diagnostics`,
`v2_candidate_snapshots`, `v2_fill_commands`, `v2_fill_results` and
`v2_source_provenance`. Direction counts were C 17,820 / D 17,840; provenance
counts were C 10,606 / D 10,618. These full payloads retain inputs for a later,
separately bounded existing-owner investigation.

B's stationary route had no epoch publisher, subscription or recorded epoch
topic. Its explicit `NOT_PUBLISHED_IN_STATIONARY_ROUTE` manifest record is
retained in `alias_preflight_v1.json` and `B/aliases_v1.json`; no epoch was
invented. C/D candidate, command and result topics existed in the recorded
metadata with zero messages; their full applicability metadata is retained.

All 623 source pins matched the original final M4v5 source receipt before,
after and at exit for each extraction. The same three checks verified each
run's 11 original files, including its closed bag: 33 disjoint original files
in total. No original was rewritten, reindexed or reclassified. Exact proofs
are each arm's `hashes_before_v1.json`, `hashes_after_v1.json` and
`hashes_exit_v1.json`, bound by `diagnostic_hold_v1.json`.

## Commands, fixtures and finite execution

The executed commands, from the repository root, were:

```bash
timeout --signal=SIGINT --kill-after=2s 43s python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_development_diagnostic_v1/run_fixture_v1.py
python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_development_diagnostic_v1/run_extract_v1.py B
python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_development_diagnostic_v1/run_extract_v1.py C
python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_development_diagnostic_v1/run_extract_v1.py D
```

These are retained execution history, not instructions to repeat the attempts.
Exact child argv and environment are in `fixture_command_v1.json` and
`B_command_v1.json`, `C_command_v1.json`, `D_command_v1.json`. Each uses
`env -u PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`, then sources Humble,
`q2_policy_runtime_v1/install/local_setup.bash` and
`q5_stationary_centroid_adapter_v1/install/local_setup.bash`, in that order.
It appends `/home/mattb/dsim-lab/extremum-seeking/src` to `PYTHONPATH` and sets
`ROS_DOMAIN_ID=186`, `ROS_LOCALHOST_ONLY=1`. No ROS graph is initialized.

The fixture had one 45-second allowance. Its retained log reports 10 tests
PASS in 0.319 seconds; the wrapper took 1.149968581 seconds, with 623 source
pins and three helper/fixture/driver pins unchanged. Fixtures exercised full
generated direction and nested candidate payloads, nonfinite values, validity
and transition preservation, strict threshold boundaries, optional-topic
absence, row caps, exclusive output creation, timeout handling, and the
unchanged coverage owner's entry/internal/exit and duplicate-stamp semantics.

Each extraction had a 60-second execution plus 10-second exit/hash allowance.
The wrapper imposed a 70-second absolute alarm, SIGINT at elapsed 59 seconds,
forced exit at 68 seconds, and reserved final time for the outer receipt.
No timeout or forced exit occurred. All outputs used exclusive filenames.

| Attempt | Return code / outcome | Bag read seconds | Inclusive wrapper seconds |
| --- | --- | ---: | ---: |
| Fixture | 0 / PASS | Not applicable | 1.149968581 |
| B | 0 / `DIAGNOSTIC_ONLY_COMPLETE` | 3.949783542 | 12.545025209 |
| C | 0 / `DIAGNOSTIC_ONLY_COMPLETE` | 8.599267877 | 23.317407830 |
| D | 0 / `DIAGNOSTIC_ONLY_COMPLETE` | 9.466374875 | 25.475240903 |

Total fixture plus three inclusive extraction times: **62.487642523 seconds**
within the approved 255-second maximum. Per-arm execution receipts include
child exit and output-hash processing; raw logs and child receipts are retained.

## Recorded findings

B retained 10,718 centroid diagnostics. Of these, 217 were outside readiness,
1,059 had invalid history during readiness, and 9,442 had valid computed score
and confinement values. All 9,442 failed the unchanged strict score test
`score_m < 0.18`: recorded finite scores ranged from 0.289676733 to
1.020874251 metres. Among those valid histories, 8,206 passed radius
`<= 0.5 m` and 1,236 failed both tests. No diagnostic was eligible or confirmed.
This distinguishes a computed score failing its threshold from unavailable
history. `metric_valid` and `confinement_valid` mean computability, not threshold
acceptance. Exported numeric ranges cover all recorded messages; eligibility
categories are readiness-scoped. B had no coverage violations under the
unchanged owner.

C recorded four confirmations. Its recorded VERIFY entries were at 71.0,
151.3, 231.7 and 312.0 simulated seconds; SEARCH returns were at 82.9, 163.2,
243.6 and 323.9. Each return's recorded reason was
`moving candidate cancelled; resume search`. No candidate snapshot, fill command
or fill result was recorded. The generic reason does not identify the last
unrecorded M3 evidence guard or prove callback timing.

D recorded seven confirmations, six generic cancellation returns to SEARCH,
and zero candidate snapshots, fill commands or fill results. Its 8,171 centroid
messages included 13 outside readiness, 7,426 invalid histories during
readiness and 732 valid histories: 530 failed both thresholds, 176 passed only
the score test and 26 passed both. Seven messages marked confirmation.

The unchanged `centroid_stream_errors` owner, using recorded `/clock` at the
bag-order readiness boundaries, reproduced D's original error:
`centroid diagnostics have a simulated publication coverage gap`.
The one-second threshold was unchanged. All publication intervals, including
entry and exit, are retained in compressed JSONL; the seven violations are:

| Left publication, simulated seconds | Right endpoint, simulated seconds | Gap seconds |
| ---: | ---: | ---: |
| 62.4 | 74.4 publication | 12.0 |
| 110.5 | 122.5 publication | 12.0 |
| 158.6 | 170.6 publication | 12.0 |
| 206.7 | 218.7 publication | 12.0 |
| 254.8 | 266.8 publication | 12.0 |
| 302.9 | 314.9 publication | 12.0 |
| 351.0 | 360.6 readiness exit | 9.6 |

These intervals coincide descriptively with recorded VERIFY periods. The
summary retains adjacent diagnostic indices, bag/publication timestamps and
latest recorded states. Bag adjacency cannot establish callback order or
runtime causality. Invalid-history publications still count as observations
under the original coverage owner; the diagnostic did not narrow coverage to
SEARCH or relax the completeness gate.

## Evidence receipts and closeout

All paths in this table are relative to `DROOT`, except those marked otherwise.

| Evidence | SHA256 |
| --- | --- |
| `diagnostic_hold_v1.json` | `42e32d584ed83aeab934ac5d2739cf2451af2ca0707b4e2909a14f93f6b2be24` |
| `diagnostic_result_v1.json` | `67a7138755429f39f9ef58e93d6763dc4034a29e295dc3b3224514cf31754104` |
| `extract_v1.py` | `06cc810f2f907486224a22107df69a71705bf00ca71047ac70e6801d5a2c8e6c` |
| `test_extract_v1.py` | `e768f0fae6fd5fe078b2717e0a79fb0dc09466ab4085e4ecebe2d85bedd17de9` |
| `run_extract_v1.py` | `4b62eefc8fd0460e641583aea9df15cbbf884f4b0331f67837d0ad355686d574` |
| `fixture_receipt_v1.json` | `b4d6f7f2e287409b8fce7e503efc176e6d8ea97e398a3c9ad5382491f6102e2c` |
| `alias_preflight_v1.json` | `80c80982e07d3bc94f39ff95f156c566e35cc85783e789d8c5bf8d21e1b36dc7` |
| `helper_provenance_v1.json` | `ca95aaf515c24b335610af455b5074fef025b93381f3e942e1c4b14743eb44ae` |
| `B/receipt_v1.json` | `021914a1fb984c93653c0082fd55669bda8728c2399104f285cba483ef973a60` |
| `C/receipt_v1.json` | `4fd6d22fffaceacf202bce35ede21be186372ee551c3f6120ec3c659469fe9a5` |
| `D/receipt_v1.json` | `e3bd954aa0257e7cf1e29080c9696cc85c2aded021af028d8d876938f3946234` |
| External `builds/m4_v5_moving_fill_v1/root_final_v1_receipt.json` | `4d68036db37e934c43d1dedbcedc3dcc37e40ea927aa2037a82e1a66353ba210` |
| External `builds/m4_v5_moving_fill_v1/pilot_closure_audit_v1.json` | `b4b7f13c5250ef8243e8c5a7205d38f2ee94c6cce899ae22cd72d464968bd109` |
| External `checkpoints/m4_v5_closed_incomplete_v1/manifest.json` | `e8d66d8f801f96a0223ef19aa2658f9fc73921f57a030d9b3fa759f09a334a12` |

The hold receipt also binds exact fixture/extraction wrapper commands and logs,
per-arm summaries, all full-output hashes and the before/after/exit equality
proofs. Documentation closeout rehashed the 84 distinct file references in the
hold/result receipts and separately checked the original closure audit and
archive-manifest references. It reused the completed 623-source/33-original
equality proofs without reopening or rehashing original bags. Reference checks
and `validate_phase_context.sh v2 implement` passed.

The result is descriptive evidence from a failed development attempt. It
establishes neither the approved settling/trapping improvement nor the moving
direction target; it does not release holdouts, replace runs or qualify the
16-run comparison. Any correction or further existing-owner reconstruction
requires its separately saved scope and bounds. All retained M4v1–v5 evidence,
legacy selectors and the original research denominators remain intact.
