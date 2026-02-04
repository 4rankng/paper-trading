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
  const query = searchParams.get('query');
  const limit = parseInt(searchParams.get('limit') || '5', 10);

  if (!sessionId || !query) {
    return NextResponse.json(
      { error: 'Session ID and query required' },
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
        context: '',
        sources: [],
      });
    }

    const files = await readdir(sessionDir);

    const conversations = [];

    for (const file of files) {
      if (file.endsWith('.json')) {
        const filepath = join(sessionDir, file);
        const content = JSON.parse(await readFile(filepath, 'utf-8'));

        // Simple keyword matching for MVP
        const messageText = content.message.content.toLowerCase();
        const queryText = query.toLowerCase();
        const keywords = queryText.split(/\s+/);

        let relevance = 0;
        keywords.forEach((keyword) => {
          if (keyword.length > 2 && messageText.includes(keyword)) {
            relevance += 1;
          }
        });

        if (relevance > 0) {
          conversations.push({
            ...content,
            relevance,
          });
        }
      }
    }

    // Sort by relevance and limit
    conversations.sort((a, b) => b.relevance - a.relevance);
    const topConversations = conversations.slice(0, limit);

    // Build context string
    const context = topConversations
      .map((conv) => {
        const role = conv.message.role === 'user' ? 'User' : 'Assistant';
        return `${role}: ${conv.message.content}`;
      })
      .join('\n\n');

    const sources = topConversations.map((conv) => ({
      message_id: conv.id,
      timestamp: conv.timestamp,
      relevance: conv.relevance,
    }));

    return NextResponse.json({
      context,
      sources,
    });
  } catch (error) {
    console.error('Failed to query conversations:', error);
    return NextResponse.json(
      { error: 'Failed to query conversations', context: '', sources: [] },
      { status: 500 }
    );
  }
}
