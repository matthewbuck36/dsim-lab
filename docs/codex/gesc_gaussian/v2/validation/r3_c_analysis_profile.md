# R3 single retained C analysis profile

PASS, 2026-09-10, under the saved
[single-C profile plan](../r3_c_analysis_profile_plan.md). No production source
changed for this diagnostic. The original 120-second full four-bag benchmark
remains FAILED/TIMEOUT; no historical job or result was rerun or promoted.

Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/c_analysis_profile_v1/`.
The exact `preparation_command.sh` has a30-second bound and
`dispatch_command.sh` a100-second outer bound. Preparation took1.498632 seconds,
bound99 source files and11 small inputs, and opened no bag or cached normalized
bytes. It followed the runner correction's terminal source/test release.
Existing `finite_science_job` ran one child under90 seconds inclusive with its
original3-second cleanup reserve and `subreaper_group_v3` ownership.

The child completed normally in63.829282 seconds, exit0, clean termination,
integrity passed, no remaining owned processes, and unchanged source/input
identity. Existing `_acquired` checked the original C input SHA receipts. There
was exactly one declared C bag decode through `read_run_bag`, followed by exactly
one `analyze_run_data` using that returned BagData. No other bag, reference/model,
simulation or full labels block ran.

Full normalized output equality against retained C passed for all10605
observations and the complete document. New label bytes matched the retained
label SHA. Existing late label-byte receipt checks also passed. The normalized
observation SHA remains
`f638a71b9e708d60fe28b85f494796ccd1efe8af88f4767a8c7833d5e4339175`.
Only labels, actual metrics, compact topic counts/timings and parity results
were published; no duplicate full normalized export or alternate pipeline was
created.

## Measured costs

| Existing owner/component | Seconds | Calls |
| --- | ---: | ---: |
| Full acquisition receipt checks | 0.779303 | 1 |
| Selected C bag decode | 15.908000 | 1 |
| Complete `analyze_run_data` | 41.942739 | 1 |
| Independent label analysis | 3.372750 | 1 |
| Lifecycle stream validator | 17.601921 | 1 |
| Direction-input preparation | 16.201659 | 1 |
| Source-stream validator within preparation | 8.271282 | 1 |
| Normalization | 4.258609 | 1 |

Nested rows must not be added to their parent costs. The41.94-second analysis
closely reproduces the earlier42.59-second C interval. All thin-wrapper
overhead is included; there was no deterministic profiler in this job.

The lifecycle validator's20902 canonical payload hashes took7.830542 seconds;
these include PDE history and observation hashes. Detaching3111 PDE history
messages took4.332879 seconds. Across both validators, the same static stream
descriptor/origin was revalidated and hashed141776 times, taking4.708744
seconds. Policy companion indexing happened twice (1.254115 and1.217861
seconds), while17819 actual policy pair checks took1.684926 seconds.
Objective snapshots took1.079105 seconds for10605 rows. The88 top-level
`deepcopy` calls across labels and normalization took2.706125 seconds; the
earlier cached profile's6.05-second copy timing included cProfile overhead.
Supplemental direction metrics took0.222245 seconds and fixed anchors0.039114.

## Decision and prospective budget advice

Do not implement an optimization now. A small plausible future correction is
to bind one validated, detached stream descriptor/origin per offline validator
invocation and reuse its expected contract digest in the existing envelope
owner. Every schema/run/frame/stamp/origin/digest check must remain; malformed
descriptors and cross-run isolation need focused parity tests. Avoid global
or object-identity caches. The measured repeated hashing supplies an approximate
4.7-second maximum C saving, not evidence of an implemented speedup.

Mandatory work remains: complete acquisition/input hashes, selected bag decoding,
pose labels, full PDE/observation integrity and source joins, repeated-publication
conflict checks, policy arithmetic, objective extraction, output publication
and late consumer hashes. Removing those checks to fit the old allowance is
not justified. Current integrated development analysis already completes under
its separate120-second allowance.

The old benchmark reached D decoding at113.586 seconds. Adding an inferred
16–23 seconds of D decoding,35–45 seconds of D analysis and about4 seconds of
output suggests roughly169–186 seconds for that full retained block with current
source. D's remainder was not measured. A hypothetical4.7-second C reduction
and similar4–5-second D reduction would leave approximately160–177 seconds.
These are workload-based estimates, not completed four-run throughput or a
performance promise. The proposed correction was explicitly left unimplemented.

For a fresh comparison contract,240 seconds inclusive per four-development-run
labels block is a reasonable prospective measurement budget for this observed
workload, with full validation retained. This advice does not adopt a budget,
release a comparison, or guarantee capacity for longer/larger future runs.
Bind actual fresh durations, selected streams and capacity limits, then measure
the development analysis before releasing confirmation/holdouts. Keep the old
120-second benchmark FAILED. No unchanged retry is authorized by this record.

Retained authority: `result.json`; `job.json` SHA256
`be6f5e41df3bb7cf6b43f9341bae7345656c84cf777adc5f63ce9169d90621fd`;
`profile_result.json` SHA256
`dcfbd0863b35db3d4fba2d292369cd9db88a319e81c092e18a9e227252a0d773`.
The directory also holds exact helpers/commands, pinned manifest, full logs,
sparse progress, `captured_counts.json`, `labels.json` and `metrics.json`.
The parent owns live status, handoff and the material checkpoint.
