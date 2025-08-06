"""
JudgeAgent class for the Philosophical Multi-Agent Debate System.
Each judge agent has a configurable judging style and votes for the best debate participant.
"""

class JudgeAgent:
    """
    Represents a judge agent with a specific judging prompt (e.g., logical rigor, ethical impact).
    Uses LLM to analyze debate and vote for a winner with rationale.
    """
    def __init__(self, name, prompt):
        self.name = name
        self.prompt = prompt  # The judging prompt loaded from definition

    def judge(self, agent_summaries, transcript, **kwargs):
        """
        Use LLM to analyze agent summaries only (not full transcript), return vote and rationale.
        Args:
            agent_summaries (dict): {agent_name: summary}
            transcript (list): Full debate transcript (ignored for LLM input)
            return_usage (bool): If True, also return token usage info
        Returns:
            dict: {"vote": agent_name, "rationale": str} (default)
            OR
            dict: {"result": {"vote": ..., "rationale": ...}, "usage": {...}} if return_usage=True
            OR
            dict: {"result": {"rank1": ..., "rank2": ..., "rank3": ...}, "usage": {...}} if return_usage=True and ranked-choice judging
        """
        from .llm_utils import call_openai
        return_usage = kwargs.get('return_usage', False)
        # Prepare the judging prompt for the LLM (summaries only)
        agent_list = '\n'.join([f"- {k}: {v}" for k, v in agent_summaries.items()])
        user_prompt = (
            f"Agent summaries:\n{agent_list}\n\n"
            f"Your task: {self.prompt}\n"
            "Respond in the following format (replace AGENT_NAME and RATIONALE):\n"
            "RANK1: AGENT_NAME\nRATIONALE1: ...\n"
            "RANK2: AGENT_NAME\nRATIONALE2: ...\n"
            "RANK3: AGENT_NAME\nRATIONALE3: ...\n"
            "Note: If you cannot rank all three, provide as much information as possible."
        )
        # Call the LLM
        result = call_openai(self.prompt, user_prompt, return_usage=return_usage)
        if return_usage:
            llm_response = result["response"]
            usage = result.get("usage", {})
        else:
            llm_response = result
            usage = {}
        # Parse the LLM response for vote and rationale
        rank1 = None
        rank2 = None
        rank3 = None
        rationale1 = ""
        rationale2 = ""
        rationale3 = ""
        for line in llm_response.splitlines():
            if line.strip().upper().startswith('RANK1:'):
                rank1 = line.split(':', 1)[-1].strip()
            elif line.strip().upper().startswith('RANK2:'):
                rank2 = line.split(':', 1)[-1].strip()
            elif line.strip().upper().startswith('RANK3:'):
                rank3 = line.split(':', 1)[-1].strip()
            elif line.strip().upper().startswith('RATIONALE1:'):
                rationale1 = line.split(':', 1)[-1].strip()
            elif line.strip().upper().startswith('RATIONALE2:'):
                rationale2 = line.split(':', 1)[-1].strip()
            elif line.strip().upper().startswith('RATIONALE3:'):
                rationale3 = line.split(':', 1)[-1].strip()
        if not rank1:
            # Fallback: pick the first agent
            rank1 = list(agent_summaries.keys())[0] if agent_summaries else None
        result_dict = {
            "rank1": {"agent": rank1, "rationale": rationale1},
            "rank2": {"agent": rank2, "rationale": rationale2},
            "rank3": {"agent": rank3, "rationale": rationale3}
        }
        if return_usage:
            return {"result": result_dict, "usage": usage}
        return result_dict
