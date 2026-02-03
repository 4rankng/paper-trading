#!/bin/bash

# schedule-notify.sh - Schedule a ntfy.sh notification via launchd (macOS native)
# Usage: schedule-notify.sh "message" "delay"
# Delay formats: Nm (minutes), Nh (hours), Nd (days), HH:MM (absolute time)

set -e

# Load environment variables from .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

MESSAGE="$1"
DELAY="$2"
TOPIC="${NTFY_TOPIC:-}"

# Launch agents directory
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TEMP_SCRIPT_DIR="$HOME/.schedule-notify-temp"
mkdir -p "$TEMP_SCRIPT_DIR"

# Function to calculate target time in seconds since epoch
calculate_target_time() {
    local delay="$1"

    # Check if absolute time (HH:MM)
    if [[ "$delay" =~ ^([0-1][0-9]|2[0-3]):([0-5][0-9])$ ]]; then
        local hour="${BASH_REMATCH[1]}"
        local minute="${BASH_REMATCH[2]}"
        local now=$(date +%s)

        # Build target date for today
        local target_date=$(date +"%Y-%m-%d")
        local target=$(date -j -f "%Y-%m-%d %H:%M:%S" "${target_date} ${hour}:${minute}:00" +"%s" 2>/dev/null)

        if [[ -z "$target" ]] || [[ "$target" -lt "$now" ]]; then
            # Time has passed today, schedule for tomorrow
            target=$(date -j -v+1d -f "%Y-%m-%d %H:%M:%S" "${target_date} ${hour}:${minute}:00" +"%s")
        fi
        echo "$target"
        return
    fi

    # Relative delays
    local interval="${delay%[mhd]}"
    local unit="${delay: -1}"

    case "$unit" in
        m) date -v+${interval}M +"%s" ;;
        h) date -v+${interval}H +"%s" ;;
        d) date -v+${interval}d +"%s" ;;
        *) echo "Error: Invalid delay format" >&2; exit 1 ;;
    esac
}

# Calculate target time
TARGET_EPOCH=$(calculate_target_time "$DELAY")

# Create unique job ID
JOB_ID="com.user.schedule-notify.$(date +%s)"
PLIST_FILE="$LAUNCH_AGENTS_DIR/$JOB_ID.plist"
TEMP_SCRIPT="$TEMP_SCRIPT_DIR/notify_$JOB_ID.sh"

# Create notification script
cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
# Send notification
curl -s -d "$(echo "$MESSAGE" | sed 's/"/\\"/g')" "ntfy.sh/$TOPIC"
# Cleanup
rm -f "$TEMP_SCRIPT"
launchctl bootout gui/$(id -u) "$JOB_ID" 2>/dev/null || true
rm -f "$PLIST_FILE"
EOF

chmod +x "$TEMP_SCRIPT"

# Calculate interval in seconds from now
NOW=$(date +%s)
INTERVAL=$((TARGET_EPOCH - NOW))

# Create launchd plist
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$JOB_ID</string>
    <key>ProgramArguments</key>
    <array>
        <string>$TEMP_SCRIPT</string>
    </array>
    <key>StartInterval</key>
    <integer>$INTERVAL</integer>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

# Load the job
launchctl load "$PLIST_FILE" 2>/dev/null

# Output confirmation
target_display=$(date -r "$TARGET_EPOCH" +"%H:%M:%S %d %b %Y")
echo "Notification scheduled: \"$MESSAGE\""
echo "Scheduled for: $target_display"
echo "Job ID: $JOB_ID"
