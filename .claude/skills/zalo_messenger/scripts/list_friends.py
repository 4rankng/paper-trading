#!/usr/bin/env python3
"""List Zalo friends with their IDs."""

import json
import subprocess
import sys
from pathlib import Path

MCP_ZALO_PATH = Path.home() / "Documents/mcp-zalo"

def main():
    script = '''
import('./dist/zalo-wrapper.js').then(async (m) => {
  const ZaloWrapper = m.ZaloWrapper;
  const zalo = new ZaloWrapper('./zalo-session.json');
  const result = await zalo.initialize();
  if (result.type !== 'ready') {
    console.log('ERROR: Not logged in');
    process.exit(1);
  }
  const api = zalo.getAPI();
  const friends = await api.getAllFriends();
  console.log(JSON.stringify(friends || []));
  process.exit(0);
}).catch(e => {
  console.error('ERROR:', e.message);
  process.exit(1);
});
'''
    result = subprocess.run(
        ["node", "-e", script],
        cwd=MCP_ZALO_PATH,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        print("Failed to get friends:", result.stderr)
        return 1

    try:
        friends = json.loads(result.stdout.strip())
        if friends:
            print(f"Friends ({len(friends)}):")
            print("-" * 60)
            for f in friends:
                user_id = f.get('userId') or f.get('id') or 'Unknown'
                name = f.get('displayName') or f.get('zaloName') or 'Unknown'
                print(f"{user_id}: {name}")
        else:
            print("No friends found")
        return 0
    except json.JSONDecodeError:
        print("Failed to parse response")
        return 1

if __name__ == "__main__":
    sys.exit(main())
