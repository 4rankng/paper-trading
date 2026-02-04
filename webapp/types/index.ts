import { VizCommand } from './visualizations';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  visualizations?: VizCommand[];
}

export interface Session {
  id: string;
  claude_session_id?: string;
  created_at: string;
  last_active: string;
  message_count: number;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

export interface RAGQueryRequest {
  session_id: string;
  query: string;
  limit?: number;
}

export interface RAGQueryResponse {
  context: string;
  sources: {
    message_id: string;
    timestamp: string;
    relevance: number;
  }[];
}

export interface RAGStoreRequest {
  session_id: string;
  message: Message;
}

export interface TerminalState {
  sessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  commandHistory: string[];
  commandIndex: number;
}
