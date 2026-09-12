# M1 label publication attempt v1: retained implementation failure

The first bounded label-freeze command exited 1 during final labels.json
serialization: TypeError, NumPy int64 is not JSON serializable. No detector
calibration was invoked. Eight input-trace files and synthetic_inputs.json were
written; labels.json is incomplete and must not be used as a frozen manifest.

Retained directory:
/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1

Exact log:
/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1.log

The loaded reader/analyzer source patch was retained as
m1_labels_v1/label_owner_source.patch, SHA-256
41ff0d1d92ce175c970c989b33765c30232b9f9ec150e5850d5f96a9829a5d32.
No failed directory or partial file is overwritten.

The correction converts the agreeing-optimizer count to a Python integer and
serializes/validates JSON before exclusive file creation. Each distinct geometry
receipt is now saved immediately, so another final-publication failure would
not require repeating those optimizers. The fresh output attempt is v1a; the
same label contract, optimizer bounds, quadrature, regions and 36-point detector
grid remain fixed. Geometry qualification and input freezing are rerun only
because the failed final manifest did not retain complete geometry receipts.

Pre-calibration replay review also repaired causal authority invalidation:
publication/source alignment uses the declared 50 ms tolerance; same-SEARCH
restoration does not rearm; invalid-state/readiness pulses between poses carry
a history-reset generation; source/receipt freshness and epoch-start exclusion
are explicit; mask inputs are rehashed before their second read. Outside-region
negative labeling checks whole represented line segments as well as endpoints.
These changes occurred before any detector calibration output and do not revise
spatial thresholds or old experiment outcomes. The failed v1 geometry summaries
had zero qualified basins, so no published negative interval was reclassified.

Focused validation after the first source/label implementation passed 28 tests;
the follow-up pulse and epoch-start checks are included in the next retained
test receipt. All runtime/Gazebo/physical actions remain outside this attempt.
