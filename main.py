"""
Main entry point for the Baby Manus agent.
Launches the terminal-based UI for interacting with the agent.
"""

import asyncio
from dotenv import load_dotenv
from simple_ui import main as ui_main


if __name__ == "__main__":
    # Load env vars
    load_dotenv()

    # Run the terminal UI
    asyncio.run(ui_main())