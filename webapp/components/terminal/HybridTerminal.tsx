'use client';

import { useEffect, useLayoutEffect, useRef, useCallback, useState } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import { useTerminalStore } from '@/store/useTerminalStore';
import { getXtermTheme, defaultTheme } from '@/lib/themes';
import { VizCommand } from '@/types/visualizations';
import TerminalOutput from './TerminalOutput';
import 'xterm/css/xterm.css';

interface HybridTerminalProps {
  className?: string;
}

export default function HybridTerminal({ className = '' }: HybridTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const inputBufferRef = useRef('');
  const commandHistoryIndexRef = useRef(-1);
  const outputContainerRef = useRef<HTMLDivElement>(null);

  const {
    sessionId,
    messages,
    isLoading,
    error,
    commandHistory,
    addMessage,
    addToCommandHistory,
    navigateCommandHistory,
    setLoading,
    setError,
  } = useTerminalStore();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (outputContainerRef.current) {
      outputContainerRef.current.scrollTop = outputContainerRef.current.scrollHeight;
    }
  }, [messages.length]); // eslint-disable-line react-hooks/exhaustive-deps

  // Initialize xterm.js for input only
  useLayoutEffect(() => {
    if (!terminalRef.current || xtermRef.current) return;

    const terminal = new Terminal({
      theme: getXtermTheme(defaultTheme),
      fontFamily: "'Fira Code', 'Source Code Pro', monospace",
      fontSize: 14,
      lineHeight: 1.2,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 0, // No scrollback, messages render above
      rows: 3, // Just enough for input line
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();

    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);

    terminal.open(terminalRef.current);

    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;

    // Handle window resize
    const handleResize = () => {
      requestAnimationFrame(() => {
        try {
          fitAddon.fit();
        } catch (e) {
          // Silently fail if terminal not ready
        }
      });
    };

    window.addEventListener('resize', handleResize);

    // Defer fit and initial prompt to ensure container has dimensions
    // Use double requestAnimationFrame to ensure terminal viewport is ready
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        try {
          // Fit addon will handle terminal readiness internally
          fitAddon.fit();
        } catch (e) {
          // Terminal might not be ready yet, try once more with timeout
          setTimeout(() => {
            try {
              fitAddon.fit();
            } catch (e2) {
              // Give up silently
            }
          }, 50);
        }

        // Write initial prompt
        writePrompt(terminal);
      });
    });

    return () => {
      window.removeEventListener('resize', handleResize);
      terminal.dispose();
      xtermRef.current = null;
      fitAddonRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Write prompt
  const writePrompt = useCallback((terminal: Terminal, currentInput = '') => {
    terminal.clear();
    terminal.write('\r\n\x1b[1;32m➜\x1b[0m \x1b[1;36muser@termai\x1b[0m:\x1b[1;34m~\x1b[0m$ ');
    if (currentInput) {
      terminal.write(currentInput);
    }
  }, []);

  // Handle terminal input
  useEffect(() => {
    const terminal = xtermRef.current;
    if (!terminal) return;

    const handleData = (data: string) => {
      // Handle Enter key
      if (data === '\r') {
        const command = inputBufferRef.current.trim();
        inputBufferRef.current = '';
        commandHistoryIndexRef.current = -1;

        if (command) {
          executeCommand(command);
        } else {
          // Empty command, just rewrite prompt
          writePrompt(terminal);
        }
        return;
      }

      // Handle Backspace
      if (data === '\u007F') {
        if (inputBufferRef.current.length > 0) {
          inputBufferRef.current = inputBufferRef.current.slice(0, -1);
          writePrompt(terminal, inputBufferRef.current);
        }
        return;
      }

      // Handle Arrow Up (previous command)
      if (data === '\u001B[A') {
        if (commandHistoryIndexRef.current < commandHistory.length - 1) {
          commandHistoryIndexRef.current++;
          const newIndex = commandHistory.length - 1 - commandHistoryIndexRef.current;
          const cmd = commandHistory[newIndex];
          inputBufferRef.current = cmd;
          writePrompt(terminal, cmd);
        }
        return;
      }

      // Handle Arrow Down (next command)
      if (data === '\u001B[B') {
        if (commandHistoryIndexRef.current > 0) {
          commandHistoryIndexRef.current--;
          const newIndex = commandHistory.length - 1 - commandHistoryIndexRef.current;
          const cmd = commandHistory[newIndex];
          inputBufferRef.current = cmd;
          writePrompt(terminal, cmd);
        } else if (commandHistoryIndexRef.current === 0) {
          commandHistoryIndexRef.current = -1;
          inputBufferRef.current = '';
          writePrompt(terminal, '');
        }
        return;
      }

      // Handle Ctrl+C
      if (data === '\u0003') {
        terminal.clear();
        inputBufferRef.current = '';
        writePrompt(terminal);
        return;
      }

      // Regular character input (printable ASCII)
      const charCode = data.charCodeAt(0);
      if (charCode >= 32 && charCode <= 126) {
        inputBufferRef.current += data;
        terminal.write(data);
      }
    };

    terminal.onData(handleData);

    return () => {
      terminal.onData(() => {});
    };
  }, [commandHistory, writePrompt]); // eslint-disable-line react-hooks/exhaustive-deps

  // Execute command
  const executeCommand = useCallback(async (command: string) => {
    if (!sessionId) {
      setError('No session active');
      return;
    }

    addToCommandHistory(command);

    const userMessage = {
      role: 'user' as const,
      content: command,
      timestamp: new Date().toISOString(),
    };
    addMessage(userMessage);
    setLoading(true);
    setError(null);

    // Clear input line
    const terminal = xtermRef.current;
    if (terminal) {
      writePrompt(terminal);
    }

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: command, session_id: sessionId }),
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
                  const { parseVizCommands } = await import('@/lib/viz-parser');
                  const vizs = parseVizCommands(assistantMessage);
                  currentVizs = vizs.map(v => v.command);

                  // Update message in real-time for streaming effect
                  addMessage({
                    role: 'assistant',
                    content: assistantMessage,
                    timestamp: new Date().toISOString(),
                    visualizations: currentVizs,
                  });
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
  }, [sessionId, addMessage, addToCommandHistory, setLoading, setError, writePrompt]);

  return (
    <div className={`flex flex-col h-full bg-[#1E1E1E] ${className}`}>
      {/* Message output area with inline visualizations */}
      <div
        ref={outputContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {messages.length === 0 && (
          <div className="text-center py-8">
            <div className="text-[#5C6AC4] text-lg mb-2">Welcome to TermAI Explorer</div>
            <div className="text-[#858585] text-sm">
              Type a message and press Enter to start
            </div>
          </div>
        )}
        <TerminalOutput messages={messages} />
        {isLoading && (
          <div className="text-[#5C6AC4] animate-pulse">Thinking...</div>
        )}
        {error && (
          <div className="text-[#F48771] bg-[#F48771]/10 border border-[#F48771] rounded p-3">
            Error: {error}
          </div>
        )}
      </div>

      {/* Terminal input area */}
      <div className="border-t border-[#333333] bg-[#1E1E1E]">
        <div ref={terminalRef} className="w-full" style={{ minHeight: '80px', height: '80px' }} />
      </div>
    </div>
  );
}
