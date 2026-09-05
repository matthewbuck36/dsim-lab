# Topic and Message Data Contract

Phase 00 must map these logical interfaces to the repository's actual conventions.

Do not force these literal topic names when the repository already has established names. Preserve meaning and fields.

## Logical message: CostBreakdown

Required fields:

```text
timestamp
raw_sensor_value
filtered_sensor_value
raw_cost
source_score
gaussian_cost
affine_cost
augmented_cost
sensor_weight
gaussian_weight
affine_weight
validity flags
```

## Logical message: AlgorithmState

Required fields:

```text
timestamp
run_id
state enum/string
previous_state
transition_reason
state_elapsed_sec
active_fill_count
active_escape_fill_id
sensor_weight
gaussian_weight
affine_weight
failsafe flag
```

## Logical message: GaussianFill

Required fields:

```text
timestamp
fill_id
cluster_id
revision
center_x
center_y
amplitude
covariance_xx
covariance_xy
covariance_yy
sigma_major
sigma_minor
orientation
support_radius
exit_radius
confidence
sample_count
fit_residual
fit_condition_number
design_escalations
active
superseded
```

## Logical message: AlgorithmEvent

Required fields:

```text
timestamp
event type
state
fill ID
numeric reason code
human-readable detail
optional numeric values
```

## Logical control topics

Required concepts:

```text
GESC command before saturation
supervisory/escape contribution
combined command before saturation
final command after saturation
measured command/velocity feedback
saturation flags
```

## Logical environment topics

Required concepts:

```text
canonical pose
canonical velocity
wheel odometry for physical control
IMU data required by the physical stack
Vicon pose only as an optional evaluation/recording topic, never control
TF
room bounds
room center
source configuration for evaluation
collision/contact signal when available
```

## Interface-package decision rule

1. If the repository already has a custom interface package, add new message definitions there.
2. Otherwise create one interface-only package using the repository's prefix and naming pattern.
3. Do not place generated message code directly in an algorithm package when a dedicated interface package exists.
4. Preserve existing message fields and add versioned fields/messages when required for compatibility.
