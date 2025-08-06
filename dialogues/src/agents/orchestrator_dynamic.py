"""
Dynamic orchestrator agent to manage debate flow with dynamically loaded philosophical agents.
"""

import json
import os
import concurrent.futures
from typing import List, Tuple, Dict, Any, Optional

from .base import BaseAgent
from .judge_loader import load_judges_from_directory
from .quorum import quorum_decision
from .agent_loader import load_agents_from_directory
from .summarizer_loader import load_summarizer_from_directory

class OrchestratorAgent:
    """
    Manages conversation flow and coordinates all philosophical agents for the debate.
    Loads agents dynamically from definition files.
    """
    def __init__(self, agent_definitions_dir: Optional[str] = None):
        """
        Initialize the orchestrator with dynamically loaded agents.
        
        Args:
            agent_definitions_dir: Directory containing agent definition files
                                  If None, default to "agent_definitions"
        """
        # Path to agent definitions
        if agent_definitions_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            agent_definitions_dir = os.path.join(project_root, "agent_definitions")
        
        # Load agents dynamically
        self.agents = load_agents_from_directory(agent_definitions_dir)
        # Dynamically load judge agents from judge_definitions/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        judge_definitions_dir = os.path.join(project_root, "judge_definitions")
        self.judges = load_judges_from_directory(judge_definitions_dir)
        if len(self.judges) % 2 == 0:
            raise RuntimeError("Number of judge agents must be odd to provide quorum. Refusing to run.")
        self.history = []

    def run(self, prompt: str, max_parallel: int = 1):
        """
        Run a single round of multi-agent debate: Opening Statement, Rebuttal, Summarization, Judging.
        Args:
            prompt (str): The philosophical prompt to debate
            max_parallel (int): Maximum number of parallel API calls (default: 1)
        """
        import json
        import os
        from collections import defaultdict
        import concurrent.futures

        # --- Per-phase parallelism settings ---
        def get_phase_parallel(phase: str, default: int = 1) -> int:
            env_map = {
                "opening": "PARALLEL_AGENTS_OPENING",
                "rebuttal": "PARALLEL_AGENTS_REBUTTAL",
                "summary": "PARALLEL_AGENTS_SUMMARY",
                "judging": "PARALLEL_AGENTS_JUDGING",
            }
            # Try phase-specific env var, then global, then default
            val = os.environ.get(env_map.get(phase, ""))
            if val is not None:
                try:
                    return int(val)
                except ValueError:
                    pass
            val = os.environ.get("PARALLEL_AGENTS")
            if val is not None:
                try:
                    return int(val)
                except ValueError:
                    pass
            return default

        transcript = []
        opening_statements = []
        rebuttals = defaultdict(list)
        agent_summaries = {}

        # Track token usage
        token_usage = {"opening": [], "rebuttal": [], "summary": [], "judge": []}


        def get_opening(agent):
            from .llm_utils import call_openai
            if hasattr(agent, 'opening_statement'):
                result = call_openai(agent.opening_prompt, prompt, return_usage=True)
            else:
                result = call_openai(agent.analysis_prompt, prompt, return_usage=True)
            response = result['response']
            usage = result.get('usage', {})
            token_usage["opening"].append(usage)
            print(f"{agent.name} ({agent.archetype}) [Opening]: {response}")
            if usage:
                print(f"  [Tokens: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}]")
            return (agent, response, {"phase": "opening", "agent": agent.name, "text": response})

        with concurrent.futures.ThreadPoolExecutor(max_workers=get_phase_parallel("opening", max_parallel)) as executor:
            opening_results = list(executor.map(get_opening, self.agents)) # Opening statements phase parallelism

        opening_statements = [(agent, response) for agent, response, _ in opening_results]
        transcript.extend([log for _, _, log in opening_results])

        # --- Rebuttal Phase (parallelized per agent) ---
        def get_rebuttals(agent_opening):
            from .llm_utils import call_openai
            agent, opening = agent_opening
            rebuttal_logs = []
            rebuttal_list = []
            for other_agent, other_opening in opening_statements:
                if agent != other_agent:
                    if hasattr(agent, 'rebuttal'):
                        result = call_openai(agent.rebuttal_prompt, other_opening, return_usage=True)
                    else:
                        result = call_openai(agent.critique_prompt, other_opening, return_usage=True)
                    rebuttal = result['response']
                    usage = result.get('usage', {})
                    token_usage["rebuttal"].append(usage)
                    print(f"{agent.name} rebuts {other_agent.name}: {rebuttal}")
                    if usage:
                        print(f"  [Tokens: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}]")
                    rebuttal_list.append({"target": other_agent.name, "text": rebuttal})
                    rebuttal_logs.append({"phase": "rebuttal", "agent": agent.name, "target": other_agent.name, "text": rebuttal})
            return agent.name, rebuttal_list, rebuttal_logs

        with concurrent.futures.ThreadPoolExecutor(max_workers=get_phase_parallel("rebuttal", max_parallel)) as executor:
            rebuttal_results = list(executor.map(get_rebuttals, opening_statements)) # Rebuttal phase parallelism

        rebuttals = {name: rebuttal_list for name, rebuttal_list, _ in rebuttal_results}
        for _, _, logs in rebuttal_results:
            transcript.extend(logs)

        # --- Closing Statement Phase (parallelized) ---
        # Each agent receives their worldview, opening, and all rebuttals against them, and generates a closing statement.
        def get_closing(agent_opening):
            from .llm_utils import call_openai
            agent, opening = agent_opening
            agent_rebuttals = rebuttals[agent.name]
            rebuttals_against = []
            for other_agent, rebuttal_list in rebuttals.items():
                for r in rebuttal_list:
                    if r["target"] == agent.name:
                        rebuttals_against.append({"from": other_agent, "text": r["text"]})
            # Compose worldview string (from agent definition)
            worldview = getattr(agent, "worldview", None)
            if worldview is None and hasattr(agent, "archetype"):
                worldview = f"Archetype: {agent.archetype}"
            closing_prompt = (
                "You are to provide a closing response to the debate. "
                "Consider your worldview, your opening statement, and the rebuttals you received. "
                "Summarize your final position and address the main challenges raised against you.\n\n"
                f"Worldview: {worldview}\n"
                f"Opening Statement: {opening}\n"
                f"Rebuttals Against You: {'; '.join([r['text'] for r in rebuttals_against])}"
            )
            # Use the agent's critique_prompt for closing, or fallback to analysis_prompt
            prompt_to_use = getattr(agent, "closing_prompt", None) or getattr(agent, "critique_prompt", None) or getattr(agent, "analysis_prompt", None)
            result = call_openai(prompt_to_use, closing_prompt, return_usage=True)
            closing = result['response']
            usage = result.get('usage', {})
            token_usage["closing"].append(usage)
            print(f"{agent.name} Closing: {closing}")
            if usage:
                print(f"  [Tokens: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}]")
            return agent.name, closing, {"phase": "closing", "agent": agent.name, "text": closing, "token_usage": usage}

        with concurrent.futures.ThreadPoolExecutor(max_workers=get_phase_parallel("closing", max_parallel)) as executor:
            closing_results = list(executor.map(get_closing, opening_statements))
        agent_closings = {name: closing for name, closing, _ in closing_results}
        transcript.extend([log for _, _, log in closing_results])

        # --- Summarization Phase (parallelized) ---
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        summarizer_definitions_dir = os.path.join(project_root, "summarizer_definitions")
        summarizer_name, summarizer_prompt = load_summarizer_from_directory(summarizer_definitions_dir)
        from .llm_utils import call_openai
        def get_summary(agent_opening):
            from .llm_utils import call_openai
            agent, opening = agent_opening
            agent_rebuttals = rebuttals[agent.name]
            rebuttals_against = []
            for other_agent, rebuttal_list in rebuttals.items():
                for r in rebuttal_list:
                    if r["target"] == agent.name:
                        rebuttals_against.append({"from": other_agent, "text": r["text"]})
            summarization_input = (
                f"Opening Statement: {opening}\n"
                f"Rebuttals made: {'; '.join([r['text'] for r in agent_rebuttals])}\n"
                f"Rebuttals received: {'; '.join([r['text'] for r in rebuttals_against])}"
                f"\nClosing Statement: {agent_closings.get(agent.name, '')}"
            )
            result = call_openai(summarizer_prompt, summarization_input, return_usage=True)
            summary = result['response']
            usage = result.get('usage', {})
            token_usage["summary"].append(usage)
            print(f"{agent.name} Summary: {summary}")
            if usage:
                print(f"  [Tokens: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}]")
            return agent.name, summary, {"phase": "summary", "agent": agent.name, "text": summary, "token_usage": usage}

        with concurrent.futures.ThreadPoolExecutor(max_workers=get_phase_parallel("summary", max_parallel)) as executor:
            summary_results = list(executor.map(get_summary, opening_statements))
        agent_summaries = {name: summary for name, summary, _ in summary_results}
        transcript.extend([log for _, _, log in summary_results])

        # Output all agent summaries to the console before judging
        print("\n=== Agent Summaries ===")
        for name, summary in agent_summaries.items():
            print(f"Summary for {name}:\n{summary}\n")

        # --- Judging Phase ---
        # Judges receive ONLY agent_summaries (not full transcript or debate data) for evaluation
        # --- Ranked-Choice Judging Phase ---
        judge_ranks = []
        judge_rationales = []
        from collections import defaultdict
        score_board = defaultdict(int)
        agent_names = list(agent_summaries.keys())

        def get_judge_result(judge):
            judge_result = judge.judge(agent_summaries, transcript, return_usage=True)
            result = judge_result['result']
            usage = judge_result.get('usage', {})
            token_usage["judge"].append(usage)
            print(f"{judge.name} Judge Result:")
            if usage:
                print(f"  [Tokens: prompt={usage.get('prompt_tokens', 0)}, completion={usage.get('completion_tokens', 0)}, total={usage.get('total_tokens', 0)}]")
            return judge.name, result, usage

        with concurrent.futures.ThreadPoolExecutor(max_workers=get_phase_parallel("judging", max_parallel)) as executor:
            judge_results = list(executor.map(get_judge_result, self.judges)) # Judging phase parallelism

        for judge_name, result, usage in judge_results:
            # Parse and display each rank
            for i, rank_key in enumerate(['rank1', 'rank2', 'rank3']):
                rank = result.get(rank_key, {})
                agent = rank.get('agent')
                rationale = rank.get('rationale', '')
                if agent:
                    points = 3 - i  # 3 points for rank1, 2 for rank2, 1 for rank3
                    score_board[agent] += points
                    print(f"{judge_name} {rank_key.upper()}: {agent} (+{points}) Rationale: {rationale}")
                    judge_rationales.append({"judge": judge_name, "rank": rank_key, "agent": agent, "rationale": rationale, "points": points})
                    transcript.append({"phase": "judge-vote", "judge": judge_name, "rank": rank_key, "agent": agent, "rationale": rationale, "points": points, "token_usage": usage})

        # Aggregate and sort
        sorted_scores = sorted(score_board.items(), key=lambda x: (-x[1], x[0]))
        print("\n=== Ranked-Choice Judging Results ===")
        for agent, score in sorted_scores:
            print(f"{agent}: {score} points")
        # Winner logic: agent with highest score, tie if two or more agents have the exact same top score
        if not sorted_scores:
            winner = None
            is_tie = True
        else:
            top_score = sorted_scores[0][1]
            top_agents = [agent for agent, score in sorted_scores if score == top_score]
            print(f"[DEBUG] sorted_scores: {sorted_scores}")
            print(f"[DEBUG] top_agents: {top_agents}")
            if len(top_agents) == 1:
                winner = top_agents[0]
                is_tie = False
            else:
                winner = None
                is_tie = True
        print(f"Judging result: {'Tie (no majority)' if is_tie else f'Winner is {winner} with {top_score} points.'}")
        transcript.append({"phase": "judging-result", "winner": winner, "scores": dict(score_board), "is_tie": is_tie, "judge_rationales": judge_rationales})

        # --- Output total token usage summary ---
        def sum_tokens(usage_list, key):
            return sum(u.get(key, 0) for u in usage_list if u)
        print("\n=== Token Usage Summary ===")
        total_prompt = total_completion = total_total = 0
        for phase in ["opening", "rebuttal", "summary", "judge"]:
            phase_prompt = sum_tokens(token_usage[phase], "prompt_tokens")
            phase_completion = sum_tokens(token_usage[phase], "completion_tokens")
            phase_total = sum_tokens(token_usage[phase], "total_tokens")
            total_prompt += phase_prompt
            total_completion += phase_completion
            total_total += phase_total
            print(f"{phase.title()}: prompt={phase_prompt}, completion={phase_completion}, total={phase_total}")
        print(f"TOTAL: prompt={total_prompt}, completion={total_completion}, total={total_total}\n")

        # --- Final Debate Win Summary ---
        print("\n=== Final Debate Summary ===")
        summarizer_definitions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "summarizer_definitions")
        # Try to load FinalDebateSummary.md directly
        final_summarizer_path = os.path.join(summarizer_definitions_dir, "FinalDebateSummary.md")
        if os.path.exists(final_summarizer_path):
            with open(final_summarizer_path, 'r') as f:
                lines = f.readlines()
                final_summarizer_name = lines[0].strip().lstrip('#').strip()
                prompt_lines = []
                in_code = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code = not in_code
                        continue
                    if in_code:
                        prompt_lines.append(line)
                final_summarizer_prompt = ''.join(prompt_lines).strip()
        else:
            final_summarizer_name, final_summarizer_prompt = load_summarizer_from_directory(summarizer_definitions_dir)
        # Compose input for final summary
        final_summary_input = (
            f"Debate Topic: {prompt}\n\n"
            f"Agent Summaries:\n" + '\n'.join([f"{name}: {summary}" for name, summary in agent_summaries.items()]) + "\n\n"
            f"Judge Rationales:\n" + '\n'.join([f"{j['judge']} ({j['rank']}): {j['agent']} - {j['rationale']} (+{j['points']} pts)" for j in judge_rationales]) + "\n\n"
            f"Winner: {winner if winner else 'Tie'}\n"
        )
        from .llm_utils import call_openai
        final_summary_result = call_openai(final_summarizer_prompt, final_summary_input, return_usage=True)
        final_summary = final_summary_result["response"]
        final_summary_usage = final_summary_result.get("usage", {})
        print(final_summary)
        if final_summary_usage:
            print(f"  [Tokens: prompt={final_summary_usage.get('prompt_tokens', 0)}, completion={final_summary_usage.get('completion_tokens', 0)}, total={final_summary_usage.get('total_tokens', 0)}]")
        transcript.append({"phase": "final-summary", "text": final_summary, "token_usage": final_summary_usage})

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
            "final_summary": final_summary
        }
        log_path = os.path.join(os.path.dirname(__file__), "../../debate_history.jsonl")
        with open(log_path, "a") as f:
            # Persistent log step: write debate log entry
            f.write(json.dumps(log_entry) + "\n")
        
        # --- Metrics Calculation: Automatically compute and print metrics for this debate ---
        try:
            from src.metrics.debate_metrics import DebateMetricsCalculator
            import hashlib
            # Generate a debate_id (hash of prompt + winner + date if available)
            base_id = f"{prompt}-{winner}-{log_entry.get('date', '')}"
            debate_id = hashlib.sha1(base_id.encode()).hexdigest()[:12]
            # Save a debate record in memory/debates for metrics
            import os
            memory_dir = os.path.join(os.path.dirname(__file__), '../../memory')
            os.makedirs(os.path.join(memory_dir, 'debates'), exist_ok=True)
            debate_file = os.path.join(memory_dir, 'debates', f"{debate_id}.json")
            with open(debate_file, "w") as df:
                json.dump(log_entry, df, indent=2)
            # Calculate and print metrics
            metrics_calc = DebateMetricsCalculator(memory_dir=memory_dir)
            metrics_calc.calculate_metrics_for_debate(debate_id)
        except Exception as e:
            print(f"[Warning] Could not calculate metrics for debate: {e}")

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

        # Write debate log entry (fixed indentation)
        # f.write(json.dumps(log_entry) + "\n")  # Removed this line as it was incorrectly indented
