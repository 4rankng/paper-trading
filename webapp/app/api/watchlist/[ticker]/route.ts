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
  status?: string;
}

interface WatchlistData {
  entries: WatchlistEntry[];
  metadata?: {
    last_updated: string;
    total_count: number;
  };
}

// PUT /api/watchlist/[ticker] - Update watchlist entry
export async function PUT(
  request: NextRequest,
  { params }: { params: { ticker: string } }
) {
  try {
    const { ticker } = params;
    const body = await request.json();
    const tickerUpper = ticker.toUpperCase();

    if (!existsSync(WATCHLIST_PATH)) {
      return NextResponse.json({ error: 'Watchlist not found' }, { status: 404 });
    }

    const raw = await readFile(WATCHLIST_PATH, 'utf-8');
    const parsed = JSON.parse(raw);

    // Handle legacy array format or new object format
    let entries = Array.isArray(parsed) ? parsed : (parsed?.entries || []);
    const entryIndex = entries.findIndex((e: any) => e.ticker === tickerUpper);

    if (entryIndex === -1) {
      return NextResponse.json({ error: 'Ticker not in watchlist' }, { status: 404 });
    }

    const entry = entries[entryIndex];

    // Update allowed fields
    if (body.notes !== undefined) entry.notes = body.notes;
    if (body.tags !== undefined) entry.tags = body.tags;
    if (body.strategy !== undefined) entry.strategy = body.strategy;
    if (typeof body.target_entry === 'number') entry.target_entry = body.target_entry;
    if (typeof body.target_exit === 'number') entry.target_exit = body.target_exit;
    if (typeof body.stop_loss === 'number') entry.stop_loss = body.stop_loss;
    if (body.status !== undefined) entry.status = body.status;

    // Write in new format
    const data: WatchlistData = {
      entries,
      metadata: {
        last_updated: new Date().toISOString(),
        total_count: entries.length,
      }
    };

    await writeFile(WATCHLIST_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, entry });
  } catch (error) {
    console.error('Failed to update watchlist entry:', error);
    return NextResponse.json({ error: 'Failed to update watchlist entry' }, { status: 500 });
  }
}

// DELETE /api/watchlist/[ticker] - Remove from watchlist
export async function DELETE(
  request: NextRequest,
  { params }: { params: { ticker: string } }
) {
  try {
    const { ticker } = params;
    const tickerUpper = ticker.toUpperCase();

    if (!existsSync(WATCHLIST_PATH)) {
      return NextResponse.json({ error: 'Watchlist not found' }, { status: 404 });
    }

    const raw = await readFile(WATCHLIST_PATH, 'utf-8');
    const parsed = JSON.parse(raw);

    // Handle legacy array format or new object format
    let entries = Array.isArray(parsed) ? parsed : (parsed?.entries || []);
    const entryIndex = entries.findIndex((e: any) => e.ticker === tickerUpper);

    if (entryIndex === -1) {
      return NextResponse.json({ error: 'Ticker not in watchlist' }, { status: 404 });
    }

    entries.splice(entryIndex, 1);

    // Write in new format
    const data: WatchlistData = {
      entries,
      metadata: {
        last_updated: new Date().toISOString(),
        total_count: entries.length,
      }
    };

    await writeFile(WATCHLIST_PATH, JSON.stringify(data, null, 2));

    return NextResponse.json({ success: true, message: `Removed ${tickerUpper} from watchlist` });
  } catch (error) {
    console.error('Failed to delete watchlist entry:', error);
    return NextResponse.json({ error: 'Failed to delete watchlist entry' }, { status: 500 });
  }
}
