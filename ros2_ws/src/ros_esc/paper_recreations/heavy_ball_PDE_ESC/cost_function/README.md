# Active HeavyBall Cost Function Configs

Only cost maps used by active Gazebo launch paths live in this folder.

```text
2D_local_min.json                      # original hard two-basin map
multi_light_source_photoresistor.json  # multi-light rotating photoresistor map
```

Retired sweep and baseline-report cost maps live in:

```text
~/dsim-lab/docs/heavy_ball_PDE_ESC/archive/cost_function/
```

`multi_light_source_photoresistor.json` selects `Multi_Light_Source_Cost`.
That class is the multi-light rotating-sensor photoresistor model; the older
`Photoresistor_Interpolated_Map` remains the single-light legacy model. JSON
defaults are useful for standalone cost-node tests, but Gazebo runs normally
override the source list with `number_of_lights` and `light_N_*` launch
arguments so the visible light markers and the cost map stay aligned. Lumens are
relative to `reference_intensity_lumens`, not an absolute photometric
calibration.
