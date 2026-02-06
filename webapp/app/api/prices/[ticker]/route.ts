import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');

// Days threshold for considering price data stale
const STALE_THRESHOLD_DAYS = 1;

/**
 * Check if price data is stale and fetch fresh data if needed.
 * Returns true if a fetch was triggered.
 */
async function ensureFreshPrices(ticker: string): Promise<boolean> {
  const pricePath = join(FILEDB_BASE, 'prices', `${ticker}.csv`);

  if (!existsSync(pricePath)) {
    return false;
  }

  try {
    // Read last line of CSV to get most recent date
    const content = await readFile(pricePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());

    if (lines.length <= 1) {
      return false;
    }

    // Parse last data row (skip header)
    const lastLine = lines[lines.length - 1];
    const values = lastLine.split(',');
    const lastDateStr = values[0];

    if (!lastDateStr) {
      return false;
    }

    const lastDate = new Date(lastDateStr);
    const today = new Date();
    const diffTime = today.getTime() - lastDate.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays > STALE_THRESHOLD_DAYS) {
      console.log(`[Prices] ${ticker} data is ${diffDays} days old. Fetching fresh data...`);

      // Trigger price fetch using the Python script
      const scriptPath = join(process.cwd(), '../.claude/skills/analytics_generator/scripts/fetch_prices.py');
      try {
        await execAsync(`python3 "${scriptPath}" --ticker ${ticker}`, {
          timeout: 30000, // 30 second timeout
        });
        console.log(`[Prices] Successfully fetched fresh data for ${ticker}`);
        return true;
      } catch (fetchError: any) {
        console.error(`[Prices] Failed to fetch fresh data for ${ticker}:`, fetchError.message);
        // Continue with stale data rather than failing
        return false;
      }
    }

    return false;
  } catch (error) {
    console.error('[Prices] Error checking staleness:', error);
    return false;
  }
}

// GET /api/prices/[ticker] - Fetch price data for a ticker
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const tickerUpper = ticker.toUpperCase();
    const { searchParams } = new URL(request.url);

    const limit = parseInt(searchParams.get('limit') || '365'); // Default 1 year
    const startDate = searchParams.get('start_date');
    const skipRefresh = searchParams.get('skip_refresh') === 'true';

    const pricePath = join(FILEDB_BASE, 'prices', `${tickerUpper}.csv`);

    if (!existsSync(pricePath)) {
      return NextResponse.json({ ticker: tickerUpper, prices: [] }, { status: 404 });
    }

    // Auto-fetch fresh data if stale (unless explicitly skipped)
    if (!skipRefresh) {
      await ensureFreshPrices(tickerUpper);
    }

    const csvContent = await readFile(pricePath, 'utf-8');
    const lines = csvContent.split('\n').filter(line => line.trim());

    if (lines.length <= 1) {
      return NextResponse.json({ ticker: tickerUpper, prices: [] });
    }

    const prices: any[] = [];

    // Parse CSV (skip header)
    // Handle both formats: with/without Dividends/Stock Splits columns
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      if (values.length < 6) continue; // Minimum: date, OHLCV

      const date = values[0];
      if (startDate && date < startDate) continue;

      // CSV format: date,Open,High,Low,Close,Volume,Dividends,Stock Splits
      // We map: adjusted_close = close (since no actual adj close in new format)
      prices.push({
        date,
        open: parseFloat(values[1]),
        high: parseFloat(values[2]),
        low: parseFloat(values[3]),
        close: parseFloat(values[4]),
        volume: parseInt(values[5]),
        adjusted_close: parseFloat(values[4]), // Use close as adj_close
      });
    }

    // Sort by date descending and limit
    prices.sort((a, b) => b.date.localeCompare(a.date));

    return NextResponse.json({
      ticker: tickerUpper,
      prices: prices.slice(0, limit),
      total: prices.length,
    });
  } catch (error) {
    console.error('Failed to read prices:', error);
    return NextResponse.json({ error: 'Failed to read prices' }, { status: 500 });
  }
}

// POST /api/prices/[ticker] - Update price data for a ticker
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const tickerUpper = ticker.toUpperCase();
    const body = await request.json();

    if (!body.prices || !Array.isArray(body.prices)) {
      return NextResponse.json(
        { error: 'prices array is required' },
        { status: 400 }
      );
    }

    const pricesDir = join(FILEDB_BASE, 'prices');
    if (!existsSync(pricesDir)) {
      await mkdir(pricesDir, { recursive: true });
    }

    const pricePath = join(pricesDir, `${tickerUpper}.csv`);

    // Build CSV content
    let csv = 'Date,Open,High,Low,Close,Volume,Adj Close\n';

    for (const price of body.prices) {
      csv += [
        price.date,
        price.open,
        price.high,
        price.low,
        price.close,
        price.volume,
        price.adjusted_close || price.adjClose || price.close,
      ].join(',') + '\n';
    }

    await writeFile(pricePath, csv, 'utf-8');

    return NextResponse.json({
      success: true,
      ticker: tickerUpper,
      records: body.prices.length,
    });
  } catch (error) {
    console.error('Failed to save prices:', error);
    return NextResponse.json({ error: 'Failed to save prices' }, { status: 500 });
  }
}
