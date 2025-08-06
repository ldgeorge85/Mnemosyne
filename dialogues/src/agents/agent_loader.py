"""
Dynamic agent loader module.
Loads philosophical agent definitions from files and creates agent instances.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import BaseAgent
from .dynamic_agent import DynamicAgent


def extract_agent_definition_from_markdown(content: str) -> Dict[str, Any]:
    """
    Extract agent definition from a markdown file with Python code blocks.
    Format expected:
    
    ## AgentName
    ```python
    You are a [Philosophy] philosopher.
    ...details...
    ```
    
    Returns a dict with name, archetype and system_prompt
    """
    # Extract the name from the markdown heading
    name_match = re.search(r'^## (.+?)$', content, re.MULTILINE)
    if not name_match:
        raise ValueError("Could not find agent name in markdown file (expected ## AgentName format)")
    
    raw_name = name_match.group(1).strip()
    # Convert name to CamelCase and add "Agent" suffix if not present
    name_parts = raw_name.split()
    name = ''.join(part.capitalize() for part in name_parts)
    if not name.endswith("Agent"):
        name += "Agent"
    
    # Extract archetype (which is the original name without "Agent" suffix)
    archetype = raw_name
    
    # Extract the system prompt from the Python code block
    prompt_match = re.search(r'```python\s+(.*?)\s+```', content, re.DOTALL)
    if not prompt_match:
        raise ValueError("Could not find Python code block with system prompt")
    
    system_prompt = prompt_match.group(1).strip()
    
    # Enhanced prompt instructions for persona fidelity and debate realism
    analysis_instructions = (
        "You are simulating the worldview and reasoning style described above. "
        "You will be presented with a philosophical topic or question. "
        "Respond as if you are debating this topic with others, providing your answer and detailed justifications from your perspective. "
        "Clearly articulate your reasoning, values, and any relevant principles or beliefs that shape your response. "
        "Remain consistent with your defined persona throughout."
    )
    rebuttal_instructions = (
        "You are simulating the worldview and reasoning style described above. "
        "You will be presented with another agent’s opening statement or argument. "
        "Respond as if you are participating in a debate: either provide assent (agreement/support) or dissent (disagreement/critique) to their response, "
        "and justify your stance from your own philosophical perspective. Clearly explain your reasoning and reference your core beliefs or principles. "
        "Stay true to your defined persona and worldview."
    )
    return {
        "name": name,
        "archetype": archetype,
        "system_prompts": {
            # Opening/analysis prompt: simulate worldview, debate, justify answer
            "analysis": f"You are a {archetype} philosopher. {system_prompt}\n\n{analysis_instructions}",
            # Rebuttal/critique prompt: simulate worldview, respond to opening, assent or dissent, justify
            "critique": f"You are a {archetype} philosopher. {system_prompt}\n\n{rebuttal_instructions}"
        }
    }


def load_agent_definition_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load agent definition from a file. Supports JSON and Markdown formats.
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Agent definition file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if file_path.endswith('.json'):
        return json.loads(content)
    elif file_path.endswith('.md'):
        return extract_agent_definition_from_markdown(content)
    else:
        raise ValueError(f"Unsupported file format for agent definition: {file_path}")


def load_agents_from_directory(directory_path: str) -> List[BaseAgent]:
    """
    Load all agent definitions from a directory and instantiate agent objects.
    """
    agents = []
    
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Agent definitions directory not found: {directory_path}")
    
    # Find all .json and .md files in the directory
    file_paths = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json') or file.endswith('.md'):
                file_paths.append(os.path.join(root, file))
    
    # Load agent definitions from files
    for file_path in file_paths:
        try:
            agent_def = load_agent_definition_from_file(file_path)
            agent = DynamicAgent(
                name=agent_def["name"],
                archetype=agent_def["archetype"],
                analysis_prompt=agent_def["system_prompts"]["analysis"],
                critique_prompt=agent_def["system_prompts"]["critique"]
            )
            agents.append(agent)
            print(f"Loaded agent: {agent.name} ({agent.archetype})")
        except Exception as e:
            print(f"Error loading agent from {file_path}: {str(e)}")
    
    return agents


def convert_md_files_to_individual_agents(src_dir: str, dest_dir: str) -> None:
    """
    Convert the existing philosophical_agents_system_messages_part*.md files 
    to individual agent definition files.
    """
    os.makedirs(dest_dir, exist_ok=True)
    
    # Find all philosophical_agents_system_messages_part*.md files
    md_files = [f for f in os.listdir(src_dir) if f.startswith("philosophical_agents_system_messages_part") and f.endswith(".md")]
    
    for md_file in md_files:
        file_path = os.path.join(src_dir, md_file)
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split content by "##" which should mark the start of each agent definition
        sections = content.split("\n## ")
        if sections[0].startswith("# "):  # Remove the file header if present
            sections = sections[1:]
        else:
            sections[0] = sections[0].lstrip()  # Remove leading whitespace
        
        # Process each section
        for section in sections:
            if not section.strip():
                continue
                
            # Add back the "##" that was removed during splitting
            section = f"## {section}"
            
            try:
                agent_def = extract_agent_definition_from_markdown(section)
                agent_name = agent_def["name"]
                
                # Create a file for this agent
                with open(os.path.join(dest_dir, f"{agent_name}.md"), 'w') as f:
                    f.write(section)
                print(f"Created agent file: {agent_name}.md")
            except Exception as e:
                print(f"Error processing agent definition: {str(e)}")
