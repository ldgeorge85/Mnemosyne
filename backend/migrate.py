#!/usr/bin/env python
"""
Database Migration CLI

This script provides a command-line interface for managing database migrations.
It can be run directly to access migration commands.
"""

import sys

from app.db.manage_migrations import main

if __name__ == "__main__":
    sys.exit(main())
