"""
judge_loader.py - Dynamic judge agent loader for the debate system.
Loads judge definitions from markdown files in judge_definitions/.
"""
import os
from .judge_agent import JudgeAgent

def load_judges_from_directory(judge_definitions_dir):
    """
    Load JudgeAgent instances from all markdown files in the given directory.
    Args:
        judge_definitions_dir (str): Path to judge definitions directory
    Returns:
        list of JudgeAgent
    """
    judges = []
    for fname in os.listdir(judge_definitions_dir):
        if fname.endswith('.md'):
            path = os.path.join(judge_definitions_dir, fname)
            with open(path, 'r') as f:
                lines = f.readlines()
                # First line is the judge name (## JudgeName)
                name = lines[0].strip().lstrip('#').strip()
                # Everything inside the code block is the prompt
                prompt_lines = []
                in_code = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code = not in_code
                        continue
                    if in_code:
                        prompt_lines.append(line)
                prompt = ''.join(prompt_lines).strip()
                judges.append(JudgeAgent(name, prompt))
    return judges
