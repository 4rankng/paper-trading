import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');

// GET /api/prices/[ticker] - Fetch price data for a ticker
export async function GET(
  request: NextRequest,
  { params }: { params: { ticker: string } }
) {
  try {
    const { ticker } = params;
    const tickerUpper = ticker.toUpperCase();
    const { searchParams } = new URL(request.url);

    const limit = parseInt(searchParams.get('limit') || '365'); // Default 1 year
    const startDate = searchParams.get('start_date');

    const pricePath = join(FILEDB_BASE, 'prices', `${tickerUpper}.csv`);

    if (!existsSync(pricePath)) {
      return NextResponse.json({ ticker: tickerUpper, prices: [] }, { status: 404 });
    }

    const csvContent = await readFile(pricePath, 'utf-8');
    const lines = csvContent.split('\n').filter(line => line.trim());

    if (lines.length <= 1) {
      return NextResponse.json({ ticker: tickerUpper, prices: [] });
    }

    const prices: any[] = [];

    // Parse CSV (skip header)
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      if (values.length < 7) continue;

      const date = values[0];
      if (startDate && date < startDate) continue;

      prices.push({
        date,
        open: parseFloat(values[1]),
        high: parseFloat(values[2]),
        low: parseFloat(values[3]),
        close: parseFloat(values[4]),
        volume: parseInt(values[5]),
        adjusted_close: parseFloat(values[6]),
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
  { params }: { params: { ticker: string } }
) {
  try {
    const { ticker } = params;
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
