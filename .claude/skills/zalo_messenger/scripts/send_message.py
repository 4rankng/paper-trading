#!/usr/bin/env python3
"""Send Zalo message to a friend by name or ID."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SESSION_PATH = Path.home() / "Documents/mcp-zalo/zalo-session.json"
MCP_ZALO_PATH = Path.home() / "Documents/mcp-zalo"

def get_friends():
    """Get list of friends from Zalo."""
    script = f'''
import('./dist/zalo-wrapper.js').then(async (m) => {{
  const ZaloWrapper = m.ZaloWrapper;
  const zalo = new ZaloWrapper('./zalo-session.json');
  const result = await zalo.initialize();
  if (result.type !== 'ready') {{
    console.log('ERROR: Not logged in');
    process.exit(1);
  }}
  const api = zalo.getAPI();
  const friends = await api.getAllFriends();
  console.log(JSON.stringify(friends || []));
  process.exit(0);
}}).catch(e => {{
  console.error('ERROR:', e.message);
  process.exit(1);
}});
'''
    result = subprocess.run(
        ["node", "-e", script],
        cwd=MCP_ZALO_PATH,
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout.strip())
    except:
        return None

def find_friend_by_name(friends, name):
    """Find friend by name (case-insensitive, partial match)."""
    if not friends:
        return None
    name_lower = name.lower()
    # Exact match first
    for friend in friends:
        display_name = friend.get('displayName') or friend.get('zaloName') or ''
        if display_name.lower() == name_lower:
            return friend
    # Partial match
    for friend in friends:
        display_name = friend.get('displayName') or friend.get('zaloName') or ''
        if name_lower in display_name.lower():
            return friend
    return None

def send_message(recipient_id, message):
    """Send message using Node.js wrapper."""
    script = f'''
import('./dist/zalo-wrapper.js').then(async (m) => {{
  const ZaloWrapper = m.ZaloWrapper;
  const zalo = new ZaloWrapper('./zalo-session.json');
  const result = await zalo.initialize();
  if (result.type !== 'ready') {{
    console.log('ERROR: Not logged in');
    process.exit(1);
  }}
  const sendResult = await zalo.sendMessage('{recipient_id}', `{message}`, false);
  if (sendResult.success) {{
    console.log('SUCCESS: Message sent');
  }} else {{
    console.log('ERROR:', sendResult.error);
    process.exit(1);
  }}
  process.exit(0);
}}).catch(e => {{
  console.error('ERROR:', e.message);
  process.exit(1);
}});
'''
    result = subprocess.run(
        ["node", "-e", script],
        cwd=MCP_ZALO_PATH,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result

def main():
    parser = argparse.ArgumentParser(description="Send Zalo message")
    parser.add_argument("--name", help="Friend name (fuzzy match)")
    parser.add_argument("--id", help="Friend user ID")
    parser.add_argument("--message", required=True, help="Message to send")
    parser.add_argument("--list", action="store_true", help="List friends and exit")
    args = parser.parse_args()

    if args.list:
        friends = get_friends()
        if friends:
            print(f"Friends ({len(friends)}):")
            for f in friends[:20]:  # Show first 20
                user_id = f.get('userId') or f.get('id') or 'Unknown'
                name = f.get('displayName') or f.get('zaloName') or 'Unknown'
                print(f"  {user_id}: {name}")
            if len(friends) > 20:
                print(f"  ... and {len(friends) - 20} more")
        else:
            print("Failed to get friends")
        return

    # Get recipient ID
    recipient_id = args.id
    if args.name:
        friends = get_friends()
        if not friends:
            print("ERROR: Could not fetch friends list")
            return 1
        friend = find_friend_by_name(friends, args.name)
        if not friend:
            print(f"ERROR: Friend '{args.name}' not found")
            print("Use --list to see available friends")
            return 1
        recipient_id = friend.get('userId') or friend.get('id')
        display_name = friend.get('displayName') or friend.get('zaloName') or args.name
        print(f"Sending to: {display_name} (ID: {recipient_id})")

    if not recipient_id:
        print("ERROR: Must specify --name or --id")
        return 1

    # Send message
    result = send_message(recipient_id, args.message)
    if "SUCCESS" in result.stdout:
        print(f"✓ Message sent!")
        return 0
    else:
        print(f"✗ Failed: {result.stdout or result.stderr}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
