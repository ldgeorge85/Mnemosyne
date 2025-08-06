"""
token_usage.py - Utility for tracking and reporting token usage in multi-agent debates.
"""

import os
import json
from typing import Dict, Any

class TokenUsageTracker:
    """Tracks token usage per agent, phase, and debate."""
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.usage_dir = os.path.join(memory_dir, "token_usage")
        os.makedirs(self.usage_dir, exist_ok=True)

    def log_usage(self, debate_id: str, usage: Dict[str, Any]):
        """Persist token usage for a debate."""
        path = os.path.join(self.usage_dir, f"{debate_id}.json")
        with open(path, "w") as f:
            json.dump(usage, f, indent=2)

    def load_usage(self, debate_id: str) -> Dict[str, Any]:
        path = os.path.join(self.usage_dir, f"{debate_id}.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def summarize_all(self) -> Dict[str, Any]:
        """Summarize token usage across all debates."""
        summary = {}
        for fname in os.listdir(self.usage_dir):
            if fname.endswith(".json"):
                debate_id = fname[:-5]
                summary[debate_id] = self.load_usage(debate_id)
        return summary
