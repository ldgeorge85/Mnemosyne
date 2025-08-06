#!/usr/bin/env python3
"""
Download required NLP models for memory extraction.
"""

import subprocess
import sys

def download_spacy_model():
    """Download the spaCy English model."""
    print("Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✓ spaCy model downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download spaCy model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_spacy_model()
    print("\nAll models downloaded successfully!")