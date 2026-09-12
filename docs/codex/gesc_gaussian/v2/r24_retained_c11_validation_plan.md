# R24: full retained C11 validation under the R23 correction

ADOPTED after [R23 completed](r23_guidance_admission_handoff.md). Its reviewed
validator correction and187passed tests are prerequisites. One full existing-owner
validation determines whether the incomplete C11 recording can provide a separately
qualified baseline failure. It does not edit or reopen V14.

One call to `validate_run_directory(original_run_directory, write_report=False)`
under the existing sourced R21 environment, bounded by120s SIGINT plus5s kill.
Use the original C11 metadata, topics, parameters, console and bag in place. The
explicit false write flag is mandatory; never use the CLI that writes completeness.
Save the returned report only in a new exclusive external
`development/20260911/r24_retained_c11_validation_v1/validation_v1/` directory.
No alternative validator, numerical model, label/reference calculation or simulation.

Before/after checks bind all original non-bag run files, the original acquisition
and scenario result, the R23 source validation/review/archive and the actual
validator source. Check raw file size/mtime/inode/device without another raw hash
scan. Preserve original completeness and metadata flags byte-for-byte. Retain
the full new report and exact check differences, including all failures.

Success requires full returned report passed, every check passed, no new warnings
relative to the original report, stable input/source hashes and raw stats, and
exactly the two previously failed check names changing false-to-true:
v2_lifecycle_contract and algorithm_event_source_causality. Changed successful
check details must be reported and explained rather than ignored. The global
result changing false-to-true is a new derived validation, not a rewritten native
acquisition. C11's original failure, native no-fill/no-arrival and cleanup records
remain visible. Independent cached result review precedes any later use.

Stop this validation on timeout/mismatch/new failure, preserve it and diagnose
before another action. No automatic retry, replacement run or matrix release.
After this result, prepare a separately documented existing-owner path for only
the five missing cases and their scientific analysis, preserving all prior
recordings and the full16comparison provenance. No new comparison-version
infrastructure is implied. Full goal and original30% latency endpoint remain open.
No physical/Pi/snapshot/V1/commit/push.
