# HeavyBall Cost Function Configs

All cost maps live directly in this folder. Filenames start with the cost family
so scenario files can stay readable without nested cost-map directories.

```text
gaussian_two_basin_original.json       # original hard two-basin map
gaussian_two_basin_localA1p0.json      # local-well amplitude sweep
gaussian_two_basin_localA2p0.json
gaussian_two_basin_localA3p0.json
gaussian_two_basin_globalW25.json      # widened global-basin sweep
gaussian_two_basin_globalW30.json
gaussian_two_basin_globalW40.json

polynomial_quadratic_bowl_center10.json
polynomial_quartic_bowl_center10.json
polynomial_quartic_double_well_local2_global10.json

multi_light_source_photoresistor.json  # multi-light rotating photoresistor map
```

Scenario files should reference these paths directly through
`cost_function_config_filepath`.

`multi_light_source_photoresistor.json` selects `Multi_Light_Source_Cost`.
That class is the multi-light rotating-sensor photoresistor model; the older
`Photoresistor_Interpolated_Map` remains the single-light legacy model. JSON
defaults are useful for standalone cost-node tests, but Gazebo runs normally
override the source list with `number_of_lights` and `light_N_*` launch
arguments so the visible light markers and the cost map stay aligned. Lumens are
relative to `reference_intensity_lumens`, not an absolute photometric
calibration.
