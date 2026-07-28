# Phase 08.4 Simulation Validation Report

Outcome: **FAIL**.

Contract: `None`.

## Gates

- `context_qualification`: FAIL; value `{'prepare': True, 'qualification': True, 'freeze': None, 'contract': None, 'errors': ['v3 development state is missing', 'v3 freeze state is missing', 'v3 contract state is missing', 'v3 holdout state is missing', 'v3 validation state is missing', 'v3 reproducibility state is missing', 'tracked v3 acceptance contract is missing', "v3 prepare artifact invalid: 'transaction_path'"]}`; threshold `complete verified prepare/qualification/freeze/contract chain`.
- `activation`: FAIL; value `0`; threshold `10/10`.
- `development_freeze`: FAIL; value `None`; threshold `one eligible winner plus verified freeze and contract`.
- `holdout`: NOT RUN; threshold `>=18/20 and exact family floors`.
- `contract_population_binding`: NOT RUN; threshold `fixed acceptance contract`.
- `completeness_analysis_integrity`: NOT RUN; threshold `fixed acceptance contract`.
- `behavior_contracts`: NOT RUN; threshold `fixed acceptance contract`.
- `end_to_end`: NOT RUN; threshold `fixed acceptance contract`.
- `family_floors`: NOT RUN; threshold `fixed acceptance contract`.
- `local_escape`: NOT RUN; threshold `fixed acceptance contract`.
- `escape_duration`: NOT RUN; threshold `fixed acceptance contract`.
- `orbit_count`: NOT RUN; threshold `fixed acceptance contract`.
- `revisit`: NOT RUN; threshold `fixed acceptance contract`.
- `lifecycle_coverage`: NOT RUN; threshold `fixed acceptance contract`.
- `disturbance_constraint_evidence`: NOT RUN; threshold `fixed acceptance contract`.
- `metric_applicability`: NOT RUN; threshold `fixed acceptance contract`.
- `reproducibility`: NOT RUN; threshold `10/10 comparisons`.

Retained evidence root: `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b`.

No physical hardware was run.
