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
    <div className="h-6 bg-[#2D2D2D] flex items-center justify-between px-3 text-xs text-white select-none border-t border-[#333333]">
      {/* Left: Session info - smaller, lower hierarchy */}
      <div className="flex items-center gap-4 text-[10px]">
        <span className="text-[#858585]">
          Session: {sessionId?.slice(0, 8) || '...'}
        </span>
        <span className="text-[#858585]">
          {messages.length} message{messages.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Center: Quick actions - colored accents */}
      <div className="flex items-center gap-3 text-[10px]">
        <button
          onClick={handleClearHistory}
          className="text-[#5C6AC4] hover:text-[#75BEFF] transition-colors"
          aria-label="Clear history"
        >
          Clear
        </button>
        <span className="text-[#3E3E42]">|</span>
        <button
          onClick={handleSettings}
          className="text-[#5C6AC4] hover:text-[#75BEFF] transition-colors"
          aria-label="Settings"
        >
          Settings
        </button>
      </div>

      {/* Right: Timestamp and status - prioritized */}
      <div className="flex items-center gap-4">
        <span className="text-[#89D185] font-medium">
          {isLoading ? 'Processing...' : 'Ready'}
        </span>
        <span className="text-[#858585] font-mono text-[10px]">
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
