# R7 paired ideal approach feasibility

[Adopted plan](../r7_approach_feasibility_plan.md); production remains unchanged.
Existing controller/tracking/collector owners and midpoint unicycle integration
are reused. Signal is the explicitly optimistic synthetic signal, not a field
replay. C01/D02/D03 anchor geometry uses exact retained guidance/pose joins.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_approach_feasibility_v1/`.
Preparation PASS0.379320273s under30s cap,381 unchanged source/helper/input pins.
Manifest SHA256 `3aaf8e19af68add33bb488529125731ce156e1ec1455bd0f37e3dcb35c2e3276`.
Harness SHA256 `946a76f62ec9aa443e6afb9a9d40882304f2305d794afa91cd83628c988c2da6`.
Root static review verified69 cases (63 required,6 hard),138 paired trajectories,
exact retained0.1s elapsed offsets, existing gains/limits, original phase and
admission/deadline rules, and separate pre-admission/late readiness accounting.
All prepared hashes matched immediately before dispatch; no output marker existed.

Exact one-job command from `/home/mattb/dsim-lab`:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; timeout --signal=INT --kill-after=5s 85s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_approach_feasibility_v1/run.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_approach_feasibility_v1/execution.log 2>&1'
```

Internal85s work alarm includes imports and checks; outer85s SIGINT plus5s kill
grace enforces90s total. Exact session, result, elapsed times and hashes follow
the terminal receipt. No ROS initialization, Gazebo, bag decoding or numerical
field/direction-reference solver is part of this job.

## Terminal result

R7 prototype nomination PASS, session14834 terminal/reaped;138 trajectories,
383 stable pins, finalsummary45.201062s. Both laws63/63required; baseline4/6hard,
prototype6/6hard. No pass-to-fail regression;28 readinessslowdowns<=0.6s retained.
[Prototype handoff](r7_approach_feasibility_handoff.md) records limitations: ideal
baseline did not reproduce C01failure; realfield/directionquality unestablished.
Next archive modelboundary and adopt bounded phase-aware runtime source change.
No new runtime or V11 release.

Result SHA256 `9ea9b4e48c7a3f871c85b32e13feda0f612c61158dba990295e2b98a8143fb03`;
receipt SHA256 `1c1e465b30d0829a42ce08b82d4d094f58f01ac6898cabac1a0c24f7988debaa`.
Receipt elapsed44.980205s precedes output hashing; final saved console summary
reports45.201062s after output hashes/receipt publication. The unchanged90s
outer cap covers both. No failure artifact exists; all138 outcomes retained.
