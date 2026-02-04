'use client';

import { useEffect, useLayoutEffect, useRef, useCallback, useState } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import { useTerminalStore } from '@/store/useTerminalStore';
import { getXtermTheme, defaultTheme } from '@/utils/themes';
import { parseVizCommands, splitTextByVizs, replaceVizsWithErrors } from '@/utils/viz-parser';
import { VizCommand } from '@/types/visualizations';
import 'xterm/css/xterm.css';

interface XtermTerminalProps {
  className?: string;
  onVisualization?: (viz: VizCommand) => void;
}

export default function XtermTerminal({ className = '', onVisualization }: XtermTerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const inputBufferRef = useRef('');
  const commandHistoryIndexRef = useRef(-1);
  const [shouldMount, setShouldMount] = useState(false);

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

  // Delay mounting to ensure container has dimensions
  useEffect(() => {
    const timer = setTimeout(() => {
      setShouldMount(true);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Initialize xterm.js
  useLayoutEffect(() => {
    if (!terminalRef.current || xtermRef.current || !shouldMount) return;

    const terminal = new Terminal({
      theme: getXtermTheme(defaultTheme),
      fontFamily: "'Fira Code', 'Source Code Pro', monospace",
      fontSize: 14,
      lineHeight: 1.2,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 1000,
      tabStopWidth: 4,
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
      // Use requestAnimationFrame to ensure DOM is ready
      requestAnimationFrame(() => {
        try {
          fitAddon.fit();
        } catch (e) {
          // Silently fail if terminal not ready
        }
      });
    };

    window.addEventListener('resize', handleResize);

    // Defer initial fit and welcome message until terminal is ready
    requestAnimationFrame(() => {
      try {
        fitAddon.fit();
      } catch (e) {
        // Terminal might not be ready yet
      }

      // Write initial welcome message
      const welcome = [
        '\r\n\x1b[1;34mWelcome to TermAI Explorer\x1b[0m',
        '\x1b[90mModern terminal interface powered by xterm.js\x1b[0m',
        '\r\nType your message and press Enter to start.\r\n',
      ];
      terminal.writeln(welcome.join('\r\n'));
      writePrompt(terminal);
    });

    return () => {
      window.removeEventListener('resize', handleResize);
      terminal.dispose();
      xtermRef.current = null;
      fitAddonRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Write prompt
  const writePrompt = useCallback((terminal: Terminal) => {
    const prompt = '\r\n\x1b[1;32m➜\x1b[0m \x1b[1;36muser@termai\x1b[0m:\x1b[1;34m~\x1b[0m$ ';
    terminal.write(prompt);
  }, []);

  // Handle terminal input
  useEffect(() => {
    const terminal = xtermRef.current;
    if (!terminal) return;

    const handleData = (data: string) => {
      const charCode = data.charCodeAt(0);

      // Handle Enter key
      if (data === '\r') {
        terminal.writeln('');
        const command = inputBufferRef.current.trim();

        if (command) {
          // Execute command
          executeCommand(command);
        } else {
          // Empty command, just show prompt
          writePrompt(terminal);
        }

        inputBufferRef.current = '';
        commandHistoryIndexRef.current = -1;
        return;
      }

      // Handle Backspace
      if (data === '\u007F') {
        if (inputBufferRef.current.length > 0) {
          inputBufferRef.current = inputBufferRef.current.slice(0, -1);
          terminal.write('\b \b');
        }
        return;
      }

      // Handle Arrow Up (previous command)
      if (data === '\u001B[A') {
        if (commandHistoryIndexRef.current < commandHistory.length - 1) {
          // Clear current line
          const promptLen = inputBufferRef.current.length;
          terminal.write('\r\x1b[K'); // Clear line
          writePrompt(terminal);

          // Move to next command
          commandHistoryIndexRef.current++;
          const newIndex = commandHistory.length - 1 - commandHistoryIndexRef.current;
          const cmd = commandHistory[newIndex];

          inputBufferRef.current = cmd;
          terminal.write(cmd);
        }
        return;
      }

      // Handle Arrow Down (next command)
      if (data === '\u001B[B') {
        if (commandHistoryIndexRef.current > 0) {
          // Clear current line
          terminal.write('\r\x1b[K');
          writePrompt(terminal);

          commandHistoryIndexRef.current--;
          const newIndex = commandHistory.length - 1 - commandHistoryIndexRef.current;
          const cmd = commandHistory[newIndex];

          inputBufferRef.current = cmd;
          terminal.write(cmd);
        } else if (commandHistoryIndexRef.current === 0) {
          // Back to empty input
          terminal.write('\r\x1b[K');
          writePrompt(terminal);
          commandHistoryIndexRef.current = -1;
          inputBufferRef.current = '';
        }
        return;
      }

      // Handle Ctrl+C
      if (data === '\u0003') {
        terminal.writeln('^C');
        inputBufferRef.current = '';
        writePrompt(terminal);
        return;
      }

      // Handle Tab (autocomplete placeholder)
      if (data === '\t') {
        // Future: implement autocomplete
        return;
      }

      // Regular character input (printable ASCII)
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
      xtermRef.current?.writeln('\x1b[31mError: No session active\x1b[0m');
      writePrompt(xtermRef.current!);
      return;
    }

    addToCommandHistory(command);

    // Display user command
    xtermRef.current?.writeln(`\x1b[90m${command}\x1b[0m`);

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
      const terminal = xtermRef.current;

      if (reader && terminal) {
        // Parse visualizations from stream
        const vizCommands: VizCommand[] = [];

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
                  const newText = parsed.text;
                  assistantMessage += newText;

                  // Extract visualizations
                  const { vizs, errors } = parseVizCommands(newText);

                  // If there are errors, replace them with helpful messages
                  const textWithErrors = errors.length > 0
                    ? replaceVizsWithErrors(newText, errors)
                    : newText;

                  vizs.forEach(viz => {
                    vizCommands.push(viz.command);
                    if (onVisualization) {
                      onVisualization(viz.command);
                    }
                  });

                  // Display text (replace viz markers with placeholders)
                  const parts = splitTextByVizs(textWithErrors, vizs);
                  parts.forEach(part => {
                    if (part.type === 'text') {
                      // Write text in dim color
                      terminal.write(`\x1b[90m${part.content}\x1b[0m`);
                    } else if (part.type === 'viz') {
                      // Write placeholder
                      terminal.write(`\x1b[36m[Visualization ${vizCommands.length} → panel]\x1b[0m`);
                    }
                  });
                }
              } catch (e) {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }

        // Store visualizations in message
        const finalMessage = {
          role: 'assistant' as const,
          content: assistantMessage,
          timestamp: new Date().toISOString(),
          visualizations: vizCommands,
        };
        addMessage(finalMessage);
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to send message';
      xtermRef.current?.writeln(`\x1b[31mError: ${errorMsg}\x1b[0m`);
      setError(errorMsg);
    } finally {
      setLoading(false);
      writePrompt(xtermRef.current!);
    }
  }, [sessionId, addMessage, addToCommandHistory, setLoading, setError, onVisualization, writePrompt]);

  // Display existing messages on mount
  useEffect(() => {
    const terminal = xtermRef.current;
    if (!terminal || messages.length === 0) return;

    // Clear and rewrite history
    terminal.clear();
    messages.forEach(msg => {
      if (msg.role === 'user') {
        terminal.writeln(`\x1b[90m${msg.content}\x1b[0m`);
      } else {
        // Parse and display assistant message
        const { vizs, errors } = parseVizCommands(msg.content);
        const contentWithErrors = errors.length > 0
          ? replaceVizsWithErrors(msg.content, errors)
          : msg.content;
        const parts = splitTextByVizs(contentWithErrors, vizs);
        parts.forEach(part => {
          if (part.type === 'text') {
            terminal.write(`\x1b[90m${part.content}\x1b[0m`);
          } else if (part.type === 'viz') {
            terminal.write(`\x1b[36m[Visualization → panel]\x1b[0m`);
          }
        });
        terminal.writeln('');
      }
    });

    writePrompt(terminal);
  }, [messages.length, writePrompt]); // eslint-disable-line react-hooks/exhaustive-deps

  // Display loading state
  useEffect(() => {
    const terminal = xtermRef.current;
    if (!terminal) return;

    if (isLoading) {
      // Show loading indicator
    }
  }, [isLoading]);

  // Display errors
  useEffect(() => {
    const terminal = xtermRef.current;
    if (!terminal || !error) return;

    terminal.writeln(`\x1b[31mError: ${error}\x1b[0m`);
  }, [error]);

  return (
    <div
      ref={terminalRef}
      className={`bg-[#1E1E1E] ${className}`}
      style={{ height: '100%', width: '100%' }}
    />
  );
}
