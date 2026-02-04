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

// POST /api/portfolio/[id]/holdings - Add new holding
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();

    // Validate required fields
    if (!body.ticker || typeof body.shares !== 'number' || typeof body.avg_cost !== 'number') {
      return NextResponse.json(
        { error: 'ticker, shares, and avg_cost are required' },
        { status: 400 }
      );
    }

    if (!existsSync(PORTFOLIO_PATH)) {
      return NextResponse.json({ error: 'Portfolio file not found' }, { status: 404 });
    }

    const data: PortfolioData = JSON.parse(await readFile(PORTFOLIO_PATH, 'utf-8'));

    if (!data.portfolios[id]) {
      return NextResponse.json({ error: 'Portfolio not found' }, { status: 404 });
    }

    // Check if ticker already exists
    const existingHolding = data.portfolios[id].holdings.find(
      (h: any) => h.ticker.toUpperCase() === body.ticker.toUpperCase()
    );

    if (existingHolding) {
      return NextResponse.json(
        { error: `Holding ${body.ticker} already exists. Use PUT to update.` },
        { status: 409 }
      );
    }

    // Add new holding
    const newHolding = {
      ticker: body.ticker.toUpperCase(),
      shares: body.shares,
      avg_cost: body.avg_cost,
      current_price: body.current_price,
      status: body.status || 'active',
    };

    data.portfolios[id].holdings.push(newHolding);

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

    return NextResponse.json({ success: true, holding: newHolding });
  } catch (error) {
    console.error('Failed to add holding:', error);
    return NextResponse.json({ error: 'Failed to add holding' }, { status: 500 });
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

    // Update holding level calculations
    h.market_value = marketValue;
    h.gain_loss = marketValue - cost;
    h.gain_loss_pct = cost > 0 ? ((marketValue - cost) / cost) * 100 : 0;
    h.pct_portfolio = 0; // Will be calculated after total is known
  });

  const totalGainLoss = holdingsValue - costBasis;
  const totalGainLossPct = costBasis > 0 ? (totalGainLoss / costBasis) * 100 : 0;

  // Update percentages
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
