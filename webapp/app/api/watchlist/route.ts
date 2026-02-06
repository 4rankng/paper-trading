import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile } from 'fs/promises';
import { join, resolve } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = resolve(process.cwd(), process.env.FILEDB_PATH || '../filedb');
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

    const raw = await readFile(WATCHLIST_PATH, 'utf-8');
    const parsed = JSON.parse(raw);

    // Handle legacy array format: convert to new format
    if (Array.isArray(parsed)) {
      return NextResponse.json({
        entries: parsed,
        metadata: { total_count: parsed.length }
      });
    }

    // Handle new object format
    return NextResponse.json(parsed);
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

    const raw = existsSync(WATCHLIST_PATH)
      ? await readFile(WATCHLIST_PATH, 'utf-8')
      : null;
    const parsed = raw ? JSON.parse(raw) : null;

    // Handle legacy array format or new object format
    let entries = Array.isArray(parsed) ? parsed : (parsed?.entries || []);

    const tickerUpper = body.ticker.toUpperCase();

    // Check if already exists
    if (entries.find((e: any) => e.ticker === tickerUpper)) {
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

    entries.push(newEntry);

    // Write in new format
    const data: WatchlistData = {
      entries,
      metadata: {
        last_updated: new Date().toISOString(),
        total_count: entries.length,
      }
    };

    await writeFile(WATCHLIST_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, entry: newEntry });
  } catch (error) {
    console.error('Failed to add to watchlist:', error);
    return NextResponse.json({ error: 'Failed to add to watchlist' }, { status: 500 });
  }
}
