# R3 visible development attempt02 — arrival established

2026-09-10. COMPLETE recording, scoped cleanup PASS, native lifecycle VALID
with no errors. The retained run demonstrates local detection, moving raw-cycle
verification, one committed Gaussian fill, assisted escape, resumed continuous
search and arrival within the declared global-source tolerance. Under the
[user-revised arrival criterion](../global_arrival_acceptance_20260910.md), this
is successful exposed integrated development. It is not broad qualification or
untouched confirmation. Its original GOAL_HOLD-dependent scenario verdict stays
FAILED, and attempt01 stays startup INCOMPLETE.

## Retained acquisition

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/`.
Run: `runs/2026-09-10/v2_method_development_D_20260910_02/`.
Plan: [attempt02](../r3_visible_development_02_plan.md). The 210 prepared source
pins remained stable. The existing runner/recorder completed in 230.431133406 s,
within its 420 s root cap, with inner and outer scoped process/graph cleanup
passing and no remaining owned processes. Recording completeness passes with
no failures. `attempt_result.json`, `scenario_summary.yaml`, `runner.log`,
`root_execution.log`, resolved parameters and raw bag are retained. Three scoped
Gazebo window images preserve visible acquisition.

Exact dispatch (terminal tool session17814, exit0):

```bash
env -u PYTHONPATH ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/environment.sh; timeout --signal=INT --kill-after=2s 420s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/run_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/root_execution.log 2>&1'
```

## Recorded behavior

Times below are actual simulation publication times unless stated otherwise.
The confirmed support ends at78.0 s, the diagnostic latest input pose is78.008 s,
and confirmation publishes at78.1 s. The candidate center is
(1.0553851687433269,1.0862212247803813). VERIFY starts78.2 s. Centered collection
is admitted84.7 s,6.6 s after acceptance within the8 s approach cap. Three
informative verification revolutions produce a snapshot92.3 s,7.6 s after
admission within its12 s allowance. No pretrigger revolution was used.

Preparation completes92.6 s and the unique fill commits92.7 s; objective and
direction acknowledgements occur92.8 s. ESCAPE_REPULSE begins92.9 s. Measured
insufficient radial progress selects the existing bounded ESCAPE_ASSIST at95.9 s.
The robot exits the fill and resumes SEARCH112.8 s. Existing command ownership
validation passes, including the assisted transition and restoration of ordinary
GESC. This is assisted Gaussian escape; do not call it unassisted repulsion.

The separate `arrival_assessment_v1.json` reads only the saved analyzer odometry
CSV and small event/summary artifacts (0.031737 s under15 s, four input hashes
stable). Of1983 recorded readiness poses after escape completion,1150 are within
the existing0.5 m radius. First arrival is141.146 s simulation time at0.499081 m,
28.346 s after escape completion. Closest recorded distance is0.199456 m at147.946 s;
final distance is0.252970 m at180.212 s. No interpolation or new bag read was used.
All1150 readiness odometry samples from first arrival through the final sample
remain inside the0.5 m radius, spanning39.066 simulated seconds. This descriptive
residence check read the same saved odometry CSV under10 s; it adds no dwell
requirement to the user's arrival criterion.
These are proximity measurements to the declared source, not exact mathematical
minimizer equality. The user explicitly accepts arrival without GOAL_HOLD.

## Analysis and original failure boundary

The prepared existing-owner analysis completed in71.974 s within120 s, with two
native scans (12.539 and11.327 s), one retained BagData reused for supplementary
exports, and no wrapper error. Lifecycle is VALID/errors0: one confirmation,
candidate snapshot, preparation, prepared result and unique commit; two valid
SEARCH epochs. Full diagnostics, guidance, actual commands, events, normalized
direction inputs and native tables/plots are retained under `analysis_v1/`.
Exact analysis/reference commands, hashes and denominators are saved in
[the completed analysis record](r3_visible_analysis_02.md).

The separate motion audit uses actual odometry and final command exports.
Measured translational speed remains positive through approach, collection and
DESIGN (minimum0.0163,0.00574 and0.00615 m/s respectively). No simultaneous
measured linear/angular speed below0.001 occurs in those intervals. All9419
actual Twist commands match paired diagnostics.final_command. The short zero
command pulses during verification are followed by nonzero commands at the
same diagnostic simulation stamp; their maximum bag-receipt gap is17.66 ms
during collection and25.66 ms during DESIGN. This evidence supports moving
collection without a stopped sensor sweep; do not conceal the zero publications.

The fixed independent direction-reference job completed in6.762 s within45 s.
Of24 scheduled targets,6 were exposed and18 unexposed;6 references were informative
and5 targets met the state eligibility guard. All5 eligible targets had usable
averaging estimates. Median angular error12.307 degrees, p9034.940 degrees;
all5 improved over the paired instantaneous estimate, median improvement14.209
degrees. These five exposed targets support this development trajectory only.

The original monitor stopped at180 s because Stage A association was false,
despite one complete recovery episode. Its private convergence timestamp used
the78.008 s latest input pose while the committed fill correctly retained the
78.0 s confirmed support endpoint, making the convergence appear8 ms later.
Root diagnosed this from retained exact typed records. Correct the new-mode
private evaluator coordinate prospectively without changing public timestamps,
old centroid semantics, thresholds, budgets or this original failed verdict.
No further simulation or comparison is released by saving this result alone.
