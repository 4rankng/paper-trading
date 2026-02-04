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
    <div className="space-y-2">
      {messages.map((msg, i) => (
        <div key={i} className="mb-2">
          {/* System metadata: heavily de-emphasized, minimal visual weight */}
          <div className="text-[#6a6a6a] text-[10px] mb-2 font-mono opacity-40 tracking-wider">
            {msg.role === 'user' ? (
              <span className="text-[#89D185]">➜ user</span>
            ) : (
              <span className="text-[#5C6AC4]">→ assistant</span>
            )}
            {' '}{new Date(msg.timestamp).toLocaleTimeString()}
          </div>
          {/* Primary output: bolder font weight for readability */}
          <div className="text-[#E8E8E8] font-mono whitespace-pre-wrap leading-relaxed tracking-wide font-[400] text-[15px]">
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
                // Headers: bold white, not purple - create clear hierarchy
                h1: ({ children }) => <h1 className="text-white font-bold text-xl mb-4 mt-6 tracking-wide">{children}</h1>,
                h2: ({ children }) => <h2 className="text-white font-semibold text-lg mb-3 mt-5 tracking-wide">{children}</h2>,
                h3: ({ children }) => <h3 className="text-white font-medium text-base mb-2 mt-4 tracking-wide">{children}</h3>,
                // Paragraphs: tighter spacing for related content
                p: ({ children }) => <p className="mb-2 text-[#E8E8E8] leading-relaxed tracking-wide">{children}</p>,
                // Code: cyan for interactive elements
                code: ({ children }) => (
                  <code className="bg-[#252526] text-[#4FC1FF] px-1.5 py-0.5 rounded text-sm tracking-wide border border-[#333333] font-normal">{children}</code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-[#1a1a1a] border border-[#333333] rounded p-3 overflow-x-auto text-sm leading-relaxed tracking-wide my-4">{children}</pre>
                ),
                // Lists: left-aligned numbers, indented body
                ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1 ml-0">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1 ml-0">{children}</ol>,
                li: ({ children }) => <li className="text-[#D0D0D0] leading-relaxed pl-1">{children}</li>,
                // Strong/bold: white for primary emphasis, not purple
                strong: ({ children }) => <strong className="text-white font-bold">{children}</strong>,
                // Links: blue accent, kept for interactive elements
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
            <div key={i} className="my-6">
              <VizRenderer command={viz.command} />
            </div>
          );
        }
        return null;
      })}
    </>
  );
}
