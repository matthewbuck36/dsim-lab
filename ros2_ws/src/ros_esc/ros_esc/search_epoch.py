"""Shared typed SEARCH-epoch gating for robust algorithm history owners."""

from ros_esc_interfaces.msg import AlgorithmState


class SearchEpochGate:
    """Track valid typed SEARCH epochs without changing default-off owners."""

    ENTERED = "entered"
    LEFT = "left"

    def __init__(self, enabled):
        self.enabled = bool(enabled)
        self.active = not self.enabled
        self.run_id = None

    def update(self, state):
        """Return one boundary token for a valid state/run change."""
        if not self.enabled:
            return None
        valid_search = bool(
            state.state_valid
            and int(state.state) == AlgorithmState.STATE_SEARCH
        )
        run_id = str(state.run_id) if state.run_id_valid else None
        if valid_search:
            entered = not self.active or run_id != self.run_id
            self.active = True
            self.run_id = run_id
            return self.ENTERED if entered else None
        if self.active:
            self.active = False
            self.run_id = run_id
            return self.LEFT
        self.run_id = run_id
        return None
