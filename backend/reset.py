#!/usr/bin/env python3
"""
Quick Database Reset for Testing
================================

Simple script to quickly reset the database during development.
This is a shortcut for: python cleanup_db.py --force

Usage:
    python reset.py        # Quick reset without prompts
"""

import subprocess
import sys
import os

def main():
    """Run the cleanup script with force flag"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cleanup_script = os.path.join(script_dir, 'cleanup_db.py')
    
    # Run the cleanup script with --force flag
    try:
        result = subprocess.run([sys.executable, cleanup_script, '--force'], 
                              cwd=script_dir, 
                              check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n❌ Reset cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    main() 