import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { join } from 'path';
import { config } from 'dotenv';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

// Python script for semantic conversation search
const SEARCH_CONVERSATIONS_SCRIPT = join(process.cwd(), '../.claude/shared/search_conversations.py');

/**
 * Search conversations using semantic similarity via RAG.
 * Replaces old keyword-based search with proper semantic understanding.
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const sessionId = searchParams.get('session_id');
  const query = searchParams.get('query');
  const limit = parseInt(searchParams.get('limit') || '5', 10);
  const noTimeDecay = searchParams.get('no_time_decay') === 'true';

  if (!sessionId || !query) {
    return NextResponse.json(
      { error: 'Session ID and query required' },
      { status: 400 }
    );
  }

  return new Promise<NextResponse>((resolve) => {
    const args = [
      SEARCH_CONVERSATIONS_SCRIPT,
      '--session-id', sessionId,
      '--query', query,
      '--limit', String(limit),
    ];

    if (noTimeDecay) {
      args.push('--no-time-decay');
    }

    const python = spawn('python3', args);

    let output = '';
    let errorOutput = '';
    let resolved = false;

    const cleanup = () => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeoutId);
        python.kill();
      }
    };

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    python.on('close', (code) => {
      if (resolved) return; // Already timed out
      cleanup();

      if (code !== 0) {
        console.error('[RAG Query] Error:', errorOutput);
        resolve(NextResponse.json(
          {
            error: 'Failed to search conversations',
            details: errorOutput,
            context: '',
            sources: [],
          },
          { status: 500 }
        ));
        return;
      }

      try {
        const result = JSON.parse(output);
        resolve(NextResponse.json(result));
      } catch (parseError) {
        console.error('[RAG Query] Parse error:', parseError);
        resolve(NextResponse.json(
          {
            error: 'Failed to parse search results',
            details: output,
            context: '',
            sources: [],
          },
          { status: 500 }
        ));
      }
    });

    // Timeout after 10 seconds
    const timeoutId = setTimeout(() => {
      console.error('[RAG Query] Timeout');
      cleanup();
      resolve(NextResponse.json(
        {
          error: 'Search timeout',
          context: '',
          sources: [],
        },
        { status: 504 }
      ));
    }, 10000);
  });
}
