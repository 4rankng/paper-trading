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
    <div className="h-9 bg-[#252526] flex items-center px-2 gap-1.5">
      {tabs.map(tab => (
        <div
          key={tab.id}
          onClick={() => handleTabClick(tab.id)}
          className={`
            relative flex items-center gap-2 px-4 py-1.5 rounded-t cursor-pointer transition-all
            ${
              tab.isActive
                ? 'bg-[#1E1E1E] text-[#E0E0E0] border border-[#333333] border-b-0 -mb-px'
                : 'bg-[#1E1E1E] text-[#B3B3B3] hover:text-[#E0E0E0]'
            }
          `}
        >
          <span className="text-sm font-['Fira_Code',monospace]">
            {tab.label}
          </span>
          {tabs.length > 1 && (
            <button
              onClick={e => handleTabClose(e, tab.id)}
              className="
                ml-1 w-4 h-4 rounded-sm flex items-center justify-center
                hover:bg-[#333333] transition-opacity
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
          px-3 py-1 rounded hover:bg-[#2D2D2D]
          text-[#858585] hover:text-[#E0E0E0] transition-colors text-lg
        "
        aria-label="New tab"
        title="New Session"
      >
        +
      </button>
    </div>
  );
}
