import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile, appendFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');
const TRADE_LOG_PATH = join(FILEDB_BASE, 'trade_log.csv');

interface TradeLogEntry {
  timestamp: string;
  portfolio: string;
  ticker: string;
  action: 'BUY' | 'SELL' | 'TRIM';
  shares: number;
  price: number;
  total_value: number;
  notes?: string;
}

// GET /api/trades - Fetch all trades with optional filters
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const ticker = searchParams.get('ticker')?.toUpperCase();
    const portfolio = searchParams.get('portfolio');
    const startDate = searchParams.get('start_date');
    const endDate = searchParams.get('end_date');

    if (!existsSync(TRADE_LOG_PATH)) {
      return NextResponse.json({ trades: [] });
    }

    const csvContent = await readFile(TRADE_LOG_PATH, 'utf-8');
    const lines = csvContent.split('\n').filter((line) => line.trim());

    if (lines.length === 0) {
      return NextResponse.json({ trades: [] });
    }

    // Parse CSV (header + data rows)
    const headers = lines[0].split(',');
    const trades: TradeLogEntry[] = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      if (values.length < 7) continue; // Skip malformed rows

      const trade: TradeLogEntry = {
        timestamp: values[0],
        portfolio: values[1],
        ticker: values[2],
        action: values[3] as 'BUY' | 'SELL' | 'TRIM',
        shares: parseFloat(values[4]),
        price: parseFloat(values[5]),
        total_value: parseFloat(values[6]),
        notes: values[7] || '',
      };

      // Apply filters
      if (ticker && trade.ticker !== ticker) continue;
      if (portfolio && trade.portfolio !== portfolio) continue;
      if (startDate && trade.timestamp < startDate) continue;
      if (endDate && trade.timestamp > endDate) continue;

      trades.push(trade);
    }

    // Sort by timestamp descending
    trades.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

    return NextResponse.json({ trades, count: trades.length });
  } catch (error) {
    console.error('Failed to read trade log:', error);
    return NextResponse.json({ error: 'Failed to read trade log' }, { status: 500 });
  }
}

// POST /api/trades - Append new trade to log
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate required fields
    if (
      !body.ticker ||
      !body.action ||
      typeof body.shares !== 'number' ||
      typeof body.price !== 'number'
    ) {
      return NextResponse.json(
        { error: 'ticker, action (BUY/SELL/TRIM), shares, and price are required' },
        { status: 400 }
      );
    }

    const validActions = ['BUY', 'SELL', 'TRIM'];
    if (!validActions.includes(body.action.toUpperCase())) {
      return NextResponse.json(
        { error: 'action must be BUY, SELL, or TRIM' },
        { status: 400 }
      );
    }

    // Ensure filedb directory exists
    const filedbDir = join(FILEDB_BASE);
    if (!existsSync(filedbDir)) {
      await mkdir(filedbDir, { recursive: true });
    }

    const timestamp = body.timestamp || new Date().toISOString();
    const portfolio = body.portfolio || 'CORE';
    const totalValue = body.shares * body.price;

    const csvLine = [
      timestamp,
      portfolio,
      body.ticker.toUpperCase(),
      body.action.toUpperCase(),
      body.shares.toString(),
      body.price.toFixed(2),
      totalValue.toFixed(2),
      body.notes || '',
    ].join(',');

    // Create file with header if it doesn't exist
    if (!existsSync(TRADE_LOG_PATH)) {
      await writeFile(
        TRADE_LOG_PATH,
        'timestamp,portfolio,ticker,action,shares,price,total_value,notes\n',
        'utf-8'
      );
    }

    await appendFile(TRADE_LOG_PATH, csvLine + '\n', 'utf-8');

    const trade: TradeLogEntry = {
      timestamp,
      portfolio,
      ticker: body.ticker.toUpperCase(),
      action: body.action.toUpperCase() as 'BUY' | 'SELL' | 'TRIM',
      shares: body.shares,
      price: body.price,
      total_value: totalValue,
      notes: body.notes,
    };

    return NextResponse.json({ success: true, trade });
  } catch (error) {
    console.error('Failed to log trade:', error);
    return NextResponse.json({ error: 'Failed to log trade' }, { status: 500 });
  }
}
