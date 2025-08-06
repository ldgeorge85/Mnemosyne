"""
Memory Query Utility Module

This module provides functions to query the memory system for debate history and agent positions.
It implements command-line interfaces for accessing historical data from the memory system.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Add the project root to the path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.memory import MemoryManager


class MemoryQueryTool:
    """Tool to query the memory system for historical debates and agent positions."""
    
    def __init__(self, memory_dir: str = "memory"):
        """Initialize the query tool with the memory directory.
        
        Args:
            memory_dir: Path to the memory directory
        """
        self.memory_dir = Path(memory_dir)
        self.memory_manager = MemoryManager(str(self.memory_dir))
    
    def list_debates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List all debates stored in the memory system.
        
        Args:
            limit: Maximum number of debates to return
            
        Returns:
            List of debate summaries
        """
        debates_dir = self.memory_dir / "debates"
        
        if not debates_dir.exists():
            return []
        
        debates = []
        for debate_file in debates_dir.glob("*.json"):
            with open(debate_file, "r") as f:
                debate_data = json.load(f)
                
                # Extract agent names from responses if available
                agents = []
                for response in debate_data.get("responses", []):
                    agent_name = response.get("agent", "Unknown")
                    if agent_name != "Unknown":
                        agents.append(agent_name)
                
                # Build debate summary
                debate_summary = {
                    "id": debate_file.stem,
                    "topic": debate_data.get("topic", "Unknown"),
                    "date": debate_data.get("date", "Unknown"),
                    "agents": agents
                }
                
                # Add timestamp for sorting if date is missing
                if "timestamp" in debate_data and debate_summary["date"] == "Unknown":
                    debate_summary["_timestamp"] = debate_data["timestamp"]
                
                debates.append(debate_summary)
                
        # Sort by date (newest first) and limit
        # First try to sort by timestamp if date is unknown
        debates_with_unknown = [d for d in debates if d.get("date") == "Unknown"]
        if debates_with_unknown:
            debates_with_unknown.sort(key=lambda x: x.get("_timestamp", ""), reverse=True)
            
        # Then sort the debates with known dates
        debates_with_dates = [d for d in debates if d.get("date") != "Unknown"]
        debates_with_dates.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        # Combine the sorted lists
        sorted_debates = debates_with_dates + debates_with_unknown
        
        return sorted_debates[:limit]
    
    def search_debates_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Search for debates related to a specific topic.
        
        Args:
            topic: Topic to search for
            
        Returns:
            List of related debates
        """
        # Search in debate titles/topics first
        debates_dir = self.memory_dir / "debates"
        related_debates = []
        
        if not debates_dir.exists():
            return []
        
        # Simple keyword matching for topic searching
        topic_lower = topic.lower()
        
        for debate_file in debates_dir.glob("*.json"):
            try:
                with open(debate_file, "r") as f:
                    debate_data = json.load(f)
                    
                    # Calculate relevance score based on keyword matches
                    relevance = 0
                    main_topic = debate_data.get("topic", "").lower()
                    prompt = debate_data.get("prompt", "").lower()
                    
                    # Check if topic is in the main topic
                    if topic_lower in main_topic:
                        relevance += 2  # Higher score for topic match
                    
                    # Check if topic is in the prompt
                    if topic_lower in prompt:
                        relevance += 1
                    
                    # Check if topic is in any of the topic keywords
                    for keyword in debate_data.get("topics", []):
                        if topic_lower in keyword.lower():
                            relevance += 1
                            break
                    
                    # If relevant, add to results
                    if relevance > 0:
                        # Extract agent names
                        agents = []
                        for response in debate_data.get("responses", []):
                            agent_name = response.get("agent", "Unknown")
                            if agent_name != "Unknown":
                                agents.append(agent_name)
                            
                        related_debates.append({
                            "id": debate_file.stem,
                            "topic": debate_data.get("topic", "Unknown"),
                            "date": debate_data.get("date", "Unknown"),
                            "relevance": relevance,
                            "agents": agents
                        })
            except Exception as e:
                print(f"Error searching debate {debate_file}: {e}")
        
        # Sort by relevance (highest first)
        related_debates.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return related_debates
    
    def get_agent_positions(self, agent_name: str, topic: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get an agent's positions on topics.
        
        Args:
            agent_name: Name of the agent
            topic: Optional specific topic to search for
            
        Returns:
            Dictionary of topics and agent positions
        """
        agent_file = self.memory_dir / "agents" / f"{agent_name}.json"
        if not agent_file.exists():
            return {}
            
        with open(agent_file, "r") as f:
            agent_memory = json.load(f)
        
        agent_positions = {}
        
        if topic:
            # Get positions on a specific topic
            if "positions" in agent_memory and topic in agent_memory["positions"]:
                agent_positions[topic] = agent_memory["positions"][topic]
        else:
            # Get all positions for the agent
            if "positions" in agent_memory:
                for topic_name, positions in agent_memory["positions"].items():
                    agent_positions[topic_name] = positions
        
        return agent_positions
    
    def get_debate_details(self, debate_id: str) -> Dict[str, Any]:
        """Get full details of a specific debate.
        
        Args:
            debate_id: ID of the debate
            
        Returns:
            Complete debate data with properly formatted agent information
        """
        debate_file = self.memory_dir / "debates" / f"{debate_id}.json"
        
        if not debate_file.exists():
            return {}
        
        with open(debate_file, "r") as f:
            debate_data = json.load(f)
        
        # Format the data for the explorer
        # Adapt the debate_data format to match what the explorer expects
        formatted_agents = []
        for response in debate_data.get("responses", []):
            formatted_agents.append({
                "name": response.get("agent", "Unknown"),
                "analysis": response.get("response", "No analysis available.")
            })
        
        # Add the agents list in the expected format
        debate_data["agents"] = formatted_agents
        
        # Make sure summary is available
        if "summary" not in debate_data:
            debate_data["summary"] = "No summary available."
            
        return debate_data
    
    def find_contradictions(self, agent_name: str) -> List[Dict[str, Any]]:
        """Find potential contradictions in an agent's positions over time.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of potential contradictory positions
        """
        # Load the agent memory file directly
        agent_file = self.memory_dir / "agents" / f"{agent_name}.json"
        if not agent_file.exists():
            return []
            
        with open(agent_file, "r") as f:
            agent_memory = json.load(f)
        
        # This is a placeholder for more sophisticated contradiction analysis
        # A real implementation would use NLP techniques to identify semantic contradictions
        contradictions = []
        
        if "positions" not in agent_memory:
            return []
        
        # For now, just return topics where the agent has multiple positions
        for topic, positions in agent_memory["positions"].items():
            if len(positions) > 1:
                contradictions.append({
                    "topic": topic,
                    "positions": positions
                })
        
        return contradictions


def main():
    """Command-line interface for querying the memory system."""
    parser = argparse.ArgumentParser(description="Query the philosophical debate memory system")
    
    # Set up subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List debates command
    list_parser = subparsers.add_parser("list", help="List recent debates")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of debates to show")
    
    # Search by topic command
    search_parser = subparsers.add_parser("search", help="Search for debates by topic")
    search_parser.add_argument("topic", help="Topic to search for")
    
    # Agent positions command
    agent_parser = subparsers.add_parser("agent", help="Get an agent's positions")
    agent_parser.add_argument("name", help="Name of the agent")
    agent_parser.add_argument("--topic", help="Optional specific topic")
    
    # Debate details command
    debate_parser = subparsers.add_parser("debate", help="Get details of a specific debate")
    debate_parser.add_argument("id", help="ID of the debate")
    
    # Contradiction finder command
    contradiction_parser = subparsers.add_parser("contradictions", help="Find potential contradictions in agent positions")
    contradiction_parser.add_argument("name", help="Name of the agent")
    
    # Define memory directory option for all commands
    parser.add_argument("--memory-dir", default="memory", help="Path to memory directory")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize query tool
    query_tool = MemoryQueryTool(args.memory_dir)
    
    # Execute appropriate command
    if args.command == "list":
        debates = query_tool.list_debates(args.limit)
        if not debates:
            print("No debates found in memory.")
        else:
            print(f"Found {len(debates)} debate(s):")
            for i, debate in enumerate(debates):
                print(f"{i+1}. Topic: {debate['topic']}")
                print(f"   Date: {debate['date']}")
                print(f"   ID: {debate['id']}")
                print(f"   Agents: {', '.join(debate['agents'])}")
                print()
    
    elif args.command == "search":
        debates = query_tool.search_debates_by_topic(args.topic)
        if not debates:
            print(f"No debates found related to '{args.topic}'.")
        else:
            print(f"Found {len(debates)} debate(s) related to '{args.topic}':")
            for i, debate in enumerate(debates):
                print(f"{i+1}. Topic: {debate['topic']}")
                print(f"   Relevance: {debate.get('relevance', 'Unknown')}")
                print(f"   Date: {debate.get('date', 'Unknown')}")
                print(f"   ID: {debate.get('id', debate.get('debate_id', 'Unknown'))}")
                print()
    
    elif args.command == "agent":
        positions = query_tool.get_agent_positions(args.name, args.topic)
        if not positions:
            print(f"No positions found for agent '{args.name}'" + 
                  (f" on topic '{args.topic}'." if args.topic else "."))
        else:
            print(f"Positions for agent '{args.name}':")
            for topic, topic_positions in positions.items():
                print(f"Topic: {topic}")
                for i, position in enumerate(topic_positions):
                    print(f"  Position {i+1} (Date: {position.get('date', 'Unknown')}):")
                    print(f"    {position.get('position', 'No position statement')}")
                    print(f"    From debate: {position.get('debate_id', 'Unknown')}")
                    print()
    
    elif args.command == "debate":
        debate = query_tool.get_debate_details(args.id)
        if not debate:
            print(f"No debate found with ID '{args.id}'.")
        else:
            print(f"Debate: {debate.get('topic', 'Unknown')}")
            print(f"Date: {debate.get('date', 'Unknown')}")
            print(f"Agents: {', '.join(agent.get('name', 'Unknown') for agent in debate.get('agents', []))}")
            print("\nSummary:")
            print(debate.get('summary', 'No summary available.'))
            print("\nAnalysis:")
            for agent in debate.get('agents', []):
                print(f"\n{agent.get('name', 'Unknown Agent')}:")
                print(agent.get('analysis', 'No analysis available.'))
    
    elif args.command == "contradictions":
        contradictions = query_tool.find_contradictions(args.name)
        if not contradictions:
            print(f"No potential contradictions found for agent '{args.name}'.")
        else:
            print(f"Potential contradictions for agent '{args.name}':")
            for contradiction in contradictions:
                print(f"\nTopic: {contradiction['topic']}")
                for i, position in enumerate(contradiction['positions']):
                    print(f"Position {i+1} (Date: {position.get('date', 'Unknown')}):")
                    print(f"  {position.get('position', 'No position statement')}")
                    print(f"  From debate: {position.get('debate_id', 'Unknown')}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
