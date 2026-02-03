#!/usr/bin/env python3
"""Check Zalo login status and account info."""

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
  if (result.type === 'ready') {
    const api = zalo.getAPI();
    const ownId = await api.getOwnId();
    const friends = await api.getAllFriends();
    const groups = await api.getAllGroups();
    console.log(JSON.stringify({
      status: 'logged_in',
      own_id: ownId,
      friends_count: friends?.length || 0,
      groups_count: groups?.length || 0
    }));
  } else {
    console.log(JSON.stringify({ status: 'not_logged_in' }));
  }
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
        print("Failed to check status:", result.stderr)
        return 1

    try:
        data = json.loads(result.stdout.strip())
        if data.get('status') == 'logged_in':
            print("✓ Logged in to Zalo")
            print(f"  User ID: {data.get('own_id', 'Unknown')}")
            print(f"  Friends: {data.get('friends_count', 0)}")
            print(f"  Groups: {data.get('groups_count', 0)}")
        else:
            print("✗ Not logged in")
        return 0
    except json.JSONDecodeError:
        print("Failed to parse response")
        return 1

if __name__ == "__main__":
    sys.exit(main())
