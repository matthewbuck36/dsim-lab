#!/usr/bin/env python3
"""Run standard rosbag independently; a recording failure never stops control."""

import argparse
from datetime import datetime, timezone
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading


CORE_TOPICS = (
    '/odom', '/turtlebot3/encoder_chatter', '/turtlebot3/cost_value_chatter',
    '/turtlebot3/filter_value_chatter', '/cmd_vel', '/gesc/observation',
    '/gesc/events', '/gesc/fills',
)


def bag_command(output, environment='simulation', topics=None):
    """Use explicit topics, retaining /clock without changing the bag clock."""
    selected = list(CORE_TOPICS if topics is None else topics)
    if environment == 'simulation' and '/clock' not in selected:
        selected.append('/clock')
    if not selected or any(not topic.startswith('/') for topic in selected):
        raise ValueError('recording needs absolute ROS topic names')
    return ['ros2', 'bag', 'record', '-o', str(output), '-s', 'sqlite3',
            '--include-unpublished-topics', *dict.fromkeys(selected)]


def stop_bag(process, tail_sec=0.5):
    """Allow final algorithm commands to arrive, then close only our bag child."""
    # Its own process group keeps the launcher's Ctrl+C from closing the bag
    # before the algorithm's final zero publications can arrive.
    if process.poll() is not None:
        return process.returncode
    threading.Event().wait(tail_sec)
    for signum, wait_sec in ((signal.SIGINT, 8.0), (signal.SIGTERM, 1.0), (signal.SIGKILL, 1.0)):
        if process.poll() is not None:
            break
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            break
        try:
            process.wait(timeout=wait_sec)
        except subprocess.TimeoutExpired:
            continue
    if process.poll() is None:
        print('record_bag: bag did not exit within the shutdown deadline', file=sys.stderr)
    return process.returncode


def run_recorder(command, stopped, tail_sec=0.5):
    """Start no ROS node and publish no readiness, stop or motion messages."""
    try:
        process = subprocess.Popen(command, start_new_session=True)
    except OSError as error:
        print(f'record_bag: recording unavailable: {error}', file=sys.stderr)
        return 0
    while process.poll() is None and not stopped.wait(0.1):
        pass
    if stopped.is_set():
        stop_bag(process, tail_sec)
    else:
        print(f'record_bag: recording ended (exit {process.returncode}); control continues', file=sys.stderr)
    return 0


def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--environment', choices=('simulation', 'physical'), default='simulation')
    parser.add_argument('--topic', action='append', help='Replace the default topic list; repeat as needed.')
    parser.add_argument('--shutdown-tail-sec', type=float, default=0.5)
    options = parser.parse_args(args)
    if not math.isfinite(options.shutdown_tail_sec) or not 0 <= options.shutdown_tail_sec <= 2:
        parser.error('--shutdown-tail-sec must be between zero and two seconds')
    output = options.output or (Path.home() / 'Experiments' / 'ESC' /
                               datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ'))
    stopped = threading.Event()
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    for sig in previous:
        signal.signal(sig, lambda _sig, _frame: stopped.set())
    try:
        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        return run_recorder(bag_command(output, options.environment, options.topic),
                            stopped, options.shutdown_tail_sec)
    except (OSError, ValueError) as error:
        print(f'record_bag: recording unavailable: {error}', file=sys.stderr)
        return 0
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


if __name__ == '__main__':
    raise SystemExit(main())
