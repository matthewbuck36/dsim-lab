"""Actual moving transaction/ACK integration with the selected escape guards.

The existing finite DDS fixture supplies declared synthetic source, pose and
detector inputs. Gaussian preparation, committed fill, objective composition,
supervisor ledger and shared escape transition are production owners. This
does not qualify Gazebo behavior, direction estimation, or a recorded bag.
"""

import pytest

from test_v2_moving_pipeline_transport import (
    test_actual_moving_candidate_pipeline_and_pending_worker_cancel as moving_pipeline,
)


@pytest.mark.parametrize('case', [
    dict(anchor=(-10.,0.),interior=False,expected='outside_radius',metric='pde_mean_v1'),
    dict(anchor=(-10.,0.),interior=True,expected='outside_radius',metric='centroid_two_block_v2',held_ack='objective'),
    dict(anchor=None,interior=False,expected='failsafe',metric='pde_mean_v1'),
    dict(anchor=(-.75,0.),interior=True,expected='interior_farthest',metric='pde_mean_v1'),
    dict(anchor=(-.75,0.),interior=True,expected='interior_farthest',metric='centroid_two_block_v2'),
    dict(anchor=(-.25,0.),interior=True,expected='failsafe',metric='pde_mean_v1'),
], ids=['outside_legacy','outside_preferred','missing_legacy','bounded_interior_pde',
        'bounded_interior_centroid','tiny_interior_rejected'])
def test_moving_commit_ack_and_guarded_escape(monkeypatch,case):
    moving_pipeline(monkeypatch,False,metric_mode=case['metric'],ros_domain_id=187,escape_case=case)
