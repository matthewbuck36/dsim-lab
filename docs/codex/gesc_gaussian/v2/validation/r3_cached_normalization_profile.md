# R3 cached C normalization profile

PASS, 2026-09-10. This is the one diagnostic specified by
[the prospective plan](../r3_cached_normalization_profile_plan.md), after the
full four-bag benchmark timeout. No production source changed for this work.

Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/cached_c_normalization_v1/`.
The exact commands are `preparation_command.sh` (30-second bound) and
`dispatch_command.sh` (55-second outer bound). Preparation completed in
0.976 seconds and read no cached input bytes. The existing finite job owner
ran one child under its 45-second inclusive cap and 3-second cleanup reserve.
It completed normally in 11.420597 seconds, exit0, with no remaining owned
processes, clean termination, integrity passed, and all 75 source pins plus
input filesystem identity unchanged. The run followed the terminal visible02
analysis and its separate reference job.

The child read the retained 89986365-byte C normalized JSON once and verified
its unchanged SHA256
`0dd3c204e0e34f2d96574a995c0bb33b706130ad4791b63eefd8816abe013f17`.
It called the existing `normalize_direction_targets` once with all 10605
observations and their exact original arguments. Full returned-document
equality passed; the original in-memory bytes and observation receipt remained
unchanged. No bag, reference/model, upstream validator, or labels job ran.

| Measured component | Seconds | Calls |
| --- | ---: | ---: |
| Cached read plus digest | 0.214449 | 1 |
| JSON decode | 0.755381 | 1 |
| Entire normalization with cProfile | 7.809648 | 1 |
| `deepcopy` inside normalization | 6.045444 | 2 top-level; 4146589 recursive |
| Canonical observation SHA | 1.186749 | 1 |
| Direction supplemental metrics | 0.485726 | 1 |
| Fixed causal anchor selection | 0.082743 | 24 |

The nested timings include deterministic profiler overhead; they are not an
uninstrumented baseline and must not be subtracted from the earlier C analysis
time. The retained `normalization.prof` and 45-row cumulative function table
identify recursive copying as this isolated call's main measured cost.
They do not show that copying explains most of C's original 42.593500 seconds.
That interval also includes full-stream lifecycle and source validation,
objective/direction extraction, labels publication, and other outcome work.
The 89.99 MB normalized JSON publication was outside that earlier interval.

No copy removal or cache is adopted. Such changes require explicit detachment,
canonical-output and invalid-input parity tests. The next useful performance
diagnosis, if needed for comparison release, is nested timing of the existing
upstream owners on one loaded C bag: lifecycle validation, source validation,
policy companion indexing, objective snapshots and direction extraction.
Retain one actual read and reuse its in-memory union. The cached normalized
document lacks the complete source streams and cannot replace that validation.
The failed four-arm benchmark remains unchanged; this profile does not release
another comparison.

Receipts: `result.json`; `job.json` SHA256
`4720622b4c63650440d85b633b786d0fab63d1295f56d284428aa536c95176b9`;
`profile_result.json` SHA256
`9d1547b7e070333d808e3d778eea20855e8f782d4f6c8db406afac7bf872225b`.
Helpers, pinned manifest, command files and complete logs are retained beside
them. The 30-second V2 implement context validator passed before file creation.
