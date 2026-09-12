# Recorder clock-range source milestone handoff

Status: CLOSED_SOURCE_AND_SELECTED_RECORDING_VALIDATION_PASS,2026-09-10 UTC.
Read [plan](m4_v7_recording_clock_range_plan.md) and
[exact validation](validation/m4_v7_recording_clock_range.md).

The existing recording validator now computes actual min/max clock bounds
once inside the unchanged simulation/nonempty branch. It reuses them in the
same timestamp predicate. No integrity check, tolerance, readiness slice,
ordering, report field, algorithm control or deadline changed. Physical and
empty-clock branches retain their behavior; no physical source was edited.

A retained baseline showed64min/64max scans for64 typed stamps;9 semantic tests
passed and the scan regression failed as expected. The corrected source passed
all10 focused plus161 relevant unique tests on identical633-source maps, with21
actual installed bindings verified. Final validator SHA256
4165c89d00adf62fc7f0b49ca7d00f40a5f3c94be0048756b83e3fad3ffb5414.

One write_report=False call validated the retained V6 slot1 in49.042393395 s;
inclusive wrapper52.046186101 s/180 s. Exact whole48-check report equality,
all8 input hashes including the bag,633 source hashes and helper/proof hashes
PASS. Its selected<=60 s target passes for this recording only. The old115 s
finalization interval included writes, so this is not a controlled speedup.
V6 remains CLOSED_INCOMPLETE and none of its slots can be replaced/retried.

External root:
/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v7_recording_clock_range_v1/.

- source_validation_v1.json SHA256
  7e501c81b71b97b1a0dbc1c68f28a4a8ac60ba28a90f507b60c13edf33bbc994.
- retained_validation_release_v1.json SHA256
  e89b0dcbffdc3a505e80b7d8c3b6426f5f7542f56ea232a27255bcd3cfed004c.
- retained_validation_v1/receipt.json SHA256
  0ab9b5a69517c282b5a36981a97d3a2c3b070ce73a7236aa726878534d529a03.

Original validator/test snapshots, failed baseline, JUnit/logs, one corrected
helper allowlist draft and its original are retained. No new recording or
field/reference/label analysis ran. Source remains held pending material
checkpoint/archive. Next work requires separate prospective V7 identity and
comparison amendment, preserving matched-gain/heartbeat selections,16slots,
all original gates/budgets/denominators and the two research goals.

Git: feature/gesc-gaussian-robustness-v2,HEAD3369cfc83a64ff5d8354827fd5310caaf0c8e945;
all task changes remain saved uncommitted. No commits/push/V1/Pi/hardware work.

Material source archive PASS: checkpoints/m4_v7_recording_clock_range_source_v1/manifest.json
SHA256 5befd6c9408e7aeda174cabc647e00e58a800643ad0f3bca5912fd03a2a0e1e7;393 files,63 externalrefs,1542140-byte verifiedtar.
Context/diff/checkpoint PASS. This live receipt postdates immutablearchive.
