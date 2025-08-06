"""
Debate manager to facilitate structured interactions between agents.
"""

class DebateManager:
    """Manages debate rounds, turn-taking, and protocols."""
    def __init__(self):
        self.rounds = 0

    def next_round(self):
        """Advance to the next round of debate."""
        self.rounds += 1
