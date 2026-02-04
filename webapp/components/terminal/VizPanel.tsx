'use client';

import { useState } from 'react';
import { VizCommand } from '@/types/visualizations';
import VizRenderer from '@/components/visualizations/VizRenderer';

interface VizPanelProps {
  visualizations: VizCommand[];
  className?: string;
}

export default function VizPanel({ visualizations, className = '' }: VizPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed right-0 top-1/2 -translate-y-1/2 bg-[#252526] border-l border-t border-b border-[#333333] rounded-l-lg px-2 py-4 text-[#858585] hover:text-[#E0E0E0] hover:bg-[#2D2D2D] transition-all z-50"
        aria-label="Show visualizations"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="currentColor"
        >
          <path d="M6 4l4 4-4 4V4z" />
        </svg>
      </button>
    );
  }

  return (
    <div
      className={`
        bg-[#252526] border-l border-[#333333] flex flex-col transition-all duration-300
        ${isCollapsed ? 'w-12' : 'w-96'}
        ${className}
      `}
    >
      {/* Header */}
      <div className="h-10 border-b border-[#333333] flex items-center justify-between px-3">
        {!isCollapsed && (
          <h3 className="text-sm font-medium text-[#E0E0E0]">Visualizations</h3>
        )}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded hover:bg-[#333333] text-[#858585] hover:text-[#E0E0E0] transition-colors"
            aria-label={isCollapsed ? 'Expand panel' : 'Collapse panel'}
          >
            {isCollapsed ? (
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="currentColor"
              >
                <path d="M6 4l4 4-4 4V4z" />
              </svg>
            ) : (
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="currentColor"
              >
                <path d="M4 6l4 4 4-4H4z" />
              </svg>
            )}
          </button>
          <button
            onClick={() => setIsVisible(false)}
            className="p-1 rounded hover:bg-[#333333] text-[#858585] hover:text-[#E0E0E0] transition-colors"
            aria-label="Close panel"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="currentColor"
            >
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="flex-1 overflow-y-auto p-4">
          {visualizations.length === 0 ? (
            <div className="text-center py-8">
              <svg
                className="w-12 h-12 mx-auto mb-3 text-[#333333]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <p className="text-sm text-[#858585]">
                No visualizations yet
              </p>
              <p className="text-xs text-[#5C6AC4] mt-1">
                Ask for charts or tables
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {visualizations.map((viz, index) => (
                <div
                  key={`${viz.type}-${index}`}
                  className="
                    bg-[#1E1E1E] rounded-lg border border-[#333333]
                    hover:border-[#5C6AC4] transition-colors
                  "
                >
                  <div className="p-3 border-b border-[#333333]">
                    <span className="text-xs font-medium text-[#5C6AC4] uppercase">
                      {viz.type}
                    </span>
                    <span className="text-xs text-[#858585] ml-2">
                      #{index + 1}
                    </span>
                  </div>
                  <div className="p-3">
                    <VizRenderer command={viz} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      {!isCollapsed && (
        <div className="h-8 border-t border-[#333333] flex items-center justify-between px-3 text-xs text-[#858585]">
          <span>{visualizations.length} viz{visualizations.length !== 1 ? 's' : ''}</span>
          <span>Scroll ↓</span>
        </div>
      )}
    </div>
  );
}
