import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');
const PORTFOLIO_PATH = join(FILEDB_BASE, 'portfolios.json');

interface PortfolioData {
  cash?: {
    amount: number;
    target_buffer_pct: number;
  };
  portfolios: Record<string, {
    name: string;
    description?: string;
    config?: Record<string, any>;
    holdings: Array<{
      ticker: string;
      shares: number;
      avg_cost: number;
      current_price?: number;
      status?: string;
      market_value?: number;
      gain_loss?: number;
      gain_loss_pct?: number;
      pct_portfolio?: number;
    }>;
    summary?: {
      holdings_value: number;
      total_cost_basis: number;
      total_gain_loss: number;
      total_gain_loss_pct: number;
      holdings_count: number;
    };
    metadata?: {
      last_updated: string;
    };
  }>;
  metadata?: {
    base_currency: string;
    default_portfolio: string;
    last_updated: string;
    version: string;
    notes: string;
  };
}

// GET /api/portfolio - Fetch all portfolios
export async function GET(request: NextRequest) {
  try {
    if (!existsSync(PORTFOLIO_PATH)) {
      return NextResponse.json({ error: 'Portfolio file not found' }, { status: 404 });
    }

    const data: PortfolioData = JSON.parse(await readFile(PORTFOLIO_PATH, 'utf-8'));
    return NextResponse.json(data);
  } catch (error) {
    console.error('Failed to read portfolio:', error);
    return NextResponse.json({ error: 'Failed to read portfolio' }, { status: 500 });
  }
}
