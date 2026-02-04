'use client';

import { Message } from '@/types';
import { parseVizCommands, splitTextByVizs } from '@/lib/viz-parser';
import VizRenderer from '@/components/visualizations/VizRenderer';
import ReactMarkdown from 'react-markdown';

interface TerminalOutputProps {
  messages: Message[];
}

export default function TerminalOutput({ messages }: TerminalOutputProps) {
  return (
    <div className="space-y-4">
      {messages.map((msg, i) => (
        <div key={i} className="mb-4">
          {/* System metadata: smaller, lower opacity for hierarchy */}
          <div className="text-[#858585] text-xs mb-3 font-mono opacity-60">
            {msg.role === 'user' ? (
              <span className="text-[#89D185] font-semibold">➜ user@termai</span>
            ) : (
              <span className="text-[#5C6AC4]">→ assistant</span>
            )}
            {' '}@ {new Date(msg.timestamp).toLocaleTimeString()}
          </div>
          {/* Primary output: enhanced readability with better leading and spacing */}
          <div className="text-[#E0E0E0] font-mono whitespace-pre-wrap leading-relaxed tracking-wide">
            <MessageContent message={msg} />
          </div>
        </div>
      ))}
    </div>
  );
}

function MessageContent({ message }: { message: Message }) {
  const vizCommands = parseVizCommands(message.content);
  const parts = splitTextByVizs(message.content, vizCommands);

  return (
    <>
      {parts.map((part, i) => {
        if (part.type === 'text') {
          return (
            <ReactMarkdown
              key={i}
              className="prose prose-invert max-w-none prose-sm"
              components={{
                p: ({ children }) => <p className="mb-3 text-[#E0E0E0] leading-relaxed tracking-wide">{children}</p>,
                code: ({ children }) => (
                  <code className="bg-[#252526] text-[#4FC1FF] px-2 py-1 rounded text-sm tracking-wide border border-[#333333]">{children}</code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-[#252526] border border-[#333333] rounded p-3 overflow-x-auto text-sm leading-relaxed tracking-wide">{children}</pre>
                ),
                ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1.5">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1.5">{children}</ol>,
                li: ({ children }) => <li className="text-[#B3B3B3] leading-relaxed">{children}</li>,
                strong: ({ children }) => <strong className="text-[#BB86FC] font-semibold">{children}</strong>,
                a: ({ children, href }) => (
                  <a href={href} className="text-[#5C6AC4] hover:text-[#75BEFF] underline transition-colors" target="_blank" rel="noopener noreferrer">{children}</a>
                ),
              }}
            >
              {part.content}
            </ReactMarkdown>
          );
        } else if (part.type === 'viz') {
          const viz = vizCommands[part.index!];
          return (
            <div key={i} className="my-4">
              <VizRenderer command={viz.command} />
            </div>
          );
        }
        return null;
      })}
    </>
  );
}
