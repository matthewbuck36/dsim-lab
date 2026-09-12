# Q1 exact centroid CONFIG attribution — 2026-09-09 UTC

Status: bounded validator correction implemented and focused regressions PASS
under `../q1_event_attribution_plan.md`. Recovery2 remains CLOSED INCOMPLETE as
recorded in `q1_acquisition_recovery2_failure.md`; this source check neither
reclassifies that acquisition nor releases another acquisition or M4.

## Correction

The actual centroid detector publishes CONFIG detail
`centroid_windows_v2 source-time configuration`. AlgorithmEvent has no explicit
producer field, and the existing attribution function omitted this signature.
The sole source change for this milestone adds exact string equality after the
CONFIG type check in `algorithm_event_producer_stream` and returns the existing
`convergence_detector` owner. Existing prefix handling and non-CONFIG ownership
remain unchanged. No publisher, interface, runtime control, threshold, source
clock, scientific population or reference rule changes.

Recognition feeds this event into the same existing detector timestamp stream;
it does not bypass unidentified-event, regression, emission-freshness or source
causality checks. Empty and unknown detail strings and near matches remain
unidentified. The new literal does not authorize an unknown event type or
override an existing non-CONFIG event owner.

## Checks

New `test_q1_event_attribution.py` contains20 cases:

- The real ConvergenceDetector state/pose callbacks publish exactly one CONFIG
  across repeated poses; its actual serialized/deserialized AlgorithmEvent is
  recognized. This uses the existing bounded node fixture and collecting
  publisher, not a hand-authored replacement for the emitted signature.
- Seven empty/unknown/near-match details and two unknown event types reject;
  a known non-CONFIG owner retains its existing classification.
- Both CONFIG-to-candidate and confirmation-to-CONFIG regressions fail within
  the same detector stream. Valid cross-producer interleaving stays valid.
- Six central `validate_run_directory` cases exercise valid, empty, unknown,
  near-match, wrong-type and stale-emission outcomes. The synthetic records
  intentionally lack other required run streams; assertions check the relevant
  report entries and explicitly do not claim complete-run acceptance.

The full existing recorder suite and V2 recording contract tests ran with these
new cases: **115 passed in4.31s**, exit0. There were no failures in this correction
test version. Exact command from repository root:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_event_attribution.py ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_event_attribution_v1.log 2>&1
```

The corrected overlay environment appends only the external extremum-seeking
package; it does not prepend the ros_esc source-package path. Context preflight
`timeout30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
and `git diff --check` both passed. Source review confirms the attribution change
is exactly two added lines; all earlier validator work is preserved.

No retained bag was reassessed by this subtask. No original completeness,
metadata, scenario result, acquisition receipt or scientific artifact was
modified. No Gazebo, physical operation, build, checkpoint, commit or push was
performed. Parent owns any separately retained diagnostic reassessment and the
subsequent source checkpoint/release decision.

## Parent-owned retained-bag diagnostic

After the source checks, the parent ran the permitted read-only corrected
validation of the retained recovery2 bag: **PASS, all60 checks**, with all15
original closure artifacts unchanged. This isolates the attribution defect;
the original fixed acquisition remains CLOSED INCOMPLETE and its published
classification is not replaced. No scientific results were opened.

Exclusive diagnostic directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery2/diagnostics/`.
The new `event_attribution_validation.json` records the corrected report, source
owner, original closure and unchanged-artifact assertion. Its adjacent
`event_attribution_validation.py` is the exact copy of the executed temporary
script. This subtask verified those small artifact hashes and report fields;
it did not repeat the bag validation.

Parent-reported exact command after the same two setup files above:

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 /tmp/dsim_q1_event_validation.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_event_attribution_retained_v1.log 2>&1
```

| Retained artifact | SHA256 |
| --- | --- |
| `diagnostics/event_attribution_validation.json` | `9ea5627e3ecaec00eb532bfa07bede274d81bb7c45661ff1287ed4302cf380f5` |
| `diagnostics/event_attribution_validation.py` | `e4335064cf029e1c12d8d3317b50fa36d3a32c7a489ce9379b650078cdc37d1a` |
| External `builds/initial/q1_event_attribution_retained_v1.log` | `de7689fde49da35dec291d906f14aab9c9031610ea4aa95cac040dbab85c7f87` |

## Frozen source and evidence hashes

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py` | `5c3b2bf51962bae722836c91585ca83c8c8c12d8bea93c757ab8c73d83159d81` |
| `ros2_ws/src/ros_esc/test/test_q1_event_attribution.py` | `3906d993996f4ebfc6fe72bad7a0b941786954bb57fbce2acb9eaf09e05eff25` |
| External `builds/initial/q1_event_attribution_v1.log` | `16540afcb553a9e0efc5603baed93659a79fef76cef31250cc0a549d09b1b3b0` |

The external log path is rooted at
`/home/mattb/Experiments/GESC-Gaussian/v2/`.
