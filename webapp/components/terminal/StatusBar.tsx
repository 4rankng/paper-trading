'use client';

import { useEffect, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';

export default function StatusBar() {
  const { sessionId, messages, isLoading } = useTerminalStore();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleClearHistory = () => {
    // TODO: Implement clear history
    console.log('Clear history');
  };

  const handleSettings = () => {
    // TODO: Open settings panel
    console.log('Settings');
  };

  return (
    <div className="h-6 bg-[#007ACC] flex items-center justify-between px-3 text-xs text-white select-none">
      {/* Left: Session info */}
      <div className="flex items-center gap-4">
        <span className="text-[#E0E0E0]">
          Session: {sessionId?.slice(0, 8) || '...'}
        </span>
        <span className="text-[#B3B3B3]">
          {messages.length} message{messages.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Center: Quick actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleClearHistory}
          className="hover:text-[#E0E0E0] transition-colors"
          aria-label="Clear history"
        >
          Clear
        </button>
        <span className="text-[#5C6AC4]">|</span>
        <button
          onClick={handleSettings}
          className="hover:text-[#E0E0E0] transition-colors"
          aria-label="Settings"
        >
          Settings
        </button>
      </div>

      {/* Right: Timestamp and status */}
      <div className="flex items-center gap-4">
        <span className="text-[#B3B3B3]">
          {isLoading ? 'Processing...' : 'Ready'}
        </span>
        <span className="text-[#E0E0E0] font-mono">
          {currentTime.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          })}
        </span>
      </div>
    </div>
  );
}
