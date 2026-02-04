'use client';

import { useState } from 'react';

interface Tab {
  id: string;
  label: string;
  isActive: boolean;
}

interface TabBarProps {
  onNewTab?: () => void;
  onTabClose?: (tabId: string) => void;
  onTabSwitch?: (tabId: string) => void;
}

export default function TabBar({ onNewTab, onTabClose, onTabSwitch }: TabBarProps) {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: 'session-1', label: 'Session 1', isActive: true },
  ]);

  const handleTabClick = (tabId: string) => {
    setTabs(prev =>
      prev.map(tab => ({
        ...tab,
        isActive: tab.id === tabId,
      }))
    );
    onTabSwitch?.(tabId);
  };

  const handleTabClose = (e: React.MouseEvent, tabId: string) => {
    e.stopPropagation();
    if (tabs.length === 1) return; // Don't close last tab

    const newTabs = tabs.filter(tab => tab.id !== tabId);
    if (tabs.find(t => t.id === tabId)?.isActive && newTabs.length > 0) {
      newTabs[0].isActive = true;
      onTabSwitch?.(newTabs[0].id);
    }
    setTabs(newTabs);
    onTabClose?.(tabId);
  };

  const handleNewTab = () => {
    const newTabId = `session-${tabs.length + 1}`;
    const newTab: Tab = {
      id: newTabId,
      label: `Session ${tabs.length + 1}`,
      isActive: true,
    };

    setTabs(prev => [
      ...prev.map(tab => ({ ...tab, isActive: false })),
      newTab,
    ]);
    onNewTab?.();
  };

  return (
    <div className="h-9 bg-[#1E1E1E] border-b border-[#333333] flex items-end px-2">
      {tabs.map(tab => (
        <div
          key={tab.id}
          onClick={() => handleTabClick(tab.id)}
          className={`
            relative flex items-center gap-2 px-4 py-1.5 mr-1 rounded-t cursor-pointer transition-colors
            ${
              tab.isActive
                ? 'bg-[#252526] border-t border-x border-[#333333] -mb-px'
                : 'bg-[#1E1E1E] hover:bg-[#252526]/50'
            }
          `}
        >
          <span
            className={`text-sm ${
              tab.isActive ? 'text-[#E0E0E0]' : 'text-[#858585]'
            }`}
          >
            {tab.label}
          </span>
          {tabs.length > 1 && (
            <button
              onClick={e => handleTabClose(e, tab.id)}
              className="
                ml-1 w-4 h-4 rounded-sm flex items-center justify-center
                hover:bg-[#333333] opacity-0 group-hover:opacity-100
                transition-opacity
              "
              aria-label="Close tab"
            >
              <span className="text-[#858585] text-xs">×</span>
            </button>
          )}
        </div>
      ))}

      {/* New tab button */}
      <button
        onClick={handleNewTab}
        className="
          mb-1 px-2 py-1 rounded hover:bg-[#252526]/50
          text-[#858585] hover:text-[#E0E0E0] transition-colors
        "
        aria-label="New tab"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="currentColor"
        >
          <path d="M8 1v14M1 8h14" stroke="currentColor" strokeWidth="2" />
        </svg>
      </button>
    </div>
  );
}
