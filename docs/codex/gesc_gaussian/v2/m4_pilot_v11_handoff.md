# M4v11 closure: arrivals established, comparison incomplete

Status: CLOSED_INCOMPLETE, 2026-09-11 UTC. The sole dispatcher session59849
terminated and was reaped with exit1. Wrapper1478.291230s; acquisition1474.156589s.
All806 source/helper pins passed the wrapper's completion recheck. No replacement,
confirmation, source tuning, physical action, commit or push occurred.

All four nominal development runs reached the evaluator-only0.5m global region
after a valid local fill, escape and restored SEARCH. GOAL_HOLD is optional.

| Arm | Arrival, s | Final distance, m | Frozen behavior |
| --- | ---: | ---: | --- |
| A, PDE/stationary | 298.959 | 0.495668 | PASS12/12 |
| B, recurrent/stationary | 167.367 | 0.480612 | PASS12/12 |
| C, PDE/continuous | 226.755 | 0.491464 | FAIL11/12: initial rejected verification adds a SEARCH transition |
| D, recurrent/continuous | 179.946 | 0.495698 | PASS12/12 |

C's arrival, local recovery, cardinality, safety and ownership pass. Its prescribed
state-path failure remains separately retained. Every recording, final-zero and
inner/outer/independent cleanup check passed. Read-only process inspection after
dispatcher termination found no matching Gazebo/recorder/scenario/dispatcher.

The four existing scientific jobs completed with exit0 and integrity/cleanup PASS:
labels111.581580s, C reference10.315326s, D reference8.201399s, summary5.534933s;
block139.769499s. Scientific completeness remains false because C's motion
measurement cannot pair12119 actual commands with12118 diagnostic rows. Positional
pairing reports5197 mismatches. This is unavailable attribution, not proof of a
stopped sweep. D has10596 exact pairs and OBSERVED_CONTINUOUS_ACQUISITION.

Both selected direction references pass against stationary-position observed-phase
GESC, not a spatial gradient. Each retains all24 scheduled targets:

| Arm | Eligible/24 | Median error | P90 error | Averaging availability |
| --- | ---: | ---: | ---: | ---: |
| C | 7 | 19.563960deg | 59.043175deg | 6/7 |
| D | 4 | 13.045676deg | 30.889580deg | 4/4 |

The frozen first-opportunity latency measurement has0/4 observed endpoints and
0/2 development pairs. First basin residences A/B/C/D last0.578/0.850/0.544/5.882s,
below its12s eligibility condition. These results remain censored/unavailable;
arrival-time differences do not establish the original30% detector-latency target.
All four have zero wrong fills/goals under the existing attribution owner;
unknown detector endpoint labels are retained and are not negative-control proof.

The gate correctly withheld all12 confirmation slots. All16 outcomes and the
unavailable confirmation metrics are retained. V11 is closed; V2 and the full
research goal remain open. Do not rerun/relabel this fixed comparison.

## Exact retained evidence

Root: `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v11/`.
Commands and per-run details: [execution record](validation/m4_v11_execution.md).

- `acquisition/acquisition.json` SHA256
  `424d36079fe38b0ef5d7171e526c3e4098448331c2d04982b80900937f3e9a29`.
- `analysis/block_0/result.json` SHA256
  `fa89f031549b75bc0ca42f5dc2c4af50aae2b60f45554e182c052eb4b590f1a0`.
- `analysis/block_0/block_receipt.json` SHA256
  `b73368014efc543966a414d143c7e29106883c112bb7e3cf23ac393cf348ff25`.
- C/D reference SHA256 respectively
  `a1a73424f28c3932ae416b31b352520ae9d602566d3bdd5691db35925e07ca99`,
  `30d0c062a71520aabfbe2782a6db7038b6f3894954159c4953c232fd6643ae0b`.
- `report/result.json` SHA256
  `1ac6f8b636fb792444e425ef3d95de6e067384ced4bc3ca6189ec375152e4167`;
  adjacent `report.md` contains all16 outcomes and scope limitations.
- External `development/20260910/m4_v11_source_v1/acquisition_execution_v1.json`
  records the reaped wrapper, exit1 and no source-recheck exception.

Next: a separately planned bounded measurement diagnosis using cached trajectories
and, only where caches lack the data, one filtered command-stream extraction.
No new matrix until usable measurements and their independent meaning are established.
