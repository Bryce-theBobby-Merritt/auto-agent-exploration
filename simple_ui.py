"""
Simple terminal-based user interface for the Baby Manus agent.
Handles user input and displays agent responses with streaming.
"""

import asyncio
from typing import Callable, Awaitable
from agent import Agent, EventText, EventInputJson, EventToolUse, EventToolResult
from tools import (
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
    create_tool_interact_with_user,
    start_python_dev_container,
    configure_git
)


class SimpleUI:
    """Simple terminal UI for interacting with the agent."""

    def __init__(self):
        self.agent = None

    async def prompt_user(self, query: str) -> str:
        """Prompt the user for input in the terminal."""
        print(f"\n🤔 {query}")
        return input("> ").strip()

    def initialize_agent(self, model: str = "gpt-4o-mini"):
        """Initialize the agent with tools."""
        # Start the Python dev container
        container_started = start_python_dev_container("python-dev")
        if not container_started:
            print("[WARN] Docker container failed to start. Docker tools may not work.")
            print("   Make sure Docker is running and you have the python:3.12 image.")

        # Create tools
        tools = [
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
            create_tool_interact_with_user(self.prompt_user)
        ]

        # System prompt for coding tasks with branch-based workflow
        system_prompt = """
You are a helpful AI coding assistant that works within a containerized development environment with git branch management.

You have access to tools that allow you to:
1. Run commands in a Python development container (ToolRunCommandInDevContainer)
2. Create and update files in the container (ToolUpsertFile)
3. Read files from the host filesystem to understand your codebase (ToolReadFile)
4. List directory contents on the host filesystem (ToolListDirectory)
5. Search for text patterns across files in your codebase (ToolSearchFiles)
6. Check git status (ToolGitStatus)
7. View and manage git branches (ToolGitBranch)
8. Create new feature branches (ToolGitCreateBranch)
9. Stage files for commit (ToolGitAddFiles)
10. Commit changes (ToolGitCommit)
11. Push branches to remote (ToolGitPushBranch)
12. Ask the user for clarification when needed

BRANCH-BASED WORKFLOW:
- For any coding task, create a new feature branch using ToolGitCreateBranch
- Use descriptive branch names like "feature/add-user-auth" or "bugfix/fix-login-validation"
- Make your changes and test them within the container
- Stage and commit your changes with clear, descriptive commit messages
- Push the branch when ready for host review
- The host will review and merge approved branches manually

IMPORTANT GUIDELINES:
- Always use the tools to test and run code - do not just describe what code would do
- When creating files, use relative paths from the container's /app directory (which is mounted to the project root)
- You can now read your own source code to understand your capabilities and plan extensions
- Use ToolReadFile to examine your own code and understand how to modify yourself
- Use ToolSearchFiles to find specific functions, classes, or patterns in the codebase
- Always create feature branches for changes - never work directly on main
- If a tool fails, analyze the error message and try a different approach
- For complex tasks, break them down into smaller steps
- Use simple, working code rather than complex solutions
- If Docker tools are not available, inform the user and suggest alternatives

WORKFLOW:
1. Read and understand your current codebase using ToolReadFile and ToolSearchFiles
2. Create files using ToolUpsertFile
3. Test them using ToolRunCommandInDevContainer
4. Iterate based on results
5. Ask for clarification if requirements are unclear

Always be helpful and provide clear explanations of what you're doing.
"""

        self.agent = Agent(
            system_prompt=system_prompt,
            model=model,
            tools=tools,
            messages=[]
        )

    async def run_interaction(self, user_input: str):
        """Run a single interaction with the agent."""
        if not self.agent:
            self.initialize_agent()

        # Add user message
        self.agent.add_user_message(user_input)

        # Stream agent response
        print("\nAgent:", end=" ", flush=True)

        
        async for event in self.agent.agentic_loop():
            if isinstance(event, EventText):
                print(event.text, end="", flush=True)
            elif isinstance(event, EventInputJson):
                # Could show partial JSON if needed
                pass
            elif isinstance(event, EventToolUse):
                print(f"\n[TOOL] Using tool: {event.tool.__class__.__name__}")
                if hasattr(event.tool, 'command'):
                    print(f"   Command: {event.tool.command}")
                elif hasattr(event.tool, 'file_path'):
                    print(f"   File: {event.tool.file_path}")
            elif isinstance(event, EventToolResult):
                print(f"[RESULT] Tool result: {event.result[:100]}{'...' if len(event.result) > 100 else ''}")

        print("\n")

    async def run(self):
        """Main UI loop for continuous interaction."""
        print("Welcome to the Bobby AI Coding Assistant!")
        print("Type your requests and I'll help you with coding tasks.")
        print("Commands: 'status' to check Docker, 'quit' or 'exit' to stop.\n")

        if not self.agent:
            self.initialize_agent()

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if user_input.lower() in ['status', 'docker status', 'check docker']:
                    from tools import check_container_status
                    status = check_container_status("python-dev")
                    print(f"[STATUS] Docker Status: {status}")
                    continue

                if not user_input:
                    continue

                await self.run_interaction(user_input)

            except EOFError:
                print("\nInput stream ended. Goodbye!")
                break
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue


async def main():
    """Main entry point for the UI."""
    ui = SimpleUI()
    await ui.run()


if __name__ == "__main__":
    asyncio.run(main())
