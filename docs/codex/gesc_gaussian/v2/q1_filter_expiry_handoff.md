# Q1 filter expiry recovery handoff — 2026-09-09 UTC

The bounded expiry recovery is implemented and validated. The final combined
suite passes233 checks in5.38s, including actual CustomFilter ROS transport,
late-fragment permutations, malformed/revoked evidence, legacy/source/clock
regressions and the combined pending-queue capacity edge. Log:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_filter_expiry_core_v6.log`,
SHA256 `45c9d1bb21dc83fafc8d6dca6bb0363f05846b9f2ca96c0029eefaaf3134d110`.
All initial failed test versions remain retained and explained in the validation
records. No scientific gate, freshness threshold or reference rule changed.

The selected schema2 model-input path now distinguishes incomplete cost-join
expiry from invalid pose/encoder/context input. It discards and retires expired
joins while retaining independent support with original receipts. Numerical
integration and rolling history still reset. Late retired fragments cannot
recreate joins or refresh data. Structure, identity, actual used-key conflicts,
explicit revocation and clock/context faults keep their strict checks.
Retirement capacity covers both pending queues (2048 default); each remains
bounded at1024. No additional time allowance or extrapolation is introduced.

Admission-only replay evidence, outside Git under recovery3
`diagnostics/filter_startup_confirmation_residence/corrective_v1/`, records:

- Complete-prefix proxy: unchanged288 observations and identical saved report.
- Seeded first-raw omission: corrected287 observations with one expiry and
  recovery; original version admitted14 and then remained trapped in resets.
- `_evaluate_filter` numerical function is byte-identical to the recovery3
  checkpoint. No numerical field or scientific performance was evaluated.

The final capacity-only closeout does not affect those replays: at most288 unique
keys occur, below both the previous retirement limit and unchanged partial cap.
The final combined regression specifically exercises the union-capacity edge.
The recorded actual callback-loss trigger remains uncertain; bag order cannot
prove subscriber callback order. The demonstrated recovery defect is corrected.

Both accepted recovery3 discovery inputs have contiguous diagnostics and zero
expiry resets throughout; original input/bag/configuration receipts remain
unchanged. Recovery3 itself remains CLOSED INCOMPLETE. Its failed third input
is excluded. `q1_acquisition_recovery4_plan.md` selects a separately frozen
two-import/two-new continuation after exact equivalence/preflight/checkpoint.
No acquisition or M4 result is implied by this source handoff.

Repository remains on `feature/gesc-gaussian-robustness-v2` at3369cfc with
task-owned uncommitted work; V1 remains closed. No physical source, hardware,
transfer, commit or push is included. Source freeze and checkpoint receipts
in live status define the next acquisition boundary.
