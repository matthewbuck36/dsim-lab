# R7 visible C02 validation

[Adopted plan](../r7_visible_c02_plan.md). One fresh exposed development case;
C01 and V10 failures retained. Source R7 archive564 members verified and332
focused checks passed before adoption. No full comparison released.

Preparation PASS3.766192s, session43362 terminal/reaped0,771 stable pins including
all764 validated pins and21 installed entries. Actual scenario, seed26091011,
selected moving modes/controller, arrival criterion and original budgets reviewed.
Prepared SHA256 `d1de9a41247bb8ee61650a4adcb9741849d17f8166eba8b84f7b067e406e29f8`.
The static scenario comparison permits only six identity/path/description changes;
scientific settings and reference helper remain identical to C01.

External owner: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_02/`.
Exact preparation command:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 85s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_02/prepare_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_02/preparation.log 2>&1'
```

One acquisition, prepared source/helpers held, no unchanged retry:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 415s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_02/run_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_02/acquisition_outer.log 2>&1'
```

Native analysis and24-target reference follow complete recording/cleanup. Their
results, source/input hashes, actual elapsed time and commands will be appended
after execution. No behavioral or direction result exists at this boundary.

## Retained startup failure

C02 CLOSED_INCOMPLETE at startup; session95566 terminal/reaped0,33.076955s.
771 prepared pins stable; inner and outer scoped cleanup PASS. Recording never
reached readiness and is INCOMPLETE; final-zero evidence is unavailable. Upstream
velocity_controller spawner lost a load response, retried, then failed because
the controller was already loaded. No candidate/admission/fill/arrival exposure;
R7 behavior is untested. Native analysis/reference NOT_STARTED because required
recording gate failed. [Failure handoff](r7_visible_c02_handoff.md).

Attempt SHA256 `1ce0d0411a406d2a3be16ba64841fb0daa0c80f2dead964836d43163ac193233`.
Console records load-response failure at23:50:33.578UTC, retry failure at
23:50:43.404UTC, and preflight abort at23:50:43.598UTC. Logs, partial bag,
metadata, completeness and both cleanup receipts remain external. The absent
readiness/final-zero evidence is not relabeled as a passing recording.

C02 closure archive PASS566 members verified0.917217s, manifest SHA256
`883cf0eb66a0ae176b520b499565946160d5be685fdb02cb2bade15c6e5bba83`
at external `checkpoints/r7_c02_closed_startup_failure_v1/`. Receipt postdates
the immutable archive; original evidence and source remain unchanged.
