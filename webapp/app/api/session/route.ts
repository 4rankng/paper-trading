import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir, readFile, access } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');
const SESSIONS_DIR = join(FILEDB_BASE, 'webapp', 'sessions');

async function ensureDir(dir: string) {
  try {
    await access(dir);
  } catch {
    await mkdir(dir, { recursive: true });
  }
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const action = searchParams.get('action');

  if (action === 'create') {
    try {
      await ensureDir(SESSIONS_DIR);

      const sessionId = crypto.randomUUID();
      const session = {
        id: sessionId,
        created_at: new Date().toISOString(),
        last_active: new Date().toISOString(),
        message_count: 0,
      };

      const sessionPath = join(SESSIONS_DIR, `${sessionId}.json`);
      await writeFile(sessionPath, JSON.stringify(session, null, 2));

      return NextResponse.json({ session_id: sessionId });
    } catch (error) {
      console.error('Failed to create session:', error);
      return NextResponse.json(
        { error: 'Failed to create session' },
        { status: 500 }
      );
    }
  }

  if (action === 'validate') {
    const sessionId = searchParams.get('id');
    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID required' }, { status: 400 });
    }

    try {
      const sessionPath = join(SESSIONS_DIR, `${sessionId}.json`);
      await access(sessionPath);
      return NextResponse.json({ valid: true });
    } catch {
      return NextResponse.json({ valid: false });
    }
  }

  return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
}
