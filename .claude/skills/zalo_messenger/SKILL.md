---
name: zalo-messenger
description: Send and manage Zalo messages. ALWAYS use for: "send zalo message", "zalo message", "message on zalo", "zalo chat", "check zalo status", "list zalo friends", "zalo contacts". Requires zca-js package and active Zalo session.
allowed-tools:
  - Bash(node:*)
  - Read
  - Write
---

# Zalo Messenger - Quick Reference

Send messages and manage Zalo account through zca-js library.

---

## Quick Start

```bash
# Send message to friend by name
python .claude/skills/zalo_messenger/scripts/send_message.py --name "Friend Name" --message "Hello"

# Send message to friend by ID
python .claude/skills/zalo_messenger/scripts/send_message.py --id "123456789" --message "Hello"

# List friends
python .claude/skills/zalo_messenger/scripts/list_friends.py

# Check login status
python .claude/skills/zalo_messenger/scripts/status.py
```

---

## Configuration

**Session file:** `~/Documents/mcp-zalo/zalo-session.json`

**Zalo package location:** `~/Documents/mcp-zalo/`

**Requirements:**
- Active Zalo session (QR login if first time)
- zca-js package installed

---

## Available Scripts

**Messaging:**
- `send_message.py` - Send message to friend by name or ID

**Listening:**
- `listen.py` - Start real-time message listener (runs until Ctrl+C)

**Account:**
- `status.py` - Check login status and account info
- `list_friends.py` - List all friends with IDs

---

## Usage Examples

```bash
# Listen for new messages (real-time)
python .claude/skills/zalo_messenger/scripts/listen.py

# Send Vietnamese message
python .claude/skills/zalo_messenger/scripts/send_message.py \
  --name "Đỗ Tuấn Cường" \
  --message "Xin chào! Tôi là Claude Code AI."

# Send to multiple friends
python .claude/skills/zalo_messenger/scripts/send_message.py \
  --name "Friend 1" --message "Hi" && \
python .claude/skills/zalo_messenger/scripts/send_message.py \
  --name "Friend 2" --message "Hello"

# Get friend ID for reference
python .claude/skills/zalo_messenger/scripts/list_friends.py | grep -i "friend name"
```

---

## Real-time Listener

The listener runs continuously and shows:

| Event | Display |
|-------|---------|
| New message | `[time] Friend Name: message text` |
| Your message | `[time] You: message text` (gray) |
| Group message | `[GROUP: name] Friend Name: text` |
| Typing | `[Typing] Friend Name is typing...` |
| Reaction | `[Reaction] Friend Name reacted: emoji` |

**Features:**
- Color-coded output (green for received, gray for sent)
- Friend name resolution from contacts
- Messages logged to `~/Documents/mcp-zalo/messages.log`
- Auto-reconnect on disconnect
- Keep-alive every 5 minutes

**Stop listener:** Press `Ctrl+C`

---

## Friend Name Matching

The script performs fuzzy matching on friend names:
- Case-insensitive
- Partial matches supported
- Returns first match if multiple found
- Shows exact name used in Zalo

---

## Error Handling

| Error | Solution |
|-------|----------|
| Session expired | Re-login with QR code |
| Friend not found | Use exact name from `list_friends.py` |
| API error | Check internet connection |
| Module not found | Install with `npm install zca-js` |

---

## Session Management

**First time setup:**
```bash
cd ~/Documents/mcp-zalo
node dist/index.js  # Will generate QR code
# Scan QR with Zalo app
```

**Session location:** `~/Documents/mcp-zalo/zalo-session.json`
