# R3 retained C normalization profile

ADOPTED, 2026-09-10, as a bounded diagnosis after the unchanged full four-bag
[labels benchmark](r2_labels_block_benchmark_plan.md) timed out. The benchmark
remains failed and the historical V9 contracts/results remain unchanged.

The retained C timing is 16.156252 seconds of bag decoding followed by
42.593500 seconds inside `evaluate_m4.analyze_run_data`. Its normalized JSON
publication follows that interval. The small metrics receipt reports 10605
unique observations, 7208 duplicate publications, and no candidate snapshots,
fill commands, preparations or commits. Those facts narrow possible work;
they do not establish a measured hotspot.

## Exact cached-only experiment

New exclusive diagnostic root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/cached_c_normalization_v1/`.
Read only the existing `labels_block_benchmark_v1/labels/slot_3_normalized.json`
(89986365 bytes), with SHA256
`0dd3c204e0e34f2d96574a995c0bb33b706130ad4791b63eefd8816abe013f17`.
Preparation inventories its filesystem identity without reading its bytes.
Inside the child allowance read those bytes once, verify the declared digest,
decode once, and call the existing `m4_pilot.normalize_direction_targets` once
with the document's observations, qualification and exact identity/exposure
arguments. No bag reader, lifecycle/source-stream reconstruction, labels stage,
direction reference or numerical field model runs.

Thin timed wrappers retain original return objects and count calls to the
existing normalization's `deepcopy`, `canonical_sha256`,
`direction_supplemental`, and `select_causal_anchor`. Enable `cProfile` around
that one normalization call; its overhead is included and must not be
subtracted or described as uninstrumented performance. Preserve a profile file,
bounded top-function summary, stage times, and full returned-document equality
with the retained document. Restore original module bindings afterward.
Rehash the in-memory source bytes and observation payload, and verify pre/post
source pins and input filesystem identity. No output document is substituted
for historical evidence.

Use the existing `m4_science_job.finite_science_job`, 45 seconds inclusive,
`subreaper_group_v3`, existing 3-second cleanup reserve, and a 55-second outer
command. The allowance includes imports, verification, decode, profiling,
comparison and result writes. One separately bounded 30-second preparation
imports and pins the scoped existing owners, environment, helper files and
this plan; it does not warm the cached input. Hold those sources only while
the child runs. Dispatch follows terminal completion of the visible attempt02
analysis to avoid simultaneous analysis CPU work. Preserve timeout or failure;
no unchanged retry or expanded allowance.

## Decision rule and next boundary

PASS means the one call completes within the bound, returns the identical full
document, preserves source/input identity and leaves no owned processes.
Report normalized-stage timing separately from decode and wrapper work.
This can attribute only normalization, not the original upstream validation or
adapter work, and cannot establish full-block throughput or release comparison.
If normalization is small, a further saved diagnosis must time the existing
upstream owners using one actual C bag read shared in memory, preserving full
stream validation. Do not reconstruct a lossy bag from normalized observations.

A source-visible candidate is the adapter's second `message_payload(wire)`
after it already detached the same wire via `observation_payload(wire)` for its
fingerprint. Reusing that detached payload plus validated publication stamp
may preserve exact rows, but no production change is adopted by this profile.
Copy removal, shared caches and any correction require measured justification,
exact output/error/detachment tests, and a separate prospective source boundary.
