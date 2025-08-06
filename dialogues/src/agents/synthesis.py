"""
Synthesis agent to summarize debates into a coherent response.
"""

class SynthesisAgent:
    """
    Synthesizes debate responses into a clear, multi-perspective summary.
    Each response is attributed to the respective agent/archetype.
    """
    def summarize(self, responses):
        """
        Summarize a list of (agent, response) tuples into a readable, attributed summary.
        """
        summary_lines = [
            f"- {agent.name} ({agent.archetype}): {response}" for agent, response in responses
        ]
        summary = "\n".join(summary_lines)
        return (
            "Debate Summary:\n"
            "The following perspectives were presented by each philosophical agent:\n"
            f"{summary}"
        )
