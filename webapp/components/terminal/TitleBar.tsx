'use client';

import { useTerminalStore } from '@/store/useTerminalStore';

interface TitleBarProps {
  onNewTab?: () => void;
}

export default function TitleBar({ onNewTab }: TitleBarProps) {
  const { sessionId, isLoading } = useTerminalStore();

  const handleMinimize = () => {
    // Placeholder - would integrate with window manager in desktop app
    console.log('Minimize');
  };

  const handleMaximize = () => {
    // Placeholder
    console.log('Maximize');
  };

  const handleClose = () => {
    // Placeholder
    console.log('Close');
  };

  return (
    <div className="h-10 bg-[#252526] border-b border-[#333333] flex items-center justify-between px-4 select-none">
      {/* Window controls - macOS style */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleClose}
          className="w-3 h-3 rounded-full bg-[#F48771] hover:bg-[#FF6B5B] transition-colors"
          aria-label="Close"
        />
        <button
          onClick={handleMinimize}
          className="w-3 h-3 rounded-full bg-[#DCDCAA] hover:bg-[#FFE05E] transition-colors"
          aria-label="Minimize"
        />
        <button
          onClick={handleMaximize}
          className="w-3 h-3 rounded-full bg-[#89D185] hover:bg-[#6BFF6B] transition-colors"
          aria-label="Maximize"
        />
      </div>

      {/* Title */}
      <h1 className="text-sm text-[#E0E0E0] font-medium">TermAI Explorer</h1>

      {/* Session status */}
      <div className="flex items-center gap-2">
        <div
          className={`w-2 h-2 rounded-full ${
            isLoading ? 'bg-[#DCDCAA] animate-pulse' : 'bg-[#89D185]'
          }`}
        />
        <span className="text-xs text-[#858585]">
          {sessionId ? 'Connected' : 'Connecting...'}
        </span>
      </div>
    </div>
  );
}
