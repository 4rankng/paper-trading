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
  portfolios: Record<string, {
    name: string;
    positions: Array<{
      symbol: string;
      shares: number;
      avg_cost: number;
    }>;
    cash: number;
  }>;
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

    const context: string[] = [];
    const queryLower = query.toLowerCase();

    // Check for portfolio-related queries
    if (queryLower.match(/\b(portfolio|holdings|positions|my portfolio|show portfolio)\b/)) {
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
        if (portfolioEntries.length > 0) {
          const [name, portfolio] = portfolioEntries[0];
          const holdings = portfolio.positions.map(pos =>
            `- ${pos.symbol}: ${pos.shares} shares @ $${pos.avg_cost.toFixed(2)}`
          ).join('\n');

          context.push(`PORTFOLIO DATA (${name}):\n${holdings}\nCash: $${portfolio.cash.toFixed(2)}`);
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

    return NextResponse.json({
      context: context.join('\n\n---\n\n'),
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
