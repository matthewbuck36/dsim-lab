# Q2v2 recorded detector gate result

Status: PASS extraction; scientific qualification unchanged. The single bounded
job from `../q2_recorded_detector_diagnostic_plan.md` exited0 in3.174949s, using
the existing bag reader and only centroid diagnostics plus automatic readiness
from the two discovery recordings. No detector replay, model/filter/reference
calculation, parameter change or confirmation read occurred.

```bash
env -u PYTHONPATH bash -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && export ROS_DOMAIN_ID=191 && timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v2/diagnostics/recorded_detector_v1/extract.py extract'
```

All source/input hashes were rechecked. Recorded W6/epsilon.30/R.75, six
contiguous window bounds, source gaps and score=sum(five recorded distances)
match exactly. First complete publications were chosen before checking validity;
none was replaced by a later favorable snapshot. All other messages remain saved.

| Discovery run | First complete snapshots | Score range, m | Radius range, m | Recorded rejection |
| --- | ---: | ---: | ---: | --- |
| Residence26090931 | 5 | 1.250966–1.882891 | 0.281259–0.332986 | 5 score-only |
| Approach26090932 | 15 | 1.842276–2.296653 | 0.271903–1.001990 | 12 score-only; first3 both |

Every complete snapshot is valid but fails `score<0.30m`. The first three
approach snapshots also fail `radius<=0.75m`; later local looping snapshots pass
radius. No eligible or confirmed messages occur. These are measured wire results
for the declared parameters, not new labels or alternate-setting results.

## Separate live detector history limitation

The earlier motion report's124.882s uninterrupted support describes admitted
pose/SEARCH history and direction-policy continuity. It is not proof of the
live detector's separate state-callback history. Residence records:

- `stale_or_future_algorithm_state` at publication56.8s and85.6s;
- three `outside_search` notifications at85.7s, with SEARCH epoch still1;
- reset generations103–108, and first complete publications only at
  38.4/44.4/50.4/56.4/121.8s.

Approach has one in-readiness reset generation137, no reset-reason notifications,
and15 complete publications every6s from39s through123s. Source gaps are0.034s
in both. No publication-clock regression or identity mismatch exists.

Residence resets reduce available complete histories. They do not explain
rejection of its five valid histories, which all fail the score. Diagnostics do
not identify the triggering AlgorithmState input: this extraction cannot
distinguish stale from future state or prove actual supervisor state transitions.
Do not equate pose/policy support with live detector support or describe the
`outside_search` notices here as verified SEARCH departure.

Source inspection finds immediate invalidation for any future state stamp in
`_centroid_algorithm_state_cb`; bounded clock-order admission is absent there.
This potential ordering fragility is separate from score sensitivity. A correction
must preserve stale/invalid rejection, original receipts,0.5s freshness and no
use before clock coverage. The notices alone do not prove this potential cause.

## Receipts and next boundary

External root: `qualification/q2_primary_shadow_v2/diagnostics/recorded_detector_v1/`.

- `report.json`: SHA256
  `aad7f05ebffcefefb6e3edd46c88008b149db63665976f3c6c3158ea7ee87e15`.
- `freeze.json`: SHA256
  `06269f9d15ac94ee4fafdb46e6fb26226912c4bfcac9aa7984842a6bb33ac709`.
- `extract.py`: SHA256
  `a5ab4b7169999f932ca890139c4c27ae18fbeaaf05114775ff68f7152015fc53`.
- Extraction log: SHA256
  `8c2d59badeec7acd4f167dbcfc0865259e6a0aa04123d774157cc195f0325e65`.

The report binds all four message/window CSVs. Reset timestamps were projected
from saved CSVs without a second bag read. `q2_centroid_response_note.md` explains
why partial-orbit window means can keep adjacent centroid distances high even
for a fixed center. No orbit was fitted to assign these measured scores a cause.

A future finite calibration must address both score responsiveness and an
independent settling oracle while preserving drift/large-loop negatives. Simply
raising a threshold until these runs flag is not qualification. The direction
diagnostic's large upper tail is a separate unresolved requirement. Q2 remains
CLOSED_EVIDENCE_UNAVAILABLE, confirmation SEALED and M4 unreleased. No repeated
diagnostic/model/grid job is authorized by this report.
