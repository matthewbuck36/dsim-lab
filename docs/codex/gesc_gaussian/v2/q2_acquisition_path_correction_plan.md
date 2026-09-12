# Q2 acquisition path correction and fresh v2 inputs

Status: ACTIVE Level B correction under the approved simulation-only V2
implementation goal. Incomplete q2-primary-shadow-v1 is closed at
acquisition_closed.json SHA256
`672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02`;
material checkpoint `checkpoints/q2_acquisition_closed_v1/manifest.json`, SHA256
`670a20d983dd2919807e324c2a305258c9e4166853d34b8769ca26079bfaeb44`,
preserves260files/1083715-byte archive/98retained hashes before source changes.
No frozen attempt is rewritten or retried.
Read this amendment with plan.md, status.md and q2_qualification_plan.md.

## Observed failure and narrow correction

The first Q2 case completed125 simulated seconds and passed recording, spawn,
safety, final-zero and cleanup. Acquisition then stopped before case2 because
the new analyzer expected `runs_root/run_id`, whereas the unchanged recorder
creates `runs_root/UTC-YYYY-MM-DD/run_id`. Zero inputs reached the accepted-study
ledger. The69 synthetic contract tests used the same incorrect direct path and
missed this owner-integration mismatch. Preserve the failed attempt, complete
recording, source checkpoint and all logs. No labels, detector outcomes or
numerical direction references from that case select this correction.

Correct only Q2 run-path admission before input hashing/reading. Use the existing
scenario runner's unique exact-run lookup, require the supplied resolved path
to match that result and its reserved run identity, and require exactly one
valid ISO UTC-date bucket beneath the declared runs root. Do not use today's
date: recording creation and later evaluation may cross midnight. Reject wrong
IDs, invalid/nested buckets, duplicate exact IDs and symlink escapes before
input reads. Preserve confirmation partition sealing and all content receipts.
No recorder/runtime/filter/controller/numerical-model change is needed.

## A separately frozen acquisition version

Use `q2-primary-shadow-v2` at external
`qualification/q2_primary_shadow_v2/` with fresh seeds26090931–34 in the same
ordered discovery residence/approach and confirmation residence/approach roles.
Verify nonuse before freeze and dispatch. Retain the failed21-series recording
as incomplete-attempt evidence only; no import, replacement or resumption under
its old identity. This new acquisition's31-series seeds still do not establish
independent stochastic replicates.

Preserve exactly q2_qualification_plan.md's four starts, sources, geometry,
gains, speed ceilings,125sim/240case/1200suite budgets, first visible case,
observation-only supervisor,75% policy, detector/neighborhood gates,42s first
positive opportunity, negative labels, nine finite settings and reference
numerical/qualification thresholds. Retain48 symbolic target slots and the
completed-nomination-controlled48-or-sealed24 branch. No scientific tuning.

Extend existing version/profile owners with this finite second Q2 identity;
preserve Q1 routes and the first Q2 version's declared values/default API.
Keep `Q2_VERSION` as the original v1 alias, add `Q2_CORRECTED_VERSION` for v2
and `Q2_VERSIONS` for family dispatch. `q2_contract_fields(version=Q2_VERSION)`
and `qualification_partition_seeds(version)` select exact per-version identities.
Bind v2 to the immutable failed-v1 closure and this source amendment. Cross-
version jobs, labels, nomination/settings, targets and traces must be rejected.
The v1 acquisition guard continues to refuse its already-used root/identities.

## Required preflight before new evidence

- Test the analyzer against paths produced by the real recorder layout and the
  existing exact-run lookup, including UTC rollover, duplicate IDs, escapes and
  partition redirects before file reads. Correct the synthetic fixture layout.
- Cover v1/v2 finite identities, unchanged scientific settings, source/closure
  binding, companion routing and completed48/sealed24 branches. Preserve old
  Q1/D1/D2 regression coverage. No repeated scientific calculation.
- Review source differences against the closed failed attempt; runtime and
  numerical owners remain byte-identical. Build only the new installed scenario
  resource, verify installed/source bindings, checkpoint and freeze source/config
  and exact commands before dispatch.
- Run once: the bounded four-case acquisition, then only on complete integrity
  one600s label job and its permitted single300s reference branch. No automatic
  retries. Keep acquisition, detector, direction and combined results separate.

Any integrity/safety/cleanup failure again stops dispatch and closes that
version. Scientific FAIL/EVIDENCE_UNAVAILABLE keeps the unchanged gates and
withholds M4. The16-run pilot and the full user goal remain incomplete.
