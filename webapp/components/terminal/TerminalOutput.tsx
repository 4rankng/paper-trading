'use client';

import { Message } from '@/types';
import { parseVizCommands, splitTextByVizs, replaceVizsWithErrors } from '@/utils/viz-parser';
import VizRenderer from '@/components/visualizations/VizRenderer';
import ReactMarkdown from 'react-markdown';

interface TerminalOutputProps {
  messages: Message[];
}

export default function TerminalOutput({ messages }: TerminalOutputProps) {
  return (
    <div className="space-y-6">
      {messages.map((msg, i) => (
        <div key={i} className="animate-fadeIn break-words overflow-wrap-anywhere" style={{ animationDuration: '0.3s' }}>
          {msg.role === 'user' ? (
            <UserMessage content={msg.content} />
          ) : (
            <AssistantMessage message={msg} />
          )}
        </div>
      ))}
    </div>
  );
}

function UserMessage({ content }: { content: string }) {
  return (
    <div className="bg-[#252526] px-4 py-3 pb-[25px] rounded-r border-l-3 border-[#5C6AC4] border-l-[3px] break-words overflow-wrap-anywhere">
      <div className="text-[#E0E0E0] font-['Fira_Code',monospace] text-sm break-words whitespace-pre-wrap">
        <span className="text-[#5C6AC4] font-semibold">➜ user@termai:~$ </span>
        {content}
      </div>
    </div>
  );
}

function AssistantMessage({ message }: { message: Message }) {
  // Parse viz commands and get any errors
  const { vizs, errors } = parseVizCommands(message.content);

  // Replace error vizs with helpful error messages
  const contentWithErrors = errors.length > 0
    ? replaceVizsWithErrors(message.content, errors)
    : message.content;

  // Split text by viz positions to remove markdown syntax
  const parts = splitTextByVizs(contentWithErrors, vizs);

  return (
    <div className="bg-[#252526] px-4 py-4 pb-[75px] rounded-r border-l-3 border-[#BB86FC] border-l-[3px] break-words overflow-wrap-anywhere">
      {/* Content with inline visualizations */}
      <div className="text-[#E0E0E0] text-sm leading-relaxed break-words overflow-wrap-anywhere">
        {parts.map((part, i) => {
          if (part.type === 'text') {
            return (
              <ReactMarkdown
                key={i}
                className="prose prose-invert max-w-none prose-sm break-words"
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
      </div>
    </div>
  );
}
