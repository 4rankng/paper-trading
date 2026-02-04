import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');
const WATCHLIST_PATH = join(FILEDB_BASE, 'watchlist.json');

interface WatchlistEntry {
  ticker: string;
  added_date: string;
  notes?: string;
  tags?: string[];
  strategy?: string;
  target_entry?: number;
  target_exit?: number;
  stop_loss?: number;
  status?: 'tracking' | 'entry-triggered' | 'exited';
}

interface WatchlistData {
  entries: WatchlistEntry[];
  metadata?: {
    last_updated: string;
    total_count: number;
  };
}

// GET /api/watchlist - Fetch all watchlist entries
export async function GET(request: NextRequest) {
  try {
    if (!existsSync(WATCHLIST_PATH)) {
      return NextResponse.json({ entries: [], metadata: { total_count: 0 } });
    }

    const data: WatchlistData = JSON.parse(await readFile(WATCHLIST_PATH, 'utf-8'));
    return NextResponse.json(data);
  } catch (error) {
    console.error('Failed to read watchlist:', error);
    return NextResponse.json({ error: 'Failed to read watchlist' }, { status: 500 });
  }
}

// POST /api/watchlist - Add ticker to watchlist
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (!body.ticker) {
      return NextResponse.json({ error: 'ticker is required' }, { status: 400 });
    }

    const data: WatchlistData = existsSync(WATCHLIST_PATH)
      ? JSON.parse(await readFile(WATCHLIST_PATH, 'utf-8'))
      : { entries: [] };

    const tickerUpper = body.ticker.toUpperCase();

    // Check if already exists
    if (data.entries.find((e) => e.ticker === tickerUpper)) {
      return NextResponse.json({ error: 'Ticker already in watchlist' }, { status: 409 });
    }

    const newEntry: WatchlistEntry = {
      ticker: tickerUpper,
      added_date: new Date().toISOString(),
      notes: body.notes,
      tags: body.tags,
      strategy: body.strategy,
      target_entry: body.target_entry,
      target_exit: body.target_exit,
      stop_loss: body.stop_loss,
      status: body.status || 'tracking',
    };

    data.entries.push(newEntry);
    data.metadata = {
      last_updated: new Date().toISOString(),
      total_count: data.entries.length,
    };

    await writeFile(WATCHLIST_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, entry: newEntry });
  } catch (error) {
    console.error('Failed to add to watchlist:', error);
    return NextResponse.json({ error: 'Failed to add to watchlist' }, { status: 500 });
  }
}
