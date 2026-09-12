"""Explicit recurrent geometry wire contract; no six-centroid arithmetic."""
import math

RECURRENT_GEOMETRY_V3 = 'recurrent_geometry_v3'
RECURRENT_MODE = RECURRENT_GEOMETRY_V3
RECURRENT_TOPIC = '/gesc_gaussian/v2/recurrent_convergence_diagnostics'
RECURRENT_HISTORY_KIND = 'recurrent_geometry'
SCORE_SCALE_SEC = 12.0


def _ns(stamp):
    return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)


def recurrent_diagnostic_errors(
    messages, expected_source_pose_topic=None, supervisor_run_ids=None,
    maximum_source_gap_sec=None, allow_clock_admission=False,
    expected_frame_id=None, pose_freshness_sec=.5, expected_metric_mode=None,
):
    """Validate declared model arithmetic/identity, not trajectory ground truth."""
    if (isinstance(pose_freshness_sec, bool)
            or not isinstance(pose_freshness_sec, (float, int))
            or not math.isfinite(pose_freshness_sec) or pose_freshness_sec <= 0):
        return ['recurrent diagnostic configuration: invalid pose freshness']
    errors = []; confirmed = set(); sequence = {}
    for index, msg in enumerate(messages):
        local = []
        if msg is None:
            errors.append(f'recurrent diagnostic {index}: undecodable message'); continue
        if msg.metric_mode != RECURRENT_MODE or (expected_metric_mode is not None and msg.metric_mode != expected_metric_mode):
            local.append('wrong selected metric mode')
        if (not msg.source_pose_topic.strip() or (expected_source_pose_topic is not None and msg.source_pose_topic != expected_source_pose_topic)):
            local.append('source pose topic differs from selection')
        if expected_frame_id is not None and msg.source_valid and msg.frame_id != expected_frame_id:
            local.append('frame differs from selected stream')
        if msg.confirmed and not msg.eligible:
            local.append('confirmation without eligibility')
        if msg.eligible and not all((msg.source_valid, msg.history_valid, msg.metric_valid, msg.confinement_valid)):
            local.append('eligibility without valid source/history/model/radius')
        if msg.metric_valid and not (msg.source_valid and msg.history_valid):
            local.append('metric without valid source/history')
        if msg.history_valid:
            start, end, origin = map(_ns, (msg.history_start, msg.history_end, msg.epoch_started_at))
            branch = msg.branch; width = msg.support_duration_sec
            expected_widths = {'static': (30.,), 'circle': (30., 36.), 'oscillation': (36., 54.)}
            if branch not in expected_widths or width not in expected_widths.get(branch, ()):
                local.append('unsupported branch or duration')
                errors.extend(f'recurrent diagnostic {index}: {error}' for error in local)
                continue
            if (not math.isfinite(width) or width <= 0 or end - start != round(width * 1e9)
                    or not 0 <= origin <= start
                    or not math.isclose(msg.represented_duration_sec, width, abs_tol=1e-9)):
                local.append('invalid causal fit support')
            gap = msg.maximum_source_gap_sec
            if (not math.isfinite(gap) or not 0 < gap <= .5 + 1e-9
                    or (maximum_source_gap_sec is not None and gap > maximum_source_gap_sec + 1e-9)
                    or msg.sample_count < max(0, math.ceil(width / gap - 1e-9) - 1)):
                local.append('source samples do not cover support within gap allowance')
            source, receipt, publication = map(_ns, (msg.source_stamp, msg.receipt_stamp, msg.stamp))
            valid_time = end <= source <= receipt <= publication
            if allow_clock_admission:
                valid_time = (end <= source <= publication and 0 <= receipt <= publication
                              and publication - source <= round(pose_freshness_sec * 1e9)
                              and publication - receipt <= round(pose_freshness_sec * 1e9))
            if not valid_time:
                local.append('support/source/receipt/publication disagree')
            if (not msg.run_id or not msg.frame_id or msg.search_epoch <= 0
                    or (supervisor_run_ids is not None and msg.run_id not in supervisor_run_ids)):
                local.append('missing observed run/frame/epoch identity')
            required = 1 if branch == 'static' else 3
            if msg.persistence_required != required or not 0 <= msg.persistence_count <= required:
                local.append('invalid branch persistence counter')
            if msg.persistence_count:
                expected_start = start - (msg.persistence_count - 1) * 6_000_000_000
                if _ns(msg.persistence_start) != expected_start or expected_start < origin:
                    local.append('persistence support does not match consecutive same-width fits')
            elif _ns(msg.persistence_start) != 0:
                local.append('failed model retains persistence support')
        if msg.metric_valid:
            limit = .005 if msg.branch == 'static' else .006
            finite = (msg.score_m, msg.drift_m_s, msg.maximum_drift_m_s,
                      msg.score_scale_sec, msg.score_threshold_m,
                      msg.center_x_m, msg.center_y_m)
            if not all(math.isfinite(v) for v in finite):
                local.append('model metric lacks finite values')
            if (msg.score_scale_sec != SCORE_SCALE_SEC or msg.maximum_drift_m_s != limit
                    or not math.isclose(msg.score_threshold_m, limit * SCORE_SCALE_SEC, abs_tol=1e-12)
                    or not math.isclose(msg.score_m, msg.drift_m_s * SCORE_SCALE_SEC, abs_tol=1e-9)
                    or msg.drift_m_s < 0 or msg.evaluation_interval_sec != 6.):
                local.append('drift/score units or fixed thresholds disagree')
        if msg.confinement_valid and not (math.isfinite(msg.confinement_radius_m) and msg.confinement_radius_m >= 0 and msg.maximum_radius_m == .5):
            local.append('invalid actual confinement')
        if msg.eligible:
            if not (0 <= msg.score_m <= msg.score_threshold_m and msg.confinement_radius_m <= .5
                    and msg.persistence_count == msg.persistence_required):
                local.append('eligibility violates drift/confinement/persistence')
            if msg.branch == 'static':
                if msg.confinement_radius_m > .04:
                    local.append('static radius exceeds threshold')
            elif msg.branch == 'circle':
                arrays = (msg.arc_center_x_m, msg.arc_center_y_m, msg.arc_radius_m,
                          msg.arc_radial_rms_m, msg.arc_net_angle_rad)
                if any(len(a) != 2 or not all(math.isfinite(v) for v in a) for a in arrays):
                    local.append('circle lacks two finite arc fits')
                else:
                    dx = msg.arc_center_x_m[1] - msg.arc_center_x_m[0]
                    dy = msg.arc_center_y_m[1] - msg.arc_center_y_m[0]
                    if (not math.isclose(math.hypot(dx, dy) / (msg.support_duration_sec / 2), msg.drift_m_s, abs_tol=1e-9)
                            or not math.isclose(abs(msg.arc_radius_m[1] - msg.arc_radius_m[0]), msg.radius_difference_m, abs_tol=1e-9)
                            or not math.isclose(msg.fit_residual_rms_m, max(msg.arc_radial_rms_m), abs_tol=1e-9)
                            or msg.radius_difference_m > .08
                            or any(not .03 <= r <= .5 for r in msg.arc_radius_m)
                            or any(not 0 <= r <= .02 for r in msg.arc_radial_rms_m)
                            or any(abs(a) < math.pi / 3 for a in msg.arc_net_angle_rad)
                            or not math.isclose(msg.center_x_m, sum(msg.arc_center_x_m) / 2, abs_tol=1e-9)
                            or not math.isclose(msg.center_y_m, sum(msg.arc_center_y_m) / 2, abs_tol=1e-9)):
                        local.append('circle quality or center arithmetic disagrees')
            elif msg.branch == 'oscillation':
                if not (6. <= msg.period_sec <= min(96., msg.support_duration_sec / .75)
                        and msg.amplitude_m >= .05 and 0 <= msg.fit_residual_rms_m <= .02
                        and 0 <= msg.perpendicular_rms_m <= .02
                        and 0 <= msg.axis_variance_ratio <= .1 and 0 <= msg.design_condition <= 50.):
                    local.append('oscillation quality violates fixed model guards')
        if msg.confirmed:
            key = (msg.run_id, msg.search_epoch)
            if key in confirmed or msg.confirmation_sequence <= sequence.get(msg.run_id, 0):
                local.append('repeated epoch or nonincreasing confirmation sequence')
            confirmed.add(key); sequence[msg.run_id] = msg.confirmation_sequence
        errors.extend(f'recurrent diagnostic {index}: {error}' for error in local)
    return errors


def recurrent_nomination_errors(confirmation, diagnostic, *,
                                expected_source_pose_topic, epoch_start_ns=None):
    """Authenticate a recurrent decision's declared support, not raw trajectory truth.

    The confirmation carries the authoritative SEARCH context. The diagnostic's
    epoch is detector-local and therefore joins ``detector_local_epoch``. Live
    owners must additionally validate that context, original receipt freshness,
    selected stream identity and current state before allocating a candidate.
    """
    from ros_esc.v2_stream import time_to_ns
    errors = []
    try:
        c, d = confirmation, diagnostic
        ct = {key: time_to_ns(getattr(c, key)) for key in (
            'stamp', 'time_origin', 'epoch_started_at', 'source_stamp',
            'history_start', 'history_end')}
        dt = {key: time_to_ns(getattr(d, key)) for key in (
            'stamp', 'receipt_stamp', 'source_stamp', 'epoch_started_at',
            'history_start', 'history_end', 'persistence_start')}
        if (not expected_source_pose_topic or c.schema_version != 1
                or not c.valid or c.metric_mode != RECURRENT_MODE
                or c.history_kind != RECURRENT_HISTORY_KIND
                or c.source_stamp_kind != 'pose_input'
                or not c.run_id or not c.stream_contract_id or not c.frame_id
                or min(c.search_epoch, c.context_sequence, c.confirmation_sequence,
                       c.detector_local_epoch) <= 0
                or not c.convergence_score_valid or c.legacy_r_mean_valid
                or len(c.legacy_snapshot) != 0):
            errors.append('invalid recurrent confirmation authority')
        if not all((d.confirmed, d.eligible, d.source_valid, d.history_valid,
                    d.metric_valid, d.confinement_valid)):
            errors.append('recurrent diagnostic is not an eligible confirmation')
        errors.extend(recurrent_diagnostic_errors(
            [d], expected_source_pose_topic=expected_source_pose_topic,
            supervisor_run_ids={c.run_id}, expected_frame_id=c.frame_id,
            expected_metric_mode=RECURRENT_MODE, allow_clock_admission=True))
        if (d.run_id != c.run_id or d.frame_id != c.frame_id
                or d.search_epoch != c.detector_local_epoch
                or d.confirmation_sequence != c.confirmation_sequence
                or dt['epoch_started_at'] != ct['epoch_started_at']
                or dt['history_start'] != ct['history_start']
                or dt['history_end'] != ct['history_end']
                or (d.center_x_m, d.center_y_m, d.score_m)
                   != (c.center_x_m, c.center_y_m, c.convergence_score_m)
                or not all(math.isfinite(v) for v in
                           (c.center_x_m, c.center_y_m, c.convergence_score_m))):
            errors.append('confirmation and diagnostic identities disagree')
        if (not ct['time_origin'] <= ct['epoch_started_at']
                <= dt['persistence_start'] <= ct['history_start']
                <= ct['history_end'] == ct['source_stamp'] <= dt['source_stamp']
                <= dt['stamp'] <= ct['stamp']
                or ct['stamp'] - ct['source_stamp'] > 500_000_000
                or (epoch_start_ns is not None
                    and ct['epoch_started_at'] != epoch_start_ns)):
            errors.append('recurrent nomination support is outside its SEARCH authority')
    except (AttributeError, TypeError, ValueError, OverflowError):
        errors.append('malformed recurrent nomination')
    return errors
