"""
Quorum logic for judging phase of the Philosophical Multi-Agent Debate System.
Determines the winner based on judge votes.
"""

def quorum_decision(judge_votes):
    """
    Determine the winner from a list of judge votes.
    Args:
        judge_votes (list): List of agent names voted for by judges
    Returns:
        tuple: (winner, vote_count, is_tie, vote_breakdown)
    """
    from collections import Counter
    if not judge_votes:
        return (None, 0, True, {})
    counter = Counter(judge_votes)
    # If only one agent has the most votes, they win; otherwise, it's a tie
    most_common = counter.most_common()
    if len(most_common) == 1:
        # Only one agent received any votes
        winner, count = most_common[0]
        is_tie = False
    else:
        top_count = most_common[0][1]
        top_agents = [agent for agent, c in most_common if c == top_count]
        if len(top_agents) == 1:
            winner = top_agents[0]
            count = top_count
            is_tie = False
        else:
            winner = None
            count = top_count
            is_tie = True
    # Output full vote breakdown for debugging
    vote_breakdown = dict(counter)
    return (winner, count, is_tie, vote_breakdown)
