import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { config } from 'dotenv';
import { spawn } from 'child_process';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../../.env');
config({ path: envPath });

const SEARCH_SCRIPT = join(process.cwd(), '../../.claude/skills/rag_search/scripts/search.py');

interface SearchResult {
  id: string;
  text: string;
  metadata: {
    ticker?: string;
    date?: string;
    source?: string;
    url?: string;
    title?: string;
    doc_type?: string;
    [key: string]: any;
  };
  score: number;
  collection: string;
}

interface SearchResponse {
  query: string;
  model: string;
  count: number;
  results: SearchResult[];
}

// Helper function to run Python script with timeout
function runPythonScript(args: string[], timeoutMs: number = 10000): Promise<string> {
  return new Promise((resolve, reject) => {
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
      if (resolved) return;
      cleanup();

      if (code !== 0) {
        reject(new Error(`Python script failed: ${errorOutput || output}`));
      } else {
        resolve(output);
      }
    });

    const timeoutId = setTimeout(() => {
      cleanup();
      reject(new Error('Python script timeout'));
    }, timeoutMs);
  });
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const query = searchParams.get('query');
    const collection = searchParams.get('collection') || 'all';
    const limit = parseInt(searchParams.get('limit') || '5');
    const ticker = searchParams.get('ticker');

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    // Validate collection
    const validCollections = ['all', 'news', 'analytics', 'web_searches'];
    if (!validCollections.includes(collection)) {
      return NextResponse.json(
        { error: `Invalid collection. Must be one of: ${validCollections.join(', ')}` },
        { status: 400 }
      );
    }

    // Validate limit
    if (limit < 1 || limit > 50) {
      return NextResponse.json(
        { error: 'Limit must be between 1 and 50' },
        { status: 400 }
      );
    }

    // Build Python script arguments
    const args = [SEARCH_SCRIPT, query, '--collection', collection, '--limit', limit.toString(), '--format', 'json'];

    if (ticker) {
      args.push('--ticker', ticker);
    }

    // Run search script
    const output = await runPythonScript(args);

    // Parse JSON output
    const data: SearchResponse = JSON.parse(output);

    return NextResponse.json(data);
  } catch (error) {
    console.error('RAG search error:', error);
    return NextResponse.json(
      {
        error: 'Search failed',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
