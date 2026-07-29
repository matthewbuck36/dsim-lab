# Phase 08.6 V6 Failure Report

V6 closed **FAIL / NOT 120-RUN READY**.

The selected H25 ratio passed only `1/3` full-record repeats, below the fixed
`2/3` gate. Seed 17102 converged near the global light and was correctly
rejected as nonlocal. Seed 17103 completed the requested local recovery but
later entered `FILL_REJECTED` and `FAILSAFE` during a subsequent cycle.

The dominant next question is now narrow: should the experiment gate only the
first local-recovery episode through resumed `SEARCH`, or must it also require
stable behavior for all later cycles in a 300-second record? The retained
evidence gives `2/3` for the first episode and `1/3` for the stricter full
record. That contract must be chosen prospectively in a successor Plan; V6 is
not relabelled.

Do not launch the 120-run matrix from V6.

