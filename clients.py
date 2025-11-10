"""
Client initialization for external services.
This module provides clients for OpenAI API and Docker daemon.
"""

import os
from openai import OpenAI
import docker
from dotenv import load_dotenv

load_dotenv(override=True)

# OpenAI client initialization
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY environment variable not set. Please set it to use the agent.")
    openai_client = None
else:
    openai_client = OpenAI(api_key=api_key)

# Docker client initialization
try:
    docker_client = docker.from_env()
    print("Docker client initialized successfully.")
except Exception as e:
    print(f"Warning: Docker client initialization failed: {e}")
    print("Docker-based tools will not be available.")
    docker_client = None
