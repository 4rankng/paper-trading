'use client';

import { useTerminalStore } from '@/store/useTerminalStore';

interface TitleBarProps {
  onNewTab?: () => void;
}

export default function TitleBar({ onNewTab }: TitleBarProps) {
  const { isLoading } = useTerminalStore();

  const handleMinimize = () => {
    console.log('Minimize');
  };

  const handleMaximize = () => {
    console.log('Maximize');
  };

  const handleClose = () => {
    console.log('Close');
  };

  const handleSettings = () => {
    console.log('Settings');
  };

  const handleTheme = () => {
    console.log('Theme toggle');
  };

  return (
    <div className="h-10 bg-[#252526] border-b border-[#333333] flex items-center justify-between px-4 select-none" style={{ paddingTop: 'max(0px, env(safe-area-inset-top))' }}>
      {/* Window controls - macOS style */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleClose}
          className="w-3 h-3 rounded-full bg-[#F48771] hover:bg-[#FF6B5B] transition-colors cursor-pointer"
          aria-label="Close"
        />
        <button
          onClick={handleMinimize}
          className="w-3 h-3 rounded-full bg-[#DCDCAA] hover:bg-[#FFE05E] transition-colors cursor-pointer"
          aria-label="Minimize"
        />
        <button
          onClick={handleMaximize}
          className="w-3 h-3 rounded-full bg-[#89D185] hover:bg-[#6BFF6B] transition-colors cursor-pointer"
          aria-label="Maximize"
        />
        <span className="ml-3 text-sm text-[#B3B3B3] font-medium">TermAI Explorer</span>
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSettings}
          className="text-[#B3B3B3] hover:text-[#E0E0E0] transition-colors cursor-pointer text-lg"
          aria-label="Settings"
          title="Settings"
        >
          ⚙
        </button>
        <button
          onClick={handleTheme}
          className="text-[#B3B3B3] hover:text-[#E0E0E0] transition-colors cursor-pointer text-lg"
          aria-label="Toggle theme"
          title="Theme"
        >
          ☀
        </button>
      </div>
    </div>
  );
}
