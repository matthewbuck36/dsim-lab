"""Pure typed centroid evidence checks shared by runtime and recording.

This retains the canonical recorded arithmetic/support contract. Live receipt,
SEARCH authorization and historical-candidate lifetime belong to the adapters.
"""

import math


CENTROID_WINDOWS_V2 = 'centroid_windows_v2'
CENTROID_TWO_BLOCK_V2 = 'centroid_two_block_v2'
CENTROID_METRIC_MODES = (CENTROID_WINDOWS_V2, CENTROID_TWO_BLOCK_V2)


def centroid_score(centroids, metric_mode=CENTROID_WINDOWS_V2):
    """Score six oldest-first equal-duration means in metres by explicit law."""
    if metric_mode not in CENTROID_METRIC_MODES:
        raise ValueError('unsupported centroid metric mode')
    if len(centroids) != 6 or any(len(point) != 2 for point in centroids):
        raise ValueError('centroid score requires six two-dimensional means')
    if not all(math.isfinite(value) for point in centroids for value in point):
        raise ValueError('centroid score requires finite means')
    if metric_mode == CENTROID_WINDOWS_V2:
        return math.fsum(math.hypot(new[0] - old[0], new[1] - old[1])
                         for old, new in zip(centroids, centroids[1:]))
    older = tuple(math.fsum(point[axis] / 3 for point in centroids[:3])
                  for axis in (0, 1))
    newer = tuple(math.fsum(point[axis] / 3 for point in centroids[3:])
                  for axis in (0, 1))
    return math.hypot(newer[0] - older[0], newer[1] - older[1])


def _stamp_nanoseconds(stamp):
    return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)


def centroid_diagnostic_errors(
    messages, expected_source_pose_topic=None, supervisor_run_ids=None,
    maximum_source_gap_sec=None, allow_clock_admission=False, expected_frame_id=None,
    pose_freshness_sec=0.5, expected_metric_mode=None,
):
    """Check V2 units, complete support and single confirmation per run/epoch.

    This verifies recorded claims internally; trajectory replay must separately
    establish their numerical/behavioral correctness. Invalid histories may
    carry NaNs but cannot claim eligibility or confirmation.
    """
    try:
        if (isinstance(pose_freshness_sec, bool)
                or not isinstance(pose_freshness_sec, (int, float))):
            raise ValueError('non-numeric pose freshness')
        scaled_freshness = pose_freshness_sec * 1e9
        if (not math.isfinite(scaled_freshness) or scaled_freshness <= 0
                or round(scaled_freshness) < 1):
            raise ValueError('nonpositive or nonfinite pose freshness')
        freshness_ns = round(scaled_freshness)
    except (TypeError, ValueError, OverflowError):
        return ['centroid diagnostic configuration: pose freshness must be finite positive seconds']
    errors = []
    confirmed_epochs = set()
    previous_sequences = {}
    for index, message in enumerate(messages):
        prefix = f'centroid diagnostic {index}: '
        if message is None:
            errors.append(prefix + 'undecodable message')
            continue
        flags = (message.source_valid, message.history_valid,
                 message.metric_valid, message.confinement_valid)
        if message.confirmed and not message.eligible:
            errors.append(prefix + 'confirmation without eligibility')
        if message.eligible and not all(flags):
            errors.append(prefix + 'eligibility without valid source/history/metric/radius')
        if message.metric_valid and not (message.source_valid and message.history_valid):
            errors.append(prefix + 'metric validity lacks source/history validity')
        if message.metric_mode not in CENTROID_METRIC_MODES:
            errors.append(prefix + 'wrong metric mode on centroid diagnostic topic')
        if expected_metric_mode is not None and message.metric_mode != expected_metric_mode:
            errors.append(prefix + 'metric mode differs from selection')
        if (expected_frame_id is not None and message.source_valid
                and message.frame_id != expected_frame_id):
            errors.append(prefix + 'frame does not match selected stream')
        if (not message.source_pose_topic.strip()
                or (expected_source_pose_topic is not None
                    and message.source_pose_topic != expected_source_pose_topic)):
            errors.append(prefix + 'source pose topic does not match selection')
        if message.metric_valid:
            numeric = (message.score_m, message.confinement_radius_m,
                       message.center_x_m, message.center_y_m,
                       message.window_duration_sec, message.epsilon_m,
                       message.maximum_radius_m,
                       message.represented_duration_sec,
                       message.maximum_source_gap_sec, *message.centroid_x_m,
                       *message.centroid_y_m, *message.displacement_m)
            sizes = (message.completed_window_count, len(message.window_start),
                     len(message.window_end), len(message.centroid_x_m),
                     len(message.centroid_y_m), len(message.displacement_m))
            if sizes != (6, 6, 6, 6, 6, 5) or not all(
                math.isfinite(float(value)) for value in numeric
            ):
                errors.append(prefix + 'metric lacks six finite windows and five distances')
                continue
            scaled_times = (
                message.window_duration_sec * 1e9,
                message.maximum_source_gap_sec * 1e9,
                message.represented_duration_sec * 1e9,
            )
            if any(not math.isfinite(value) or value < 1 for value in scaled_times):
                errors.append(prefix + 'duration/source gap cannot represent positive nanoseconds')
                continue
            duration, maximum_gap_ns, represented_ns = map(round, scaled_times)
            starts = [_stamp_nanoseconds(value) for value in message.window_start]
            ends = [_stamp_nanoseconds(value) for value in message.window_end]
            if (duration <= 0 or any(end - start != duration for start, end in zip(starts, ends))
                    or starts[1:] != ends[:-1]
                    or _stamp_nanoseconds(message.history_start) != starts[0]
                    or _stamp_nanoseconds(message.history_end) != ends[-1]
                    or not math.isclose(message.represented_duration_sec, (ends[-1] - starts[0]) * 1e-9,
                                        rel_tol=1e-9, abs_tol=1e-9)):
                errors.append(prefix + 'window support is not consecutive and time weighted')
            if not 0 <= _stamp_nanoseconds(message.epoch_started_at) <= starts[0]:
                errors.append(prefix + 'window history precedes its SEARCH epoch')
            minimum_samples = max(
                0, (represented_ns + maximum_gap_ns - 1) // maximum_gap_ns - 1,
            )
            if message.sample_count < minimum_samples:
                errors.append(prefix + 'sample count cannot cover support within source gap')
            if (maximum_source_gap_sec is not None
                    and message.maximum_source_gap_sec > maximum_source_gap_sec + 1e-9):
                errors.append(prefix + 'source gap exceeds selected detector allowance')
            if (not message.run_id or not message.frame_id or message.search_epoch <= 0
                    or (supervisor_run_ids is not None
                        and message.run_id not in supervisor_run_ids)):
                errors.append(prefix + 'identity lacks an observed valid supervisor run')
            source = _stamp_nanoseconds(message.source_stamp)
            receipt = _stamp_nanoseconds(message.receipt_stamp)
            publication = _stamp_nanoseconds(message.stamp)
            temporal_valid = ends[-1] <= source <= receipt <= publication
            if allow_clock_admission:
                temporal_valid = (ends[-1] <= source <= publication
                                  and 0 <= receipt <= publication
                                  and publication - source <= freshness_ns
                                  and publication - receipt <= freshness_ns)
            if not temporal_valid:
                errors.append(prefix + 'source/support/receipt/publication times disagree')
            distances = [math.hypot(x2 - x1, y2 - y1) for x1, y1, x2, y2 in zip(
                message.centroid_x_m[:-1], message.centroid_y_m[:-1],
                message.centroid_x_m[1:], message.centroid_y_m[1:])]
            if not all(math.isclose(a, b, abs_tol=1e-9, rel_tol=1e-9)
                       for a, b in zip(distances, message.displacement_m)):
                errors.append(prefix + 'displacements do not equal five centroid distances')
            if message.metric_mode in CENTROID_METRIC_MODES:
                centroids = tuple(zip(message.centroid_x_m, message.centroid_y_m))
                try:
                    expected_score = centroid_score(centroids, message.metric_mode)
                except (ValueError, OverflowError):
                    expected_score = math.nan
                if not math.isclose(expected_score, message.score_m, abs_tol=1e-9, rel_tol=1e-9):
                    detail = ('metre score does not equal five centroid distances'
                              if message.metric_mode == CENTROID_WINDOWS_V2 else
                              'metre score differs from selected two-block centroid formula')
                    errors.append(prefix + detail)
            if not all(math.isclose(sum(values) / 6, center, abs_tol=1e-9, rel_tol=1e-9)
                       for values, center in ((message.centroid_x_m, message.center_x_m),
                                              (message.centroid_y_m, message.center_y_m))):
                errors.append(prefix + 'center does not equal six equal-duration centroids')
            if message.eligible and not (
                message.epsilon_m > 0 and 0 <= message.score_m < message.epsilon_m
                and 0 <= message.confinement_radius_m <= message.maximum_radius_m
                and message.maximum_radius_m > 0
            ):
                errors.append(prefix + 'eligibility violates strict score or radius threshold')
        if message.confirmed:
            key = (message.run_id, message.search_epoch)
            if (not message.run_id or not message.frame_id or message.search_epoch <= 0
                    or key in confirmed_epochs or message.confirmation_sequence <= 0):
                errors.append(prefix + 'invalid identity or repeated SEARCH confirmation')
            confirmed_epochs.add(key)
            previous = previous_sequences.get(message.run_id, 0)
            if message.confirmation_sequence <= previous:
                errors.append(prefix + 'confirmation sequence did not increase')
            previous_sequences[message.run_id] = message.confirmation_sequence
    return errors
