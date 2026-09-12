"""Explicit committed-fill transport fixture, not an actual Gaussian-owner result."""
from ros_esc_interfaces.msg import FillResult
from ros_esc.v2_lifecycle import fill_registry_digest, result_sha256
from ros_esc.v2_stream import set_time, stream_contract_id


def fixture_activation(fill, config, run_id, origin_ns, stamp_ns):
    fill.frame_id = config['frame_id']
    fill.support_radius = 3.*fill.sigma_major
    fill.exit_radius = 2.5*fill.sigma_major
    fill.support_radius_valid = fill.exit_radius_valid = True
    set_time(fill.stamp, stamp_ns)
    result = FillResult()
    result.schema_version, result.run_id, result.frame_id = 1, run_id, config['frame_id']
    result.stream_contract_id = stream_contract_id(config, origin_ns)
    set_time(result.time_origin, origin_ns)
    for name in ('stamp', 'prepared_at', 'committed_at'):
        set_time(getattr(result, name), stamp_ns)
    set_time(result.expires_at, stamp_ns+5_000_000_000)
    result.search_epoch = result.candidate_id = result.objective_revision = result.preparation_id = 1
    result.command_sequence, result.registry_generation, result.return_state = 2, 1, 4
    result.result = FillResult.ACTIVATED
    result.evidence_sha256, result.prepared_sha256 = 'a'*64, 'b'*64
    result.fill = fill
    result.registry_digest_before = fill_registry_digest([])
    result.registry_digest_after = fill_registry_digest([fill])
    result.committed_sha256 = result_sha256(result)
    return result
