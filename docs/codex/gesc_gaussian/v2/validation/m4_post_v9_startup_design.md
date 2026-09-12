# Post-V9 startup recording design findings

Status: DESIGN FINDINGS ONLY, 2026-09-10 UTC. No startup source correction,
middleware profile or integration job is adopted by this note. D2 monitor work
is the current implementation milestone. This records bounded independent
reviews following the materially closed [D1 diagnostic](m4_post_v9_integrity.md).

D1 proves missing recorded startup companions for the first21 objectives. It
does not prove an exact DDS delivery cause. Original console messages already
advertised raw/provenance subscriptions before the first recorded objective.
Therefore moving subscription registration before target startup cannot alone
establish the missing delivery guarantee.

## Admission approaches ruled insufficient

Installed Humble exposes `Publisher.get_subscription_count()` as an aggregate
matched-reader count and `Node.get_subscriptions_info_by_topic()` as graph
endpoint identities. It does not expose a publisher's matched reader GIDs.
Another consumer can satisfy count>0. Equality with a graph population depends
on graph completeness and is still not an exact recorder-match proof.
`wait_for_all_acked()` concerns currently matched reliable readers collectively;
it is neither an exact recorder identity check nor persisted bag acknowledgement.
The existing motion-ready Bool cannot gate initial objective publication because
operational readiness itself depends on valid objective/source/filter heartbeats.

A hypothetical stronger data-independent producer fence could avoid that cycle,
but without recorder-specific acknowledgement it still leaves a matching-proof
gap and changes the first sampled transform/noise evaluation. Do not add fixture-
only publisher waits, discard valid startup objectives or waive full-bag joins.

## Candidate: selected bounded transient-local retention

A future default-off selection could make the existing exact cost-stream
publishers offer reliable/transient-local history, while rosbag explicitly
requests matching durability/history/depth on the resolved topics. This preserves
past publications for a late matching recorder within retained writer history.
Existing volatile algorithm subscriptions remain unchanged. In particular,
making delay-relay inputs durable would replay historical inputs into control
and is outside this proposal; only its selected output publishers need retention.

This is a retention mechanism, conditional on writer lifetime, resource capacity
and successful bag finalization. It is not a persisted-data acknowledgement.
Installed rosbag automatic QoS adaptation does not inherit offered history depth;
recorded selected overrides must request it explicitly. Full-bag identity,
exact-key and per-writer sequence/revision checks remain authoritative. The
current synchronized-stream validator permits arbitrary cross-topic bag arrival
order, so historical delivery does not require changing those joins or stamps.

The proposed40000 samples per writer is an explicit new capacity bound, not a
deduction from observed30Hz publication. Source publication is admission/callback
driven. A coherent implementation must reserve before every publication,
including provenance invalidations, and fail before eviction/publication40001.
Counters cannot silently reset or clip. Variable arrays/JSON also need a concrete
payload bound, retained metadata and actual largest-admitted-payload verification.

Installed FastDDS2.6.12 header defaults have max_samples5000,
max_samples_per_instance400 and allocated_samples100. The RMW depth conversion
does not alone set these limits; unkeyed KEEP_LAST uses depth in parts of its
history implementation. Neither a QoSProfile(depth=40000) nor header defaults
alone establish effective capacity. A future plan must bind a process-local,
topic-specific resource profile or equivalent verified effective limits, retain
the actual middleware identity and test the intended capacity. No global/default
XML or physical setting is changed by this design.

Overflow must reach the existing recorder's integrity-failure owner. A nested
algorithm exception can leave `ros2 launch` alive. The duration loop currently
checks launch-root/bag exits, whereas the existing console collector also records
nested process failures. A selected fatal-error cancellation path can reuse that
owner; raising in the producer alone is insufficient. Writer lifetime must
continue through recording finalization or its loss must remain a failed run.

Before adoption, resolve exact owners/parameter selection, per-topic XML/QoS
behavior, payload/capacity bounds and tests. Required finite actual-DDS cases
include recorder starting after a published prefix with another subscriber
already matched; sequence1 and every later objective companion retained without
retransmission; overlapping history/live delivery and delayed output;
small-cap exact-limit success/next-publication failure; production capacity;
wrong recorder QoS; writer exit; retained fatal reason and bounded cleanup.
Default/physical/legacy QoS and algorithm inputs must retain current behavior.
No original bag is reread and no V9 result is reclassified for this validation.

Primary references inspected by the independent reviewer:

- Installed `/opt/ros/humble/local/lib/python3.10/dist-packages/rclpy/publisher.py`
  and `/opt/ros/humble/include/rmw/rmw/rmw.h` for API proof limits.
- Installed `/opt/ros/humble/include/rosbag2_transport/rosbag2_transport/qos.hpp`
  for recording QoS adaptation.
- [Fast DDS durability semantics](https://fast-dds.docs.eprosima.com/en/v2.6.11/fastdds/dds_layer/core/policy/standardQosPolicies.html#durabilityqospolicy).
- [Humble RMW QoS conversion](https://raw.githubusercontent.com/ros2/rmw_fastrtps/humble/rmw_fastrtps_shared_cpp/src/qos.cpp).
- [FastDDS2.6.12 writer history](https://raw.githubusercontent.com/eProsima/Fast-DDS/v2.6.12/src/cpp/fastdds/publisher/DataWriterHistory.cpp).

No source edit, ROS call, test or bag read occurred in these design reviews.

## Concrete process/profile routing for a future amendment

Further installed-version source inspection resolves named profile routing:
RMW FastRTPS6.2.10 publisher/subscription creation looks up the fully resolved
ROS topic FQN (leading `/`), not its `rt/` DDS mapping or a node/GID. Named
profiles load independently of `RMW_FASTRTPS_USE_QOS_FROM_XML`. A target-only
writer XML and bag-only reader XML, passed through separate copied child
environments with `FASTRTPS_DEFAULT_PROFILES_FILE`, can avoid changing algorithm
reader resources. Keep the XML-mode switch unset/0 and publication mode unchanged;
this retains the RMW's reallocating memory policy, synchronous publication and
disabled data sharing. Bind actual rmw_fastrtps_cpp and reject conflicting
inherited/default profile sources before release. Do not include any default,
participant, service or client profiles.

For each selected cost topic, prospective resource fields are
max_samples40000, max_instances1, max_samples_per_instance40000,
allocated_samples100 and extra_samples1. ROS publisher QoS and recorder YAML
separately request reliable/transient-local/KEEP_LAST/depth40000. Actual installed
capacity remains a required integration result, not established by this note.

The minimal cost population is three writers for stationary A/B (raw, source
CostBreakdown, augmented), adding provenance and atomic objective for moving C/D.
Sensor-delay routes replace raw/source/provenance with final delayed output
writers; upstream and relay-input QoS can remain unchanged. The existing owners
are cost_function_node, modified_cost_node/V2ObjectiveComposer and
SimulationDisturbanceNode. Retention must reserve queued relay data at enqueue,
so pending plus published cannot exceed the explicit capacity.

Timekeeper is repeated immutable origin/mode, not a per-sample exact companion.
If the future guarantee includes its late-recorder origin, the existing
rotate_frame_node Timekeeper publisher can retain depth1 with matching reader
capacity1, keeping its existing timer and rejecting changed origin/mode. This
gives four selected topics in stationary arms and six in moving arms without
retaining40000 equivalent origin heartbeats.

A prospective common mode/descriptor would be resolved after scenario overrides,
forwarded by existing launch/metadata owners to the relevant publishers, and
verified by record_run before retaining selected XML/YAML files. An optional
child-environment argument on existing `_process` can keep coordinator/global
environment unchanged. A small shared helper inside the existing recording
package can provide selected QoS, reservations, serialized-size admission and
explicit fatal publication failures; this is not a new node or data pipeline.

The review proposed raw/augmented256-byte, source/provenance1024-byte,
objective4096-byte and Timekeeper128-byte serialized ceilings for initial
fixture review. These are not adopted supported limits. Actual longest admitted
identities, selected objective/fill configurations and payloads must determine
adequate declared ceilings before a production release. Count and byte bounds,
overflow, serialization/publish errors and writer lifetime all require retained
failure/cleanup evidence. No source edit, profile generation or test occurred.

Version-specific references:
[publisher profile lookup](https://raw.githubusercontent.com/ros2/rmw_fastrtps/6.2.10/rmw_fastrtps_cpp/src/publisher.cpp),
[reader profile lookup](https://raw.githubusercontent.com/ros2/rmw_fastrtps/6.2.10/rmw_fastrtps_cpp/src/subscription.cpp),
[XML resource fields](https://fast-dds.docs.eprosima.com/en/v2.6.11/fastdds/xml_configuration/common.html).
