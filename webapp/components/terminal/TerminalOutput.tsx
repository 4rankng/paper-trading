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
          <div className="text-terminal-dim text-sm mb-1">
            {msg.role === 'user' ? 'user@termai' : 'assistant@termai'}
            {' '}@ {new Date(msg.timestamp).toLocaleTimeString()}
          </div>
          <div className="text-terminal-green font-mono whitespace-pre-wrap">
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
              components={{
                p: ({ children }) => <p className="mb-2">{children}</p>,
                code: ({ children }) => (
                  <code className="bg-terminal-dim px-1">{children}</code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-terminal-dim p-2 overflow-x-auto">{children}</pre>
                ),
              }}
            >
              {part.content}
            </ReactMarkdown>
          );
        } else if (part.type === 'viz') {
          const viz = vizCommands[part.index!];
          return <VizRenderer key={i} command={viz.command} />;
        }
        return null;
      })}
    </>
  );
}
