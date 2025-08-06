"""
Orchestrator agent to manage overall debate flow and agent coordination.
"""

"""
Legacy OrchestratorAgent wrapper for backward compatibility.
Agents are now dynamically loaded from the agent_definitions/ directory using agent_loader.py.
For advanced features and parallel debate, use orchestrator_dynamic.py.
"""

from .agent_loader import load_agents_from_directory
from .judge_agent import JudgeAgent
from .quorum import quorum_decision
import os

class OrchestratorAgent:
    """
    Legacy orchestrator for philosophical debates. Agents are dynamically loaded from agent_definitions/.
    For new features and parallel debate, use OrchestratorDynamic in orchestrator_dynamic.py.
    """
    def __init__(self, agent_definitions_dir=None):
        """
        Initialize the orchestrator by dynamically loading agents from the agent_definitions directory.
        Args:
            agent_definitions_dir (str): Path to the agent definitions directory. Defaults to ../../agent_definitions.
        """
        if agent_definitions_dir is None:
            agent_definitions_dir = os.path.join(os.path.dirname(__file__), '../../agent_definitions')
        self.agents = load_agents_from_directory(agent_definitions_dir)
        # Example judge agents with different judging styles (these could also be loaded dynamically in future)
        self.judges = [
            JudgeAgent("JudgeLogic", "logical rigor"),
            JudgeAgent("JudgeEthics", "ethical impact"),
            JudgeAgent("JudgeOriginality", "originality")
        ]
        self.history = []  # Debate history log

    def run(self, prompt: str):
        """
        Run a single round of multi-agent debate: Opening Statement, Rebuttal, Judging.
        Args:
            prompt (str): The philosophical prompt to debate.
        """
        import json
        import os
        from collections import defaultdict

        transcript = []
        token_usage = defaultdict(int)  # {agent_name: token_count}
        opening_statements = []
        rebuttals = defaultdict(list)
        agent_summaries = {}

        # --- Opening Statement Phase ---
        for agent in self.agents:
            # Use opening_statement if available, else fallback
            if hasattr(agent, 'opening_statement'):
                response = agent.opening_statement(prompt)
            else:
                response = agent.analyze_prompt(prompt)
            print(f"{agent.name} ({agent.archetype}) [Opening]: {response}")
            opening_statements.append((agent, response))
            transcript.append({"phase": "opening", "agent": agent.name, "text": response})
            # TODO: Track token usage per agent

        # --- Rebuttal Phase ---
        for agent, opening in opening_statements:
            for other_agent, other_opening in opening_statements:
                if agent != other_agent:
                    if hasattr(agent, 'rebuttal'):
                        rebuttal = agent.rebuttal(other_opening)
                    else:
                        rebuttal = agent.critique(other_opening)
                    print(f"{agent.name} rebuts {other_agent.name}: {rebuttal}")
                    rebuttals[agent.name].append({"target": other_agent.name, "text": rebuttal})
                    transcript.append({"phase": "rebuttal", "agent": agent.name, "target": other_agent.name, "text": rebuttal})
                    # TODO: Track token usage per agent

        # --- Judging Phase ---
        # Each agent summarizes its own opening and rebuttals
        for agent, opening in opening_statements:
            agent_rebuttals = rebuttals[agent.name]
            summary = self._agent_self_summary(agent, opening, agent_rebuttals, rebuttals)
            agent_summaries[agent.name] = summary
            transcript.append({"phase": "self-summary", "agent": agent.name, "text": summary})

        # Judges analyze all summaries and transcript, vote, and provide rationale
        judge_votes = []
        judge_rationales = []
        for judge in self.judges:
            result = judge.judge(agent_summaries, transcript)
            judge_votes.append(result["vote"])
            judge_rationales.append({"judge": judge.name, "vote": result["vote"], "rationale": result["rationale"]})
            print(f"{judge.name} voted for {result['vote']}: {result['rationale']}")
            transcript.append({"phase": "judge-vote", "judge": judge.name, "vote": result["vote"], "rationale": result["rationale"]})

        # Quorum logic: determine winner
        winner, count, is_tie = quorum_decision(judge_votes)
        if is_tie:
            print("Judging result: Tie (no majority)")
        else:
            print(f"Judging result: Winner is {winner} with {count} votes.")
        transcript.append({"phase": "judging-result", "winner": winner, "votes": judge_votes, "is_tie": is_tie})

        # --- Persistent memory: log debate history ---
        log_entry = {
            "prompt": prompt,
            "opening_statements": [
                {"agent": agent.name, "archetype": agent.archetype, "text": opening}
                for agent, opening in opening_statements
            ],
            "rebuttals": rebuttals,
            "agent_summaries": agent_summaries,
            "judge_rationales": judge_rationales,
            "winner": winner,
            "is_tie": is_tie,
            "transcript": transcript,
            # "token_usage": dict(token_usage)  # Uncomment when implemented
        }
        log_path = os.path.join(os.path.dirname(__file__), "../../debate_history.jsonl")
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _agent_self_summary(self, agent, opening, agent_rebuttals, all_rebuttals):
        """
        Create a summary for an agent, including its opening, all rebuttals it made, and all rebuttals made against it.
        Keeps the agent's original tone and worldview.
        """
        # Find all rebuttals made against this agent
        rebuttals_against = []
        for other_agent, rebuttal_list in all_rebuttals.items():
            for r in rebuttal_list:
                if r["target"] == agent.name:
                    rebuttals_against.append({"from": other_agent, "text": r["text"]})
        summary = f"Opening Statement: {opening}\n"
        summary += "Rebuttals made: " + "; ".join([r["text"] for r in agent_rebuttals]) + "\n"
        summary += "Rebuttals received: " + "; ".join([r["text"] for r in rebuttals_against])
        return summary
