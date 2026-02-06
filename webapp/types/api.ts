// Additional type definitions for API routes

export interface PortfolioData {
  cash: number;
  portfolios: Record<string, Portfolio>;
}

export interface Portfolio {
  name: string;
  summary?: {
    holdings_value?: number;
    total_gain_loss?: number;
    total_gain_loss_pct?: number;
  };
  holdings?: Holding[];
}

export interface Holding {
  ticker: string;
  shares: number;
  avg_cost: number;
  current_price?: number;
  market_value?: number;
  gain_loss?: number;
  gain_loss_pct?: number;
}

export interface WatchlistEntry {
  ticker: string;
  strategy?: string;
  notes?: string;
  target_entry?: number;
  target_exit?: number;
  stop_loss?: number;
  status?: string;
  tags?: string[];
}

export interface WatchlistData {
  entries: WatchlistEntry[];
  total_count: number;
}

export interface Trade {
  timestamp: string;
  portfolio: string;
  ticker: string;
  action: 'BUY' | 'SELL' | 'TRIM';
  shares: number;
  price: number;
  total_value: number;
  notes?: string;
}

export interface AnalyticsData {
  ticker: string;
  technical?: string | null;
  fundamental?: string | null;
  thesis?: string | null;
}

export interface NewsArticle {
  date: string;
  title: string;
  source: string;
  url: string;
}

export interface NewsData {
  ticker: string;
  articles: NewsArticle[];
}

export interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
}

export interface RAGResult {
  text: string;
  metadata: Record<string, any>;
  score: number;
  collection: string;
}
