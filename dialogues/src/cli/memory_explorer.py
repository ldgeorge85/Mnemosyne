#!/usr/bin/env python
"""
Memory Explorer CLI Tool

A command-line interface for exploring the debate memory system, viewing agent positions,
and analyzing philosophical consistency over time.
"""

import os
import sys
import cmd
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root to the path to make imports work
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.utils.memory_query import MemoryQueryTool


class MemoryExplorerShell(cmd.Cmd):
    """Interactive shell for exploring the memory system."""
    
    intro = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  PHILOSOPHICAL MEMORY EXPLORER                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    Explore debate history and agent positions through time.
    Type 'help' or '?' to list commands.
    """
    prompt = '(memory) '
    
    def __init__(self, memory_dir: str = "memory"):
        """Initialize the shell with a query tool.
        
        Args:
            memory_dir: Path to the memory directory
        """
        super().__init__()
        self.query_tool = MemoryQueryTool(memory_dir)
        self.current_debate = None
        self.current_agent = None
    
    def do_list(self, arg):
        """List recent debates: list [limit]"""
        try:
            limit = int(arg) if arg else 10
        except ValueError:
            print("Error: limit must be a number")
            return
        
        debates = self.query_tool.list_debates(limit)
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
    
    def do_search(self, arg):
        """Search for debates by topic: search <topic>"""
        if not arg:
            print("Error: topic required")
            return
        
        debates = self.query_tool.search_debates_by_topic(arg)
        if not debates:
            print(f"No debates found related to '{arg}'.")
        else:
            print(f"Found {len(debates)} debate(s) related to '{arg}':")
            for i, debate in enumerate(debates):
                print(f"{i+1}. Topic: {debate['topic']}")
                print(f"   Relevance: {debate.get('relevance', 'Unknown')}")
                print(f"   Date: {debate.get('date', 'Unknown')}")
                print(f"   ID: {debate.get('id', debate.get('debate_id', 'Unknown'))}")
                print()
    
    def do_debate(self, arg):
        """View debate details: debate <id>"""
        if not arg:
            print("Error: debate ID required")
            return
        
        debate = self.query_tool.get_debate_details(arg)
        if not debate:
            print(f"No debate found with ID '{arg}'.")
            return
        
        self.current_debate = debate
        
        print(f"Debate: {debate.get('topic', 'Unknown')}")
        print(f"Date: {debate.get('date', 'Unknown')}")
        print(f"Agents: {', '.join(agent.get('name', 'Unknown') for agent in debate.get('agents', []))}")
        print("\nSummary:")
        print(debate.get('summary', 'No summary available.'))
        
        # Ask if user wants to see full details
        response = input("\nView full analysis from all agents? (y/n): ")
        if response.lower() == 'y':
            print("\nAnalysis:")
            for agent in debate.get('agents', []):
                print(f"\n{agent.get('name', 'Unknown Agent')}:")
                print(agent.get('analysis', 'No analysis available.'))
    
    def do_agent(self, arg):
        """View agent positions: agent <name> [topic]"""
        args = arg.split(maxsplit=1)
        if not args:
            print("Error: agent name required")
            return
        
        agent_name = args[0]
        topic = args[1] if len(args) > 1 else None
        
        positions = self.query_tool.get_agent_positions(agent_name, topic)
        if not positions:
            print(f"No positions found for agent '{agent_name}'" + 
                  (f" on topic '{topic}'." if topic else "."))
            return
        
        self.current_agent = agent_name
        
        print(f"Positions for agent '{agent_name}':")
        for topic, topic_positions in positions.items():
            print(f"\nTopic: {topic}")
            for i, position in enumerate(topic_positions):
                print(f"  Position {i+1} (Date: {position.get('date', 'Unknown')}):")
                print(f"    {position.get('position', 'No position statement')}")
                print(f"    From debate: {position.get('debate_id', 'Unknown')}")
    
    def do_contradictions(self, arg):
        """Find potential contradictions in agent positions: contradictions <name>"""
        if not arg:
            print("Error: agent name required")
            return
        
        contradictions = self.query_tool.find_contradictions(arg)
        if not contradictions:
            print(f"No potential contradictions found for agent '{arg}'.")
        else:
            print(f"Potential contradictions for agent '{arg}':")
            for contradiction in contradictions:
                print(f"\nTopic: {contradiction['topic']}")
                for i, position in enumerate(contradiction['positions']):
                    print(f"Position {i+1} (Date: {position.get('date', 'Unknown')}):")
                    print(f"  {position.get('position', 'No position statement')}")
                    print(f"  From debate: {position.get('debate_id', 'Unknown')}")
    
    def do_agents(self, arg):
        """List all philosophical agents in the system"""
        agent_memories_dir = Path(self.query_tool.memory_dir) / "agents"
        
        if not agent_memories_dir.exists():
            print("No agent memories found.")
            return
        
        agents = []
        for agent_file in agent_memories_dir.glob("*.json"):
            agents.append(agent_file.stem)
        
        if not agents:
            print("No agent memories found.")
            return
        
        print("Philosophical agents with memory records:")
        for i, agent in enumerate(sorted(agents)):
            print(f"{i+1}. {agent}")
    
    def do_topics(self, arg):
        """List all topics discussed in debates"""
        debates_dir = Path(self.query_tool.memory_dir) / "debates"
        
        if not debates_dir.exists():
            print("No debate records found.")
            return
        
        topics = set()
        for debate_file in debates_dir.glob("*.json"):
            with open(debate_file, "r") as f:
                debate_data = json.load(f)
                topics.add(debate_data.get("topic", "Unknown"))
        
        if not topics:
            print("No topics found.")
            return
        
        print("Topics discussed in debates:")
        for i, topic in enumerate(sorted(topics)):
            if topic != "Unknown":
                print(f"{i+1}. {topic}")
    
    def do_exit(self, arg):
        """Exit the shell"""
        print("Goodbye!")
        return True
    
    # Aliases for common commands
    do_quit = do_exit
    do_bye = do_exit


def main():
    """Main function to run the memory explorer CLI."""
    parser = argparse.ArgumentParser(description="Explore the philosophical debate memory system")
    parser.add_argument("--memory-dir", default="memory", help="Path to memory directory")
    
    args = parser.parse_args()
    
    # Start the interactive shell
    shell = MemoryExplorerShell(args.memory_dir)
    shell.cmdloop()


if __name__ == "__main__":
    main()
