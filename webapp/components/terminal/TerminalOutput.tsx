'use client';

import { Message } from '@/types';
import { parseVizCommands, splitTextByVizs, replaceVizsWithErrors } from '@/utils/viz-parser';
import VizRenderer from '@/components/visualizations/VizRenderer';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ToolExecution } from './HybridTerminal';

interface TerminalOutputProps {
  messages: Message[];
  isLoading?: boolean;
  activeTool?: ToolExecution | null;
  validationProgress?: string | null;
  onRegenerate?: (vizType: string, userMessage: string) => void;
}

export default function TerminalOutput({ messages, isLoading = false, activeTool = null, validationProgress = null, onRegenerate }: TerminalOutputProps) {
  const shouldShowLoading = isLoading && messages.length > 0;
  const lastIndex = messages.length - 1;

  return (
    <div className="space-y-6">
      {messages.map((msg, i) => {
        const isLast = i === lastIndex;
        const isLastAssistant = isLast && msg.role === 'assistant';
        const isLastUser = isLast && msg.role === 'user';
        return (
          <div key={i} className="animate-fadeIn break-words overflow-wrap-anywhere" style={{ animationDuration: '0.3s' }}>
            {msg.role === 'user' ? (
              <>
                <UserMessage content={msg.content} />
                {/* Show loading indicator after the last user message when waiting for assistant */}
                {shouldShowLoading && isLastUser && (
                  <LoadingIndicator activeTool={activeTool} validationProgress={validationProgress} />
                )}
              </>
            ) : (
              <>
                <AssistantMessage message={msg} onRegenerate={onRegenerate} />
                {/* Show loading indicator after the last assistant message when streaming */}
                {shouldShowLoading && isLastAssistant && (
                  <LoadingIndicator activeTool={activeTool} validationProgress={validationProgress} />
                )}
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}

function UserMessage({ content }: { content: string }) {
  return (
    <div className="bg-[#252526] px-4 py-3 rounded-r border-l-3 border-[#5C6AC4] border-l-[3px] break-words overflow-wrap-anywhere">
      <div className="text-[#E0E0E0] font-['Fira_Code',monospace] text-sm break-words whitespace-pre-wrap">
        <span className="text-[#5C6AC4] font-semibold">➜ user@termai:~$ </span>
        {content}
      </div>
    </div>
  );
}

function PulsingDots({ size = 'sm' }: { size?: 'sm' | 'md' }) {
  const dotSize = size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2';
  return (
    <div className="flex gap-1">
      <span className={`${dotSize} bg-[#BB86FC] rounded-full animate-pulse`} style={{ animationDelay: '0ms' }}></span>
      <span className={`${dotSize} bg-[#BB86FC] rounded-full animate-pulse`} style={{ animationDelay: '150ms' }}></span>
      <span className={`${dotSize} bg-[#BB86FC] rounded-full animate-pulse`} style={{ animationDelay: '300ms' }}></span>
    </div>
  );
}

function LoadingIndicator({ activeTool, validationProgress }: { activeTool: ToolExecution | null; validationProgress?: string | null }) {
  return (
    <div className="flex items-center gap-3 mt-4 py-2 px-3 bg-[#1E1E1E]/50 rounded border border-[#3E3E42]/50">
      {activeTool?.status === 'running' ? (
        <>
          <svg className="animate-spin h-4 w-4 text-[#BB86FC]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-xs">
            {activeTool.name}...
          </span>
        </>
      ) : activeTool ? (
        <>
          <PulsingDots size="sm" />
          <div className="flex items-center gap-2">
            <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-xs">
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
      ) : validationProgress ? (
        <>
          <svg className="animate-spin h-4 w-4 text-[#03A9F4]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-[#03A9F4] font-semibold font-['Fira_Code',monospace] text-xs">
            {validationProgress}
          </span>
        </>
      ) : (
        <>
          <PulsingDots size="sm" />
          <span className="text-[#BB86FC] font-semibold font-['Fira_Code',monospace] text-xs">
            Thinking...
          </span>
        </>
      )}
    </div>
  );
}

function AssistantMessage({ message, onRegenerate }: { message: Message; onRegenerate?: (vizType: string, userMessage: string) => void }) {
  // Parse viz commands (server-side validated, so minimal client-side parsing needed)
  const { vizs, errors } = parseVizCommands(message.content);

  // If we somehow still have errors (shouldn't happen with server validation), replace them
  // This is a fallback for edge cases
  const contentWithErrors = errors.length > 0
    ? replaceVizsWithErrors(message.content, errors)
    : message.content;

  // Split text by viz positions to remove markdown syntax
  const parts = splitTextByVizs(contentWithErrors, vizs);

  return (
    <div className="bg-[#252526] px-4 py-4 rounded-r border-l-3 border-[#BB86FC] border-l-[3px] break-words overflow-wrap-anywhere">
      {/* Content with inline visualizations */}
      <div className="text-[#E0E0E0] text-sm leading-relaxed break-words overflow-wrap-anywhere">
        {parts.map((part, i) => {
          if (part.type === 'text') {
            return (
              <ReactMarkdown
                key={i}
                className="prose prose-invert max-w-none prose-sm break-words"
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => <h1 className="text-white font-bold text-lg mb-3 mt-4 tracking-wide break-words">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-white font-semibold text-base mb-2.5 mt-3 tracking-wide break-words">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-white font-medium text-sm mb-2 mt-2 tracking-wide break-words">{children}</h3>,
                  p: ({ children }) => <p className="mb-3 text-[#E0E0E0] leading-relaxed break-words">{children}</p>,
                  code: ({ children }) => (
                    <code className="bg-[#2D2D2D] text-[#4FC1FF] px-1.5 py-0.5 rounded text-sm border border-[#333333] break-all">{children}</code>
                  ),
                  pre: ({ children }) => (
                    <pre className="bg-[#1a1a1a] border border-[#333333] rounded p-3 overflow-x-auto text-sm leading-relaxed my-3 whitespace-pre-wrap break-words">{children}</pre>
                  ),
                  ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1 break-words">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1 break-words">{children}</ol>,
                  li: ({ children }) => <li className="text-[#D0D0D0] leading-relaxed break-words">{children}</li>,
                  strong: ({ children }) => <strong className="text-white font-bold break-words">{children}</strong>,
                  a: ({ children, href }) => (
                    <a href={href} className="text-[#5C6AC4] hover:text-[#75BEFF] underline transition-colors break-all" target="_blank" rel="noopener noreferrer">{children}</a>
                  ),
                }}
              >
                {part.content}
              </ReactMarkdown>
            );
          } else if (part.type === 'viz') {
            const viz = vizs[part.index!];
            return (
              <div key={i} className="my-4">
                <VizRenderer command={viz.command} />
              </div>
            );
          }
          return null;
        })}

        {/* Render regeneration buttons if present */}
        {message.regenerateButtons && message.regenerateButtons.length > 0 && onRegenerate && (
          <div className="mt-4 flex flex-wrap gap-2">
            {message.regenerateButtons.map((button, idx) => (
              <button
                key={idx}
                onClick={() => onRegenerate(button.vizType, button.userMessage)}
                className="px-3 py-1.5 bg-[#5C6AC4] hover:bg-[#75BEFF] text-white text-xs font-['Fira_Code',monospace] rounded border border-[#5C6AC4]/50 transition-all duration-200 flex items-center gap-2"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Regenerate {button.vizType}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
