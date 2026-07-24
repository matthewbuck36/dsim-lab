# Data Collection and Rosbag Specification

## Principle

For every software transformation, record the input and the output.

The minimum traceable chain is:

```text
sensor measurement
→ raw cost
→ normalized source score
→ Gaussian contribution
→ affine contribution
→ augmented cost
→ GESC internal estimate
→ unsaturated command
→ supervisor contribution
→ final saturated command
→ measured robot motion
```

## Authoritative data source

- Structured ROS topics and rosbag2 are authoritative.
- Console messages are diagnostic convenience.
- Terminal output must never be the only place an event or parameter exists.

## Common time base

- Simulation uses ROS simulation time consistently.
- Physical runs use the configured ROS clock consistently.
- Every custom message contains a header or timestamp.
- Static run metadata includes both wall-clock and ROS start time.
- Timestamp regression or mixed-clock use is a run failure.

## Required data categories

### Sensor and cost

- raw ADC/light measurement,
- filtered sensor value,
- raw minimization cost,
- calibrated source score,
- Gaussian contribution,
- affine contribution,
- augmented cost,
- individual component weights.

### Gaussian/fill manager

- fill ID and cluster ID,
- center,
- amplitude,
- covariance,
- principal widths,
- support radius,
- exit radius,
- active/inactive/superseded status,
- confidence,
- sample count,
- fit residual,
- fit condition number,
- design-escalation count,
- merge event.

### State and events

- state machine mode,
- state entry timestamp,
- transition reason,
- convergence event,
- goal verification event,
- local-minimum event,
- fill creation/update event,
- escape start,
- stall,
- assisted escape,
- escape success,
- recenter start/complete,
- timeout,
- failsafe.

### Control

- GESC internal gradient/demodulation/filter values already available,
- controller gains,
- dither phase/amplitude/frequency,
- command before saturation,
- command after saturation,
- velocity saturation flags,
- supervisory contribution,
- final command.

### Robot and environment

- pose,
- yaw,
- measured velocity,
- Vicon pose,
- odometry,
- TF and TF static,
- environment bounds,
- room center,
- source configuration for evaluation,
- simulation seed,
- collision/contact data if available.

## Topic manifest

Phase 01 maps these concepts to existing topic names. Phase 05 writes a repository-specific `topic_manifest.yaml`.

The recording launcher must:

1. Load the manifest.
2. Query live topic names and types.
3. Fail before motion if a required topic is absent.
4. Record optional topics when present.
5. Save the resolved topic list into run metadata.

## Rosbag storage

Use the ROS 2 Humble storage backend already available in the environment. Do not add an external bag dependency solely for this work.

Use one run directory per trial:

```text
runs/<date>/<run_id>/
├── bag/
├── metadata.yaml
├── resolved_parameters.yaml
├── resolved_topics.yaml
├── console.log
├── completeness.json
└── notes.md
```

## Metadata requirements

- run ID,
- date/time,
- Git commit,
- Git branch,
- dirty state and diff hash,
- simulation or physical mode,
- algorithm profile,
- scenario ID,
- random seed,
- source positions and levels,
- robot starting pose,
- launch command,
- parameter-file paths,
- resolved parameters,
- host and ROS distribution,
- bag start/end,
- human intervention flag,
- operator notes.

## Run completeness validation

A run is invalid unless:

- all required topics exist,
- each required topic has at least one message,
- time ranges overlap sufficiently,
- state and command topics cover the motion interval,
- raw and augmented costs are present,
- pose is present,
- final zero command appears at shutdown,
- metadata is complete.

## Console requirements

Mirror major state transitions with throttled, readable logs. Example:

```text
[47.212] VERIFY_EXTREMUM entered
[50.226] Local minimum accepted for fill design
[50.241] Fill cluster 3 updated: A=0.82, sigma=(0.44,0.31)
[50.245] ESCAPE_REPULSE entered; raw-cost weight=0
[54.003] Escape stalled; redesign escalation=1
[54.020] ESCAPE_ASSIST entered
[58.331] Escape complete; distance=1.12 m
```

The same information must also exist in structured topics.

## Data retention policy

- Retain raw bags.
- Do not delete a bag after CSV export.
- Store analysis outputs beside the bag.
- Never overwrite a run ID.
- Parameter changes create a new experiment version.
