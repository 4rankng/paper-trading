import { NextRequest, NextResponse } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
  baseURL: process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com',
});

const SYSTEM_PROMPT = `You are a financial advisor and equity research specialist. You provide institutional-grade research and reasoned investment recommendations.

When asked to regenerate a visualization, you MUST:
1. Generate ONLY the specific visualization type requested
2. Use the exact format: ![viz:type]({...})
3. Ensure ALL JSON is complete and properly closed
4. Double-check bracket matching: every { must have }, every [ must have ]
5. No trailing commas inside objects/arrays
6. Provide complete data (no truncated arrays or objects)

Visualization types:
- table: {"type":"table","columns":[...],"rows":[[...],...]}
- chart: {"type":"chart","chartType":"line"/"bar"/"scatter",...}
- pie: {"type":"pie","slices":[{"label":...,"value":...},...]}

CRITICAL: The response must contain ONLY the visualization markdown, no additional text.`;

export async function POST(request: NextRequest) {
  try {
    const { vizType, userMessage, session_id } = await request.json();

    if (!vizType || !userMessage || !session_id) {
      return NextResponse.json(
        { error: 'Missing required fields: vizType, userMessage, session_id' },
        { status: 400 }
      );
    }

    console.log(`[Regenerate API] Regenerating ${vizType} for session ${session_id}`);

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 8192,
      system: SYSTEM_PROMPT,
      messages: [{
        role: 'user',
        content: `The user originally asked: "${userMessage}"

Please regenerate ONLY the ${vizType} visualization with complete, properly formatted JSON. Respond with just the visualization markdown (no additional text).`,
      }],
    });

    let regeneratedContent = '';
    for (const block of response.content) {
      if (block.type === 'text') {
        regeneratedContent += block.text;
      }
    }

    console.log(`[Regenerate API] Generated ${regeneratedContent.length} characters`);

    return NextResponse.json({
      success: true,
      content: regeneratedContent,
    });

  } catch (error: any) {
    console.error('[Regenerate API] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to regenerate visualization' },
      { status: 500 }
    );
  }
}
