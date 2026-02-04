import { NextRequest } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';
import { Message } from '@/types';
import { config } from 'dotenv';
import { join } from 'path';

// Load environment variables from project root .env
const envPath = join(process.cwd(), '../.env');
config({ path: envPath });

// Support both direct Anthropic API and Z.AI proxy
const apiKey = process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN || '';
const baseUrl = process.env.ANTHROPIC_BASE_URL;

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
];

const SYSTEM_PROMPT = `You are TermAI Explorer, a financial AI assistant with access to REAL portfolio and market data.

CRITICAL RULES:
1. ALWAYS use the available tools to fetch REAL data before responding
2. NEVER make up or fabricate numbers, holdings, prices, or financial information
3. CONSOLIDATE and INTERPRET the data - then PRESENT WITH VISUALIZATIONS
4. NEVER use ASCII tables, terminal art, or markdown tables - USE THE PROVIDED VISUALIZATION FORMAT ONLY

FORBIDDEN FORMATS (DO NOT USE):
- ❌ ASCII tables with | and --- separators
- ❌ Markdown tables
- ❌ Box drawing characters
- ❌ Terminal art/borders

REQUIRED VISUALIZATION FORMAT:
Use ONLY these markdown formats for charts and tables:

1. LINE CHART - For trends over time (prices, portfolio value)
   ![viz:chart]({"type":"line","chartType":"line","data":{"labels":["Jan","Feb","Mar"],"datasets":[{"label":"Portfolio Value","data":[100000,105000,102000]}]},"options":{"title":"Portfolio Value Trend"}})

2. BAR CHART - For comparisons (holdings by value, P/L by stock)
   ![viz:chart]({"type":"bar","chartType":"bar","data":{"labels":["AAPL","MSFT","GOOGL"],"datasets":[{"label":"Holdings Value","data":[50000,30000,20000]}]},"options":{"title":"Holdings by Stock"}})

3. PIE CHART - For distributions (asset allocation, sector breakdown)
   ![viz:pie]({"data":[{"label":"CORE","value":127522},{"label":"AI_PICKS","value":13749}],"options":{"title":"Portfolio Allocation"}})

4. TABLE - For detailed data (holdings list, trade history)
   ![viz:table]({"headers":["Ticker","Shares","Value","P/L %"],"rows":[["AAPL",100,"$50,000","+12.5%"],["MSFT",50,"$30,000","+8.3%"]]})

WHEN TO USE EACH VISUALIZATION:
- LINE CHART: Time-series data, price history, portfolio growth over time
- BAR CHART: Comparing values across categories (holdings, P/L by ticker)
- PIE CHART: Parts-of-whole relationships (portfolio allocation, sector breakdown)
- TABLE: Detailed multi-column listings (holdings with all details, trade history)

RESPONSE STRUCTURE:
1. One sentence summary of the key insight
2. Visualization to present the data
3. 2-3 bullet points with observations or insights
4. No fluff, no ASCII art, just clean formatted visualizations

EXAMPLE GOOD RESPONSE:
"Your portfolio is down $49K (-28%). LAES is your biggest loser.

![viz:pie]({"data":[{"label":"CORE","value":127522},{"label":"AI_PICKS","value":15125}],"options":{"title":"Portfolio Allocation"}})

![viz:table]({"headers":["Ticker","Shares","Value","P/L %"],"rows":[["LAES",18000,"$81,000","-29.7%"],["WRD",2800,"$24,500","-20.5%"],["PONY",1400,"$22,022","-27.2%"]]})

• Core portfolio needs attention - all positions underwater
• Consider trimming losers or waiting for recovery"

Keep responses concise. Always cite data sources.`;

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
        return {
          success: true,
          data: {
            entries: data.entries?.map((e: any) => ({
              ticker: e.ticker,
              strategy: e.strategy,
              notes: e.notes,
              target_entry: e.target_entry,
              target_exit: e.target_exit,
              stop_loss: e.stop_loss,
              status: e.status,
            })) || [],
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
        const data = await safeFetch(`${BASE_URL}/api/prices/${toolInput.ticker}?${params}`);
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
      }

      default:
        return { error: `Unknown tool: ${toolName}` };
    }
  } catch (error: any) {
    console.error(`[Chat API] Tool execution error for ${toolName}:`, error);
    return { error: error.message || 'Tool execution failed' };
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
    try {
      const ragResponse = await fetch(
        `${BASE_URL}/api/rag/query?session_id=${encodeURIComponent(session_id)}&query=${encodeURIComponent(message)}&limit=3`
      );
      if (ragResponse.ok) {
        const ragData = await ragResponse.json();
        context = ragData.context || '';
      }
    } catch (error) {
      console.error('Failed to fetch RAG context:', error);
    }

    // Build system prompt with context
    let enhancedPrompt = SYSTEM_PROMPT;
    if (context) {
      enhancedPrompt += `\n\nRelevant context from conversation history:\n${context}`;
    }

    // Store user message
    try {
      await fetch(`${BASE_URL}/api/rag/store`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id,
          message: {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
          } as Message,
        }),
      });
    } catch (error) {
      console.error('Failed to store user message:', error);
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
          while (maxIterations-- > 0) {
            // Call Claude API
            const response = await anthropic.messages.create({
              model: 'claude-sonnet-4-20250514',
              max_tokens: 4096,
              system: enhancedPrompt,
              messages,
              tools: TOOLS,
            });

            // Check if Claude wants to use tools
            const toolUseBlocks = response.content.filter(
              (block): block is Anthropic.ToolUseBlock => block.type === 'tool_use'
            );

            if (toolUseBlocks.length === 0) {
              // No tool use, stream the text response
              for (const block of response.content) {
                if (block.type === 'text') {
                  const text = block.text;
                  fullResponse += text;
                  controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text })}\n\n`));
                }
              }
              break;
            }

            // Execute tools and get results
            const toolResults: Anthropic.ToolResultBlockParam[] = [];

            for (const toolUse of toolUseBlocks) {
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

          // Store assistant response
          try {
            await fetch(`${BASE_URL}/api/rag/store`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id,
                message: {
                  role: 'assistant',
                  content: fullResponse,
                  timestamp: new Date().toISOString(),
                } as Message,
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
