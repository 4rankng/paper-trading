import { NextRequest, NextResponse } from 'next/server';
import { readdir, readFile, access } from 'fs/promises';
import { join } from 'path';
import { constants } from 'fs';
import { config } from 'dotenv';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

// Default to relative path from webapp to parent filedb directory
const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');
const CONVERSATIONS_DIR = join(FILEDB_BASE, 'webapp', 'conversations');

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const sessionId = searchParams.get('session_id');
  const limit = parseInt(searchParams.get('limit') || '10', 10);

  if (!sessionId) {
    return NextResponse.json(
      { error: 'Session ID required' },
      { status: 400 }
    );
  }

  try {
    const sessionDir = join(CONVERSATIONS_DIR, sessionId);

    // Check if session directory exists
    try {
      await access(sessionDir, constants.F_OK);
    } catch {
      // Directory doesn't exist yet (new session)
      return NextResponse.json({
        messages: [],
        count: 0,
      });
    }

    const files = await readdir(sessionDir);

    // Filter JSON files and sort by timestamp (filename is timestamp)
    const jsonFiles = files
      .filter(f => f.endsWith('.json'))
      .sort((a, b) => {
        const aTime = parseInt(a.replace('.json', ''), 10);
        const bTime = parseInt(b.replace('.json', ''), 10);
        return bTime - aTime; // Most recent first
      })
      .slice(0, limit);

    const messages = [];

    for (const file of jsonFiles) {
      const filepath = join(sessionDir, file);
      const content = JSON.parse(await readFile(filepath, 'utf-8'));
      messages.push({
        role: content.message.role,
        content: content.message.content,
        timestamp: content.timestamp,
      });
    }

    return NextResponse.json({
      messages,
      count: messages.length,
    });
  } catch (error) {
    console.error('Failed to fetch recent messages:', error);
    return NextResponse.json(
      { error: 'Failed to fetch recent messages', messages: [], count: 0 },
      { status: 500 }
    );
  }
}
