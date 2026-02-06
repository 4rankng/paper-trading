'use client';

import { useTerminalStore } from '@/store/useTerminalStore';

export default function MobileHeader() {
  const { isLoading, clearMessages } = useTerminalStore();

  const handleClearHistory = () => {
    clearMessages();
  };

  const handleSettings = () => {
    console.log('Settings');
  };

  return (
    <div className="h-12 bg-[#252526] border-b border-[#333333] flex items-center justify-between px-3 select-none shrink-0" style={{ paddingTop: 'var(--safe-area-inset-top, 0px)' }}>
      {/* Left: App name */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-[#E0E0E0] font-semibold font-['Fira_Code',monospace]">
          TermAI
        </span>
        <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-[#DCDCAA] animate-pulse' : 'bg-[#89D185]'}`} />
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleClearHistory}
          className="text-[#B3B3B3] hover:text-[#E0E0E0] transition-colors font-['Fira_Code',monospace] text-xs touch-target flex items-center justify-center"
          aria-label="Clear history"
        >
          Clear
        </button>
        <button
          onClick={handleSettings}
          className="text-[#B3B3B3] hover:text-[#E0E0E0] transition-colors text-lg touch-target flex items-center justify-center"
          aria-label="Settings"
        >
          ⚙
        </button>
      </div>
    </div>
  );
}
