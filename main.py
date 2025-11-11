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

    # Run the terminal UI with graceful error handling for Windows asyncio cleanup
    try:
        asyncio.run(ui_main())
    except KeyboardInterrupt:
        print("\nApplication interrupted. Goodbye!")
    except Exception as e:
        # Handle Windows-specific asyncio cleanup errors gracefully
        if "NoneType" in str(e) and "close" in str(e):
            print("\nApplication shutdown complete.")
        else:
            print(f"Error: {e}")
            raise