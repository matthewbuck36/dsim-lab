# R2 centered collection kinematic development

V1 CLOSED_FAILED_HYPOTHESIS, 2026-09-10. The single ideal-kinematic job completed
terminal0 in2.888299s of numerical work under85s interrupt+5s kill. It used the
existing selected Directional_Controller and MovingRawEvidence with an optimistic
repeatable artificial directional cost profile, no ROS node/field model/Gazebo.
[Prospective plan](../r2_centered_verification_plan.md).

Only3/12 required .25/.35m initial conditions reached ready before12s;0/6 harder
.50m cases did. All end near the frozen center (roughly .012–.056m for required
cases), but many retain only two center-eligible cycles or fail sector-trajectory
comparability because an earlier approach cycle is still selected. Thus moving
the robot toward the center does not itself establish timely evidence under the
old deadline. No runtime change is nominated from this failed hypothesis.

All eighteen trajectories/evaluations remain at external
`development/20260910/centered_verification_v1/` under
`/home/mattb/Experiments/GESC-Gaussian/v2/`. `pins_before.json`, `run.py`,
`trajectories.jsonl`, `evidence.jsonl`, `result.json`, `receipt.json` and
`execution.log` retain source/config identity and every case. Exact command:

```bash
timeout --signal=INT --kill-after=5s 85s env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 bash --noprofile --norc -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q5_stationary_centroid_adapter_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_verification_v1/run.py' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_verification_v1/execution.log 2>&1
```

This result concerns ideal spatial collectability only. Actual noisy field
repeatability, candidate ranking and runtime safety remain untested.

## V2 two-stage timing result

V2 COMPLETED_KINEMATIC_DEVELOPMENT_PASS, under
[the prospective v2 plan](../r2_centered_verification_v2_plan.md). The new
20-second ideal trajectories preserve the v1 tracking/controller/raw guards.
All12 required .25/.35m cases enter the .08m approach region within8s and
collect accepted evidence before their once-frozen12s additional deadline;
4/6 harder .50m probes pass. The absolute20s cap and all failed hard cases
remain. No required case has a sustained joint commanded-zero interval.

The single exact command above used `centered_verification_v2` in place of
both `centered_verification_v1` paths. It completed terminal0 in5.461519s of
numerical work under the same90s command bound. All18 full trajectories,
rejection margins, first approach times, fixed deadlines and first ready times
are retained in that exclusive v2 directory with source/config/hash receipt.
The prototype reuses all previously eligible cycles; approach admission does
not clear valid history. This matters to the measured result and must remain
explicit in any runtime design. A12s observation allowance after approach is
not a requirement to discard earlier spatially representative measurements.

This result supports a selectable visible runtime development experiment only.
The artificial repeatable signal cannot establish actual field repeatability,
ranking, or hardware behavior. V1 remains a failed hypothesis.
