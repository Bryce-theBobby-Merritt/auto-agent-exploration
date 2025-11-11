
class ToolTmuxCommand(Tool):
    """Run a command in a tmux session within the development container."""

    command: str = Field(description="The tmux command to execute")

    def _run(self) -> str:
        tmux_command = f"tmux new-session -d -s mysession '{{self.command}}; bash'"

        try:
            # Run tmux command
            result = await ToolRunCommandInDevContainer(command=tmux_command)()
            return result
            
        except Exception as e:
            return f"Error executing tmux command: {e}"
    
    async def __call__(self) -> str:
        return await asyncio.to_thread(self._run)
# Set default Git configuration for commit author
GIT_USER_NAME = 'BobbyBot'
GIT_USER_EMAIL = 'bobbybot@example.com'

# Function to configure Git user details
async def configure_git():
    await ToolRunCommandInDevContainer(command=f"git config --global user.name '{GIT_USER_NAME}'")()
    await ToolRunCommandInDevContainer(command=f"git config --global user.email '{GIT_USER_EMAIL}'")()

# Call configure_git function whenever needed.# Ensure Git configuration is set before any push or commit
await configure_git()