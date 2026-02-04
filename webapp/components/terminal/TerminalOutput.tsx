'use client';

import { Message } from '@/types';
import { parseVizCommands, splitTextByVizs } from '@/lib/viz-parser';
import VizRenderer from '@/components/visualizations/VizRenderer';
import ReactMarkdown from 'react-markdown';

interface TerminalOutputProps {
  messages: Message[];
}

export default function TerminalOutput({ messages }: TerminalOutputProps) {
  // Only show assistant messages - user messages are internal only
  const assistantMessages = messages.filter(msg => msg.role === 'assistant');

  return (
    <div className="space-y-4">
      {assistantMessages.map((msg, i) => (
        <div key={i} className="mb-4">
          {/* Minimal timestamp - no card styling */}
          <div className="text-[#5a5a5a] text-xs mb-2 font-mono opacity-50">
            {new Date(msg.timestamp).toLocaleTimeString()}
          </div>
          {/* Clean terminal output - no borders, no backgrounds */}
          <div className="text-[#E8E8E8] font-mono whitespace-pre-wrap text-sm leading-relaxed">
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
                // Headers: bold white, not purple - create clear hierarchy, compact spacing
                h1: ({ children }) => <h1 className="text-white font-bold text-lg mb-3 mt-4 tracking-wide">{children}</h1>,
                h2: ({ children }) => <h2 className="text-white font-semibold text-base mb-2.5 mt-3 tracking-wide">{children}</h2>,
                h3: ({ children }) => <h3 className="text-white font-medium text-sm mb-2 mt-2 tracking-wide">{children}</h3>,
                // Paragraphs: compact spacing
                p: ({ children }) => <p className="mb-1.5 text-[#E8E8E8] leading-relaxed tracking-wide">{children}</p>,
                // Code: cyan for interactive elements
                code: ({ children }) => (
                  <code className="bg-[#252526] text-[#4FC1FF] px-1 py-0.5 rounded text-sm tracking-wide border border-[#333333] font-normal">{children}</code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-[#1a1a1a] border border-[#333333] rounded p-2.5 overflow-x-auto text-sm leading-relaxed tracking-wide my-3">{children}</pre>
                ),
                // Lists: left-aligned, compact
                ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1 ml-0">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1 ml-0">{children}</ol>,
                li: ({ children }) => <li className="text-[#D0D0D0] leading-relaxed pl-0.5">{children}</li>,
                // Strong/bold: white for primary emphasis
                strong: ({ children }) => <strong className="text-white font-bold">{children}</strong>,
                // Links: blue accent
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
