import { NextRequest } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';
import { Message } from '@/types';
import { config } from 'dotenv';
import { join } from 'path';
import { validateAndFixVisualizations, generateRegenerationPrompt, extractCorrectedVisualizations, sanitizeLoneSurrogates } from './viz-validator';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

// Support both direct Anthropic API and Z.AI proxy
const apiKey = process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN || '';
const baseUrl = process.env.ANTHROPIC_BASE_URL;
// Model selection: support GLM models via Z.AI proxy or default to Claude
const model = process.env.LLM_MODEL || (baseUrl?.includes('z.ai') ? 'glm-4.7' : 'claude-sonnet-4-20250514');

const anthropic = new Anthropic({
  apiKey,
  ...(baseUrl && { baseURL: baseUrl }),
});

export const runtime = 'nodejs';

const BASE_URL = process.env.NEXT_PUBLIC_WEBAPP_URL || 'http://localhost:3000';

// Define tools for the LLM
const TOOLS = [
  {
    name: 'get_portfolios',
    description: 'Fetch all portfolio data including holdings, values, and P/L',
    input_schema: {
      type: 'object' as const,
      properties: {},
    },
  },
  {
    name: 'get_portfolio',
    description: 'Fetch a specific portfolio by ID with its holdings',
    input_schema: {
      type: 'object' as const,
      properties: {
        id: {
          type: 'string' as const,
          description: 'Portfolio ID (e.g., CORE, AI_PICKS)',
        },
      },
      required: ['id'],
    },
  },
  {
    name: 'add_holding',
    description: 'Add a new holding to a portfolio',
    input_schema: {
      type: 'object' as const,
      properties: {
        portfolio_id: {
          type: 'string' as const,
          description: 'Portfolio ID (e.g., CORE, AI_PICKS)',
        },
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        shares: {
          type: 'number' as const,
          description: 'Number of shares',
        },
        avg_cost: {
          type: 'number' as const,
          description: 'Average cost per share',
        },
        current_price: {
          type: 'number' as const,
          description: 'Current market price (optional)',
        },
      },
      required: ['portfolio_id', 'ticker', 'shares', 'avg_cost'],
    },
  },
  {
    name: 'update_holding',
    description: 'Update an existing holding (shares, avg_cost, current_price)',
    input_schema: {
      type: 'object' as const,
      properties: {
        portfolio_id: {
          type: 'string' as const,
          description: 'Portfolio ID',
        },
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        shares: { type: 'number' as const },
        avg_cost: { type: 'number' as const },
        current_price: { type: 'number' as const },
      },
      required: ['portfolio_id', 'ticker'],
    },
  },
  {
    name: 'remove_holding',
    description: 'Remove a holding from a portfolio',
    input_schema: {
      type: 'object' as const,
      properties: {
        portfolio_id: {
          type: 'string' as const,
          description: 'Portfolio ID',
        },
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
      },
      required: ['portfolio_id', 'ticker'],
    },
  },
  {
    name: 'get_watchlist',
    description: 'Fetch all watchlist entries',
    input_schema: {
      type: 'object' as const,
      properties: {},
    },
  },
  {
    name: 'add_to_watchlist',
    description: 'Add a ticker to the watchlist',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        notes: {
          type: 'string' as const,
          description: 'Notes about the position',
        },
        tags: {
          type: 'array' as const,
          items: { type: 'string' as const },
          description: 'Tags for categorization',
        },
        strategy: {
          type: 'string' as const,
          description: 'Trading strategy',
        },
        target_entry: {
          type: 'number' as const,
          description: 'Target entry price',
        },
        target_exit: {
          type: 'number' as const,
          description: 'Target exit price',
        },
      },
      required: ['ticker'],
    },
  },
  {
    name: 'get_trades',
    description: 'Fetch trade history with optional filters',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: { type: 'string' as const, description: 'Filter by ticker' },
        portfolio: { type: 'string' as const, description: 'Filter by portfolio' },
        limit: {
          type: 'number' as const,
          description: 'Max number of trades to return (default: all)',
        },
      },
    },
  },
  {
    name: 'log_trade',
    description: 'Log a new trade (BUY, SELL, or TRIM)',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        action: {
          type: 'string' as const,
          description: 'Trade action: BUY, SELL, or TRIM',
          enum: ['BUY', 'SELL', 'TRIM'],
        },
        shares: {
          type: 'number' as const,
          description: 'Number of shares traded',
        },
        price: {
          type: 'number' as const,
          description: 'Price per share',
        },
        portfolio: {
          type: 'string' as const,
          description: 'Portfolio ID (default: CORE)',
        },
        notes: {
          type: 'string' as const,
          description: 'Trade notes or reasoning',
        },
      },
      required: ['ticker', 'action', 'shares', 'price'],
    },
  },
  {
    name: 'get_analytics',
    description: 'Fetch analytics data (technical, fundamental, thesis) for a ticker',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
      },
      required: ['ticker'],
    },
  },
  {
    name: 'update_analytics',
    description: 'Update analytics data for a ticker',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        type: {
          type: 'string' as const,
          description: 'Type of analytics',
          enum: ['technical', 'fundamental', 'thesis'],
        },
        content: {
          type: 'string' as const,
          description: 'Analytics content in markdown format',
        },
      },
      required: ['ticker', 'type', 'content'],
    },
  },
  {
    name: 'get_news',
    description: 'Fetch news articles for a ticker',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        limit: {
          type: 'number' as const,
          description: 'Max articles to return (default: 50)',
        },
      },
      required: ['ticker'],
    },
  },
  {
    name: 'get_prices',
    description: 'Fetch historical price data for a ticker',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol',
        },
        limit: {
          type: 'number' as const,
          description: 'Max days to return (default: 365)',
        },
      },
      required: ['ticker'],
    },
  },
  {
    name: 'web_search',
    description: 'Search the web for current news, events, and information. Uses DuckDuckGo (free, no API key). Great for breaking news, government announcements, market events.',
    input_schema: {
      type: 'object' as const,
      properties: {
        query: {
          type: 'string' as const,
          description: 'Search query (e.g., "government shutdown impact", "AAPL news today", "Fed interest rate decision")',
        },
        limit: {
          type: 'number' as const,
          description: 'Max results to return (default: 5, max: 10)',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'fetch_news',
    description: 'Fetch news for a specific stock ticker using yfinance. Use this for stock-specific news.',
    input_schema: {
      type: 'object' as const,
      properties: {
        ticker: {
          type: 'string' as const,
          description: 'Stock ticker symbol (e.g., NVDA, AAPL)',
        },
        limit: {
          type: 'number' as const,
          description: 'Max articles to return (default: 20)',
        },
      },
      required: ['ticker'],
    },
  },
  {
    name: 'invoke_skill',
    description: 'Invoke a Python skill script with access to full data access layer and tools. Use GET /api/skill?name=portfolio_manager to list available scripts for a skill. Common examples: portfolio_manager/get_portfolio.py, news_fetcher/fetch_news.py --ticker NVDA, trading_plan/generate_plan_template.py NVDA 1d.',
    input_schema: {
      type: 'object' as const,
      properties: {
        skill: {
          type: 'string' as const,
          description: 'Skill name (portfolio_manager, watchlist_manager, news_fetcher, trading_plan, analytics_generator, macro_fetcher, trading_debate, signal_formatter, read_csv, read_pdf)',
        },
        script: {
          type: 'string' as const,
          description: 'Script name within the skill (e.g., "get_portfolio.py", "fetch_news.py", "trading_plan.py")',
        },
        args: {
          type: 'array' as const,
          description: 'Command-line arguments for the script',
          items: { type: 'string' as const },
        },
      },
      required: ['skill', 'script', 'args'],
    },
  },
  {
    name: 'rag_search',
    description: 'Search stored news articles, research analytics, and web searches using semantic search. Use this to find relevant historical data, news, and analysis about stocks or market conditions.',
    input_schema: {
      type: 'object' as const,
      properties: {
        query: {
          type: 'string' as const,
          description: 'Search query for finding relevant documents',
        },
        collection: {
          type: 'string' as const,
          enum: ['news', 'analytics', 'web_searches', 'all'],
          description: 'Collection to search (default: all)',
        },
        limit: {
          type: 'number' as const,
          description: 'Max results to return (default: 5)',
        },
        ticker: {
          type: 'string' as const,
          description: 'Filter by ticker symbol (optional)',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'create_visualization',
    description: 'Create a visualization from structured data. Use this for complex charts requiring data fetched from other tools.',
    input_schema: {
      type: 'object' as const,
      properties: {
        viz_type: {
          type: 'string' as const,
          enum: ['line', 'bar', 'pie', 'table', 'scatter'],
          description: 'Visualization type',
        },
        data: {
          type: 'object' as const,
          description: 'Visualization data object - structure depends on viz_type',
        },
        options: {
          type: 'object' as const,
          description: 'Optional: title, axis labels, legend, colors, etc.',
        },
      },
      required: ['viz_type', 'data'],
    },
  },
];

const SYSTEM_PROMPT = `You are TermAI Explorer, a financial AI assistant with access to REAL portfolio and market data.

CRITICAL RULES:
1. BE DIRECT AND CLEAR - Avoid unnecessary fluff, but provide complete analysis
2. ALWAYS use the available tools to fetch REAL data before responding
3. NEVER make up or fabricate numbers, holdings, prices, or financial information
4. CRITICAL: Before discussing ANY portfolio holdings, you MUST call get_portfolios tool. Conversation history may contain outdated or incorrect holdings information - ONLY trust live data from get_portfolios
5. Distinguish between "on watchlist" vs "owned in portfolio" - these are different things
6. CONSOLIDATE and INTERPRET the data - then PRESENT WITH VISUALIZATIONS
7. NEVER use ASCII tables, terminal art, or markdown tables - USE THE create_visualization TOOL
8. For complex visualizations with lots of data, use create_visualization tool - it generates guaranteed-valid JSON
9. For simple 2-4 row tables, you MAY write viz:table syntax directly - but tool is safer
10. LET DATA SPEAK - Use visualizations to show information, supplement with key insights

🎨 HOW TO CREATE VISUALIZATIONS:
You have TWO options:

OPTION 1 - Use create_visualization tool (RECOMMENDED for data-heavy charts):
- Use for: line charts, bar charts, pie charts with many data points
- Process: get_portfolios → analyze → create_visualization({viz_type, data, options})
- Returns ready-to-use visualization markdown - just include it in your response

OPTION 2 - Write viz: syntax directly (ONLY for simple tables):
- Use for: small tables (2-4 rows), quick summaries
- Format: ![viz:table]({"headers":["A","B"],"rows":[["x","y"]]})
- Risk: Syntax errors will cause visualization to fail

FORBIDDEN FORMATS (NEVER USE THESE):
❌ MARKDOWN TABLES (these will NOT render properly):
| Issue | Status |
|-------|--------|
| Item 1 | Value 1 |
| Item 2 | Value 2 |

❌ ASCII/TERMINAL ART:
+-------+--------+
| Issue | Status |
+-------+--------+

❌ BOX DRAWING:
┌───────┬────────┐
│ Issue │ Status │
└───────┴────────┘

❌ WRONG CHART TYPES (these will fail to render):
![viz:line]({"data":{...}})        ← WRONG: "line" is not a valid type
![viz:bar]({"data":{...}})         ← WRONG: "bar" is not a valid type
![viz:chart]({"type":"line",...})  ← WRONG: type must be "chart", not "line"

REQUIRED VISUALIZATION FORMAT (USE THIS INSTEAD):
For tabular data, ALWAYS use the viz:table format:
![viz:table]({"headers":["Issue","Status"],"rows":[["Shutdown Duration","4 days (brief)"],["DHS Funding","2-week continuing resolution"]]})

AVAILABLE VISUALIZATION TYPES:

1. LINE CHART - For trends over time (prices, portfolio value)
   IMPORTANT: Use type="chart" with chartType="line" inside
   ![viz:chart]({"type":"chart","chartType":"line","data":{"labels":["Jan","Feb","Mar"],"datasets":[{"label":"Portfolio Value","data":[100000,105000,102000]}]},"options":{"title":"Portfolio Value Trend"}})

2. BAR CHART - For comparisons (holdings by value, P/L by stock)
   IMPORTANT: Use type="chart" with chartType="bar" inside
   ![viz:chart]({"type":"chart","chartType":"bar","data":{"labels":["AAPL","MSFT","GOOGL"],"datasets":[{"label":"Holdings Value","data":[50000,30000,20000]}]},"options":{"title":"Holdings by Stock"}})

3. PIE CHART - For distributions (asset allocation, sector breakdown)
   IMPORTANT: ALWAYS use raw dollar amounts, NEVER percentages - the system auto-converts to %
   ![viz:pie]({"data":[{"label":"CORE","value":127522},{"label":"AI_PICKS","value":13749},{"label":"Cash","value":22000}],"options":{"title":"Portfolio Allocation"}}})

4. TABLE - For detailed data (holdings list, trade history)
   IMPORTANT: Notice the "rows" key is inside the object, comma-separated
   ![viz:table]({"headers":["Ticker","Shares","Value","P/L %"],"rows":[["AAPL",100,"$50,000","+12.5%"],["MSFT",50,"$30,000","+8.3%"]]})

CRITICAL SYNTAX RULES:
- Line/Bar charts: type="chart" (NOT type="line" or type="bar")
- chartType="line" or chartType="bar" goes INSIDE the data object
- Pie charts: type="pie" with RAW dollar amounts (not percentages)
- Tables: type="table"
- NEVER use type="line" or type="bar" directly - this will fail to render!
- NEVER repeat the same key twice in JSON (e.g., don't use "data" twice)
- ALWAYS use proper JSON syntax - no trailing commas, all keys quoted

COMMON CHART SYNTAX ERRORS:
❌ WRONG - This will NOT render:
![viz:chart]({"type":"line","data":{...}})
![viz:line]({"data":{...}})

✅ CORRECT - This WILL render:
![viz:chart]({"type":"chart","chartType":"line","data":{...}})

❌ WRONG - This will NOT render:
![viz:chart]({"type":"bar","data":{...}})

✅ CORRECT - This WILL render:
![viz:chart]({"type":"chart","chartType":"bar","data":{...}})

WHEN TO USE EACH VISUALIZATION:
- LINE CHART: Time-series data, price history, portfolio growth over time
- BAR CHART: Comparing values across categories (holdings, P/L by ticker)
- PIE CHART: Parts-of-whole relationships (portfolio allocation, sector breakdown)
- TABLE: Detailed multi-column listings (holdings with all details, trade history, event summaries)

IMPORTANT - TABLE USAGE:
When you need to show tabular data (issues, comparisons, summaries), ALWAYS use viz:table format.

WRONG (markdown table - will NOT render):
| Issue | Status |
|-------|--------|
| Item 1 | Value 1 |

CORRECT (viz:table - WILL render):
![viz:table]({"headers":["Issue","Status"],"rows":[["Item 1","Value 1"]]})

RESPONSE STRUCTURE:
1. Fetch data using tools (get_portfolios, get_news, etc.)
2. Provide a clear summary of key findings
3. For complex charts (lots of data points): Use create_visualization tool
   - Returns ready-to-use visualization markdown
   - Just include the returned string in your response
4. For simple tables (2-4 rows): Write viz:table syntax directly
5. Provide detailed analysis and insights to complement the visualizations

RECOMMENDED WORKFLOW FOR CHARTS:
Step 1: get_portfolios → extract dates/values from result
Step 2: create_visualization({viz_type: "line", data: {labels: [...], datasets: [...]}, options: {...}})
Step 3: Include the returned visualization in your response
Step 4: Add your analysis and insights

EXAMPLE GOOD RESPONSE:
"Your portfolio is down $49K (-28%) across all positions. LAES is your biggest loser at -$34K.

![viz:table]({"headers":["Ticker","Shares","Value","P/L %","P/L $"],"rows":[["LAES",18000,"$81,000","-29.7%","-$34,200"],["WRD",2800,"$24,500","-20.5%","-$6,300"],["PONY",1400,"$22,022","-27.2%","-$8,250"]]})

**Key Concerns:**
• All core positions underwater - LAES driving 70% of losses
• Concentration risk in small-cap stocks
• Consider: trim LAES on any bounce, diversify into quality names

**Outlook:** These positions can recover if broader market rallies, but loss magnitude suggests fundamental issues beyond market cycle."

QUALITY GUIDELINES:
- Be comprehensive but efficient - explain the "why" behind the data
- Don't repeat numbers that are clearly visible in visualizations
- Avoid generic filler phrases ("Based on the data", "As you can see")
- Provide context and insights that add value beyond raw numbers
- For complex topics, provide thorough analysis with clear structure

Always cite data sources.`;

// Helper function to safely fetch and parse JSON
async function safeFetch(url: string, options?: RequestInit): Promise<any> {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`Fetch error for ${url}:`, error);
    throw error;
  }
}

// Helper function to detect if query is news-related
function isNewsQuery(query: string): boolean {
  const newsKeywords = ['news', 'latest', 'recent', 'headline', 'breaking', 'update', 'what\'s new', 'what is happening'];
  const queryLower = query.toLowerCase();
  return newsKeywords.some(kw => queryLower.includes(kw));
}

// Helper function to execute tool calls and return structured data for LLM
async function executeToolCall(toolName: string, toolInput: any) {
  console.log('[Chat API] Executing tool:', toolName, 'with input:', toolInput);

  try {
    switch (toolName) {
      case 'get_portfolios': {
        const data = await safeFetch(`${BASE_URL}/api/portfolio`);
        // Return structured data for LLM to consolidate
        const structured: any = { cash: data.cash, portfolios: {} };
        for (const [id, portfolio] of Object.entries(data.portfolios || {})) {
          const p = portfolio as any;
          structured.portfolios[id] = {
            name: p.name,
            holdings_value: p.summary?.holdings_value,
            total_gain_loss: p.summary?.total_gain_loss,
            total_gain_loss_pct: p.summary?.total_gain_loss_pct,
            holdings: p.holdings?.map((h: any) => ({
              ticker: h.ticker,
              shares: h.shares,
              avg_cost: h.avg_cost,
              current_price: h.current_price,
              market_value: h.market_value,
              gain_loss: h.gain_loss,
              gain_loss_pct: h.gain_loss_pct,
            })) || [],
          };
        }
        return { success: true, data: structured };
      }

      case 'get_portfolio': {
        const data = await safeFetch(`${BASE_URL}/api/portfolio/${toolInput.id}`);
        return {
          success: true,
          data: {
            id: toolInput.id,
            name: data.name,
            holdings_value: data.summary?.holdings_value,
            total_gain_loss: data.summary?.total_gain_loss,
            total_gain_loss_pct: data.summary?.total_gain_loss_pct,
            holdings: data.holdings?.map((h: any) => ({
              ticker: h.ticker,
              shares: h.shares,
              avg_cost: h.avg_cost,
              current_price: h.current_price,
              market_value: h.market_value,
              gain_loss: h.gain_loss,
              gain_loss_pct: h.gain_loss_pct,
            })) || [],
          },
        };
      }

      case 'add_holding': {
        const result = await safeFetch(`${BASE_URL}/api/portfolio/${toolInput.portfolio_id}/holdings`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ticker: toolInput.ticker,
            shares: toolInput.shares,
            avg_cost: toolInput.avg_cost,
            current_price: toolInput.current_price,
          }),
        });
        return result.success ? { success: true } : result;
      }

      case 'update_holding': {
        const result = await safeFetch(
          `${BASE_URL}/api/portfolio/${toolInput.portfolio_id}/holdings/${toolInput.ticker}`,
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(toolInput),
          }
        );
        return result.success ? { success: true } : result;
      }

      case 'remove_holding': {
        const result = await safeFetch(
          `${BASE_URL}/api/portfolio/${toolInput.portfolio_id}/holdings/${toolInput.ticker}`,
          { method: 'DELETE' }
        );
        return result.success ? { success: true } : result;
      }

      case 'get_watchlist': {
        const data = await safeFetch(`${BASE_URL}/api/watchlist`);
        const entries = Array.isArray(data?.entries) ? data.entries :
                         (data?.tickers ? Object.keys(data.tickers).map((ticker: string) => ({
                           ticker,
                           ...data.tickers[ticker],
                         })) : []);

        return {
          success: true,
          data: {
            entries: entries.map((e: any) => ({
              ticker: e.ticker,
              strategy: e.strategy,
              notes: e.notes,
              target_entry: e.target_entry,
              target_exit: e.target_exit,
              stop_loss: e.stop_loss,
              status: e.status,
            })),
            total_count: entries.length,
          },
        };
      }

      case 'add_to_watchlist': {
        const result = await safeFetch(`${BASE_URL}/api/watchlist`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(toolInput),
        });
        return result.success ? { success: true } : result;
      }

      case 'get_trades': {
        const params = new URLSearchParams();
        if (toolInput.ticker) params.set('ticker', toolInput.ticker);
        if (toolInput.portfolio) params.set('portfolio', toolInput.portfolio);
        const data = await safeFetch(`${BASE_URL}/api/trades?${params}`);
        return {
          success: true,
          data: {
            trades: data.trades?.map((t: any) => ({
              timestamp: t.timestamp,
              portfolio: t.portfolio,
              ticker: t.ticker,
              action: t.action,
              shares: t.shares,
              price: t.price,
              total_value: t.total_value,
            })) || [],
          },
        };
      }

      case 'log_trade': {
        const result = await safeFetch(`${BASE_URL}/api/trades`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(toolInput),
        });
        return result.success ? { success: true } : result;
      }

      case 'get_analytics': {
        const res = await fetch(`${BASE_URL}/api/analytics/${toolInput.ticker}`);
        if (!res.ok) {
          return { success: true, data: { ticker: toolInput.ticker, technical: null, fundamental: null, thesis: null } };
        }
        const data = await res.json();
        return {
          success: true,
          data: {
            ticker: toolInput.ticker,
            technical: data.technical?.substring?.(0, 1000) || null,
            fundamental: data.fundamental?.substring?.(0, 1000) || null,
            thesis: data.thesis?.substring?.(0, 1000) || null,
          },
        };
      }

      case 'update_analytics': {
        const result = await safeFetch(`${BASE_URL}/api/analytics/${toolInput.ticker}/${toolInput.type}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: toolInput.content }),
        });
        return result.success ? { success: true } : result;
      }

      case 'get_news': {
        const params = new URLSearchParams();
        if (toolInput.limit) params.set('limit', Math.min(toolInput.limit, 10).toString());
        const data = await safeFetch(`${BASE_URL}/api/news/${toolInput.ticker}?${params}`);
        return {
          success: true,
          data: {
            ticker: toolInput.ticker,
            articles: data.articles?.map((a: any) => ({
              date: a.date,
              title: a.title,
              source: a.source,
              url: a.url,
            })) || [],
          },
        };
      }

      case 'get_prices': {
        const params = new URLSearchParams();
        if (toolInput.limit) params.set('limit', Math.min(toolInput.limit, 10).toString());
        try {
          const data = await safeFetch(`${BASE_URL}/api/prices/${toolInput.ticker}?${params}`);
          // If 404 (no price data), return empty array instead of error
          if (!data || data.error === 'HTTP 404: Not Found' || !data.prices) {
            return {
              success: true,
              data: {
                ticker: toolInput.ticker,
                prices: [],
                note: 'No price data available - fetch first using invoke_skill with analytics_generator/fetch_prices',
              },
            };
          }
          return {
            success: true,
            data: {
              ticker: toolInput.ticker,
              prices: data.prices?.map((p: any) => ({
                date: p.date,
                open: p.open,
                high: p.high,
                low: p.low,
                close: p.close,
              })) || [],
            },
          };
        } catch (e: any) {
          // Handle fetch errors (404, network issues, etc) gracefully
          const errorMsg = e?.message || 'Unknown error';
          if (errorMsg.includes('404') || errorMsg.includes('Not Found')) {
            return {
              success: true,
              data: {
                ticker: toolInput.ticker,
                prices: [],
                note: 'No price data available - fetch first using invoke_skill with analytics_generator/fetch_prices',
              },
            };
          }
          // For other errors, still return gracefully
          return {
            success: true,
            data: {
              ticker: toolInput.ticker,
              prices: [],
              note: `Price fetch error: ${errorMsg}`,
            },
          };
        }
      }

      case 'web_search': {
        const params = new URLSearchParams();
        params.set('q', toolInput.query);
        if (toolInput.limit) params.set('limit', Math.min(toolInput.limit, 10).toString());
        const data = await safeFetch(`${BASE_URL}/api/search?${params}`);
        return {
          success: true,
          data: {
            query: toolInput.query,
            results: data.results?.map((r: any) => ({
              title: r.title,
              url: r.url,
              snippet: r.snippet,
              source: r.source,
            })) || [],
            count: data.count || 0,
          },
        };
      }

      case 'fetch_news': {
        // Use news_fetcher skill as reliable alternative
        const limit = toolInput.limit || 20;
        try {
          const data = await safeFetch(`${BASE_URL}/api/skill`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              skill: 'news_fetcher',
              script: 'fetch_news.py',
              args: ['--ticker', toolInput.ticker, '--limit', String(limit)],
              session_id: 'webapp',
            }),
          });
          if (data.error) {
            return {
              success: true,
              data: {
                ticker: toolInput.ticker,
                source: 'news_fetcher skill (yfinance)',
                output: `Error fetching news: ${data.error}`,
                error: data.error,
              },
            };
          }
          // Parse news from Python script output
          return {
            success: true,
            data: {
              ticker: toolInput.ticker,
              source: 'news_fetcher skill (yfinance)',
              output: data.output || 'No articles found',
            },
          };
        } catch (e: any) {
          return {
            success: true,
            data: {
              ticker: toolInput.ticker,
              source: 'news_fetcher skill (yfinance)',
              output: `Failed to fetch news: ${e.message}`,
              error: e.message,
            },
          };
        }
      }

      case 'invoke_skill': {
        try {
          const data = await safeFetch(`${BASE_URL}/api/skill`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              skill: toolInput.skill,
              script: toolInput.script,
              args: toolInput.args || [],
              session_id: 'webapp',
            }),
          });
          if (data.error) {
            // Return success with error info instead of failing
            return {
              success: true,
              data: {
                skill: toolInput.skill,
                script: toolInput.script,
                output: `Error: ${data.error}`,
                error: data.error,
              },
            };
          }
          return {
            success: true,
            data: {
              skill: toolInput.skill,
              script: toolInput.script,
              output: data.output || 'Skill executed successfully',
            },
          };
        } catch (e: any) {
          // Handle fetch errors gracefully
          return {
            success: true,
            data: {
              skill: toolInput.skill,
              script: toolInput.script,
              output: `Failed to execute skill: ${e.message}`,
              error: e.message,
            },
          };
        }
      }

      case 'rag_search': {
        const params = new URLSearchParams();
        params.set('query', toolInput.query);
        params.set('collection', toolInput.collection || 'all');
        if (toolInput.limit) params.set('limit', toolInput.limit.toString());
        if (toolInput.ticker) params.set('ticker', toolInput.ticker);

        const data = await safeFetch(`${BASE_URL}/api/rag/search?${params}`);
        return {
          success: true,
          data: {
            query: toolInput.query,
            results: data.results?.map((r: any) => ({
              text: r.text?.substring(0, 500) || '',  // Truncate for LLM
              metadata: r.metadata,
              score: r.score,
              collection: r.collection,
            })) || [],
            count: data.count || 0,
          },
        };
      }

      case 'create_visualization': {
        // Generate visualization JSON from structured data
        const { viz_type, data, options } = toolInput;

        let vizCommand: any = {
          type: viz_type,
          ...data,
        };

        // Add options if provided
        if (options) {
          vizCommand = { ...vizCommand, ...options };
        }

        // For chart types, ensure proper structure
        if (viz_type === 'line' || viz_type === 'bar' || viz_type === 'scatter') {
          vizCommand = {
            type: 'chart',
            chartType: viz_type,
            ...data,
            ...options,
          };
        }

        // Generate the viz markdown string
        const vizString = JSON.stringify(vizCommand);
        const vizMarkdown = `![viz:${viz_type}](${vizString})`;

        return {
          success: true,
          data: {
            visualization: vizMarkdown,
            type: viz_type,
            data: vizCommand,
          },
        };
      }

      default:
        return { error: `Unknown tool: ${toolName}` };
    }
  } catch (error: any) {
    console.error(`[Chat API] Tool execution error for ${toolName}:`, error);
    return { error: error.message || 'Tool execution failed' };
  }
}

/**
 * Attempt to auto-regenerate truncated visualizations
 */
async function attemptRegenerate(
  text: string,
  errors: any[],
  anthropic: any,
  model: string,
  systemPrompt: string,
  conversationHistory: any[]
): Promise<{ success: boolean; text: string; fixedCount: number }> {
  try {
    // Extract viz types that need regeneration
    const vizTypes = errors.map(e => e.type);

    const regeneratePrompt = `${systemPrompt}

The previous response had ${errors.length} truncated visualization(s) that need to be regenerated. The user's request remains the same.

Please regenerate ONLY these visualization types with complete, properly formatted JSON:
${vizTypes.map((t, i) => `${i + 1}. ${t}`).join('\n')}

CRITICAL:
- Ensure ALL JSON is complete and properly closed
- Use the correct viz syntax: ![viz:type](...)
- Double-check bracket matching: every { must have }, every [ must have ]
- No trailing commas inside objects/arrays
- Provide complete data (no truncated arrays or objects)

Generate the visualizations now:`;

    const response = await anthropic.messages.create({
      model,
      max_tokens: 128000, // Full token limit for GLM-4 (same as main request)
      system: regeneratePrompt,
      messages: conversationHistory.slice(-2), // Only last 2 turns for context
    });

    let regeneratedText = '';
    for (const block of response.content) {
      if (block.type === 'text') {
        regeneratedText += block.text;
      }
    }

    // Validate the regenerated visualizations
    const { validateAndFixVisualizations } = await import('./viz-validator');
    const validationResult = validateAndFixVisualizations(regeneratedText);

    if (validationResult.isValid) {
      // Success! Extract just the viz markdown from the response
      const vizRegex = /!\[viz:\w+\]\([^)]+\)/g;
      const regeneratedVizs = regeneratedText.match(vizRegex) || [];

      if (regeneratedVizs.length > 0) {
        // Replace error markers with regenerated vizs
        let updatedText = text;
        let replacedCount = 0;

        errors.forEach((error, index) => {
          if (index < regeneratedVizs.length) {
            // Find and replace the error marker
            const errorMarker = updatedText.substring(error.startIndex, error.endIndex);
            if (errorMarker.includes('⚠️')) {
              updatedText =
                updatedText.substring(0, error.startIndex) +
                regeneratedVizs[index] +
                updatedText.substring(error.endIndex);
              replacedCount++;
            }
          }
        });

        return { success: true, text: updatedText, fixedCount: replacedCount };
      }
    }

    return { success: false, text, fixedCount: 0 };
  } catch (error) {
    console.error('[Chat API] Auto-regeneration failed:', error);
    return { success: false, text, fixedCount: 0 };
  }
}

export async function POST(request: NextRequest) {
  try {
    const { message, session_id } = await request.json();

    if (!message || !session_id) {
      return new Response(JSON.stringify({ error: 'Message and session ID required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Fetch RAG context (conversation history)
    let context = '';
    let hasHistory = false;

    // First, try semantic RAG search
    try {
      const ragResponse = await fetch(
        `${BASE_URL}/api/rag/query?session_id=${encodeURIComponent(session_id)}&query=${encodeURIComponent(message)}&limit=5`
      );
      if (ragResponse.ok) {
        const ragData = await ragResponse.json();
        context = ragData.context || '';
        hasHistory = context.length > 0;
      }
    } catch (error) {
      console.error('Failed to fetch RAG context:', error);
    }

    // Fallback: if no context from RAG, fetch recent messages directly
    if (!hasHistory) {
      try {
        const recentResponse = await fetch(
          `${BASE_URL}/api/rag/recent?session_id=${encodeURIComponent(session_id)}&limit=10`
        );
        if (recentResponse.ok) {
          const recentData = await recentResponse.json();
          if (recentData.messages && recentData.messages.length > 0) {
            context = recentData.messages.map((m: any) => {
              const role = m.role === 'user' ? 'User' : 'Assistant';
              return `${role}: ${m.content}`;
            }).join('\n\n');
            hasHistory = true;
          }
        }
      } catch (error) {
        console.error('Failed to fetch recent messages:', error);
      }
    }

    // Auto-RAG search for news queries
    let ragSearchResults = '';
    if (isNewsQuery(message)) {
      try {
        const searchResponse = await fetch(
          `${BASE_URL}/api/rag/search?query=${encodeURIComponent(message)}&collection=news&limit=5`
        );
        if (searchResponse.ok) {
          const searchData = await searchResponse.json();
          if (searchData.results && searchData.results.length > 0) {
            ragSearchResults = '\n\nRelevant news from RAG search:\n';
            searchData.results.forEach((r: any, i: number) => {
              ragSearchResults += `\n[${i + 1}] ${r.metadata?.title || r.metadata?.ticker || 'Unknown'} (Score: ${r.score?.toFixed(2) || 'N/A'})\n${r.text?.substring(0, 300) || ''}...\n`;
            });
          }
        }
      } catch (error) {
        console.error('Failed to fetch RAG search results:', error);
      }
    }

    // Build system prompt with context
    let enhancedPrompt = SYSTEM_PROMPT;

    // Include conversation history if available (RAG + recent messages fallback)
    if (hasHistory && context) {
      enhancedPrompt += `\n\nCONVERSATION HISTORY:
Below is our previous conversation context. Use this to:
- Reference what we discussed earlier when I ask about it
- Build upon previous analysis instead of starting fresh
- Maintain continuity in our discussion

⚠️ WARNING: Portfolio holdings information in conversation history may be OUTDATED or INCORRECT. Before discussing ANY holdings, you MUST call get_portfolios to verify current positions. DO NOT trust holdings mentions in conversation history.

${context}`;
    }

    if (ragSearchResults) {
      enhancedPrompt += ragSearchResults;
    }

    // Store user message
    try {
      const messageId = crypto.randomUUID();
      await fetch(`${BASE_URL}/api/rag/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id,
          type: 'conversation',
          document: {
            id: messageId,
            text: message,
            metadata: {
              role: 'user',
              timestamp: new Date().toISOString(),
            },
          },
        }),
      });
    } catch (error) {
      console.error('Failed to store user message:', error);
    }

    // Progressive Token Allocation: Detect complex visualization requests
    const vizCount = (message.match(/visualization|chart|graph|plot|table|pie/gi) || []).length;
    const hasMultipleVizRequest = vizCount >= 3 || message.includes('all') && message.includes('visualization');

    if (hasMultipleVizRequest) {
      console.log(`[Chat API] Detected complex visualization request (${vizCount} viz keywords) - using optimized prompt`);

      // Add optimization hint to system prompt
      enhancedPrompt += `

IMPORTANT: Generate visualizations ONE AT A TIME, ensuring each is complete before starting the next.
- Focus on quality over quantity
- If unsure about token limits, prioritize the most important 2-3 visualizations
- Each visualization must be COMPLETE: all brackets closed, all arrays filled, all objects valid
- It's better to show 2 complete visualizations than 5 incomplete ones`;
    }

    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        let fullResponse = '';
        let messages: Anthropic.MessageParam[] = [{ role: 'user', content: message }];
        let hasError = false;

        try {
          // Main loop for handling tool use
          let maxIterations = 5; // Prevent infinite loops
          let finalTextResponse = '';

          while (maxIterations-- > 0) {
            // Call LLM API
            const response = await anthropic.messages.create({
              model,
              max_tokens: 128000, // Maximum for GLM-4 via Z.AI proxy
              system: enhancedPrompt,
              messages,
              tools: TOOLS,
            });

            console.log(`[Chat API] LLM API returned ${response.content.length} content blocks`);

            // Check if Claude wants to use tools
            const toolUseBlocks = response.content.filter(
              (block): block is Anthropic.ToolUseBlock => block.type === 'tool_use'
            );

            if (toolUseBlocks.length === 0) {
              // No tool use - collect the text response for validation
              for (const block of response.content) {
                if (block.type === 'text') {
                  finalTextResponse += block.text;
                }
              }
              console.log(`[Chat API] No tools used - collected ${finalTextResponse.length} characters of text`);
              console.log(`[Chat API] Response preview: ${finalTextResponse.substring(0, 100)}...`);

              // Early validation: check for obvious truncation patterns before main validation
              const { detectTruncation } = await import('@/utils/parsers/vizExtractor');
              const vizMatches = finalTextResponse.match(/!\[viz:(\w+)\]\(/g) || [];
              console.log(`[Chat API] Found ${vizMatches.length} visualization(s) in response`);

              if (vizMatches.length >= 3) {
                // Multiple visualizations detected - warn about potential truncation
                const truncatedCheck = detectTruncation(finalTextResponse.slice(-500)); // Check last 500 chars
                if (truncatedCheck.isTruncated) {
                  console.warn(`[Chat API] ⚠️ Early warning: Response may be truncated (${truncatedCheck.reason})`);
                  controller.enqueue(
                    encoder.encode(
                      `data: ${JSON.stringify({
                        validation_warning: {
                          message: `⚠️ Response may be incomplete - auto-regeneration will be attempted if needed`,
                        },
                      })}\n\n`
                    )
                  );
                }
              }

              break;
            }

            // Execute tools and get results
            const toolResults: Anthropic.ToolResultBlockParam[] = [];

            for (const toolUse of toolUseBlocks) {
              // Send tool start notification to client
              controller.enqueue(
                encoder.encode(
                  `data: ${JSON.stringify({
                    tool_start: {
                      name: toolUse.name,
                      input: toolUse.input,
                    },
                  })}\n\n`
                )
              );

              const result = await executeToolCall(toolUse.name, toolUse.input);

              // Format result content for LLM
              let content: string;
              if (result.error) {
                content = `Error: ${result.error}`;
              } else if (result.data) {
                // Send structured data as JSON for LLM to consolidate
                content = JSON.stringify(result.data);
              } else if (result.success !== undefined) {
                // Mutation operations - return success confirmation
                content = result.success ? 'Success' : 'Failed';
              } else {
                content = JSON.stringify(result);
              }

              toolResults.push({
                type: 'tool_result',
                tool_use_id: toolUse.id,
                content,
              });

              // Send tool use notification to client
              controller.enqueue(
                encoder.encode(
                  `data: ${JSON.stringify({
                    tool_use: {
                      name: toolUse.name,
                      input: toolUse.input,
                      result: result.success ? 'Success' : result.error || 'Failed',
                    },
                  })}\n\n`
                )
              );
            }

            // Add assistant response and tool results to conversation
            messages.push({ role: 'assistant', content: response.content });
            messages.push({ role: 'user', content: toolResults });
          }

          // Now validate the text response before streaming
          let validatedResponse = sanitizeLoneSurrogates(finalTextResponse);
          const originalResponse = validatedResponse; // Store original before error replacement for troubleshooting

          // Send validation progress event
          controller.enqueue(
            encoder.encode(
              `data: ${JSON.stringify({
                validation_start: {
                  message: 'Validating visualizations...',
                },
              })}\n\n`
            )
          );

          // Validate once and rely on auto-fix (no LLM regeneration)
          const validationResult = validateAndFixVisualizations(validatedResponse);

          if (validationResult.autoFixedCount > 0) {
            console.log(`[Chat API] Auto-fixed ${validationResult.autoFixedCount} visualization(s)`);
            // Send auto-fix notification
            controller.enqueue(
              encoder.encode(
                `data: ${JSON.stringify({
                  validation_progress: {
                    message: `Auto-fixed ${validationResult.autoFixedCount} visualization(s)`,
                  },
                })}\n\n`
              )
            );
          }

          if (!validationResult.isValid) {
            // Check if errors are due to truncation (auto-regeneratable)
            const truncatedErrors = validationResult.errors.filter(e => e.truncationDetected);
            const otherErrors = validationResult.errors.filter(e => !e.truncationDetected);

            if (truncatedErrors.length > 0) {
              console.log(`[Chat API] Detected ${truncatedErrors.length} truncated visualization(s) - attempting auto-regenerate`);

              controller.enqueue(
                encoder.encode(
                  `data: ${JSON.stringify({
                    validation_progress: {
                      message: `Auto-regenerating ${truncatedErrors.length} truncated visualization(s)...`,
                    },
                  })}\n\n`
                )
              );

              // Try to auto-regenerate truncated visualizations
              const regenerated = await attemptRegenerate(
                validatedResponse,
                truncatedErrors,
                anthropic,
                model,
                enhancedPrompt,
                messages
              );

              if (regenerated.success) {
                console.log(`[Chat API] Successfully regenerated ${regenerated.fixedCount} visualization(s)`);
                validatedResponse = regenerated.text;

                controller.enqueue(
                  encoder.encode(
                    `data: ${JSON.stringify({
                      validation_progress: {
                        message: `Successfully regenerated ${regenerated.fixedCount} visualization(s)`,
                      },
                    })}\n\n`
                  )
                );
              } else {
                console.warn(`[Chat API] Auto-regenerate failed, showing error markers for ${truncatedErrors.length} visualization(s)`);
              }
            }

            if (otherErrors.length > 0) {
              console.log(`[Chat API] Note: ${otherErrors.length} non-truncation error(s) - error markers will be shown`);
              controller.enqueue(
                encoder.encode(
                  `data: ${JSON.stringify({
                    validation_warning: {
                      message: `${otherErrors.length} visualization(s) have syntax errors`,
                    },
                  })}\n\n`
                )
              );
            }
          }

          validatedResponse = validationResult.fixedText;

          console.log(`[Chat API] About to stream ${validatedResponse.length} characters to client`);
          console.log(`[Chat API] Response preview: ${validatedResponse.substring(0, 100)}...`);

          // Stream the final validated response character by character for smooth UX
          for (const char of validatedResponse) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: char })}\n\n`));
            // Small delay for smooth streaming effect
            await new Promise(resolve => setTimeout(resolve, 5));
          }
          fullResponse = validatedResponse;

          console.log(`[Chat API] Finished streaming ${fullResponse.length} characters`);

          // Store assistant response (original LLM output, not error-replaced)
          try {
            const messageId = crypto.randomUUID();
            await fetch(`${BASE_URL}/api/rag/store`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id,
                type: 'conversation',
                document: {
                  id: messageId,
                  text: originalResponse, // Store original for troubleshooting
                  metadata: {
                    role: 'assistant',
                    timestamp: new Date().toISOString(),
                  },
                },
              }),
            });
          } catch (error) {
            console.error('Failed to store assistant message:', error);
          }
        } catch (error: any) {
          console.error('Chat API error:', error);
          hasError = true;
          // Send error as message instead of using controller.error()
          const errorMsg = error?.message || 'An error occurred';
          fullResponse += `\n\n[Error: ${errorMsg}]`;
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: `\n\n[Error: ${errorMsg}]` })}\n\n`));
        } finally {
          // Always send DONE signal
          controller.enqueue(encoder.encode('data: [DONE]\n\n'));
          controller.close();
        }
      },
    });

    return new Response(readable, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Chat error:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
