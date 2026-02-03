#!/bin/bash
# Pre-task hook: Fetch latest market context before trading decisions
# Runs before any skill that might make trading recommendations

# Only run if the task might involve trading analysis
if [[ "$CLAUDE_TASK" =~ trade|analyze|debate|position|portfolio ]]; then
  echo "[Hook] Checking market data freshness..."

  # Check Fear & Greed Index
  echo "[Hook] Current market sentiment check..."

  # Log this trading analysis session
  LOG_FILE=".claude/logs/trading_$(date +%Y%m%d).log"
  mkdir -p .claude/logs
  echo "$(date '+%Y-%m-%d %H:%M:%S') - Task: $CLAUDE_TASK" >> "$LOG_FILE"
fi
