"""Finite pure-Python M4 science jobs using the existing process identity owner."""

import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from ros_esc.scenario_runner import run_scenario as owner


def _source_receipt(argv):
    if (not isinstance(argv, (list, tuple)) or len(argv) < 2
            or any(not isinstance(value, str) for value in argv)
            or Path(argv[0]).resolve() != Path(sys.executable).resolve()):
        raise ValueError('M4 science job requires the current Python executable and explicit source')
    if argv[1] == '-c' and len(argv) >= 3:
        return {'kind': 'inline_python', 'sha256': hashlib.sha256(argv[2].encode()).hexdigest()}
    path = Path(argv[1]).resolve()
    if path.suffix != '.py' or not path.is_file():
        raise ValueError('M4 science job requires an explicit Python script')
    return {'kind': 'script', 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def _explicit_unavailable(path):
    """A clean nonzero job needs a specific typed unavailable declaration."""
    try:
        with Path(path).open('rb') as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell()-65536))
            lines = stream.read().decode('utf-8').splitlines()
        value = json.loads(next(line for line in reversed(lines) if line.strip()))
        if (isinstance(value, dict) and value.get('scientific_status') == 'EVIDENCE_UNAVAILABLE'
                and value.get('integrity_passed') is True
                and isinstance(value.get('reason'), str) and value['reason'].strip()):
            return value
    except (OSError, ValueError, StopIteration, UnicodeDecodeError):
        pass
    return None


def finite_science_job(argv, log_path, receipt_path, *, cap_sec, suite_end,
                       process_ownership_mode='observed_tree_v1'):
    """Bound work, identity-checked termination and receipt writing in one cap.

Observed descendants are a contract violation: these frozen numerical workers
use one Python process. Threads are permitted. No ROS graph probe is created.
Partial outputs remain in place and callers decide scientific availability.
"""
    if process_ownership_mode not in ('observed_tree_v1', 'subreaper_v2', 'subreaper_group_v3'):
        raise ValueError('unknown process ownership mode')
    started = time.monotonic()
    source = _source_receipt(argv)
    for value in (cap_sec, suite_end):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('M4 science job bounds must be finite numbers')
    if cap_sec <= 0.:
        raise ValueError('M4 science cap must be positive')
    log_path, receipt_path = Path(log_path).resolve(), Path(receipt_path).resolve()
    if log_path == receipt_path or receipt_path.exists():
        raise FileExistsError('M4 science log/receipt must be distinct unused paths')
    end = min(started+cap_sec, suite_end)
    if end <= time.monotonic()+.25:
        raise TimeoutError('M4 science job lacks time to retain even an unavailable receipt')
    work_end, cleanup_end = end-3., end-.25
    result = dict(argv=list(argv), source=source, started_monotonic=started,
        absolute_deadline=end, work_deadline=work_end, cleanup_deadline=cleanup_end,
        cap_sec=cap_sec, suite_end=suite_end, complete=False, integrity_passed=False,
        timed_out=False, return_code=None, launched=False, signals=[],
        scope='one pure Python child; observed owned identities only, no unseen-future descendant proof')
    log_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    process, failure, reaper = None, None, None
    tracking = owner._process_tracking(True)
    clean = False
    with log_path.open('x') as output:
        try:
            if time.monotonic() >= work_end:
                result['timed_out'] = True
                result['reason'] = 'remaining suite budget cannot fit work and cleanup reserve'
                clean = True  # No process exists; this is explicit unavailability.
            else:
                if process_ownership_mode != 'observed_tree_v1':
                    reaper = owner._SubreaperOwner(cleanup_end, .5, escalation_sec=.5,
                        process_ownership_mode=process_ownership_mode).start()
                    reaper.work_end = work_end
                    tracking = reaper.audit
                    if time.monotonic() >= work_end:
                        raise TimeoutError('subreaper setup exhausted science work budget')
                process = subprocess.Popen(list(argv), cwd=owner.REPOSITORY_ROOT,
                    stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
                result.update(launched=True, session_id=process.pid)
                owner._track_owned_processes(process, tracking)
                while process.poll() is None:
                    if time.monotonic() >= work_end:
                        result['timed_out'] = True
                        break
                    owner._track_owned_processes(process, tracking)
                    time.sleep(min(.05, max(0., work_end-time.monotonic())))
        except (Exception, KeyboardInterrupt) as error:
            failure = f'{type(error).__name__}: {error}'
        finally:
            if reaper is not None:
                tracking = reaper.finish()
                clean = tracking['kernel_proof']['complete']
                if process is not None:
                    result['return_code'] = process.returncode
                result['remaining_owned_processes'] = [] if clean else None
            elif process is not None:
                snapshot = {item['pid']: item for item in tracking['identities']}
                if process.pid not in snapshot:
                    try:
                        identity = owner._process_identity(process.pid, strict=True)
                        if (identity is not None and identity['parent_pid'] == os.getpid()
                                and identity['session_id'] == process.pid):
                            snapshot[process.pid] = identity
                    except Exception as error:
                        failure = failure or f'{type(error).__name__}: {error}'
                try:
                    for signum, allowance in ((signal.SIGTERM, 1.), (signal.SIGKILL, 1.75)):
                        live = owner._live_snapshot_processes(snapshot, strict=True)
                        if process.poll() is not None and not live:
                            break
                        for group, identities in owner._owned_process_groups(snapshot, live).items():
                            sent = owner._signal_owned_process_group(group, identities, signum, strict=True)
                            result['signals'].append({'process_group_id': group, 'signal': int(signum), 'sent': sent})
                        owner._wait_for_cancelled_tree(process, snapshot,
                            min(allowance, max(0., cleanup_end-time.monotonic())), False,
                            absolute_deadline=cleanup_end)
                    live = owner._live_snapshot_processes(snapshot, strict=True)
                    clean = process.poll() is not None and not live
                    result['remaining_owned_processes'] = list(live.values())
                except Exception as error:
                    failure = failure or f'{type(error).__name__}: {error}'
                result['return_code'] = process.poll()
    result['process_ownership'] = tracking
    if process_ownership_mode != 'observed_tree_v1':
        result['process_ownership_mode'] = process_ownership_mode
        result['scope'] = 'one pure Python child; exclusive kernel subreaper ancestry exhaustion'
        if not result['launched']:
            tracking.update(mode=process_ownership_mode, no_child_launched=True)
            if process_ownership_mode == 'subreaper_group_v3':
                tracking['signal_strategy'] = 'initial_unreaped_root_group_sigint_then_adopted_pidfd'
    explicit = _explicit_unavailable(log_path) if process is not None and process.returncode else None
    pure = (len(tracking['identities']) <= 1 and len(tracking['session_ids']) <= 1
            and not tracking.get('reaped_descendants'))
    inspection = tracking['inspection_complete'] and (not result['launched'] or bool(tracking['identities']))
    clean = clean and time.monotonic() < end
    expected_interruption = (result['timed_out']
                             and result['return_code'] in ((-signal.SIGINT, -signal.SIGTERM, -signal.SIGKILL)
                                 if process_ownership_mode != 'observed_tree_v1'
                                 else (-signal.SIGTERM, -signal.SIGKILL)))
    exit_valid = (not result['launched'] or expected_interruption
                  or result['return_code'] == 0 or explicit is not None)
    result.update(complete=result['launched'] and result['return_code'] == 0 and not result['timed_out'],
        integrity_passed=bool(clean and pure and inspection and failure is None and exit_valid),
        timed_out=bool(result['timed_out']), failure=failure, explicit_unavailable=explicit,
        unexpected_observed_descendants=not pure, clean_termination=clean,
        log_path=str(log_path), log_sha256=hashlib.sha256(log_path.read_bytes()).hexdigest(),
        elapsed_wall_sec=time.monotonic()-started)
    atomic_exclusive_json(receipt_path, result)
    return result
