# R7 approach runtime validation

The [adopted runtime plan](../r7_approach_runtime_plan.md) nominates fixed-center
approach before immutable collection admission. The retained ideal prototype
supports approach margin only; it did not reproduce actual C01 failure.

Current boundary: SOURCE_VALIDATED. No C02 preparation/acquisition has run.

External owner:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_runtime_validation_v1/`.
The named selection in `tests_v1.json` combines two new R7 modules with existing
centered guidance/runtime, controller/supervisor, R5 and R6 regressions. It uses
actual source owners and generated interfaces. No model rerun or bag decode.

Planned single bundle after source/tests are held and reviewed:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 255s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_runtime_validation_v1/validate_source.py --version focused_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_runtime_validation_v1/tests_v1.json > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r7_runtime_validation_v1/focused_outer_v1.log 2>&1'
```

The existing helper records complete logs/JUnit, source/test/helper hashes and
all21 installed bindings before and after. Pytest work is bounded to240s within
260s total. Exact outcomes, elapsed time, review and archive receipts follow
after completion. Passing source tests alone cannot release a comparison.

## Final result

R7 SOURCE_VALIDATED:332 unique checks PASS52.822781s (pytest50.58s),
764 stable pins and21 unchanged installed bindings; session89193 terminal/reaped0.
[Source handoff](r7_approach_runtime_handoff.md) records the two-owner change and
independent review. Receipt SHA256
`7251d316bcecd729ebd97df716035e2d6a3d9528574766b7959dcc1313995118`.
No new acquisition or empirical qualification. Next source checkpoint, then
adopt and prepare the already-reviewed C02 draft. Source/test files remain held.

All20 new cases (5 main,15 adversarial) and312 selected prior regressions passed.
The generated supervisor guidance and actual controller output match the retained
C01 prototype first command. Admission, original circular phase, re-entry, DESIGN,
R5/R6, invalid input, bounds/fill/freshness and legacy paths passed. Exact two-owner
diff, before files, C01 anchor and held hashes are retained in the external owner.
Root reviewed both diffs and test modules; independent detector_audit review found
no blocker. No existing test was changed, and no source edit followed validation.

R7 source archive PASS:564 members verified0.888729s; manifest SHA256
`ba29d5b2dfe05166e1cc35fc740f93feb49cea5c67c0261ca15886963d7e0fae`
at external `checkpoints/r7_approach_runtime_source_v1/`. This receipt postdates
the immutable source archive. Source/test files remain unchanged.
