# Stationary recurrent development01 — entry-point failure retained

INCOMPLETE before Gazebo/recording/motion, 2026-09-10. Root tool session5706
is terminal/reaped. The wrapper completed in3.765820 s within420 s; all260
prepared source pins remained stable and strict owned cleanup PASS. No run
directory, bag or scenario summary was created. Do not analyze or retry this
unchanged attempt.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_01/`.
`attempt_result.json`, `runner.log`, `command.json`, `prepared.json` and
`root_execution.log` retain the exact attempt. The installed scenario console
script exited1 with `StopIteration` in `load_entry_point`; there is no behavioral
or algorithm result from this attempt.

Read-only environment diagnosis establishes the cause. The new test environment
prepended `/home/mattb/dsim-lab/ros2_ws/src/ros_esc` to PYTHONPATH. Imports then
used the right source, but `importlib.metadata.distribution('ros-esc')` selected
that directory's pre-existing `ros_esc.egg-info`, which has no `run_scenario`
entry point. Without this extra prepend, the existing Q5 build overlay supplies
its complete installed metadata and the declared `run_scenario` entry point;
its `ros_esc.__file__` resolves through the build symlink to the same current
canonical repository source. The new generated interface overlay still resolves.

Preserve the original environment and attempt pins. A new runtime environment
must retain the working overlay order, use its complete entry-point metadata,
and omit the unnecessary source prepend. Verify actual `ros2 run ros_esc
run_scenario --help` and recorder entry point before a separately planned02
freeze. No repository metadata cleanup, numerical change, rebuild, matrix,
physical/Pi/snapshot/V1 action or original-result relabel is justified.
