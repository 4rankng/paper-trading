import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { config } from 'dotenv';
import { spawn } from 'child_process';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../../.env');
config({ path: envPath });

const INGEST_NEWS_SCRIPT = join(process.cwd(), '../../.claude/skills/rag_ingest/scripts/ingest_news.py');
const INGEST_ANALYTICS_SCRIPT = join(process.cwd(), '../../.claude/skills/rag_ingest/scripts/ingest_analytics.py');

interface IngestRequest {
  collections: Array<'news' | 'analytics' | 'all'>;
  force?: boolean;
  ticker?: string;
}

interface IngestResponse {
  success: boolean;
  message: string;
  stats?: {
    news?: number;
    analytics?: number;
  };
}

// Helper function to run Python script
function runPythonScript(scriptPath: string, args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [scriptPath, ...args]);
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
        reject(new Error(`Python script failed: ${errorOutput || output}`));
      } else {
        resolve(output);
      }
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    const body: IngestRequest = await request.json();
    const { collections, force = false, ticker } = body;

    if (!collections || !Array.isArray(collections) || collections.length === 0) {
      return NextResponse.json(
        { error: 'Collections array is required' },
        { status: 400 }
      );
    }

    // Validate collections
    const validCollections = ['news', 'analytics', 'all'];
    const invalidCollections = collections.filter(c => !validCollections.includes(c));
    if (invalidCollections.length > 0) {
      return NextResponse.json(
        { error: `Invalid collections: ${invalidCollections.join(', ')}` },
        { status: 400 }
      );
    }

    const results: IngestResponse = {
      success: true,
      message: 'Ingestion completed',
      stats: {},
    };

    // Determine which collections to ingest
    const ingestNews = collections.includes('all') || collections.includes('news');
    const ingestAnalytics = collections.includes('all') || collections.includes('analytics');

    // Run ingestion scripts
    const promises: Promise<void>[] = [];

    if (ingestNews) {
      const newsPromise = runPythonScript(INGEST_NEWS_SCRIPT, [
        ...(ticker ? ['--ticker', ticker] : []),
        ...(force ? ['--force'] : []),
      ]).then(output => {
        // Parse output to get stats
        const match = output.match(/News collection now has (\d+) documents/);
        if (match) {
          results.stats!.news = parseInt(match[1]);
        }
      });
      promises.push(newsPromise);
    }

    if (ingestAnalytics) {
      const analyticsPromise = runPythonScript(INGEST_ANALYTICS_SCRIPT, [
        ...(ticker ? ['--ticker', ticker] : []),
        ...(force ? ['--force'] : []),
      ]).then(output => {
        // Parse output to get stats
        const match = output.match(/Analytics collection now has (\d+) documents/);
        if (match) {
          results.stats!.analytics = parseInt(match[1]);
        }
      });
      promises.push(analyticsPromise);
    }

    await Promise.all(promises);

    return NextResponse.json(results);
  } catch (error) {
    console.error('RAG ingestion error:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Ingestion failed',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
