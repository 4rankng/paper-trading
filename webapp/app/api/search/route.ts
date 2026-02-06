import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { join } from 'path';

export const runtime = 'nodejs';

interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source: string;
}

async function searchWeb(query: string, limit: number = 5): Promise<{
  query: string;
  results: SearchResult[];
  count: number;
}> {
  return new Promise((resolve, reject) => {
    const projectRoot = join(process.cwd(), '..');
    const scriptPath = join(projectRoot, '.claude/shared/web_search.py');

    console.log(`[Search API] Invoking: python3 ${scriptPath}`, query, limit);

    const python = spawn('python3', [scriptPath, query, String(limit)], {
      cwd: projectRoot,
      env: {
        ...process.env,
        PYTHONPATH: join(projectRoot, '.claude/shared'),
      },
    });

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout.trim());
          resolve(result);
        } catch (e) {
          reject(new Error(`Failed to parse search results: ${stdout}`));
        }
      } else {
        reject(new Error(stderr || `Search exited with code ${code}`));
      }
    });

    python.on('error', (error) => {
      reject(new Error(`Failed to spawn Python: ${error.message}`));
    });

    // Timeout after 15 seconds
    setTimeout(() => {
      python.kill();
      reject(new Error('Search timed out (15s)'));
    }, 15000);
  });
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  try {
    const query = searchParams.get('q');
    const limit = parseInt(searchParams.get('limit') || '5', 10);

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter "q" is required' },
        { status: 400 }
      );
    }

    if (query.length > 200) {
      return NextResponse.json(
        { error: 'Query too long (max 200 characters)' },
        { status: 400 }
      );
    }

    const result = await searchWeb(query, Math.min(limit, 10));

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[Search API] Error:', error);
    return NextResponse.json(
      {
        error: 'Search failed',
        message: error?.message || 'Unknown error',
        query: searchParams.get('q') || '',
        results: [],
        count: 0,
      },
      { status: 500 }
    );
  }
}
