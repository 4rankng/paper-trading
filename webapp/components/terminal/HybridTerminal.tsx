'use client';

import { useEffect, useLayoutEffect, useRef, useCallback } from 'react';
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
  const cleanupRef = useRef<(() => void) | null>(null);
  const handlerAttachedRef = useRef(false);

  const {
    sessionId,
    messages,
    isLoading,
    error,
    commandHistory,
    addMessage,
    addToCommandHistory,
    setLoading,
    setError,
  } = useTerminalStore();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (outputContainerRef.current) {
      outputContainerRef.current.scrollTop = outputContainerRef.current.scrollHeight;
    }
  }, [messages.length]);

  // Write prompt - bold, high-contrast for visual anchor
  const writePrompt = useCallback((terminal: Terminal, currentInput = '') => {
    console.log('[writePrompt] Called with input:', JSON.stringify(currentInput));
    terminal.clear();
    // Bold green arrow, bold cyan username for clear visual hierarchy
    terminal.write('\r\n\x1b[1;32m➜\x1b[0m \x1b[1;36muser@termai\x1b[0m:\x1b[1;34m~\x1b[0m$ ');
    if (currentInput) {
      terminal.write(currentInput);
    }
  }, []);

  // Execute command - accepts store state to avoid closure staleness
  const executeCommandWithStore = useCallback(async (
    command: string,
    storeState: {
      sessionId: string | null;
      addMessage: (msg: any) => void;
      addToCommandHistory: (cmd: string) => void;
      setLoading: (loading: boolean) => void;
      setError: (error: string | null) => void;
    }
  ) => {
    const { sessionId, addMessage, addToCommandHistory, setLoading, setError } = storeState;

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
      // Rewrite prompt after completion
      const terminal = xtermRef.current;
      if (terminal) {
        writePrompt(terminal);
      }
    }
  }, [writePrompt]);

  // Execute command for external calls (e.g., from data handler)
  const executeCommand = useCallback(async (command: string) => {
    const storeState = useTerminalStore.getState();
    await executeCommandWithStore(command, storeState);
  }, [executeCommandWithStore]);

  // Initialize xterm.js for input only (runs once)
  useLayoutEffect(() => {
    if (!terminalRef.current || xtermRef.current) return;

    // Delay opening terminal until container has computed dimensions
    // This prevents "Cannot read properties of undefined (reading 'dimensions')" error
    const initTimer = setTimeout(() => {
      if (!terminalRef.current || xtermRef.current) return;

      try {
        const terminal = new Terminal({
            theme: getXtermTheme(defaultTheme),
            fontFamily: "'Fira Code', 'Source Code Pro', monospace",
            fontSize: 14,
            lineHeight: 1.6,
            cursorBlink: true,
            cursorStyle: 'block',
            scrollback: 0, // No scrollback, messages render above
            rows: 3, // Just enough for input line
            letterSpacing: 1.2,
          });

          const fitAddon = new FitAddon();
          const webLinksAddon = new WebLinksAddon();

          terminal.loadAddon(fitAddon);
          terminal.loadAddon(webLinksAddon);

          // Open terminal after container has computed dimensions
          terminal.open(terminalRef.current);

          xtermRef.current = terminal;
          fitAddonRef.current = fitAddon;

        // Handle window resize
        const handleResize = () => {
          requestAnimationFrame(() => {
            try {
              fitAddonRef.current?.fit();
            } catch (e) {
              // Silently fail if terminal not ready
            }
          });
        };

        window.addEventListener('resize', handleResize);

        // Set up data handler - uses refs to always access latest values
        const handleData = (data: string) => {
          console.log('[Handler] Received data:', JSON.stringify(data), 'charCode:', data.charCodeAt(0));
          const currentCommandHistory = useTerminalStore.getState().commandHistory;

          // Handle Enter key
          if (data === '\r') {
            const command = inputBufferRef.current.trim();
            inputBufferRef.current = '';
            commandHistoryIndexRef.current = -1;

            if (command) {
              // Get latest executeCommand from store
              const { sessionId, addMessage, addToCommandHistory, setLoading, setError } = useTerminalStore.getState();

              // Execute command inline with fresh store values
              executeCommandWithStore(command, { sessionId, addMessage, addToCommandHistory, setLoading, setError });
            } else {
              // Empty command, just rewrite prompt
              writePrompt(terminal);
            }
            return;
          }

          // Handle Backspace - manually move cursor back and clear character
          if (data === '\u007F') {
            console.log('[Backspace] Buffer before:', JSON.stringify(inputBufferRef.current));
            if (inputBufferRef.current.length > 0) {
              inputBufferRef.current = inputBufferRef.current.slice(0, -1);
              // Move cursor back one position and clear character
              terminal.write('\b \b');
              console.log('[Backspace] Buffer after:', JSON.stringify(inputBufferRef.current));
            }
            return;
          }

          // Handle Arrow Up (previous command)
          if (data === '\u001B[A') {
            if (commandHistoryIndexRef.current < currentCommandHistory.length - 1) {
              commandHistoryIndexRef.current++;
              const newIndex = currentCommandHistory.length - 1 - commandHistoryIndexRef.current;
              const cmd = currentCommandHistory[newIndex];
              inputBufferRef.current = cmd;
              writePrompt(terminal, cmd);
            }
            return;
          }

          // Handle Arrow Down (next command)
          if (data === '\u001B[B') {
            if (commandHistoryIndexRef.current > 0) {
              commandHistoryIndexRef.current--;
              const newIndex = currentCommandHistory.length - 1 - commandHistoryIndexRef.current;
              const cmd = currentCommandHistory[newIndex];
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
            console.log('[Char] Adding:', data, 'Buffer before:', JSON.stringify(inputBufferRef.current));
            inputBufferRef.current += data;
            terminal.write(data);
            console.log('[Char] Buffer after:', JSON.stringify(inputBufferRef.current));
          }
        };

        // Only attach handler once (prevents React Strict Mode double attachment)
        if (!handlerAttachedRef.current) {
          console.log('[Handler] Attaching onData handler');
          terminal.onData(handleData);
          handlerAttachedRef.current = true;
        }

        // Focus terminal on initialization
        requestAnimationFrame(() => {
          try {
            fitAddon.fit();
            terminal.focus();
          } catch (e) {
            // Ignore fit errors
          }
          writePrompt(terminal);
        });

        // Store cleanup function
        cleanupRef.current = () => {
          window.removeEventListener('resize', handleResize);
          terminal.dispose();
          xtermRef.current = null;
          fitAddonRef.current = null;
          handlerAttachedRef.current = false;
        };
      } catch (error) {
        console.error('Failed to initialize xterm.js:', error);
      }
    }, 0); // Zero timeout - just push to end of event loop, enough for layout computation

    // Cleanup for the setTimeout
    return () => {
      clearTimeout(initTimer);
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [writePrompt]); // Only depend on writePrompt. executeCommandWithStore is intentionally omitted to prevent re-initialization. It's accessed via closure from the data handler which calls useTerminalStore.getState() for fresh values.

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
      <div
        className="border-t border-[#333333] bg-[#1E1E1E]"
        onClick={() => {
          xtermRef.current?.focus();
        }}
      >
        <div ref={terminalRef} className="w-full" style={{ minHeight: '80px', height: '80px' }} />
      </div>
    </div>
  );
}
