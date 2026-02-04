import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir, readFile } from 'fs/promises';
import { join } from 'path';
import { Message } from '@/types';
import { config } from 'dotenv';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');
const CONVERSATIONS_DIR = join(FILEDB_BASE, 'webapp', 'conversations');

async function ensureDir(dir: string) {
  try {
    await access(dir);
  } catch {
    await mkdir(dir, { recursive: true });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { session_id, message } = await request.json();

    if (!session_id || !message) {
      return NextResponse.json(
        { error: 'Session ID and message required' },
        { status: 400 }
      );
    }

    const sessionDir = join(CONVERSATIONS_DIR, session_id);
    await ensureDir(sessionDir);

    const timestamp = Date.now();
    const filename = `${timestamp}.json`;
    const filepath = join(sessionDir, filename);

    const conversationEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      message,
    };

    await writeFile(filepath, JSON.stringify(conversationEntry, null, 2));

    return NextResponse.json({ success: true, id: conversationEntry.id });
  } catch (error) {
    console.error('Failed to store conversation:', error);
    return NextResponse.json(
      { error: 'Failed to store conversation' },
      { status: 500 }
    );
  }
}
