# Phase 08 v2 Acceptance-Contract Erratum

Date: 2026-07-25

Phase 08 v2 is a closed failed experiment. This erratum records contradictions
found during the Phase 08.1 audit without altering the historical plan,
manifest, gate JSON, report, handoff, or run evidence.

## Threshold contradiction

The saved Phase 08 plan declares:

- local-escape success at least 95%;
- successful escape p95 at most 45 seconds;
- median valid post-fill orbit count at most 1.5;
- revisit rate below 5%.

The generated v2 gate JSON and Markdown report encode:

- local-escape success 100%;
- successful escape p95 at most 35 seconds;
- median post-fill orbit count at most 2;
- revisit rate at most 10%.

Because v2 stopped at activation, none of these later gates was evaluated.
They cannot be reconciled retroactively or selected after seeing future data.
A future experiment must use one versioned machine-readable acceptance
contract whose hash is embedded in its manifest, gate results, and report.

## Not-run representation

Historical v2 artifacts represent some unexecuted gates as `passed: false`.
That can be confused with an evaluated failure. Future artifacts must use an
explicit `outcome: not_run` and `passed: null` for gates not evaluated.

## Development versus acceptance

The historical 120-run design combined 10 activation, 30 tuning, 70 unique
holdout/validation cases, and 10 repeats. For future work, activation and
tuning are development evidence and are not part of the acceptance denominator.
They may be iterated only under versioned, bounded development plans. Formal
holdout and fixed-profile validation remain sealed and non-iterative within an
experiment version.

## Historical disposition

- V1 and v2 remain immutable and excluded from future denominators.
- V2 Gate 2 remains failed at 1/10 under its historical contract.
- Gates 3–14 remain not run.
- No v2 profile was frozen.
- No simulation-ready tag or physical motion was authorized.
