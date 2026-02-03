#!/bin/bash
# Post-task hook: Audit trail for trading decisions
# Runs after any skill completes

# Only log if the task involved trading analysis
if [[ "$CLAUDE_TASK" =~ trade|analyze|debate|position|portfolio|buy|sell ]]; then
  LOG_FILE=".claude/logs/audit_trail.log"
  mkdir -p .claude/logs

  echo "==========================================" >> "$LOG_FILE"
  echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
  echo "Task: $CLAUDE_TASK" >> "$LOG_FILE"
  echo "Session: ${CLAUDE_SESSION_ID:-unknown}" >> "$LOG_FILE"

  # Log any newly created trading plans
  if [ -d "trading-plans" ]; then
    NEW_PLANS=$(find trading-plans -name "*.md" -mmin -5 2>/dev/null || echo "")
    if [ -n "$NEW_PLANS" ]; then
      echo "New Trading Plans:" >> "$LOG_FILE"
      echo "$NEW_PLANS" >> "$LOG_FILE"
    fi
  fi

  echo "" >> "$LOG_FILE"
fi
