# R6 verification expiry source validation

[Adopted plan](../r6_verification_expiry_plan.md). Current boundary: unchanged
controller regression and bounded source correction are being prepared.
No R6 final source validation or new simulation has run.

Baseline evidence owner:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r6_verification_expiry_v1/`.
Final validation owner:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r6_validation_v1/`.
Both extend existing real controller/generated-message fixtures and source
validation helpers. No new recorder, analyzer, interface or runtime node.

The named bundle is saved in `r6_validation_v1/tests_v1.json`: new main and
adversarial R6 regressions plus existing V2 controller, Q1 controller clocks,
centered guidance/runtime, both R5 handoff suites and V2 supervisor tests.
Root will execute once after all source/tests are held and reviewed:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 255s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r6_validation_v1/validate_source.py --version focused_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r6_validation_v1/tests_v1.json > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r6_validation_v1/focused_outer_v1.log 2>&1'
```

The helper binds source and all21 installed entries before/after, bounds pytest
to240s work and retains JUnit, complete logs and an exclusive receipt. Exact
baseline/final sessions, outcomes, times, hashes and limitations will be recorded
after their terminal receipts. Source tests cannot establish approach feasibility
or scientific direction quality; those C01 failures remain separate.

## Unchanged-controller baseline

R6 unchanged-controller baseline REPRODUCED in1.757365s: valid79.0 VERIFY
guidance expired79.1, actual zero plus erroneous hard fault;128 source/runtime
pins and21 installedbindings stable. Session25015 terminal/reaped, isolated
fixture domain218 cleaned up. Baseline result SHA256
`7a1751b3069518f82790897d541bbdf496adc771aa406ea65d1156925ec40475`.
Bounded controller correction is now in progress; no finalbundle/newruntime.

Retained path: `r6_verification_expiry_v1/baseline_v1/result.json`; exact helper,
outer log and execution receipt remain external. This is an actual controller
fixture, not a Gazebo run or replay of every physical sample.

## Final bundle and review

R6 SOURCE_VALIDATED:312 unique focused checks PASS50.074988s (pytest47.80s),
762 sourcepins/21 installedbindings unchanged; session10905 terminal/reaped.
Independent static review PASS; [source handoff](r6_verification_expiry_handoff.md).
Receipt SHA256 `3f182a9572f346317c086b1c456d386a2b47fc9d0c91b71e5ac1d022bb975e96`.
No application runtime active. Next source archive, then adopt R7 bounded approach
prototype. No arrival/direction qualification or V11 comparison release.

All65 new cases (14 main,51 adversarial) and247 selected existing regressions
passed. Exact source diff, before-controller, source-ready binding and baseline
fixture copy are preserved under `r6_verification_expiry_v1/`; its baseline
fixture copy exactly matches the original receipt hash. The independent review
confirmed zero output at all authorization paths, hard-fault checks continuing
past the wait, original lease identity and legal delayed admission, and reset
only after admitted non-VERIFY state. No code changes followed the passing job.
