import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir, access } from 'fs/promises';
import { join } from 'path';
import { Message } from '@/types';
import { config } from 'dotenv';
import { constants } from 'fs';
import { spawn } from 'child_process';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../../filedb');
const CONVERSATIONS_DIR = join(FILEDB_BASE, 'webapp', 'conversations');

// Python scripts for vector store operations
const VECTOR_ADD_SCRIPT = join(process.cwd(), '../../.claude/shared/vector_store.py');
const ADD_CONVERSATION_SCRIPT = join(process.cwd(), '../../.claude/shared/add_conversation.py');

interface StoreRequest {
  session_id?: string;
  type: 'conversation' | 'news' | 'web_search' | 'analytics';
  document: {
    id: string;
    text: string;
    metadata: Record<string, any>;
  };
}

async function ensureDir(dir: string) {
  try {
    await access(dir, constants.F_OK);
  } catch {
    await mkdir(dir, { recursive: true });
  }
}

// Add document to vector store using Python
async function addToVectorStore(
  docId: string,
  text: string,
  metadata: Record<string, any>,
  collection: string
): Promise<void> {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [
      '-c',
      `
import sys
sys.path.insert(0, '${VECTOR_ADD_SCRIPT.split('/vector_store.py')[0]}')
from vector_store import get_vector_store
vs = get_vector_store()
vs.add_document(
    doc_id='${docId}',
    text('''${text.replace(/'/g, "\\'")}'''),
    ${JSON.stringify(metadata)},
    collection='${collection}'
)
print('OK')
`
    ]);

    let output = '';
    let errorOutput = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Vector store error: ${errorOutput || output}`));
      } else {
        resolve();
      }
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    const body: StoreRequest = await request.json();
    const { type, document } = body;

    if (!type || !document || !document.id || !document.text) {
      return NextResponse.json(
        { error: 'Type and document (with id and text) are required' },
        { status: 400 }
      );
    }

    // Handle different document types
    if (type === 'conversation') {
      const { session_id } = body;
      if (!session_id) {
        return NextResponse.json(
          { error: 'Session ID required for conversation type' },
          { status: 400 }
        );
      }

      // Extract role from document metadata (user or assistant)
      const role = (document.metadata as any)?.role || 'user';
      const timestamp = (document.metadata as any)?.timestamp || new Date().toISOString();
      const messageId = document.id || crypto.randomUUID();

      // 1. Save to file (legacy storage)
      const sessionDir = join(CONVERSATIONS_DIR, session_id);
      await ensureDir(sessionDir);

      const filename = `${Date.now()}.json`;
      const filepath = join(sessionDir, filename);

      // Format expected by /api/rag/recent endpoint
      const conversationEntry = {
        id: messageId,
        timestamp,
        message: {
          role: role,
          content: document.text,
          timestamp: timestamp,
        },
      };

      await writeFile(filepath, JSON.stringify(conversationEntry, null, 2));

      // 2. Vectorize for semantic search (async, don't wait)
      spawn('python3', [
        ADD_CONVERSATION_SCRIPT,
        '--session-id', session_id,
        '--role', role,
        '--content', document.text,
        '--timestamp', timestamp,
        '--message-id', messageId,
      ]).on('error', (err) => {
        console.error('[RAG Store] Failed to vectorize conversation:', err);
      });

      return NextResponse.json({ success: true, id: messageId });
    }

    // Handle news, web_search, analytics types
    const validTypes = ['news', 'web_search', 'analytics'];
    if (!validTypes.includes(type)) {
      return NextResponse.json(
        { error: `Invalid type: ${type}. Must be one of: conversation, ${validTypes.join(', ')}` },
        { status: 400 }
      );
    }

    // Add to vector store
    await addToVectorStore(
      document.id,
      document.text,
      document.metadata || {},
      type === 'web_search' ? 'web_searches' : type
    );

    return NextResponse.json({
      success: true,
      id: document.id,
      collection: type === 'web_search' ? 'web_searches' : type,
    });
  } catch (error) {
    console.error('Failed to store document:', error);
    return NextResponse.json(
      {
        error: 'Failed to store document',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
