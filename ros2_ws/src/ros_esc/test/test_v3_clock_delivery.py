"""Clock delivery ordering is not permission to consume a future sample."""

from ros_esc.gesc_v3.clock_delivery import ClockDelivery


def test_clock_catchup_preserves_stamps_and_first_receipt():
    queue = ClockDelivery()
    assert queue.add(45.901, 'sample', 45.9, 100.)
    assert queue.ready(45.9, 100.04) == []
    result, = queue.ready(45.95, 100.05)
    assert (result.stamp, result.receipt, result.steady) == (45.901, 45.9, 100.)
    assert queue.ready(45.95, 100.06) == []


def test_frozen_clock_expiry_and_duplicates_never_renew_receipt():
    queue = ClockDelivery()
    assert queue.add(45.901, 'sample', 45.9, 100.)
    assert not queue.add(45.901, 'duplicate', 45.9, 100.4)
    assert queue.ready(45.9, 100.6) == []
    assert not queue.add(45.901, 'duplicate after expiry', 45.9, 100.6)
    assert queue.ready(46., 100.61) == []


def test_future_and_stale_rejections_do_not_poison_normal_inputs():
    queue = ClockDelivery()
    assert not queue.add(46.1, 'too far ahead', 45.9, 100.)
    assert not queue.add(45., 'stale', 45.9, 100.)
    assert queue.add(45.95, 'normal', 45.9, 100.)
    assert [record.value for record in queue.ready(46., 100.1)] == ['normal']


def test_queue_preserves_full_odometry_rate_and_has_finite_capacity():
    queue = ClockDelivery()
    for index in range(1, 4):
        assert queue.add(45.9+index/30, index, 45.9, 100.+index/300)
    assert [record.value for record in queue.ready(46.01, 100.1)] == [1, 2, 3]
    for index in range(100):
        assert queue.add(46.02+index*.001, index, 46.01, 100.2)
    assert len(queue.pending) == 32
    assert len(queue.ready(46.125, 100.3)) == 32


def test_source_age_expiry_is_not_relaxed_by_recent_delivery():
    queue = ClockDelivery()
    assert queue.add(1.01, 'sample', 1., 100.)
    assert queue.ready(1.6, 100.1) == []


def test_distinct_source_samples_can_share_release_time_without_renewal():
    queue = ClockDelivery()
    assert queue.add(1.01, 'first', 1., 100., available_at=1.1)
    assert queue.add(1.02, 'second', 1., 100.01, available_at=1.1)
    assert queue.ready(1.05, 100.05) == []
    assert not queue.add(1.02, 'duplicate', 1.05, 100.05, available_at=1.11)
    released = queue.ready(1.1, 100.1)
    assert [record.value for record in released] == ['first', 'second']
    assert [record.stamp for record in released] == [1.01, 1.02]
    assert [record.steady for record in released] == [100., 100.01]
    assert queue.ready(1.2, 100.2) == []


def test_separate_release_time_preserves_source_age_and_lead_bounds():
    queue = ClockDelivery()
    assert not queue.add(.4, 'stale source', 1., 100., available_at=1.1)
    assert not queue.add(1.01, 'too far ahead', 1., 100., available_at=1.2)
    assert not queue.add(1.01, 'earlier than source', 1., 100., available_at=1.)
    assert queue.add(1.01, 'normal', 1., 100., available_at=1.1)
    assert queue.ready(1.1, 100.6) == []  # No renewal by the later release time.
