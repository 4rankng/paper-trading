'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import { VizCommand } from '@/types/visualizations';
import TerminalOutput from './TerminalOutput';
import StatusBar from './StatusBar';
import { PulsingDots } from './PulsingDots';
import { useCommandHistory } from '@/hooks/terminal/useCommandHistory';
import { useChatStreaming, ToolExecution } from '@/hooks/terminal/useChatStreaming';

interface HybridTerminalProps {
  className?: string;
}

export { type ToolExecution };

export default function HybridTerminal({ className = '' }: HybridTerminalProps) {
  const [input, setInput] = useState('');
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

  const { navigateUp, navigateDown, resetIndex } = useCommandHistory(commandHistory);

  // Scroll to bottom when new messages arrive or loading state changes
  useEffect(() => {
    if (outputContainerRef.current) {
      outputContainerRef.current.scrollTop = outputContainerRef.current.scrollHeight;
    }
  }, [messages.length, isLoading]);

  const onMessage = useCallback((content: string, vizs: VizCommand[]) => {
    updateLastMessage(content, vizs);
  }, [updateLastMessage]);

  const onNewMessage = useCallback((content: string) => {
    addMessage({
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    });
  }, [addMessage]);

  const onAssistantMessage = useCallback((content: string, vizs: VizCommand[]) => {
    addMessage({
      role: 'assistant',
      content,
      visualizations: vizs,
      timestamp: new Date().toISOString(),
    });
  }, [addMessage]);

  const streamingReturn = useChatStreaming({
    sessionId,
    onMessage,
    onNewMessage,
    onAssistantMessage,
    setLoading,
    setError,
  });
  const executeCommand: (command: string) => Promise<void> = streamingReturn.executeCommand;
  const getActiveTool: () => ToolExecution | undefined = streamingReturn.getActiveTool;
  const getValidationProgress: () => string | undefined = streamingReturn.getValidationProgress;
  const cleanup: () => void = streamingReturn.cleanup;

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  const handleExecuteCommand = useCallback(async (command: string) => {
    addToCommandHistory(command);
    setInput('');
    resetIndex();
    await executeCommand(command);
  }, [addToCommandHistory, resetIndex, executeCommand]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleExecuteCommand(input);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const cmd = navigateUp();
      if (cmd !== null) setInput(cmd);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const cmd = navigateDown();
      if (cmd !== null) setInput(cmd);
    } else if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      setInput('');
      resetIndex();
    }
  };

  const handleClear = () => {
    clearMessages();
    setError(null);
  };

  const activeTool = getActiveTool();
  const validationProgress = getValidationProgress();

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
        <TerminalOutput
          messages={messages}
          isLoading={isLoading}
          activeTool={activeTool || null}
          validationProgress={validationProgress}
        />
        {isLoading && messages.length === 0 && (
          <div className="flex items-center gap-3 mt-6 py-3 px-4 bg-[#252526]/50 rounded-lg border border-[#3E3E42] animate-fadeIn">
            <PulsingDots size="md" />
            <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-sm md:text-base">
              Processing...
            </span>
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
