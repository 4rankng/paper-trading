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
  portfolios: Record<string, any>;
  metadata?: {
    default_portfolio: string;
    last_updated: string;
  };
}

// GET /api/portfolio/[id] - Fetch specific portfolio
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    if (!existsSync(PORTFOLIO_PATH)) {
      return NextResponse.json({ error: 'Portfolio file not found' }, { status: 404 });
    }

    const data: PortfolioData = JSON.parse(await readFile(PORTFOLIO_PATH, 'utf-8'));

    if (!data.portfolios[id]) {
      return NextResponse.json({ error: 'Portfolio not found' }, { status: 404 });
    }

    return NextResponse.json({
      id,
      ...data.portfolios[id],
      cash: data.cash,
    });
  } catch (error) {
    console.error('Failed to read portfolio:', error);
    return NextResponse.json({ error: 'Failed to read portfolio' }, { status: 500 });
  }
}

// PUT /api/portfolio/[id] - Update portfolio metadata
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();

    if (!existsSync(PORTFOLIO_PATH)) {
      return NextResponse.json({ error: 'Portfolio file not found' }, { status: 404 });
    }

    const data: PortfolioData = JSON.parse(await readFile(PORTFOLIO_PATH, 'utf-8'));

    if (!data.portfolios[id]) {
      return NextResponse.json({ error: 'Portfolio not found' }, { status: 404 });
    }

    // Update allowed fields
    if (body.name !== undefined) data.portfolios[id].name = body.name;
    if (body.description !== undefined) data.portfolios[id].description = body.description;
    if (body.config !== undefined) data.portfolios[id].config = body.config;

    // Update metadata timestamp
    const portfolioMetadata: any = data.portfolios[id].metadata || {};
    portfolioMetadata.last_updated = new Date().toISOString();
    data.portfolios[id].metadata = portfolioMetadata;

    const globalMetadata: any = data.metadata || {};
    globalMetadata.last_updated = new Date().toISOString();
    data.metadata = globalMetadata;

    await writeFile(PORTFOLIO_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, portfolio: data.portfolios[id] });
  } catch (error) {
    console.error('Failed to update portfolio:', error);
    return NextResponse.json({ error: 'Failed to update portfolio' }, { status: 500 });
  }
}
