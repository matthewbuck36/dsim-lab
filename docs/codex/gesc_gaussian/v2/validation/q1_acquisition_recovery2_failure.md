# Q1 recovery2 acquisition closure — 2026-09-09 UTC

The fixed acquisition is CLOSED INCOMPLETE. Only discovery residence seed26090911
was dispatched; the remaining three cases and all scientific confirmation
analysis remain unopened. No scientific threshold or trajectory performance
was evaluated for this diagnosis.

The run recorded the requested125 simulated seconds, remained in SEARCH, and
passed forbidden-event/state, source synchronization, lifecycle, diagnostic
coverage, final-zero, clean shutdown and cleanup checks. It failed the sole
completeness check `algorithm_event_producer_identified`: one CONFIG event at
bag receipt1788950708912816613 has detail
`centroid_windows_v2 source-time configuration`. Acquisition elapsed154.980014413s;
the existing runner stopped subsequent dispatch. Zero qualified inputs were
published. Recording duration completion does not override failed completeness.

The existing detector emits this exact configuration signature. AlgorithmEvent
has no producer field; the shared-bus validator recognizes configuration owners
through explicit signatures and only lists the inherited detector spelling.
This omission is an attribution defect in the validator. The event must enter
the detector's timestamp stream after recognition; ignoring unknown events or
skipping regression/freshness checks would weaken the contract.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery2/`.
Run: `runs/2026-09-09/q1-primary-shadow-v1-recovery2-discovery-residence-26090911/`.
Read-only evidence: `completeness.json`, `metadata.yaml`, `scenario_result.yaml`,
and `acquisition/acquisition.json`. The exclusive `acquisition_closed.json`
binds15 retained files including the original bag and failed reports; SHA256
`7dea4e42af6acb843b3b896f7928e20705c65521d4757d9b13ba34e0053e6335`.
Never overwrite those outcomes or restart this acquisition identity.

Permitted next work is the narrow validator correction and its independent
regressions under `q1_event_attribution_plan.md`. No runtime tuning or source
clock/graph change is justified by this failure.
