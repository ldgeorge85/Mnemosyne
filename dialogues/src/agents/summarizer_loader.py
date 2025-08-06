"""
summarizer_loader.py - Loads the summarizer agent definition from summarizer_definitions/.
"""
import os

def load_summarizer_from_directory(summarizer_definitions_dir):
    """
    Load the summarizer prompt from the first markdown file in the directory.
    Args:
        summarizer_definitions_dir (str): Path to summarizer definitions directory
    Returns:
        (name, prompt): Tuple[str, str]
    """
    for fname in os.listdir(summarizer_definitions_dir):
        if fname.endswith('.md'):
            path = os.path.join(summarizer_definitions_dir, fname)
            with open(path, 'r') as f:
                lines = f.readlines()
                name = lines[0].strip().lstrip('#').strip()
                prompt_lines = []
                in_code = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code = not in_code
                        continue
                    if in_code:
                        prompt_lines.append(line)
                prompt = ''.join(prompt_lines).strip()
                return name, prompt
    raise FileNotFoundError("No summarizer definition found in directory.")
