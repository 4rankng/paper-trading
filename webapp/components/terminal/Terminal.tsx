'use client';

import { useEffect, useRef } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import TerminalInput from './TerminalInput';
import TerminalOutput from './TerminalOutput';
import { Message } from '@/types';

export default function Terminal() {
  const {
    sessionId,
    messages,
    isLoading,
    error,
    commandHistory,
    commandIndex,
    addMessage,
    addRegenerateButtons,
    setLoading,
    setError,
    addToCommandHistory,
    clearMessages,
  } = useTerminalStore();

  const outputRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    outputRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleRegenerate = async (vizType: string, userMessage: string) => {
    if (!sessionId) {
      setError('No session active');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat/regenerate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vizType,
          userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to regenerate visualization');
      }

      const data = await response.json();

      const regeneratedMessage: Message = {
        role: 'assistant',
        content: data.content || `Regenerated ${vizType} visualization`,
        timestamp: new Date().toISOString(),
      };

      addMessage(regeneratedMessage);
    } catch (err) {
      console.error('Regeneration error:', err);
      setError(err instanceof Error ? err.message : 'Failed to regenerate visualization');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (command: string) => {
    if (!sessionId) {
      setError('No session active');
      return;
    }

    addToCommandHistory(command);

    const userMessage: Message = {
      role: 'user',
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
      const startTime = Date.now();
      const regenerateButtons: Array<{ vizType: string; vizIndex: number }> = [];

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

                  // Update message in real-time
                  if (Date.now() - startTime > 100) {
                    const existingMsg = messages.find(
                      (m) => m.role === 'assistant' && m.timestamp === new Date().toISOString()
                    );
                    if (existingMsg) {
                      existingMsg.content = assistantMessage;
                    }
                  }
                } else if (parsed.regenerate_button) {
                  // Store regenerate button info
                  regenerateButtons.push(parsed.regenerate_button);
                }
              } catch (e) {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }
      }

      const finalMessage: Message = {
        role: 'assistant',
        content: assistantMessage,
        timestamp: new Date().toISOString(),
        regenerateButtons: regenerateButtons.length > 0
          ? regenerateButtons.map(b => ({
              ...b,
              userMessage: command,
              originalResponse: assistantMessage,
            }))
          : undefined,
      };

      addMessage(finalMessage);
    } catch (err) {
      console.error('Chat error:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      e.preventDefault();
    }
  };

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-full font-mono bg-terminal-black p-4">
      <div className="flex-1 overflow-y-auto mb-4" ref={outputRef}>
        <TerminalOutput messages={messages} onRegenerate={handleRegenerate} />
        {isLoading && (
          <div className="text-terminal-green animate-pulse">
            Processing...
          </div>
        )}
        {error && (
          <div className="text-red-500">
            Error: {error}
          </div>
        )}
      </div>

      <div className="border-t border-terminal-green pt-4">
        <TerminalInput onSubmit={handleSubmit} isLoading={isLoading} disabled={!sessionId} />
      </div>
    </div>
  );
}
