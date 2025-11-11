
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