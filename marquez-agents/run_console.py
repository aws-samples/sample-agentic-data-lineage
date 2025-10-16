#!/usr/bin/env python3
"""
AWS Strands True Multi-Agent System Startup Script V3
Modular version
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Set environment configuration
# Local development environment, set environment variable for EKS: ENV_FOR_DYNACONF=development
if not os.environ.get("ENV_FOR_DYNACONF"):
    os.environ["ENV_FOR_DYNACONF"] = "local"

if __name__ == "__main__":
    from main import main

    main()
