import { NextRequest, NextResponse } from 'next/server';
import { readFile, access } from 'fs/promises';
import { join } from 'path';
import { constants } from 'fs';
import { config } from 'dotenv';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

// Default to relative path from webapp to parent filedb directory
const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');

interface PortfolioData {
  cash?: {
    amount: number;
    target_buffer_pct: number;
  };
  portfolios: Record<string, {
    name: string;
    description?: string;
    holdings: Array<{
      ticker: string;
      shares: number;
      avg_cost: number;
      current_price?: number;
      status?: string;
    }>;
    summary?: {
      holdings_value: number;
      total_cost_basis: number;
      total_gain_loss: number;
      total_gain_loss_pct: number;
      holdings_count: number;
    };
  }>;
  metadata?: {
    default_portfolio: string;
  };
}

interface PriceData {
  [key: string]: string | number;
}

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query) {
      return NextResponse.json(
        { error: 'Query required' },
        { status: 400 }
      );
    }

    console.log('[Data API] Received query:', query);

    const context: string[] = [];
    const queryLower = query.toLowerCase();

    // Check for portfolio-related queries
    if (queryLower.match(/\b(portfolio|holdings|positions|my portfolio|show portfolio)\b/)) {
      console.log('[Data API] Portfolio query detected');
      try {
        const portfolioPath = join(FILEDB_BASE, 'portfolios.json');
        console.log('[Data API] Looking for portfolio at:', portfolioPath);
        await access(portfolioPath, constants.F_OK);

        const portfolioData: PortfolioData = JSON.parse(
          await readFile(portfolioPath, 'utf-8')
        );
        console.log('[Data API] Found portfolio with', Object.keys(portfolioData.portfolios).length, 'portfolios');

        // Format portfolio data for LLM
        const portfolioEntries = Object.entries(portfolioData.portfolios);

        // Get default portfolio or first one
        const defaultPortfolioId = portfolioData.metadata?.default_portfolio;
        const portfolioId = defaultPortfolioId || portfolioEntries[0]?.[0];
        const portfolio = portfolioId ? portfolioData.portfolios[portfolioId] : null;

        if (portfolio && portfolio.holdings) {
          const holdings = portfolio.holdings.map(holding => {
            const pl = holding.current_price
              ? ((holding.current_price - holding.avg_cost) * holding.shares).toFixed(2)
              : 'N/A';
            const plPct = holding.current_price
              ? (((holding.current_price - holding.avg_cost) / holding.avg_cost) * 100).toFixed(2)
              : 'N/A';
            return `- ${holding.ticker}: ${holding.shares} shares @ $${holding.avg_cost.toFixed(2)}` +
              (holding.current_price ? ` | Current: $${holding.current_price.toFixed(2)} | P/L: $${pl} (${plPct}%)` : '');
          }).join('\n');

          const cash = portfolioData.cash?.amount || 0;
          const summary = portfolio.summary;

          let portfolioText = `PORTFOLIO: ${portfolio.name} (${portfolioId})\n`;
          portfolioText += `${holdings}\n\n`;
          portfolioText += `Cash: $${cash.toFixed(2)}`;

          if (summary) {
            portfolioText += `\nTotal Holdings Value: $${summary.holdings_value.toFixed(2)}`;
            portfolioText += `\nTotal P/L: $${summary.total_gain_loss.toFixed(2)} (${summary.total_gain_loss_pct.toFixed(2)}%)`;
          }

          context.push(portfolioText);
        } else {
          context.push('No portfolio holdings found');
        }
      } catch (error) {
        context.push('No portfolio data found in filedb/portfolios.json');
      }
    }

    // Check for ticker symbols to fetch price data
    const tickerRegex = /\b([A-Z]{2,5})\b/g;
    const tickers = Array.from(new Set(query.match(tickerRegex) || []));

    if (tickers.length > 0) {
      for (const ticker of tickers.slice(0, 5) as string[]) { // Limit to 5 tickers
        try {
          const pricePath = join(FILEDB_BASE, 'prices', `${ticker}.csv`);
          await access(pricePath, constants.F_OK);

          const csvContent = await readFile(pricePath, 'utf-8');
          const lines = csvContent.split('\n').filter(line => line.trim());

          if (lines.length > 1) {
            // Get the most recent price data (last line)
            const latestLine = lines[lines.length - 1].split(',');
            const [
              , date, open, high, low, close, , adjustedClose
            ] = latestLine;

            context.push(
              `${ticker} PRICE DATA (as of ${date}):\n` +
              `- Open: $${parseFloat(open).toFixed(2)}\n` +
              `- High: $${parseFloat(high).toFixed(2)}\n` +
              `- Low: $${parseFloat(low).toFixed(2)}\n` +
              `- Close: $${parseFloat(close).toFixed(2)}\n` +
              `- Adjusted Close: $${parseFloat(adjustedClose).toFixed(2)}`
            );
          }
        } catch (error) {
          // Price file not found for this ticker, skip silently
        }
      }
    }

    // Check for analytics data
    if (tickers.length > 0) {
      for (const ticker of tickers.slice(0, 3) as string[]) { // Limit to 3 tickers for analytics
        try {
          const analyticsDir = join(FILEDB_BASE, 'analytics', ticker);
          await access(analyticsDir, constants.F_OK);

          const technicalPath = join(analyticsDir, 'technical.md');
          const fundamentalPath = join(analyticsDir, 'fundamental.md');
          const thesisPath = join(analyticsDir, 'thesis.md');

          const analyses: string[] = [];

          try {
            const technical = await readFile(technicalPath, 'utf-8');
            analyses.push(`TECHNICAL ANALYSIS for ${ticker}:\n${technical.substring(0, 500)}...`);
          } catch {}

          try {
            const fundamental = await readFile(fundamentalPath, 'utf-8');
            analyses.push(`FUNDAMENTAL ANALYSIS for ${ticker}:\n${fundamental.substring(0, 500)}...`);
          } catch {}

          try {
            const thesis = await readFile(thesisPath, 'utf-8');
            analyses.push(`THESIS for ${ticker}:\n${thesis.substring(0, 500)}...`);
          } catch {}

          if (analyses.length > 0) {
            context.push(analyses.join('\n\n'));
          }
        } catch (error) {
          // Analytics not found for this ticker, skip silently
        }
      }
    }

    const result = context.join('\n\n---\n\n');
    console.log('[Data API] Returning context length:', result.length);
    console.log('[Data API] Context preview:', result.substring(0, 200));

    return NextResponse.json({
      context: result,
      sources: [],
    });
  } catch (error) {
    console.error('Failed to query data:', error);
    return NextResponse.json(
      { error: 'Failed to query data', context: '', sources: [] },
      { status: 500 }
    );
  }
}
