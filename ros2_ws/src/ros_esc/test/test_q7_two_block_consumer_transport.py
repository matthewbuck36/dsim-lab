"""Actual DDS consumer receipts for the Q7 metric through existing fixtures.

Detector candidates and pose/cost observations are declared synthetic inputs.
The stationary fixture's W=3 seconds is an integration-test selection, not the
prospective W=6, epsilon=.18 pilot setting or an empirical detector result.
"""

import pytest

import test_q5_stationary_fill_transport as stationary
import test_v2_moving_pipeline_transport as moving


def test_new_metric_actual_stationary_verification_fit_acknowledgment(monkeypatch):
    monkeypatch.setenv('ROS_DOMAIN_ID', '78')
    stationary.test_actual_stationary_centroid_verification_fill_and_result_acknowledgment(
        metric_mode='centroid_two_block_v2')


@pytest.mark.parametrize('depart_during_worker', [False, True])
def test_new_metric_actual_moving_activation_and_worker_cancel(monkeypatch, depart_during_worker):
    moving.test_actual_moving_candidate_pipeline_and_pending_worker_cancel(
        monkeypatch, depart_during_worker, metric_mode='centroid_two_block_v2', ros_domain_id=78)
