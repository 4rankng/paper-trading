import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');

// GET /api/analytics/[ticker] - Fetch all analytics for a ticker
export async function GET(
  request: NextRequest,
  { params }: { params: { ticker: string } }
) {
  try {
    const { ticker } = params;
    const tickerUpper = ticker.toUpperCase();

    const analyticsDir = join(FILEDB_BASE, 'analytics', tickerUpper);

    if (!existsSync(analyticsDir)) {
      return NextResponse.json({
        ticker: tickerUpper,
        technical: null,
        fundamental: null,
        thesis: null,
      });
    }

    const types = ['technical', 'fundamental', 'thesis'];
    const analytics: Record<string, string | null> = {
      technical: null,
      fundamental: null,
      thesis: null,
    };

    for (const type of types) {
      const filePath = join(analyticsDir, `${type}.md`);
      if (existsSync(filePath)) {
        try {
          analytics[type] = await readFile(filePath, 'utf-8');
        } catch (error) {
          analytics[type] = null;
        }
      }
    }

    return NextResponse.json({ ticker: tickerUpper, ...analytics });
  } catch (error) {
    console.error('Failed to read analytics:', error);
    return NextResponse.json({ error: 'Failed to read analytics' }, { status: 500 });
  }
}

// POST /api/analytics/[ticker] - Create/update analytics for a ticker
export async function POST(
  request: NextRequest,
  { params }: { params: { ticker: string } }
) {
  try {
    const { ticker } = params;
    const tickerUpper = ticker.toUpperCase();
    const body = await request.json();

    // Validate: at least one analytics type must be provided
    if (!body.technical && !body.fundamental && !body.thesis) {
      return NextResponse.json(
        { error: 'At least one of technical, fundamental, or thesis must be provided' },
        { status: 400 }
      );
    }

    const analyticsDir = join(FILEDB_BASE, 'analytics', tickerUpper);

    // Create directory if it doesn't exist
    if (!existsSync(analyticsDir)) {
      await mkdir(analyticsDir, { recursive: true });
    }

    const updated: string[] = [];

    for (const type of ['technical', 'fundamental', 'thesis']) {
      if (body[type]) {
        const filePath = join(analyticsDir, `${type}.md`);
        await writeFile(filePath, body[type], 'utf-8');
        updated.push(type);
      }
    }

    return NextResponse.json({
      success: true,
      ticker: tickerUpper,
      updated,
    });
  } catch (error) {
    console.error('Failed to write analytics:', error);
    return NextResponse.json({ error: 'Failed to write analytics' }, { status: 500 });
  }
}
