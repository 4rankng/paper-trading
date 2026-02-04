'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { VizCommand } from '@/types/visualizations';
import TerminalOutput from './TerminalOutput';

interface HybridTerminalProps {
  className?: string;
}

export default function HybridTerminal({ className = '' }: HybridTerminalProps) {
  const [input, setInput] = useState('');
  const [historyIndex, setHistoryIndex] = useState(-1);
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

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (outputContainerRef.current) {
      outputContainerRef.current.scrollTop = outputContainerRef.current.scrollHeight;
    }
  }, [messages.length]);

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
                if (parsed.text) {
                  assistantMessage += parsed.text;

                  // Parse visualizations from accumulated text
                  const { parseVizCommands } = await import('@/utils/viz-parser');
                  const vizs = parseVizCommands(assistantMessage);
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
        className="flex-1 overflow-y-auto p-5"
      >
        {messages.length === 0 && (
          <div className="text-center py-16">
            <div className="text-white font-bold text-xl mb-3 tracking-wide font-['Fira_Code',monospace]">
              TermAI Explorer
            </div>
            <div className="text-[#5a5a5a] text-sm font-['Fira_Code',monospace]">
              Type a command and press Enter
            </div>
          </div>
        )}
        <TerminalOutput messages={messages} />
        {isLoading && (
          <div className="flex items-center gap-2 mt-4 text-sm">
            <div className="flex gap-1">
              <span className="w-1 h-1 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></span>
              <span className="w-1 h-1 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '200ms' }}></span>
              <span className="w-1 h-1 bg-[#BB86FC] rounded-full animate-pulse" style={{ animationDelay: '400ms' }}></span>
            </div>
            <span className="text-[#B3B3B3] font-['Fira_Code',monospace]">Processing...</span>
          </div>
        )}
        {error && (
          <div className="text-[#F48771] bg-[#F48771]/10 border-l-2 border-[#F48771] rounded-r p-3 mt-4 font-['Fira_Code',monospace] text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Terminal Input Area */}
      <div className="h-20 bg-[#252526] border-t border-[#333333] px-4 py-3 flex flex-col shrink-0">
        <div className="text-[#5C6AC4] font-semibold mb-1.5 text-sm font-['Fira_Code',monospace]">
          ➜ user@termai:~$
        </div>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a command... (Press Enter to send, Shift+Enter for new line)"
          className="flex-1 bg-[#1E1E1E] border border-[#3E3E42] rounded px-3 py-2 text-[#E0E0E0] font-['Fira_Code',monospace] text-sm resize-none outline-none focus:border-[#5C6AC4] placeholder:text-[#858585] wrap-soft"
          rows={2}
          wrap="soft"
        />
      </div>
    </div>
  );
}
