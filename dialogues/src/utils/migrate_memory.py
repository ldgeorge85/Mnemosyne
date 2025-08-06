#!/usr/bin/env python
"""
Memory Data Migration Utility

This script updates existing debate and agent memory files to use the new
field structure. It adds proper topic, date, and agent information to debates,
and updates agent memory files to track positions correctly.
"""

import json
import os
import datetime
from pathlib import Path
import re


def migrate_memory_data(memory_dir="memory"):
    """
    Migrate existing memory data to the new format.
    
    Args:
        memory_dir: Path to the memory directory
    """
    print(f"Migrating memory data in {memory_dir}...")
    
    memory_dir = Path(memory_dir)
    debates_dir = memory_dir / "debates"
    agents_dir = memory_dir / "agents"
    
    if not debates_dir.exists() or not agents_dir.exists():
        print("Memory directories not found. No migration needed.")
        return
    
    # Migrate debate files
    debate_files = list(debates_dir.glob("*.json"))
    print(f"Found {len(debate_files)} debate files to migrate")
    
    for debate_file in debate_files:
        try:
            # Load the debate data
            with open(debate_file, "r") as f:
                debate_data = json.load(f)
            
            modified = False
            
            # Add date if missing
            if "date" not in debate_data:
                # Try to parse date from timestamp or debate_id
                if "timestamp" in debate_data:
                    date_str = debate_data["timestamp"]
                    try:
                        # Parse YYYYMMDD_HHMMSS format
                        date_obj = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                        formatted_date = date_obj.strftime("%B %d, %Y")
                        debate_data["date"] = formatted_date
                        modified = True
                    except ValueError:
                        # If timestamp is not in expected format, use debate_id
                        debate_id = debate_data.get("debate_id", debate_file.stem)
                        match = re.search(r"(\d{8})_", debate_id)
                        if match:
                            try:
                                date_obj = datetime.datetime.strptime(match.group(1), "%Y%m%d")
                                debate_data["date"] = date_obj.strftime("%B %d, %Y")
                                modified = True
                            except ValueError:
                                debate_data["date"] = "June 09, 2025"  # Fallback date
                                modified = True
                        else:
                            debate_data["date"] = "June 09, 2025"  # Fallback date
                            modified = True
                else:
                    debate_data["date"] = "June 09, 2025"  # Fallback date
                    modified = True
            
            # Add topic if missing
            if "topic" not in debate_data and "prompt" in debate_data:
                prompt = debate_data["prompt"]
                main_topic = prompt.split(".")[0] if prompt else "Unknown"
                if len(main_topic) > 50:  # Truncate if too long
                    main_topic = main_topic[:47] + "..."
                debate_data["topic"] = main_topic
                modified = True
            
            # Update agents information for responses
            has_responses = False
            if "responses" in debate_data and debate_data["responses"]:
                has_responses = True
                for response in debate_data["responses"]:
                    response_text = response.get("response", "")
                    
                    # If agent name is missing, try to extract it from the response
                    if "agent" not in response or response.get("agent") == "Unknown":
                        # Try to find signatures like "- The Utilitarian" or "Sincerely, Kantian"
                        signature_patterns = [
                            r'- The ([A-Za-z]+)',
                            r'--([A-Za-z]+)',
                            r'Sincerely, ([A-Za-z]+)',
                            r'([A-Za-z]+) Perspective:'
                        ]
                        
                        for pattern in signature_patterns:
                            match = re.search(pattern, response_text)
                            if match:
                                extracted_name = match.group(1).strip()
                                if len(extracted_name) > 2:  # Avoid things like "I" or "A"
                                    response["agent"] = extracted_name
                                    modified = True
                                    break
                        
                        # If no agent name found, assign a default
                        if "agent" not in response or response.get("agent") == "Unknown":
                            response["agent"] = "Philosopher"  # Default agent name
                            modified = True
            
            # Create formatted agents list for the explorer
            if "agents" not in debate_data and has_responses:
                # Extract agent names from responses
                formatted_agents = []
                for response in debate_data["responses"]:
                    formatted_agents.append({
                        "name": response.get("agent", "Unknown"),
                        "analysis": response.get("response", "No analysis available.")
                    })
                debate_data["agents"] = formatted_agents
                modified = True
            
            # Add summary if missing
            if "summary" not in debate_data:
                debate_data["summary"] = "Debate Summary:\nThe following perspectives were presented by each philosophical agent:"
                modified = True
                
            if modified:
                print(f"Updated debate {debate_file.stem}")
                with open(debate_file, "w") as f:
                    json.dump(debate_data, f, indent=2)
        except Exception as e:
            print(f"Error migrating debate {debate_file}: {e}")
    
    # Migrate agent memory files
    agent_files = list(agents_dir.glob("*.json"))
    print(f"Found {len(agent_files)} agent files to migrate")
    
    for agent_file in agent_files:
        try:
            # Load the agent memory
            with open(agent_file, "r") as f:
                agent_memory = json.load(f)
            
            modified = False
            
            # Migrate position_history to positions if needed
            if "position_history" in agent_memory and "positions" not in agent_memory:
                agent_memory["positions"] = agent_memory["position_history"]
                modified = True
            
            # Update debates with proper fields
            if "debates" in agent_memory:
                for debate in agent_memory["debates"]:
                    if "date" not in debate and "timestamp" in debate:
                        try:
                            # Parse YYYYMMDD_HHMMSS format
                            date_obj = datetime.datetime.strptime(debate["timestamp"], "%Y%m%d_%H%M%S")
                            debate["date"] = date_obj.strftime("%B %d, %Y")
                            modified = True
                        except ValueError:
                            debate["date"] = "June 09, 2025"  # Fallback date
                            modified = True
                    
                    if "topic" not in debate and "prompt" in debate:
                        prompt = debate["prompt"]
                        main_topic = prompt.split(".")[0] if prompt else "Unknown"
                        if len(main_topic) > 50:  # Truncate if too long
                            main_topic = main_topic[:47] + "..."
                        debate["topic"] = main_topic
                        modified = True
            
            # Make sure positions exists
            if "positions" not in agent_memory:
                agent_memory["positions"] = {}
                modified = True
            
            if modified:
                print(f"Updated agent {agent_file.stem}")
                with open(agent_file, "w") as f:
                    json.dump(agent_memory, f, indent=2)
        except Exception as e:
            print(f"Error migrating agent {agent_file}: {e}")
    
    print("Memory data migration complete.")


if __name__ == "__main__":
    import sys
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(project_root)
    
    memory_dir = sys.argv[1] if len(sys.argv) > 1 else "memory"
    migrate_memory_data(memory_dir)
