'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { VizCommand } from '@/types/visualizations';
import TerminalOutput from './TerminalOutput';
import StatusBar from './StatusBar';

interface HybridTerminalProps {
  className?: string;
}

interface ToolExecution {
  name: string;
  status: 'running' | 'success' | 'error';
  result?: string;
}

export default function HybridTerminal({ className = '' }: HybridTerminalProps) {
  const [input, setInput] = useState('');
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [activeTool, setActiveTool] = useState<ToolExecution | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const outputContainerRef = useRef<HTMLDivElement>(null);

  const {
    sessionId,
    messages,
    isLoading,
    error,
    commandHistory,
    addMessage,
    updateLastMessage,
    addToCommandHistory,
    setLoading,
    setError,
    clearMessages,
  } = useTerminalStore();

  // Scroll to bottom when new messages arrive or loading state changes
  useEffect(() => {
    if (outputContainerRef.current) {
      outputContainerRef.current.scrollTop = outputContainerRef.current.scrollHeight;
    }
  }, [messages.length, isLoading]);

  // Execute command
  const executeCommand = useCallback(async (command: string) => {
    if (!sessionId) {
      setError('No session active');
      return;
    }

    const trimmedCommand = command.trim();
    if (!trimmedCommand) return;

    addToCommandHistory(trimmedCommand);
    setInput('');
    setHistoryIndex(-1);

    // Add user message
    addMessage({
      role: 'user',
      content: trimmedCommand,
      timestamp: new Date().toISOString(),
    });

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmedCommand, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let assistantMessage = '';
      let currentVizs: VizCommand[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') continue;

              try {
                const parsed = JSON.parse(data);

                // Handle tool start event - set running immediately
                if (parsed.tool_start) {
                  setActiveTool({
                    name: parsed.tool_start.name,
                    status: 'running',
                  });
                  continue;
                }

                // Handle tool execution completion events
                if (parsed.tool_use) {
                  setActiveTool({
                    name: parsed.tool_use.name,
                    status: parsed.tool_use.result === 'Success' ? 'success' : 'error',
                    result: parsed.tool_use.result,
                  });
                  // Clear the tool status after 2 seconds
                  setTimeout(() => setActiveTool(null), 2000);
                  continue;
                }

                if (parsed.text) {
                  assistantMessage += parsed.text;

                  // Parse visualizations from accumulated text
                  const { parseVizCommands } = await import('@/utils/viz-parser');
                  const { vizs } = parseVizCommands(assistantMessage);
                  currentVizs = vizs.map(v => v.command);

                  // Update last message in real-time
                  if (assistantMessage === parsed.text) {
                    addMessage({
                      role: 'assistant',
                      content: assistantMessage,
                      timestamp: new Date().toISOString(),
                      visualizations: currentVizs,
                    });
                  } else {
                    updateLastMessage(assistantMessage, currentVizs);
                  }
                }
              } catch (e) {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMsg);
    } finally {
      setLoading(false);
      setActiveTool(null);
    }
  }, [sessionId, addMessage, updateLastMessage, addToCommandHistory, setLoading, setError]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      executeCommand(input);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex < commandHistory.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        const cmdIndex = commandHistory.length - 1 - newIndex;
        setInput(commandHistory[cmdIndex] || '');
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        const cmdIndex = commandHistory.length - 1 - newIndex;
        setInput(commandHistory[cmdIndex] || '');
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    } else if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      setInput('');
      setHistoryIndex(-1);
    }
  };

  const handleClear = () => {
    clearMessages();
    setError(null);
  };

  return (
    <div className={`flex flex-col h-full bg-[#1E1E1E] ${className}`}>
      {/* Message output area with inline visualizations */}
      <div
        ref={outputContainerRef}
        className="flex-1 overflow-y-auto overflow-x-hidden p-3 md:p-5 scroll-area-above-input smooth-scroll-touch"
      >
        {messages.length === 0 && (
          <div className="text-center py-12 md:py-16">
            <div className="text-white font-bold text-lg md:text-xl mb-3 tracking-wide font-['Fira_Code',monospace]">
              TermAI Explorer
            </div>
            <div className="text-[#858585] text-xs md:text-sm font-['Fira_Code',monospace]">
              Type a command and press Enter
            </div>
          </div>
        )}
        <TerminalOutput messages={messages} />
        {isLoading && (
          <div className="flex items-center gap-3 mt-6 py-3 px-4 bg-[#252526]/50 rounded-lg border border-[#3E3E42] animate-fadeIn">
            {activeTool?.status === 'running' ? (
              <>
                <svg className="animate-spin h-5 w-5 text-[#BB86FC]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-sm md:text-base">
                  {activeTool.name}...
                </span>
              </>
            ) : activeTool ? (
              <>
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-sm md:text-base">
                    {activeTool.name}
                  </span>
                  {activeTool.status === 'success' && (
                    <span className="text-green-400 text-xs font-['Fira_Code',monospace]">✓</span>
                  )}
                  {activeTool.status === 'error' && (
                    <span className="text-red-400 text-xs font-['Fira_Code',monospace]">✗</span>
                  )}
                </div>
              </>
            ) : (
              <>
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></span>
                </div>
                <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-sm md:text-base">
                  Processing...
                </span>
              </>
            )}
          </div>
        )}
        {error && (
          <div className="text-[#F48771] bg-[#F48771]/10 border-l-2 border-[#F48771] rounded-r p-2 md:p-3 mt-4 font-['Fira_Code',monospace] text-xs md:text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Bottom area: Input + StatusBar */}
      <div className="shrink-0 bg-[#1E1E1E] flex flex-col" style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}>
        {/* Terminal Input Area */}
        <div className="bg-[#252526] border-t border-[#333333] px-3 md:px-4 py-2 md:py-3">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command... (Press Enter to send, Shift+Enter for new line)"
            className="w-full bg-[#1E1E1E] border border-[#3E3E42] rounded px-2 md:px-3 py-2 md:py-2 text-[#E0E0E0] font-['Fira_Code',monospace] text-xs md:text-sm resize-none outline-none focus:border-[#5C6AC4] placeholder:text-[#858585] wrap-soft min-h-[44px] touch-target"
            rows={2}
            wrap="soft"
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
          />
        </div>

        {/* StatusBar */}
        <StatusBar />
      </div>
    </div>
  );
}
