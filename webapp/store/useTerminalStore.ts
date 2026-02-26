import { create } from 'zustand';
import { Message, TerminalState, RegenerateButton } from '@/types';
import { VizCommand } from '@/types/visualizations';
import { Storage } from '@/utils/storage';

interface TerminalStore extends TerminalState {
  // Visualization state
  visualizations: VizCommand[];

  // Theme state
  currentTheme: string;

  // Actions
  setSessionId: (id: string) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string, visualizations?: VizCommand[]) => void;
  addRegenerateButtons: (buttons: RegenerateButton[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addToCommandHistory: (command: string) => void;
  navigateCommandHistory: (direction: 'up' | 'down') => void;
  clearMessages: () => void;

  // Visualization actions
  addVisualization: (viz: VizCommand) => void;
  clearVisualizations: () => void;

  // Theme actions
  setTheme: (theme: string) => void;
}

export const useTerminalStore = create<TerminalStore>((set, get) => ({
  // Initialize sessionId from localStorage for persistence across refreshes
  sessionId: typeof window !== 'undefined' ? Storage.getSessionId() : null,
  messages: [],
  isLoading: false,
  error: null,
  commandHistory: [],
  commandIndex: -1,
  visualizations: [],
  currentTheme: 'oneDark',

  setSessionId: (id) => set({ sessionId: id }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
      // Extract visualizations from the new message
      visualizations: message.visualizations
        ? [...state.visualizations, ...message.visualizations]
        : state.visualizations,
    })),

  updateLastMessage: (content, visualizations) =>
    set((state) => {
      const messages = [...state.messages];
      const lastMessage = messages[messages.length - 1];

      // If last message is from assistant, update it (streaming)
      if (lastMessage && lastMessage.role === 'assistant') {
        messages[messages.length - 1] = {
          ...lastMessage,
          content,
          visualizations,
        };
      } else {
        // Otherwise add a new assistant message (first chunk of response)
        messages.push({
          role: 'assistant',
          content,
          timestamp: new Date().toISOString(),
          visualizations,
        });
      }

      return {
        messages,
        visualizations: visualizations || [],
      };
    }),

  addRegenerateButtons: (buttons) =>
    set((state) => {
      const messages = [...state.messages];
      const lastMessage = messages[messages.length - 1];

      if (lastMessage && lastMessage.role === 'assistant') {
        messages[messages.length - 1] = {
          ...lastMessage,
          regenerateButtons: buttons,
        };
      }

      return { messages };
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  addToCommandHistory: (command) =>
    set((state) => ({
      commandHistory: [...state.commandHistory, command],
      commandIndex: state.commandHistory.length,
    })),

  navigateCommandHistory: (direction) =>
    set((state) => {
      const { commandHistory, commandIndex } = state;
      let newIndex = commandIndex;

      if (direction === 'up' && commandIndex > 0) {
        newIndex = commandIndex - 1;
      } else if (direction === 'down' && commandIndex < commandHistory.length - 1) {
        newIndex = commandIndex + 1;
      }

      return { commandIndex: newIndex };
    }),

  clearMessages: () => set({ messages: [], visualizations: [] }),

  addVisualization: (viz) =>
    set((state) => ({
      visualizations: [...state.visualizations, viz],
    })),

  clearVisualizations: () => set({ visualizations: [] }),

  setTheme: (theme) => set({ currentTheme: theme }),
}));
