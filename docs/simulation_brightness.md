# Simulated light brightness

Use **brightness percentage (0–100)** for new simulated light configurations.
The nominal bulb maximum is 1600 lumens, so the existing light model receives:

```text
nominal_lumens = 1600 × brightness_percent / 100
```

| Brightness | Nominal model input |
|---|---:|
| 0% (off) | 0 lumens |
| 25% | 400 lumens |
| 50% | 800 lumens |
| 75% | 1200 lumens |
| 100% | 1600 lumens |

This is a linear simulation assumption based on the requested 1600-lumen bulb.
It is not a measured calibration of the Hue app's dimming curve, bulb color/
temperature, or photoresistor response. Lumens describe light output; watts
describe power. [Philips Hue lists 1600 lumens as maximum brightness](https://www.philips-hue.com/en-us/p/hue-white-100w-a21-e26-smart-bulb/046677591076).

## Gazebo launch settings

For a launch using `Multi_Light_Source_Cost`, set:

```text
number_of_lights:=2
light_1_x:=1.0 light_1_y:=0.5 light_1_brightness_percent:=25.0
light_2_x:=3.5 light_2_y:=3.5 light_2_brightness_percent:=100.0
```

The same setting is available for `light_1` through `light_5`. Explicit
percentages override that light's legacy lumen argument/default. An omitted
percentage uses the `legacy` compatibility sentinel and retains the old
behavior. For new Hue-style runs, set the percentage of every enabled light.
NaN, infinity, negative percentages, and percentages above 100 are rejected;
they are never silently clamped.

The rendered Gazebo lamps remain position markers. The simulated sensor's
brightness response comes from the Python cost model; this change does not
implement optical ray tracing or dim the SDF marker graphics.

## Scenario YAML and cost JSON

Use this in a scenario's existing `sources` list:

```yaml
- id: local
  x_m: 1.0
  y_m: 0.5
  brightness_percent: 25.0
  evaluation_role: local_minimum
- id: goal
  x_m: 3.5
  y_m: 3.5
  brightness_percent: 100.0
  evaluation_role: goal
```

The complete [percentage example](../ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/brightness_percent_example.yaml)
is installed with the scenario runner. After building and sourcing the
simulation workspace, validate and preview it without launching Gazebo:

```bash
timeout 30 ros2 run ros_esc run_scenario \
  ~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/brightness_percent_example.yaml \
  --operator "$USER" --dry-run \
  --runs-root /tmp/dsim-brightness-preview
```

This is an infrastructure example with a finite 30-second simulated duration,
not an accepted behavioral experiment or a continuation of a frozen suite.

For `Multi_Light_Source_Cost` JSON, its `light_sources` parameter accepts:

```json
[
  {"x": 1.0, "y": 0.5, "brightness_percent": 25.0},
  {"x": 3.5, "y": 3.5, "brightness_percent": 100.0}
]
```

Specify exactly one unit per source in YAML/JSON. The surface plotter accepts
matching `--light_source_N_brightness_percent` CLI flags and labels percentage
lights with `%`. Resolved scenarios and recorded metadata retain both the
requested percentage and the derived internal nominal intensity. Source
configuration events likewise record `source_N_brightness_percent` alongside
the existing intensity field.

## Historical compatibility and evidence

Old `intensity_lumens`, `relative_lumen_input`, level maps, and
`light_N_intensity_lumens` settings remain supported. Historical inputs above
1600 retain their original values; they do not describe a 0–100% setting of
the new nominal bulb. Frozen scenarios, old wrappers, reports, and results
have not been rewritten.

The existing `reference_intensity_lumens` fitted-curve normalization is
unchanged. Percentage-to-lumen conversion occurs at the simulation input
boundary, so equivalent inputs produce the same cost surface. Controller
cost signs/units, Gaussian/supervisor behavior, physical sensing, and snapshot
files are unchanged. This interface change establishes no new simulation or
physical robustness result.

Implementation and validation are recorded in the
[interface status](codex/gesc_gaussian/status/simulation_brightness_percent_status.md).
