import { NextRequest, NextResponse } from 'next/server';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { config } from 'dotenv';
import { existsSync, readdirSync, statSync } from 'fs';

const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

const FILEDB_BASE = process.env.FILEDB_PATH || join(process.cwd(), '../filedb');

interface NewsArticle {
  date: string;
  title: string;
  url?: string;
  source?: string;
  content: string;
  filename: string;
}

// GET /api/news/[ticker] - Fetch all news articles for a ticker
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const tickerUpper = ticker.toUpperCase();
    const { searchParams } = new URL(request.url);

    const limit = parseInt(searchParams.get('limit') || '50');
    const year = searchParams.get('year');
    const month = searchParams.get('month');

    const newsDir = join(FILEDB_BASE, 'news', tickerUpper);

    if (!existsSync(newsDir)) {
      return NextResponse.json({ ticker: tickerUpper, articles: [] });
    }

    const articles: NewsArticle[] = [];
    const years = year ? [year] : readdirSync(newsDir);

    for (const y of years) {
      const yearDir = join(newsDir, y);
      if (!existsSync(yearDir)) continue;

      const months = month ? [month.padStart(2, '0')] : readdirSync(yearDir);

      for (const m of months) {
        const monthDir = join(yearDir, m);
        if (!existsSync(monthDir)) continue;

        const files = readdirSync(monthDir).filter(f => f.endsWith('.md'));

        for (const file of files) {
          const filePath = join(monthDir, file);
          const content = await readFile(filePath, 'utf-8');

          // Extract YAML frontmatter and content
          let title = '';
          let url = '';
          let source = '';
          let articleContent = content;

          const yamlMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
          if (yamlMatch) {
            const yaml = yamlMatch[1];
            articleContent = yamlMatch[2];

            const titleMatch = yaml.match(/title:\s*(.*)/);
            if (titleMatch) title = titleMatch[1].replace(/['"]/g, '');

            const urlMatch = yaml.match(/url:\s*(.*)/);
            if (urlMatch) url = urlMatch[1].replace(/['"]/g, '');

            const sourceMatch = yaml.match(/source:\s*(.*)/);
            if (sourceMatch) source = sourceMatch[1].replace(/['"]/g, '');
          }

          articles.push({
            date: file.replace('.md', ''),
            title,
            url,
            source,
            content: articleContent.trim(),
            filename: file,
          });

          if (articles.length >= limit) break;
        }

        if (articles.length >= limit) break;
      }

      if (articles.length >= limit) break;
    }

    // Sort by date descending
    articles.sort((a, b) => b.date.localeCompare(a.date));

    return NextResponse.json({ ticker: tickerUpper, articles: articles.slice(0, limit) });
  } catch (error) {
    console.error('Failed to read news:', error);
    return NextResponse.json({ error: 'Failed to read news' }, { status: 500 });
  }
}

// POST /api/news/[ticker] - Add news article for a ticker
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ ticker: string }> }
) {
  try {
    const { ticker } = await params;
    const tickerUpper = ticker.toUpperCase();
    const body = await request.json();

    if (!body.content && !body.title) {
      return NextResponse.json(
        { error: 'content or title is required' },
        { status: 400 }
      );
    }

    // Determine date/filename
    const date = body.date || new Date().toISOString().split('T')[0];
    const filename = body.filename || `${date}.md`;

    // Determine directory path (YYYY/MM)
    const dateObj = new Date(date);
    const year = dateObj.getFullYear().toString();
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');

    const targetDir = join(FILEDB_BASE, 'news', tickerUpper, year, month);

    if (!existsSync(targetDir)) {
      await mkdir(targetDir, { recursive: true });
    }

    // Build YAML frontmatter
    let yaml = '---\n';
    if (body.title) yaml += `title: '${body.title.replace(/'/g, "''")}'\n`;
    if (body.url) yaml += `url: ${body.url}\n`;
    if (body.source) yaml += `source: ${body.source}\n`;
    if (body.date) yaml += `date: ${body.date}\n`;
    yaml += '---\n';

    const content = yaml + (body.content || '');

    // Use string interpolation to avoid Next.js 16 broad pattern warning
    const filePath = `${targetDir}/${filename}`;
    await writeFile(filePath, content, 'utf-8');

    return NextResponse.json({
      success: true,
      ticker: tickerUpper,
      path: `${year}/${month}/${filename}`,
    });
  } catch (error) {
    console.error('Failed to save news:', error);
    return NextResponse.json({ error: 'Failed to save news' }, { status: 500 });
  }
}
