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
    # Test that Docker is actually accessible
    docker_client.ping()
    print("Docker client initialized successfully.")
except docker.errors.DockerException as e:
    print(f"Warning: Docker daemon not accessible: {e}")
    print("Please ensure Docker Desktop is running and try again.")
    docker_client = None
except Exception as e:
    print(f"Warning: Docker client initialization failed: {e}")
    print("Docker-based tools will not be available.")
    print("Try: 1) Start Docker Desktop, 2) Restart this application")
    docker_client = None
