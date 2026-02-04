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

const SYSTEM_PROMPT = `You are TermAI Explorer, a terminal-based financial AI assistant with access to REAL portfolio and market data.

CRITICAL RULES:
1. ALWAYS use the available tools to fetch REAL data before responding
2. NEVER make up or fabricate numbers, holdings, prices, or financial information
3. When asked about portfolio/holdings, use get_portfolios() or get_portfolio() tools
4. When asked to add/update/remove positions, use the appropriate holding tools
5. When asked about trades, use get_trades() tool
6. When asked about watchlist, use get_watchlist() or add_to_watchlist() tools
7. When asked about a specific stock's analysis, use get_analytics() and get_news() tools

VISUALIZATION FORMAT:
To create visualizations, use this markdown format:
- Line chart: ![viz:chart]({"type":"line","chartType":"line","data":{"labels":["A","B","C"],"datasets":[{"label":"Data","data":[1,2,3]}]}})
- Bar chart: ![viz:chart]({"type":"bar","chartType":"bar","data":{"labels":["A","B","C"],"datasets":[{"label":"Data","data":[1,2,3]}]}})
- Pie chart: ![viz:pie]({"data":[{"label":"A","value":10},{"label":"B","value":20}],"options":{"title":"Distribution"}})
- Table: ![viz:table]({"headers":["Name","Value"],"rows":[["Item 1",100],["Item 2",200]]})

Keep responses concise and terminal-appropriate. Always cite data sources.`;

// Helper function to execute tool calls and return formatted results
async function executeToolCall(toolName: string, toolInput: any) {
  console.log('[Chat API] Executing tool:', toolName, 'with input:', toolInput);

  try {
    switch (toolName) {
      case 'get_portfolios': {
        const data = await fetch(`${BASE_URL}/api/portfolio`).then(r => r.json());
        // Format portfolio data into readable summary
        let summary = 'PORTFOLIOS:\n\n';
        for (const [id, portfolio] of Object.entries(data.portfolios || {})) {
          const p = portfolio as any;
          summary += `${id}: ${p.name}\n`;
          summary += `  Holdings: ${p.holdings?.length || 0}\n`;
          if (p.summary) {
            summary += `  Value: $${p.summary.holdings_value?.toLocaleString()}\n`;
            summary += `  P/L: $${p.summary.total_gain_loss?.toLocaleString()} (${p.summary.total_gain_loss_pct?.toFixed(2)}%)\n`;
          }
          if (p.holdings && p.holdings.length > 0) {
            summary += '  Positions:\n';
            p.holdings.forEach((h: any) => {
              summary += `    - ${h.ticker}: ${h.shares} shares @ $${h.avg_cost}`;
              if (h.current_price) {
                const pl = ((h.current_price - h.avg_cost) * h.shares).toFixed(2);
                const plPct = (((h.current_price - h.avg_cost) / h.avg_cost) * 100).toFixed(2);
                summary += ` | P/L: $${pl} (${plPct}%)`;
              }
              summary += '\n';
            });
          }
          summary += '\n';
        }
        if (data.cash) {
          summary += `Cash: $${data.cash.amount?.toLocaleString()}\n`;
        }
        return { success: true, summary };
      }

      case 'get_portfolio': {
        const data = await fetch(`${BASE_URL}/api/portfolio/${toolInput.id}`).then(r => r.json());
        const p = data;
        let summary = `${toolInput.id}: ${p.name}\n`;
        if (p.holdings && p.holdings.length > 0) {
          summary += 'Holdings:\n';
          p.holdings.forEach((h: any) => {
            summary += `  - ${h.ticker}: ${h.shares} shares @ $${h.avg_cost}`;
            if (h.current_price) {
              const pl = ((h.current_price - h.avg_cost) * h.shares).toFixed(2);
              const plPct = (((h.current_price - h.avg_cost) / h.avg_cost) * 100).toFixed(2);
              summary += ` | Current: $${h.current_price} | P/L: $${pl} (${plPct}%)`;
            }
            summary += '\n';
          });
        }
        if (p.summary) {
          summary += `\nTotal Value: $${p.summary.holdings_value?.toLocaleString()}\n`;
          summary += `Total P/L: $${p.summary.total_gain_loss?.toLocaleString()} (${p.summary.total_gain_loss_pct?.toFixed(2)}%)\n`;
        }
        return { success: true, summary };
      }

      case 'add_holding': {
        const result = await fetch(`${BASE_URL}/api/portfolio/${toolInput.portfolio_id}/holdings`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ticker: toolInput.ticker,
            shares: toolInput.shares,
            avg_cost: toolInput.avg_cost,
            current_price: toolInput.current_price,
          }),
        }).then(r => r.json());
        return result.success
          ? { success: true, summary: `Added ${toolInput.ticker} to ${toolInput.portfolio_id}: ${toolInput.shares} shares @ $${toolInput.avg_cost}` }
          : result;
      }

      case 'update_holding': {
        const result = await fetch(
          `${BASE_URL}/api/portfolio/${toolInput.portfolio_id}/holdings/${toolInput.ticker}`,
          {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(toolInput),
          }
        ).then(r => r.json());
        return result.success
          ? { success: true, summary: `Updated ${toolInput.ticker} in ${toolInput.portfolio_id}` }
          : result;
      }

      case 'remove_holding': {
        const result = await fetch(
          `${BASE_URL}/api/portfolio/${toolInput.portfolio_id}/holdings/${toolInput.ticker}`,
          { method: 'DELETE' }
        ).then(r => r.json());
        return result.success ? result : { success: true, summary: result.message };
      }

      case 'get_watchlist': {
        const data = await fetch(`${BASE_URL}/api/watchlist`).then(r => r.json());
        if (!data.entries || data.entries.length === 0) {
          return { success: true, summary: 'Watchlist is empty' };
        }
        let summary = `WATCHLIST (${data.entries.length} entries):\n`;
        data.entries.forEach((e: any) => {
          summary += `  - ${e.ticker}`;
          if (e.strategy) summary += ` [${e.strategy}]`;
          if (e.notes) summary += `: ${e.notes}`;
          if (e.target_entry) summary += ` | Entry: $${e.target_entry}`;
          if (e.target_exit) summary += ` | Exit: $${e.target_exit}`;
          summary += '\n';
        });
        return { success: true, summary };
      }

      case 'add_to_watchlist': {
        const result = await fetch(`${BASE_URL}/api/watchlist`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(toolInput),
        }).then(r => r.json());
        return result.success
          ? { success: true, summary: `Added ${toolInput.ticker} to watchlist` }
          : result;
      }

      case 'get_trades': {
        const params = new URLSearchParams();
        if (toolInput.ticker) params.set('ticker', toolInput.ticker);
        if (toolInput.portfolio) params.set('portfolio', toolInput.portfolio);
        const data = await fetch(`${BASE_URL}/api/trades?${params}`).then(r => r.json());
        if (!data.trades || data.trades.length === 0) {
          return { success: true, summary: 'No trades found' };
        }
        let summary = `TRADES (${data.trades.length}):\n`;
        data.trades.slice(0, 20).forEach((t: any) => {
          summary += `  ${t.timestamp} | ${t.portfolio} | ${t.action} ${t.ticker} ${t.shares} @ $${t.price}\n`;
        });
        if (data.trades.length > 20) {
          summary += `  ... and ${data.trades.length - 20} more\n`;
        }
        return { success: true, summary };
      }

      case 'log_trade': {
        const result = await fetch(`${BASE_URL}/api/trades`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(toolInput),
        }).then(r => r.json());
        return result.success
          ? { success: true, summary: `Logged ${toolInput.action} ${toolInput.ticker}: ${toolInput.shares} shares @ $${toolInput.price}` }
          : result;
      }

      case 'get_analytics': {
        const data = await fetch(`${BASE_URL}/api/analytics/${toolInput.ticker}`).then(r => r.json());
        let summary = `${toolInput.ticker} ANALYTICS:\n`;
        if (data.technical) summary += `\nTechnical:\n${data.technical.substring(0, 300)}...\n`;
        if (data.fundamental) summary += `\nFundamental:\n${data.fundamental.substring(0, 300)}...\n`;
        if (data.thesis) summary += `\nThesis:\n${data.thesis.substring(0, 300)}...\n`;
        return { success: true, summary };
      }

      case 'update_analytics': {
        const result = await fetch(`${BASE_URL}/api/analytics/${toolInput.ticker}/${toolInput.type}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: toolInput.content }),
        }).then(r => r.json());
        return result.success
          ? { success: true, summary: `Updated ${toolInput.ticker} ${toolInput.type} analysis` }
          : result;
      }

      case 'get_news': {
        const params = new URLSearchParams();
        if (toolInput.limit) params.set('limit', Math.min(toolInput.limit, 10).toString());
        const data = await fetch(`${BASE_URL}/api/news/${toolInput.ticker}?${params}`).then(r => r.json());
        if (!data.articles || data.articles.length === 0) {
          return { success: true, summary: `No news found for ${toolInput.ticker}` };
        }
        let summary = `${toolInput.ticker} NEWS (${data.articles.length} articles):\n`;
        data.articles.slice(0, 5).forEach((a: any) => {
          summary += `  - ${a.date}: ${a.title || 'No title'}\n`;
        });
        return { success: true, summary };
      }

      case 'get_prices': {
        const params = new URLSearchParams();
        if (toolInput.limit) params.set('limit', Math.min(toolInput.limit, 5).toString());
        const data = await fetch(`${BASE_URL}/api/prices/${toolInput.ticker}?${params}`).then(r => r.json());
        if (!data.prices || data.prices.length === 0) {
          return { success: true, summary: `No price data for ${toolInput.ticker}` };
        }
        let summary = `${toolInput.ticker} PRICES:\n`;
        data.prices.slice(0, 5).forEach((p: any) => {
          summary += `  ${p.date}: O:$${p.open} H:$${p.high} L:$${p.low} C:$${p.close}\n`;
        });
        return { success: true, summary };
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
              } else if (result.summary) {
                content = result.summary;
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
