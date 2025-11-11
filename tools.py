
"""
Tools for the AI agent to interact with the environment.
These tools allow the agent to run commands in Docker containers and manipulate files.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from clients import docker_client
import docker.errors as docker_errors
import requests


class Tool(BaseModel):
    """Base class for all tools."""

    async def __call__(self) -> str:
        raise NotImplementedError


class ToolRunCommandInDevContainer(Tool):
    """Run a command in the dev container you have at your disposal to test and run code.

    The command will run in the container and the output will be returned.

    The container is a Python development container with Python 3.12 installed.

    It has the port 8888 exposed to the host in case the user asks you to run an http server.
    """

    command: str

    def _run(self) -> str:
        if docker_client is None:
            return "Error: Docker client not available. Please ensure Docker is running."

        try:
            # Get the container
            container = docker_client.containers.get("python-dev")
        except docker_errors.NotFound:
            return "Error: Python development container 'python-dev' not found. The container may not have started properly."
        except Exception as e:
            return f"Error: Failed to access container: {e}"

        # Check if container is running
        container.reload()
        if container.status != "running":
            return f"Error: Container 'python-dev' is not running (status: {container.status}). Please restart the agent."

        # Use bash -c to properly execute shell commands with operators
        exec_command = ["bash", "-c", self.command]

        try:
            result = container.exec_run(exec_command)
            exit_code = result.exit_code
            output = result.output

            # Debug: print raw output type and length
            # print(f"DEBUG: exit_code={exit_code}, output_type={type(output)}, output_len={len(output) if hasattr(output, '__len__') else 'N/A'}")

            if isinstance(output, bytes):
                output_str = output.decode("utf-8")
            elif isinstance(output, tuple) and len(output) >= 2:
                # Handle case where output is (stdout, stderr) tuple
                stdout_bytes, stderr_bytes = output[0], output[1]
                stdout_str = stdout_bytes.decode("utf-8") if isinstance(stdout_bytes, bytes) else str(stdout_bytes)
                stderr_str = stderr_bytes.decode("utf-8") if isinstance(stderr_bytes, bytes) else str(stderr_bytes)
                output_str = stdout_str + stderr_str
            else:
                output_str = str(output)

            if exit_code != 0:
                return f"Command failed with exit code {exit_code}:\n{output_str}"
            return output_str
        except Exception as e:
            return f"""Error executing command: {e}

Command attempted: {exec_command}"""

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


class ToolUpsertFile(Tool):
    """Create a file in the dev container you have at your disposal to test and run code.

    If the file exists, it will be updated, otherwise it will be created.
    """

    file_path: str = Field(description="The path to the file to create or update")
    content: str = Field(description="The content of the file")

    def _run(self) -> str:
        if docker_client is None:
            return "Error: Docker client not available. Please ensure Docker is running."

        try:
            # Get the container
            container = docker_client.containers.get("python-dev")
        except docker_errors.NotFound:
            return "Error: Python development container 'python-dev' not found. The container may not have started properly."
        except Exception as e:
            return f"Error: Failed to access container: {e}"

        # Check if container is running
        container.reload()
        if container.status != "running":
            return f"Error: Container 'python-dev' is not running (status: {container.status}). Please restart the agent."

        # Use Python with base64 to handle any content safely
        import base64
        encoded_content = base64.b64encode(self.content.encode('utf-8')).decode('utf-8')
        cmd = f"python3 -c \"import base64, sys; content = base64.b64decode('{encoded_content}').decode('utf-8'); open('{self.file_path}', 'w').write(content)\""

        try:
            # Execute the command
            exit_code, output = container.exec_run(cmd, stdout=True, stderr=True)

            if isinstance(output, bytes):
                output_str = output.decode("utf-8")
            else:
                output_str = str(output)

            if exit_code == 0:
                return "File written successfully"
            else:
                return f"""Error writing file: Command failed with exit code {exit_code}

File path: {self.file_path}
Command attempted: {cmd}
Error output: {output_str}"""
        except Exception as e:
            return f"""Error writing file: {e}

File path: {self.file_path}
Command attempted: {cmd}"""

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


class ToolGitStatus(Tool):
    """Check the current git status within the development container.

    This shows staged, unstaged, and untracked files in the git repository.
    """

    async def __call__(self) -> str:
        command = "git status --porcelain"
        return await ToolRunCommandInDevContainer(command=command)()


class ToolGitBranch(Tool):
    """Show current branch and available branches in the git repository."""

    async def __call__(self) -> str:
        command = "git branch -a"
        return await ToolRunCommandInDevContainer(command=command)()


class ToolGitCreateBranch(Tool):
    """Create a new git branch for feature development."""

    branch_name: str = Field(description="Name of the new branch to create")

    async def __call__(self) -> str:
        # First check if branch already exists
        check_command = f"git branch --list {self.branch_name}"
        check_result = await ToolRunCommandInDevContainer(command=check_command)()

        if self.branch_name in check_result:
            return f"Branch '{self.branch_name}' already exists"

        # Create and switch to the new branch
        create_command = f"git checkout -b {self.branch_name}"
        return await ToolRunCommandInDevContainer(command=create_command)()


class ToolGitAddFiles(Tool):
    """Add files to git staging area. Use '.' to add all files."""

    files: str = Field(description="Files to add (use '.' for all files, or space-separated file names)")

    async def __call__(self) -> str:
        command = f"git add {self.files}"
        return await ToolRunCommandInDevContainer(command=command)()


class ToolGitCommit(Tool):
    """Commit staged changes with a descriptive message."""

    message: str = Field(description="Commit message describing the changes")

    async def __call__(self) -> str:
        command = f"git commit -m \"{self.message}\""
        return await ToolRunCommandInDevContainer(command=command)()


class ToolGitPushBranch(Tool):
    """Push the current branch to remote repository."""

    async def __call__(self) -> str:
        # Get current branch name
        branch_command = "git rev-parse --abbrev-ref HEAD"
        branch_result = await ToolRunCommandInDevContainer(command=branch_command)()
        branch_name = branch_result.strip()

        if "fatal" in branch_result or not branch_name:
            return f"Error getting current branch: {branch_result}"

        command = f"git push -u origin {branch_name}"
        return await ToolRunCommandInDevContainer(command=command)()


class ToolTmuxCommand(Tool):
    """Run a command in a tmux session within the development container."""

    command: str = Field(description="The tmux command to execute")

    async def _run(self) -> str:
        tmux_command = f"tmux new-session -d -s mysession '{{self.command}}; bash'"

        try:
            # Run tmux command
            result = await ToolRunCommandInDevContainer(command=tmux_command)()
            return result

        except Exception as e:
            return f"Error executing tmux command: {e}"

    async def __call__(self) -> str:
        return await self._run()


class ToolReadFile(Tool):
    """Read a file from the host filesystem.

    This allows you to examine files on the host system, including your own source code.
    Useful for understanding the current codebase and planning modifications.
    """

    file_path: str = Field(description="The path to the file to read, relative to the project root")
    offset: Optional[int] = Field(default=None, description="Line number to start reading from (1-indexed)")
    limit: Optional[int] = Field(default=None, description="Maximum number of lines to read")

    def _run(self) -> str:
        try:
            # Resolve the path relative to the current working directory
            full_path = Path(self.file_path).resolve()

            # Basic security check - prevent reading files outside the project
            cwd = Path.cwd()
            if not str(full_path).startswith(str(cwd)):
                return f"Error: Cannot read files outside the project directory. Requested: {full_path}, Project: {cwd}"

            if not full_path.exists():
                return f"Error: File does not exist: {full_path}"

            if not full_path.is_file():
                return f"Error: Path is not a file: {full_path}"

            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Apply offset and limit if specified
            start_line = (self.offset - 1) if self.offset else 0
            end_line = (start_line + self.limit) if self.limit else None

            selected_lines = lines[start_line:end_line]

            # Format output with line numbers
            result = []
            for i, line in enumerate(selected_lines, start=start_line + 1):
                result.append(f"{i:4d}|{line}")

            content = "".join(result)

            if self.offset or self.limit:
                total_lines = len(lines)
                return f"File: {self.file_path} (lines {start_line + 1}-{start_line + len(selected_lines)} of {total_lines})\n\n{content}"
            else:
                return f"File: {self.file_path} ({len(lines)} lines)\n\n{content}"

        except UnicodeDecodeError:
            return f"Error: File contains binary data or unsupported encoding: {self.file_path}"
        except Exception as e:
            return f"Error reading file {self.file_path}: {e}"

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


class ToolListDirectory(Tool):
    """List contents of a directory on the host filesystem.

    This allows you to explore the project structure and see what files are available.
    """

    directory_path: str = Field(description="The path to the directory to list, relative to the project root")
    show_hidden: bool = Field(default=False, description="Whether to show hidden files (starting with .)")

    def _run(self) -> str:
        try:
            # Resolve the path relative to the current working directory
            full_path = Path(self.directory_path).resolve()

            # Basic security check
            cwd = Path.cwd()
            if not str(full_path).startswith(str(cwd)):
                return f"Error: Cannot access directories outside the project directory. Requested: {full_path}, Project: {cwd}"

            if not full_path.exists():
                return f"Error: Directory does not exist: {full_path}"

            if not full_path.is_dir():
                return f"Error: Path is not a directory: {full_path}"

            items = []
            for item in sorted(full_path.iterdir()):
                if not self.show_hidden and item.name.startswith('.'):
                    continue

                item_type = "DIR" if item.is_dir() else "FILE"
                size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                items.append(f"{item_type}: {item.name}{size}")

            if not items:
                return f"Directory: {self.directory_path}\n\n(No items found)"

            return f"Directory: {self.directory_path}\n\n" + "\n".join(items)

        except Exception as e:
            return f"Error listing directory {self.directory_path}: {e}"

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


class ToolSearchFiles(Tool):
    """Search for text patterns in files on the host filesystem.

    This allows you to find specific code, functions, or text across the codebase.
    """

    pattern: str = Field(description="The text pattern to search for (supports basic regex)")
    file_pattern: Optional[str] = Field(default=None, description="File pattern to limit search (e.g., '*.py' for Python files)")
    directory: str = Field(default=".", description="Directory to search in, relative to project root")

    def _run(self) -> str:
        try:
            import re

            # Resolve the directory path
            search_dir = Path(self.directory).resolve()
            cwd = Path.cwd()

            if not str(search_dir).startswith(str(cwd)):
                return f"Error: Cannot search outside the project directory. Requested: {search_dir}, Project: {cwd}"

            if not search_dir.exists() or not search_dir.is_dir():
                return f"Error: Invalid search directory: {search_dir}"

            matches = []

            # Walk through all files in the directory
            for file_path in search_dir.rglob('*'):
                if not file_path.is_file():
                    continue

                # Check file pattern if specified
                if self.file_pattern:
                    try:
                        import fnmatch
                        if not fnmatch.fnmatch(file_path.name, self.file_pattern):
                            continue
                    except:
                        # Skip file pattern matching if fnmatch fails
                        pass

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        if re.search(self.pattern, line):
                            # Get relative path for cleaner output
                            rel_path = file_path.relative_to(cwd)
                            matches.append(f"{rel_path}:{line_num}: {line.rstrip()}")

                except (UnicodeDecodeError, OSError):
                    # Skip binary files or files that can't be read
                    continue

            if not matches:
                return f"No matches found for pattern '{self.pattern}' in {search_dir}"

            # Limit results to prevent overwhelming output
            if len(matches) > 50:
                matches = matches[:50]
                matches.append(f"... and {len(matches) - 50} more matches (truncated)")

            return f"Search results for '{self.pattern}' in {self.directory}:\n\n" + "\n".join(matches)

        except Exception as e:
            return f"Error searching files: {e}"

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


def create_tool_interact_with_user(
    prompter: callable,
) -> type[Tool]:
    """Create a tool for interacting with the user."""

    class ToolInteractWithUser(Tool):
        """This tool will ask the user to clarify their request, provide your query and it will be asked to the user.

        You'll get the answer. Make sure that the content in display is properly markdowned, for instance if you display code, use the triple backticks to display it properly with the language specified for highlighting.
        """

        query: str = Field(description="The query to ask the user")
        display: str = Field(
            description="The interface has a panel on the right to display artifacts why you asks your query, use this field to display the artifacts, for instance code or file content, you must give the entire content to display, or use an empty string if you don't want to display anything."
        )

        async def __call__(self) -> str:
            res = await prompter(self.query)
            return res

    return ToolInteractWithUser


def check_container_status(container_name: str) -> str:
    """Check the status of a Docker container and return diagnostic information."""
    if docker_client is None:
        return "Docker client not available. Please ensure Docker is running."

    try:
        container = docker_client.containers.get(container_name)
        container.reload()
        return f"Container '{container_name}' status: {container.status}"
    except docker_errors.NotFound:
        return f"Container '{container_name}' not found."
    except Exception as e:
        return f"Error checking container status: {e}"


def start_python_dev_container(container_name: str) -> bool:
    """Start a Python development container with project directory mounted. Returns True if successful."""
    if docker_client is None:
        print("Warning: Docker client not available. Cannot start container.")
        return False

    try:
        # Check if container exists and clean it up
        try:
            existing_container = docker_client.containers.get(container_name)
            if existing_container.status == "running":
                existing_container.kill()
            existing_container.remove()
        except docker_errors.NotFound:
            pass

        # Get the project root directory (parent of current working directory)
        project_root = Path.cwd()

        # Ensure we're mounting the project directory
        volumes = {
            str(project_root): {"bind": "/app", "mode": "rw"}
        }

        # Use a custom image with git pre-installed, or build it if needed
        image_name = "simple-agent-dev:latest"

        try:
            # Try to use existing image
            docker_client.images.get(image_name)
        except docker_errors.ImageNotFound:
            # Build the image if it doesn't exist
            dockerfile_content = """FROM python:3.12
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
CMD ["tail", "-f", "/dev/null"]
"""
            # Write Dockerfile temporarily
            dockerfile_path = Path(".dockerfile_temp")
            dockerfile_path.write_text(dockerfile_content)

            try:
                # Build the image
                docker_client.images.build(
                    path=".",
                    dockerfile=str(dockerfile_path),
                    tag=image_name,
                    rm=True
                )
                print(f"[INFO] Built development container image: {image_name}")
            finally:
                # Clean up temp file
                dockerfile_path.unlink(missing_ok=True)

        container = docker_client.containers.run(
            image_name,
            detach=True,
            name=container_name,
            ports={"8888/tcp": 8888},
            tty=True,
            stdin_open=True,
            working_dir="/app",
            volumes=volumes,
            command="bash -c 'echo \"Container ready - project directory mounted at /app with git support\" && tail -f /dev/null'"
        )

        # Wait a moment for container to be ready
        import time
        time.sleep(2)

        # Verify container is running
        container.reload()
        if container.status == "running":
            return True
        else:
            print(f"[FAIL] Container '{container_name}' failed to start. Status: {container.status}")
            return False

    except Exception as e:
        print(f"[ERROR] Error starting container '{container_name}': {e}")
        return False


class ToolSearchAndReplace(Tool):
    """
    Search and replace a specific pattern in files across the project.
    """

    pattern: str = Field(description="The text pattern to search for")
    replacement: str = Field(description="The text to replace the found pattern with")
    directory: str = Field(description="The directory in which to perform the search and replace")

    def _run(self) -> str:
        if docker_client is None:
            return "Error: Docker client not available. Please ensure Docker is running."

        try:
            # Searching in the specified directory
            search_path = Path(self.directory)
            if not search_path.is_dir():
                return f"Error: The specified directory '{self.directory}' does not exist."

            # Walk through the directory
            for root, _, files in os.walk(search_path):
                for file in files:
                    file_path = Path(root) / file

                    # Skip files in __pycache__ directories and other binary files
                    if '__pycache__' in str(file_path) or file_path.suffix in ['.pyc', '.pyo', '.pyd']:
                        continue

                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Replace content
                        new_content = content.replace(self.pattern, self.replacement)

                        # If modified, write it back
                        if content != new_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)

                    except (UnicodeDecodeError, OSError):
                        # Skip binary files or files that can't be read as UTF-8
                        continue

            return "Search and replace completed successfully."
        except Exception as e:
            return f"Error during search and replace: {e}"

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


class ToolEditFile(Tool):
    """
    Edit a file in the dev container you have at your disposal to test and run code.

    If the file exists, it allows for appending to the file, otherwise creates a new one.
    """

    file_path: str = Field(description="The path to the file to edit")
    content: str = Field(description="The content to append to the file")

    def _run(self) -> str:
        if docker_client is None:
            return "Error: Docker client not available. Please ensure Docker is running."

        try:
            # Get the container
            container = docker_client.containers.get("python-dev")
        except docker_errors.NotFound:
            return "Error: Python development container 'python-dev' not found. The container may not have started properly."
        except Exception as e:
            return f"Error: Failed to access container: {e}"

        # Check if container is running
        container.reload()
        if container.status != "running":
            return f"Error: Container 'python-dev' is not running (status: {container.status}). Please restart the agent."

        # Use Python to append content
        import base64
        encoded_content = base64.b64encode(self.content.encode('utf-8')).decode('utf-8')
        cmd = f"python3 -c \"import base64; open('{self.file_path}', 'a').write(base64.b64decode('{encoded_content}').decode('utf-8'))\""

        try:
            # Execute the command
            exit_code, output = container.exec_run(cmd, stdout=True, stderr=True)

            if isinstance(output, bytes):
                output_str = output.decode("utf-8")
            else:
                output_str = str(output)

            if exit_code == 0:
                return "File edited successfully"
            else:
                return f"Error editing file: Command failed with exit code {exit_code}\n\nFile path: {self.file_path}\nCommand attempted: {cmd}\nError output: {output_str}"
        except Exception as e:
            return f"Error editing file: {e}\n\nFile path: {self.file_path}\nCommand attempted: {cmd}"

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


# Set default Git configuration for commit author
GIT_USER_NAME = 'BobbyBot'
GIT_USER_EMAIL = 'bobbybot@example.com'

# Function to configure Git user details
async def configure_git():
    await ToolRunCommandInDevContainer(command=f"git config --global user.name '{GIT_USER_NAME}'")()
    await ToolRunCommandInDevContainer(command=f"git config --global user.email '{GIT_USER_EMAIL}'")()

# Git configuration will be set when needed during tool usage


class WebSearchTool:
    """Web search tool for finding information online."""

    def __init__(self):
        pass

    def search(self, query):
        import requests
        response = requests.get(f'https://api.example.com/search?q={query}')
        return response.json()

    def open_url(self, url):
        response = requests.get(url)
        return {'data': response.text}


# Registering WebSearchTool as a tool
web_search_tool = WebSearchTool()


class ToolCurlCommand(Tool):
    """Execute curl commands for testing web APIs, downloading files, or making HTTP requests.

    This tool allows you to run curl commands directly on the host system, making it useful for:
    - Testing web APIs and endpoints (like the Flask app running in Docker)
    - Downloading files from URLs
    - Making various HTTP requests with custom headers, methods, and data
    - Debugging network connectivity issues

    Examples:
    - curl -X GET "http://localhost:8889/search?query=test"
    - curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://api.example.com/endpoint
    - curl -I http://example.com (just headers)
    - curl -L -o output.txt http://example.com/file.txt (download with redirects)
    """

    command: str = Field(description="The complete curl command to execute (without the 'curl' prefix)")

    def _run(self) -> str:
        """Execute the curl command and return the result."""
        import subprocess

        try:
            # Build the full command
            full_command = f"curl {self.command}"

            # Execute the curl command
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout for network requests
            )

            # Format the output
            output_lines = []

            if result.returncode == 0:
                output_lines.append("✅ Curl command executed successfully")
            else:
                output_lines.append(f"⚠️  Curl command failed with exit code {result.returncode}")

            if result.stdout.strip():
                output_lines.append("STDOUT:")
                output_lines.append(result.stdout)

            if result.stderr.strip():
                output_lines.append("STDERR:")
                output_lines.append(result.stderr)

            return "\n".join(output_lines)

        except subprocess.TimeoutExpired:
            return "❌ Curl command timed out after 30 seconds"
        except FileNotFoundError:
            return "❌ curl command not found. Please ensure curl is installed on the system."
        except Exception as e:
            return f"❌ Error executing curl command: {str(e)}"

    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)


class ToolSpawnSubagent(Tool):
    """Spawn a subagent to handle a specific task independently.

    This tool creates a separate agent instance with a focused prompt to complete
    the specified task, keeping the main agent's context minimal by offloading
    complex work to specialized subagents.
    """

    task: str = Field(description="The specific task for the subagent to complete")

    async def __call__(self) -> str:
        """Spawn a subagent for the given task that runs in the background."""
        try:
            # Import here to avoid circular imports
            from agent import Agent
            import asyncio

            # Create a focused system prompt for the subagent
            subagent_prompt = f"""You are a specialized subagent tasked with: {self.task}

Complete this task efficiently using the available tools. Focus only on the assigned task and provide clear, actionable results.

Available tools include:
- File operations (read, write, edit files)
- Directory listing and file search
- Command execution in development container
- Git operations (status, branch management, commits)
- User interaction for clarification

Work step-by-step and use tools as needed to complete the task successfully."""

            # Create subagent with all available tools (same as main agent)
            from simple_ui import (
                ToolRunCommandInDevContainer,
                ToolUpsertFile,
                ToolReadFile,
                ToolListDirectory,
                ToolSearchFiles,
                ToolGitStatus,
                ToolGitBranch,
                ToolGitCreateBranch,
                ToolGitAddFiles,
                ToolGitCommit,
                ToolGitPushBranch,
                ToolEditFile,
                ToolSearchAndReplace,
                ToolTmuxCommand,
                ToolCurlCommand,
            )

            # Create a user interaction tool that forwards to main agent
            def subagent_prompter(query: str) -> str:
                # For now, return a message that will be handled by the main agent
                # TODO: Implement proper inter-agent communication
                return f"[SUBAGENT REQUESTS CLARIFICATION] {query}"

            ToolInteractWithUser = create_tool_interact_with_user(subagent_prompter)

            subagent_tools = [
                ToolRunCommandInDevContainer,
                ToolUpsertFile,
                ToolReadFile,
                ToolListDirectory,
                ToolSearchFiles,
                ToolGitStatus,
                ToolGitBranch,
                ToolGitCreateBranch,
                ToolGitAddFiles,
                ToolGitCommit,
                ToolGitPushBranch,
                ToolEditFile,
                ToolSearchAndReplace,
                ToolTmuxCommand,
                ToolCurlCommand,
                ToolInteractWithUser
            ]

            # Create subagent instance
            subagent = Agent(
                system_prompt=subagent_prompt,
                model="gpt-4o-mini",
                tools=subagent_tools,
                messages=[]
            )

            # Add the task as a user message
            subagent.add_user_message(f"Please complete this task: {self.task}")

            # Start the subagent in the background
            async def run_subagent():
                """Run the subagent and handle its events."""
                try:
                    text_buffer = ""
                    async for event in subagent.agentic_loop():
                        from agent import EventText, EventToolUse, EventToolResult
                        if isinstance(event, EventText):
                            text_buffer += event.text
                            # Print complete lines or when buffer gets too large
                            if '\n' in text_buffer or len(text_buffer) > 100:
                                lines = text_buffer.split('\n')
                                for line in lines[:-1]:  # Print complete lines
                                    if line.strip():
                                        try:
                                            print(f"[SUBAGENT] {line}", flush=True)
                                        except UnicodeEncodeError:
                                            # Handle encoding issues by replacing problematic characters
                                            safe_line = line.encode('ascii', 'replace').decode('ascii')
                                            print(f"[SUBAGENT] {safe_line}", flush=True)
                                text_buffer = lines[-1]  # Keep incomplete line
                        elif isinstance(event, EventToolUse):
                            # Flush any buffered text first
                            if text_buffer.strip():
                                try:
                                    print(f"[SUBAGENT] {text_buffer}", flush=True)
                                except UnicodeEncodeError:
                                    safe_text = text_buffer.encode('ascii', 'replace').decode('ascii')
                                    print(f"[SUBAGENT] {safe_text}", flush=True)
                                text_buffer = ""
                            print(f"[SUBAGENT TOOL] {event.tool.__class__.__name__}", flush=True)
                        elif isinstance(event, EventToolResult):
                            # Flush any buffered text first
                            if text_buffer.strip():
                                try:
                                    print(f"[SUBAGENT] {text_buffer}", flush=True)
                                except UnicodeEncodeError:
                                    safe_text = text_buffer.encode('ascii', 'replace').decode('ascii')
                                    print(f"[SUBAGENT] {safe_text}", flush=True)
                                text_buffer = ""
                            result_preview = event.result[:100] + "..." if len(event.result) > 100 else event.result
                            try:
                                print(f"[SUBAGENT RESULT] {result_preview}", flush=True)
                            except UnicodeEncodeError:
                                safe_result = result_preview.encode('ascii', 'replace').decode('ascii')
                                print(f"[SUBAGENT RESULT] {safe_result}", flush=True)

                    # Flush any remaining buffered text
                    if text_buffer.strip():
                        try:
                            print(f"[SUBAGENT] {text_buffer}", flush=True)
                        except UnicodeEncodeError:
                            safe_text = text_buffer.encode('ascii', 'replace').decode('ascii')
                            print(f"[SUBAGENT] {safe_text}", flush=True)

                    print("[SUBAGENT] Task completed successfully.", flush=True)
                except Exception as e:
                    print(f"[SUBAGENT ERROR] {str(e)}", flush=True)

            # Create background task for subagent
            asyncio.create_task(run_subagent())

            # Return immediately so main thread isn't blocked
            return f"Subagent started for task: {self.task[:100]}{'...' if len(self.task) > 100 else ''}. It will run in the background and output will be prefixed with [SUBAGENT]."

        except Exception as e:
            return f"Error spawning subagent: {str(e)}"