"""
Main entry point for the Baby Manus agent.
Launches the terminal-based UI for interacting with the agent.
"""

import asyncio
import sys
import traceback
from dotenv import load_dotenv
from simple_ui import main as ui_main


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler to catch all unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't print traceback for keyboard interrupts
        print("\nApplication interrupted. Goodbye!")
        return

    print(f"\n[CRITICAL ERROR] Unhandled exception: {exc_type.__name__}: {exc_value}")
    print("Full traceback:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    # Check for the specific Python executable error
    error_str = str(exc_value)
    if "executable" in error_str.lower() and ("python" in error_str.lower() or ".exe" in error_str.lower()):
        print("\n[PYTHON EXECUTABLE ERROR DETECTED]")
        print("This error suggests a path issue with Python executable detection.")
        print("Possible causes:")
        print("- Docker container trying to execute Python with wrong path")
        print("- Subprocess call with incorrect executable path")
        print("- Environment variable pointing to wrong Python location")
        print(f"Error details: {error_str}")


if __name__ == "__main__":
    # Install global exception handler
    sys.excepthook = global_exception_handler

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