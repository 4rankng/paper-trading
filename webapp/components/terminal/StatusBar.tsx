'use client';

import { useEffect, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';

export default function StatusBar() {
  const { sessionId, messages, isLoading, clearMessages } = useTerminalStore();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleClearHistory = () => {
    clearMessages();
  };

  const handleSettings = () => {
    // TODO: Open settings panel
    console.log('Settings');
  };

  return (
    <div className="h-6 bg-[#2D2D2D] flex items-center justify-between px-2 md:px-4 text-xs select-none border-t border-[#333333]">
      {/* Left: Session info */}
      <div className="flex items-center gap-2 md:gap-4">
        <div className="flex items-center gap-1.5 text-[#858585]">
          <span className="text-[10px]">Session:</span>
          <code className="text-[#B3B3B3] font-['Fira_Code',monospace]">
            {sessionId?.slice(0, 8) || '...'}
          </code>
        </div>
        <div className="text-[#858585] text-[10px] md:text-xs hidden md:block">
          {messages.length} message{messages.length !== 1 ? 's' : ''}
        </div>
        <button
          onClick={handleClearHistory}
          className="text-[#858585] hover:text-[#E0E0E0] transition-colors font-['Fira_Code',monospace] text-[10px] md:text-xs touch-target px-1"
          aria-label="Clear history"
        >
          Clear
        </button>
        <button
          onClick={handleSettings}
          className="text-[#858585] hover:text-[#E0E0E0] transition-colors font-['Fira_Code',monospace] text-[10px] md:text-xs touch-target px-1"
          aria-label="Settings"
        >
          Settings
        </button>
      </div>

      {/* Right: Status indicator */}
      <div
        className={`font-semibold font-['Fira_Code',monospace] ${
          isLoading ? 'text-[#DCDCAA]' : 'text-[#89D185]'
        }`}
      >
        {isLoading ? '● Processing...' : '● Ready'}
      </div>
    </div>
  );
}
