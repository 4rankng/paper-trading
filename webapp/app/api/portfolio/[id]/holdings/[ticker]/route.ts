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

// PUT /api/portfolio/[id]/holdings/[ticker] - Update holding
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; ticker: string }> }
) {
  try {
    const { id, ticker } = await params;
    const body = await request.json();
    const tickerUpper = ticker.toUpperCase();

    if (!existsSync(PORTFOLIO_PATH)) {
      return NextResponse.json({ error: 'Portfolio file not found' }, { status: 404 });
    }

    const data: PortfolioData = JSON.parse(await readFile(PORTFOLIO_PATH, 'utf-8'));

    if (!data.portfolios[id]) {
      return NextResponse.json({ error: 'Portfolio not found' }, { status: 404 });
    }

    const holdingIndex = data.portfolios[id].holdings.findIndex(
      (h: any) => h.ticker.toUpperCase() === tickerUpper
    );

    if (holdingIndex === -1) {
      return NextResponse.json({ error: 'Holding not found' }, { status: 404 });
    }

    const holding = data.portfolios[id].holdings[holdingIndex];

    // Update allowed fields
    if (typeof body.shares === 'number') holding.shares = body.shares;
    if (typeof body.avg_cost === 'number') holding.avg_cost = body.avg_cost;
    if (typeof body.current_price === 'number') holding.current_price = body.current_price;
    if (typeof body.status === 'string') holding.status = body.status;

    // Recalculate summary
    recalculateSummary(data, id);

    // Update metadata timestamp
    const portfolioMetadata: any = data.portfolios[id].metadata || {};
    portfolioMetadata.last_updated = new Date().toISOString();
    data.portfolios[id].metadata = portfolioMetadata;

    const globalMetadata: any = data.metadata || {};
    globalMetadata.last_updated = new Date().toISOString();
    data.metadata = globalMetadata;

    await writeFile(PORTFOLIO_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, holding });
  } catch (error) {
    console.error('Failed to update holding:', error);
    return NextResponse.json({ error: 'Failed to update holding' }, { status: 500 });
  }
}

// DELETE /api/portfolio/[id]/holdings/[ticker] - Remove holding
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; ticker: string }> }
) {
  try {
    const { id, ticker } = await params;
    const tickerUpper = ticker.toUpperCase();

    if (!existsSync(PORTFOLIO_PATH)) {
      return NextResponse.json({ error: 'Portfolio file not found' }, { status: 404 });
    }

    const data: PortfolioData = JSON.parse(await readFile(PORTFOLIO_PATH, 'utf-8'));

    if (!data.portfolios[id]) {
      return NextResponse.json({ error: 'Portfolio not found' }, { status: 404 });
    }

    const holdingIndex = data.portfolios[id].holdings.findIndex(
      (h: any) => h.ticker.toUpperCase() === tickerUpper
    );

    if (holdingIndex === -1) {
      return NextResponse.json({ error: 'Holding not found' }, { status: 404 });
    }

    // Remove holding
    data.portfolios[id].holdings.splice(holdingIndex, 1);

    // Recalculate summary
    recalculateSummary(data, id);

    // Update metadata timestamp
    const portfolioMetadata: any = data.portfolios[id].metadata || {};
    portfolioMetadata.last_updated = new Date().toISOString();
    data.portfolios[id].metadata = portfolioMetadata;

    const globalMetadata: any = data.metadata || {};
    globalMetadata.last_updated = new Date().toISOString();
    data.metadata = globalMetadata;

    await writeFile(PORTFOLIO_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, message: `Removed ${tickerUpper} from ${id}` });
  } catch (error) {
    console.error('Failed to delete holding:', error);
    return NextResponse.json({ error: 'Failed to delete holding' }, { status: 500 });
  }
}

function recalculateSummary(data: PortfolioData, portfolioId: string) {
  const portfolio = data.portfolios[portfolioId];
  const holdings = portfolio.holdings || [];

  let holdingsValue = 0;
  let costBasis = 0;

  holdings.forEach((h: any) => {
    const currentPrice = h.current_price || h.avg_cost;
    const marketValue = h.shares * currentPrice;
    const cost = h.shares * h.avg_cost;

    holdingsValue += marketValue;
    costBasis += cost;

    h.market_value = marketValue;
    h.gain_loss = marketValue - cost;
    h.gain_loss_pct = cost > 0 ? ((marketValue - cost) / cost) * 100 : 0;
    h.pct_portfolio = 0;
  });

  const totalGainLoss = holdingsValue - costBasis;
  const totalGainLossPct = costBasis > 0 ? (totalGainLoss / costBasis) * 100 : 0;

  holdings.forEach((h: any) => {
    h.pct_portfolio = holdingsValue > 0 ? (h.market_value / holdingsValue) * 100 : 0;
  });

  portfolio.summary = {
    holdings_value: Math.round(holdingsValue * 100) / 100,
    total_cost_basis: Math.round(costBasis * 100) / 100,
    total_gain_loss: Math.round(totalGainLoss * 100) / 100,
    total_gain_loss_pct: Math.round(totalGainLossPct * 100) / 100,
    holdings_count: holdings.length,
  };
}
