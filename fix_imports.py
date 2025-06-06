#!/usr/bin/env python3
"""
Script to automatically fix import errors in the Mnemosyne backend codebase.
This script replaces instances of 'from app.api import deps' with the correct
imports from app.api.dependencies.
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(filepath):
    """Fix imports in a specific file."""
    with open(filepath, 'r') as file:
        content = file.read()
    
    # Replace 'from app.api import deps' with correct imports
    if 'from app.api import deps' in content:
        new_content = content.replace(
            'from app.api import deps',
            'from app.api.dependencies.db import get_db\nfrom app.api.dependencies.auth import get_current_user'
        )
        
        # Replace 'deps.get_db' with 'get_db'
        new_content = re.sub(r'Depends\(deps\.get_db\)', r'Depends(get_db)', new_content)
        
        # Replace 'deps.get_current_user_id' with 'get_current_user'
        new_content = re.sub(
            r'current_user_id: str = Depends\(deps\.get_current_user_id\)', 
            r'current_user: Dict[str, Any] = Depends(get_current_user)', 
            new_content
        )
        
        # Write back to file
        with open(filepath, 'w') as file:
            file.write(new_content)
        
        return True
    
    return False

def main():
    # Path to backend app directory
    base_path = Path('/home/lewis/dev/personal/mnemosyne/backend/app')
    
    # Find all Python files
    python_files = list(base_path.glob('**/*.py'))
    files_changed = 0
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            print(f"Fixed imports in {file_path}")
            files_changed += 1
    
    print(f"Total files changed: {files_changed}")

if __name__ == "__main__":
    main()
