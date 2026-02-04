import { NextRequest } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';
import { Message } from '@/types';

// Support both direct Anthropic API and Z.AI proxy
const apiKey = process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN || '';
const baseUrl = process.env.ANTHROPIC_BASE_URL;

const anthropic = new Anthropic({
  apiKey,
  ...(baseUrl && { baseURL: baseUrl }),
});

export const runtime = 'nodejs';

const SYSTEM_PROMPT = `You are TermAI Explorer, a terminal-based AI assistant. You can respond with text and generate visualizations using a special syntax.

To create a visualization, use this format:
![viz:chart]({"type":"line","data":{"labels":["A","B","C"],"datasets":[{"label":"Data","data":[1,2,3]}]}})
![viz:table]({"headers":["Name","Value"],"rows":[["Item 1",100],["Item 2",200]]})
![viz:pie]({"data":[{"label":"A","value":10},{"label":"B","value":20}],"options":{"title":"Distribution"}})

Keep responses concise and terminal-appropriate. Use monospace-friendly formatting.`;

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
        `${process.env.NEXT_PUBLIC_WEBAPP_URL || 'http://localhost:3000'}/api/rag/query?session_id=${encodeURIComponent(session_id)}&query=${encodeURIComponent(message)}&limit=3`
      );
      if (ragResponse.ok) {
        const ragData = await ragResponse.json();
        context = ragData.context || '';
      }
    } catch (error) {
      console.error('Failed to fetch RAG context:', error);
    }

    // Fetch real data from filedb
    let dataContext = '';
    try {
      const dataResponse = await fetch(
        `${process.env.NEXT_PUBLIC_WEBAPP_URL || 'http://localhost:3000'}/api/data/query`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: message }),
        }
      );
      if (dataResponse.ok) {
        const dataData = await dataResponse.json();
        dataContext = dataData.context || '';
      }
    } catch (error) {
      console.error('Failed to fetch data context:', error);
    }

    // Build system prompt with context
    let enhancedPrompt = SYSTEM_PROMPT;

    if (context) {
      enhancedPrompt += `\n\nRelevant context from conversation history:\n${context}`;
    }

    if (dataContext) {
      enhancedPrompt += `\n\nRelevant data from filedb:\n${dataContext}\n\nIMPORTANT: Use this REAL data in your response. Do NOT make up or fabricate any numbers or holdings.`;
    }

    // Store user message
    try {
      await fetch(`${process.env.NEXT_PUBLIC_WEBAPP_URL || 'http://localhost:3000'}/api/rag/store`, {
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

    // Stream Claude response
    const stream = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      system: enhancedPrompt,
      messages: [{ role: 'user', content: message }],
      stream: true,
    });

    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        let fullResponse = '';

        try {
          for await (const event of stream) {
            if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
              const text = event.delta.text;
              fullResponse += text;
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text })}\n\n`));
            }
          }

          // Store assistant response
          try {
            await fetch(`${process.env.NEXT_PUBLIC_WEBAPP_URL || 'http://localhost:3000'}/api/rag/store`, {
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

          controller.enqueue(encoder.encode('data: [DONE]\n\n'));
          controller.close();
        } catch (error) {
          console.error('Streaming error:', error);
          controller.error(error);
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
