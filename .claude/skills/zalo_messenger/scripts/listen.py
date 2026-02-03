#!/usr/bin/env python3
"""Start Zalo real-time message listener."""

import subprocess
import sys
from pathlib import Path

MCP_ZALO_PATH = Path.home() / "Documents/mcp-zalo"
LISTENER_SCRIPT = MCP_ZALO_PATH / "listen-messages.js"

def main():
    print("Starting Zalo message listener...")
    print("Press Ctrl+C to stop\n")

    # Run the listener
    result = subprocess.run(
        ["node", str(LISTENER_SCRIPT)],
        cwd=MCP_ZALO_PATH,
        timeout=None  # Run indefinitely
    )

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
