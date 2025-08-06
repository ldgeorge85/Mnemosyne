#!/usr/bin/env python3
"""
Utility to convert the existing philosophical_agents_system_messages_part*.md files
into individual agent definition files in the agent_definitions directory.

Usage:
    python convert_agent_definitions.py

This will create agent_definitions/*.md files from the content in
agents/philosophical_agents_system_messages_part*.md files.
"""

import os
import re
import sys
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.agents.agent_loader import extract_agent_definition_from_markdown


def convert_md_files_to_individual_agents(src_dir: str, dest_dir: str) -> None:
    """
    Convert the existing philosophical_agents_system_messages_part*.md files 
    to individual agent definition files.
    """
    os.makedirs(dest_dir, exist_ok=True)
    
    # Find all philosophical_agents_system_messages_part*.md files
    md_files = [f for f in os.listdir(src_dir) 
                if f.startswith("philosophical_agents_system_messages_part") and f.endswith(".md")]
    
    print(f"Found {len(md_files)} system message files to process")
    agent_count = 0
    
    for md_file in sorted(md_files):
        file_path = os.path.join(src_dir, md_file)
        print(f"Processing {file_path}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split content by markdown headings (##)
        sections = re.split(r'\n(?=## )', content)
        
        # Remove the file header if present (# heading)
        if sections and sections[0].startswith("# "):
            first_section = sections[0]
            heading_end = first_section.find("\n")
            sections[0] = first_section[heading_end:].strip()
            if not sections[0]:
                sections = sections[1:]
        
        file_agent_count = 0
        
        # Process each section (each representing one agent)
        for i, section in enumerate(sections):
            if not section.strip():
                continue
                
            # Add back the "##" if it was removed during splitting
            if not section.startswith("##"):
                section = f"## {section}"
            
            try:
                # Extract agent info
                agent_def = extract_agent_definition_from_markdown(section)
                agent_name = agent_def["name"]
                
                # Create a file for this agent
                output_path = os.path.join(dest_dir, f"{agent_name}.md")
                with open(output_path, 'w') as f:
                    f.write(section)
                print(f"  Created agent file: {output_path}")
                file_agent_count += 1
                agent_count += 1
            except Exception as e:
                print(f"  Error processing agent definition ({md_file} section {i+1}): {str(e)}")
        
        print(f"  Processed {file_agent_count} agents from {md_file}")
    
    print(f"\nSuccessfully created {agent_count} agent definition files in {dest_dir}")


if __name__ == "__main__":
    agents_dir = os.path.join(project_root, "agents")
    agent_definitions_dir = os.path.join(project_root, "agent_definitions")
    
    print(f"Converting agent definitions from {agents_dir} to {agent_definitions_dir}")
    convert_md_files_to_individual_agents(agents_dir, agent_definitions_dir)
    
    print("\nDone! You can now use the dynamic agent loading by:")
    print("1. Using src/agents/orchestrator_dynamic.py instead of the original orchestrator.py")
    print("2. Modifying main.py to import and use the dynamic orchestrator")
