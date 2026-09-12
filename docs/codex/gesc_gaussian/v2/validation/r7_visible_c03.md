# R7 C03 startup selection and visible validation

[Prospective C03 plan](../r7_visible_c03_plan.md). C02 remains closed incomplete;
its retained startup error led to selection of an existing idempotent load route.
No production source or algorithm setting is changed. Existing R7 source tests
and hashes remain authoritative, supplemented by two existing startup modules.

External owner: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/`.
The installed-route audit is `startup_route_audit_v1.json`: the load request
succeeded server-side in C02 but lost its response; the default upstream retry
failed on already-loaded state. The optional wrapper issues one load request,
confirms loaded after response loss, and retains upstream configure/activation
checks. Existing45s preflight/420s root caps remain authoritative.

No startup validation, preparation or runtime has run at this draft boundary.
Exact commands and terminal receipts will follow. Both the332-case R7 receipt
and the startup receipt must pass unchanged and be pinned by C03 preparation.

## Validated and prepared boundary

C03 startup validation PASS38 checks7.416883s (session8757 terminal/reaped0),
766 stable pins/21 entries. Preparation PASS3.842385s (session84696 terminal0),
776 stable pins combining both source receipts. Actual recovery override=True
and arrival-only criterion verified. Prepared SHA256
`f13c7a2b82df163e10b7d48470ddc60a197a55254a52ad4e0cd1a303eb3e4682`.
Next sole visible acquisition under420s; source/helpers held, no V11 release.

Startup receipt SHA256 `905e1ed0a19b4a5066c404c6351bed4ddabd30ebed8c78fc7fb0161b387f927f`.

Startup validation:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 55s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/validate_startup.py --version startup_validation_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/startup_tests_v1.json > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/startup_validation_outer.log 2>&1'
```

Preparation:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 85s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/prepare_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/preparation.log 2>&1'
```

Single acquisition:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 415s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/run_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/acquisition_outer.log 2>&1'
```

## Acquisition result

C03 acquisition terminal/reaped session67868,234.281428s; recording/inner+outer
cleanup PASS and776 prepared pins stable. Frozen behavior FAIL:8/12 predicates;
full required state/event path and ownership/safety pass, but fill association
unassigned (local-recovery/cardinality fail), so StageA expired and arrival was
not admitted by evaluator. No verdict rewrite. Native two-scan analysis ACTIVE
session10152,110s work/120s max; do not duplicate. Read analysis_v1 receipts.

Attempt SHA256 `3b18ccfa8029b73a919072eac4e478a6e2f987ead969ebcd8686e750c3d0ad5e`.
Readiness was observed23:57:27.157385UTC. One actual full escape episode and
restored SEARCH are recorded; assignment failure remains under read-only audit.

## Completed native and reference evidence

C03 acquisition/native/reference all terminal/reaped (67868/10152/57790).
Complete recording and both cleanup PASS234.281428s; native COMPLETE72.273257s,
source/input pins stable; full continuous VERIFY+DESIGN observed. ReferencePASS
6.248689s,4 eligible/24 scheduled,median10.8613deg/P9020.3482deg,4/4 improved.
Actual final global distance0.256424m after fill/escape/SEARCH satisfies the user
arrival objective. Frozen evaluator stillFAIL8/12 because public PDEevent85.0s
is later than typedconfirmation/fill support84.927s, preventing local association.
Original verdict retained. Next strict private evaluator timestamp correction
and separate cached reevaluation; no production edit or V11 release yet.

Native receipt SHA256 `dcd42a06af70f012a6d425d1fe0f0062726377f3d04efad893ec09661468105b`.
Exactly two scans completed11.878723s and10.506583s. Native lifecycle valid/errors[];
all measurement checks pass. Motion receipt
`f714f8df5afdd2d03d5c96e4c56cb6db4a1169684eb173390f4257b3708328b6`.
Actual10822 command/diagnostic pairs, no pairing errors. VERIFY85.1–99.6s:
426 poses/0.551672m; initial DESIGN99.6–100.2s:18 poses/0.014895m. Both have
positive motion, full coverage, no sustained stationary/zero-command interval.
166/881 VERIFY and5/38 DESIGN zero publications remain recorded; zero pulses
sharing a ROS timestamp are not claimed to have physically zero wall duration.

Candidate accepted85.0s; collection admitted91.6s within the8s budget. One fill
committed100.0s, both ACKs100.1s, REPULSE100.2s, ASSIST104.2s, SEARCH123.0s.
Final position(3.4085975504471553,3.73958063764101), global distance0.256424042782m.
The original arrival metric remains false due to its StageA association gate;
it does not erase the observed final position. GOAL_HOLD is optional.

Reference receipt SHA256 `9f55aaabe0ee591c90a477be3378c5a76324082f0c91f80ddc867b478e210552`;
result SHA256 `58671751c0ddd2374ad6836ce57371419ba3efeecb0513d97353dd97c48eaeb2`.
24 scheduled,5 exposed,19 unexposed,4 eligible/usable/paired averages. All4 improve,
none degrade; median paired improvement45.100550deg, averaging availability1.0.
Reference is stationary-position observed-phase GESC, not a full spatial gradient.
This is selected exposed development evidence, not broad direction qualification.
Nine native figures retained; trajectory_sources_fills.png visually inspected.

Exact analysis commands:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 115s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/analysis/run_analysis.py --run-directory /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/runs/2026-09-10/v2_method_development_C_20260910_03 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/analysis_v1 --expected-run-id v2_method_development_C_20260910_03 > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/native_analysis_outer.log 2>&1'
```

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 40s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/analysis/run_direction_reference.py --analysis-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/analysis_v1 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/direction_reference_v1 > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_03/direction_reference_outer.log 2>&1'
```

C03 source/evidence archive PASS570 members1.475846s; manifest SHA256
`a5bd6d63a6a836e51d39ce97968d144a47a5623810679150a36902995d93d73e`
at external `checkpoints/r7_c03_observed_arrival_v1/`. Cached association audit
postdates that archive: `cached_association_audit_v1.json`,21 stable input/source
hashes, SHA256 `d13c094540488a69c10ce65f7e6269ae736e761f44271791c801dd28b746ac33`.
All6 reviewed source pins match C03 preparation/native receipts.
