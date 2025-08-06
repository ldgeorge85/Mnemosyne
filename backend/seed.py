#!/usr/bin/env python
"""
Seed Data CLI

This script provides a command-line interface for managing seed data.
It can be run directly to access seed commands.
"""

import sys

from app.db.seed.cli import main

if __name__ == "__main__":
    sys.exit(main())
