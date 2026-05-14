# HeavyBall Cost Function Configs

Cost maps are grouped by family instead of kept in one flat folder.

```text
gaussian_two_basin/
  original_local_min.json       # original hard two-basin map
  shallow_local_A1p0.json       # local-well amplitude sweep
  shallow_local_A2p0.json
  shallow_local_A3p0.json
  wide_global_W25.json          # widened global-basin sweep
  wide_global_W30.json
  wide_global_W40.json

polynomial/
  quadratic_bowl_center10.json
  quartic_bowl_center10.json
  quartic_double_well_2_10.json
```

Scenario files should reference these paths directly through
`cost_function_config_filepath`.

