"""Render the original Matplotlib views without CSV or a live ROS graph."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pytest

from ros_esc.data_collection_node.live_plot_animation import (
    MAX_LIVE_SAMPLES, append_cost, append_position, initialize_animation, update_plot,
)
from ros_esc.run_tools.analyze_bag import write_plots


@pytest.mark.parametrize('mode', ['2D', '3D'])
def test_familiar_live_views_render_with_bounded_callback_data(tmp_path, mode):
    figure, data = initialize_animation(mode)
    try:
        for index in range(MAX_LIVE_SAMPLES + 10):
            append_position(data, index * .01, index * .001, 2., .2)
            append_cost(data, index * .01, [-2., -1.])
        assert len(data['position_tstamps']) == MAX_LIVE_SAMPLES
        assert not append_cost(data, 51., [float('nan'), 1.])
        assert not append_cost(data, 51., [1.])
        assert 'cost_value_line_0' not in data  # Callback does no GUI work.
        update_plot(0, data)
        assert len(data['ax3'].lines) == 2
        assert data['xhist_plot'].get_xdata()[-1] == pytest.approx(50.09)
        path = tmp_path / f'live_{mode}.png'
        figure.savefig(path)
        assert path.stat().st_size > 1000
        assert {axis.get_title() for axis in figure.axes} >= {
            'X Position Time History', 'Y Position Time History', 'Cost Value Time History'}
    finally:
        plt.close(figure)


def test_offline_trajectory_contains_gaussian_ellipse(tmp_path):
    types = {'/odom': 'nav_msgs/msg/Odometry', '/gesc/fills': 'ros_esc_interfaces/msg/GaussianFill'}
    rows = {'/odom': [{'bag_time_ns': 1, 'x': 0., 'y': 0., 'frame_id': 'odom'},
                     {'bag_time_ns': 2, 'x': 1., 'y': 1., 'frame_id': 'odom'}],
            '/gesc/fills': [{'bag_time_ns': 1, 'fill_id': 3, 'center_x': .5, 'center_y': .5,
                             'sigma_major': .2, 'sigma_minor': .1, 'orientation': .4,
                             'active': True, 'frame_id': 'odom'}]}
    assert write_plots(tmp_path, types, rows) == ['trajectory.png']
    assert (tmp_path / 'trajectory.png').stat().st_size > 1000
