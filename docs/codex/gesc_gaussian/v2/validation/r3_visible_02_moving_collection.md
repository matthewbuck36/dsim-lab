# Attempt02: measured moving collection and local escape

READ-ONLY DEVELOPMENT DIAGNOSIS, 2026-09-10. Source: closed first-read exports
under `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/analysis_v1/`.
No new bag access, listener, model fit or simulation was used. The original
attempt02 full-behavior failure remains; this is a component finding from its
actual recorded motion, not a replacement historical verdict.

Candidate1/epoch1 was accepted78.1 s; VERIFY began78.2. Immutable centered
collection admission84.7 gave6.6 s approach, within8. The first snapshot92.3
arrived14.2 s after acceptance and7.6 s after admission, before96.7 expiry.
It contains three informative, non-overlapping revolutions, zero pretrigger
revolutions,235 retained observations and evidence84.253671024–92.176873594.
The permitted pre-admission approach history supplies the first0.446329 s of
that evidence; collection admission does not reset existing valid raw history.
Snapshot SHA256 is `2a40647787ab6106dae5183cea545b37c3f7d2bc04bf3b3ca3b05f90e95a6b4f`.
Its raw upper cost bound is−0.026592856394468706; information amplitude
0.005731194352747665 exceeds three-cycle disagreement by0.00421343125421259.

Frozen center is(1.0553851687433269,1.0862212247803813). Odometry uses actual
header ROS stamps in half-open phase intervals; linear speed is hypot(vx,vy),
path length is the sum of consecutive recorded planar displacements.

| Interval (s) | Samples | Min/median speed (m/s) | Path (m) | Center distance range (m) |
|---|---:|---:|---:|---:|
| Approach78.2–84.7 |191|0.01633 /0.05090|0.32031|0.07940–0.19964|
| Collection84.7–92.3 |224|0.00574 /0.02543|0.19187|0.07139–0.09088|
| Design92.3–92.9 |17|0.00615 /0.02935|0.01510|0.09094–0.09159|

None of these432 odometry samples has both linear speed and absolute yaw rate
below0.001. The recorded episode therefore demonstrates moving approach,
collection and design without a stopped sensor sweep. The first-admission
radius0.08 m is not an ongoing hard radius; the unchanged evidence tolerance
and neighborhood guards remain authoritative.

All9419 final Twist messages equal their corresponding ControlDiagnostics
`final_command` six-vectors in topic publication order. Diagnostic bag receipts
follow commands by median0.651 ms and at most10.713 ms. The unstamped Twist
has no invented source timestamp: the following pulse measurements use its
paired diagnostic ROS stamp and actual command bag receipts. During approach,
collection and design, every zero publication is followed by nonzero at the
same diagnostic ROS tick. Maximum bag-receipt gaps are14.178,17.664 and25.659 ms,
respectively. The approximate19.6% VERIFY zero-message fraction in the prepared
state-join summary is not a stopped-time fraction. This audit does not prove
the absence of every sub-sample transient.

Design92.3→PREPARED92.6→COMMITTED92.7→ESCAPE_REPULSE92.9→ESCAPE_ASSIST95.9
→SEARCH112.8. The105.7 `candidate_departure` cancellation was after commit,
during escape; it is not a verification rejection. No rejection occurred during
VERIFY/DESIGN. Existing analyzer lifecycle is VALID, zero errors, one snapshot,
one preparation and one unique commit. Global-arrival measurements and the
prospective evaluator correction are owned by the parent task.

## Input receipts

SHA256, paths relative to the export root above:

- `v2_verification_guidance.jsonl`: `ea0972ec0fce1d1b92eb4de0df67fd0f0aea83d0d5211b5576f0b31cf783e01e`
- `algorithm_events.jsonl`: `274821e312560941993cb6b240e896639a0011322b425c7eff3b4e02dfd53462`
- `v2_candidate_snapshots.jsonl`: `4cb3e658bafe03a04e4f29eb76e9c0b723dd5d4c278ba76042b361d1dd83968e`
- `v2_fill_results.jsonl`: `e96e7af0bef9e6308c72d7d04655655102b96200955cf40d50cff5656d884b3b`
- `command_final.jsonl`: `9f9b4227ceecc3eef4cfe65e0143385aeb026273917e8e5c56af35dd70184c7d`
- `control_diagnostics.jsonl`: `90b368f1bffa0d848917aefafbd5e6e2e641c61fa1e584d916f6a060e722c8e5`
- `analyzer/tables/odometry.csv`: `d0365bc0364fee5de7f4289661a55384514c99b0b1b9aecfb8b073fc9c2dce17`
- `analyzer/summary_metrics.json`: `2c71e0cd8ecde902163c71b29e2aaa45d2b618d12d99650ddb15f1efef6f3cc6`

Read-only in-memory Python JSON/CSV reductions were each bounded by15 s (receipt
hashing10 s); all completed normally. No analysis source or original input was
modified. Phase/state joins, evidence coordinates and final-command limitations
are explicitly retained above.
