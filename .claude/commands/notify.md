---
name: notify
description: Send push notification via ntfy.sh immediately or scheduled via cron. Survives restarts.
argument-hint: [message] [delay: Nm, Nh, Nd, or HH:MM]
disable-model-invocation: true
allowed-tools:
  - Bash
---

Send push notification to phone via ntfy.sh.

**Input**: {TOPIC}

Parse input:
1. **message** = first argument (required)
2. **delay** = second argument (optional)
   - Relative: `Nm` (N minutes), `Nh` (N hours), `Nd` (N days)
   - Absolute: `HH:MM` (24-hour format, e.g., `14:30`)
   - Default: send immediately

---

## Send Immediately (no delay)

```bash
curl -s -d "{message}" ntfy.sh/Trade210887
```

Report: "Notification sent immediately"

---

## Send Delayed (Nm/Nh/Nd or HH:MM)

Uses the schedule-notify script which:
- Calculates target time
- Adds one-time cron entry
- Self-cleans after running (removes cron entry and temp script)

```bash
.claude/skills/notify/scripts/schedule-notify.sh "{message}" "{delay}"
```

Report output includes scheduled time and confirmation

---

## Managing Cron Jobs

```bash
# List current cron jobs
crontab -l

# Edit cron jobs manually
crontab -e

# Clear all cron jobs
crontab -r
```

---

**Note**: Working directory for cron jobs is `/Users/dev/Documents/my-schedule`
