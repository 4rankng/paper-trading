import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile, mkdir, unlink } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');

const VALID_TYPES = ['technical', 'fundamental', 'thesis'];

// GET /api/analytics/[ticker]/[type] - Fetch specific analytics type
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string; type: string }> }
) {
  try {
    const { ticker, type } = await params;
    const tickerUpper = ticker.toUpperCase();

    if (!VALID_TYPES.includes(type)) {
      return NextResponse.json(
        { error: `Invalid type. Must be one of: ${VALID_TYPES.join(', ')}` },
        { status: 400 }
      );
    }

    const filePath = join(FILEDB_BASE, 'analytics', tickerUpper, `${type}.md`);

    if (!existsSync(filePath)) {
      return NextResponse.json({ ticker: tickerUpper, type, content: null }, { status: 404 });
    }

    const content = await readFile(filePath, 'utf-8');
    return NextResponse.json({ ticker: tickerUpper, type, content });
  } catch (error) {
    console.error('Failed to read analytics:', error);
    return NextResponse.json({ error: 'Failed to read analytics' }, { status: 500 });
  }
}

// PUT /api/analytics/[ticker]/[type] - Update specific analytics type
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string; type: string }> }
) {
  try {
    const { ticker, type } = await params;
    const tickerUpper = ticker.toUpperCase();
    const body = await request.json();

    if (!VALID_TYPES.includes(type)) {
      return NextResponse.json(
        { error: `Invalid type. Must be one of: ${VALID_TYPES.join(', ')}` },
        { status: 400 }
      );
    }

    if (!body.content) {
      return NextResponse.json({ error: 'content is required' }, { status: 400 });
    }

    const analyticsDir = join(FILEDB_BASE, 'analytics', tickerUpper);

    if (!existsSync(analyticsDir)) {
      await mkdir(analyticsDir, { recursive: true });
    }

    const filePath = join(analyticsDir, `${type}.md`);
    await writeFile(filePath, body.content, 'utf-8');

    return NextResponse.json({ success: true, ticker: tickerUpper, type });
  } catch (error) {
    console.error('Failed to update analytics:', error);
    return NextResponse.json({ error: 'Failed to update analytics' }, { status: 500 });
  }
}

// DELETE /api/analytics/[ticker]/[type] - Delete specific analytics type
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string; type: string }> }
) {
  try {
    const { ticker, type } = await params;
    const tickerUpper = ticker.toUpperCase();

    if (!VALID_TYPES.includes(type)) {
      return NextResponse.json(
        { error: `Invalid type. Must be one of: ${VALID_TYPES.join(', ')}` },
        { status: 400 }
      );
    }

    const filePath = join(FILEDB_BASE, 'analytics', tickerUpper, `${type}.md`);

    if (!existsSync(filePath)) {
      return NextResponse.json({ error: 'Analytics file not found' }, { status: 404 });
    }

    await unlink(filePath);

    return NextResponse.json({ success: true, message: `Deleted ${type} for ${tickerUpper}` });
  } catch (error) {
    console.error('Failed to delete analytics:', error);
    return NextResponse.json({ error: 'Failed to delete analytics' }, { status: 500 });
  }
}
