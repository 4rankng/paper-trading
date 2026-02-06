import { useRef, useCallback } from 'react';
import { VizCommand } from '@/types/visualizations';

export interface ToolExecution {
  name: string;
  status: 'running' | 'success' | 'error';
  result?: string;
}

interface UseChatStreamingOptions {
  sessionId: string | null | undefined;
  onMessage: (content: string, vizs: VizCommand[]) => void;
  onNewMessage: (content: string) => void;
  onAssistantMessage: (content: string, vizs: VizCommand[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

interface UseChatStreamingReturn {
  executeCommand: (command: string) => Promise<void>;
  getActiveTool: () => ToolExecution | undefined;
  getValidationProgress: () => string | undefined;
  cleanup: () => void;
}

export function useChatStreaming({
  sessionId,
  onMessage,
  onNewMessage,
  onAssistantMessage,
  setLoading,
  setError,
}: UseChatStreamingOptions) {
  const toolTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const activeToolRef = useRef<ToolExecution | null>(null);
  const validationProgressRef = useRef<string | undefined>(undefined);

  const setActiveTool = useCallback((tool: ToolExecution | null) => {
    activeToolRef.current = tool;
  }, []);

  const setValidationProgress = useCallback((progress: string | null) => {
    validationProgressRef.current = progress ?? undefined;
  }, []);

  const getActiveTool = useCallback((): ToolExecution | undefined => {
    const val = activeToolRef.current;
    return val === null ? undefined : val;
  }, []);
  const getValidationProgress = useCallback((): string | undefined => validationProgressRef.current, []);

  const executeCommand = useCallback(async (command: string) => {
    if (!sessionId) {
      setError('No session active');
      return;
    }

    const trimmedCommand = command.trim();
    if (!trimmedCommand) return;

    onNewMessage(trimmedCommand);
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmedCommand, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let assistantMessage = '';
      let currentVizs: VizCommand[] = [];
      let assistantMessageAdded = false;

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

                if (parsed.tool_start) {
                  setActiveTool({
                    name: parsed.tool_start.name,
                    status: 'running',
                  });
                  continue;
                }

                if (parsed.tool_use) {
                  setActiveTool({
                    name: parsed.tool_use.name,
                    status: parsed.tool_use.result === 'Success' ? 'success' : 'error',
                    result: parsed.tool_use.result,
                  });
                  if (toolTimeoutRef.current) clearTimeout(toolTimeoutRef.current);
                  toolTimeoutRef.current = setTimeout(() => setActiveTool(null), 2000);
                  continue;
                }

                if (parsed.validation_start) {
                  setValidationProgress(parsed.validation_start.message);
                  continue;
                }

                if (parsed.validation_progress) {
                  setValidationProgress(parsed.validation_progress.message);
                  continue;
                }

                if (parsed.validation_warning) {
                  setValidationProgress(parsed.validation_warning.message);
                  if (toolTimeoutRef.current) clearTimeout(toolTimeoutRef.current);
                  toolTimeoutRef.current = setTimeout(() => setValidationProgress(null), 3000);
                  continue;
                }

                if (parsed.text) {
                  assistantMessage += parsed.text;

                  if (validationProgressRef.current) {
                    setValidationProgress(null);
                  }

                  const { parseVizCommands } = await import('@/utils/viz-parser');
                  const { vizs } = parseVizCommands(assistantMessage);
                  currentVizs = vizs.map(v => v.command);

                  // Add assistant message on first text, then update on subsequent text
                  if (!assistantMessageAdded) {
                    onAssistantMessage(assistantMessage, currentVizs);
                    assistantMessageAdded = true;
                  } else {
                    onMessage(assistantMessage, currentVizs);
                  }
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
      setActiveTool(null);
    }
  }, [sessionId, onMessage, onNewMessage, onAssistantMessage, setLoading, setError, setActiveTool, setValidationProgress]);

  // Cleanup on unmount
  const cleanup = useCallback(() => {
    if (toolTimeoutRef.current) {
      clearTimeout(toolTimeoutRef.current);
    }
  }, []);

  const result: UseChatStreamingReturn = {
    executeCommand,
    getActiveTool,
    getValidationProgress,
    cleanup,
  };
  return result;
}
