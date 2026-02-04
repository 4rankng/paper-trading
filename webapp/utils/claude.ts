import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || '',
  dangerouslyAllowBrowser: true, // Only for development; API calls should go through server
});

export interface StreamMessage {
  type: 'text' | 'error';
  content: string;
}

export interface StreamOptions {
  systemPrompt?: string;
  context?: string;
}

export async function* streamClaudeResponse(
  message: string,
  options: StreamOptions = {}
): AsyncGenerator<StreamMessage> {
  const { systemPrompt = '', context = '' } = options;

  try {
    const systemMessage = context
      ? `${systemPrompt}\n\nRelevant context from conversation history:\n${context}`
      : systemPrompt;

    const stream = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 4096,
      system: systemMessage || undefined,
      messages: [{ role: 'user', content: message }],
      stream: true,
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        yield {
          type: 'text',
          content: event.delta.text,
        };
      }
    }
  } catch (error) {
    console.error('Claude API error:', error);
    if (error instanceof Error) {
      yield {
        type: 'error',
        content: `Error: ${error.message}`,
      };
    } else {
      yield {
        type: 'error',
        content: 'An unknown error occurred',
      };
    }
  }
}

export async function sendClaudeMessage(
  message: string,
  options: StreamOptions = {}
): Promise<string> {
  let fullResponse = '';

  for await (const chunk of streamClaudeResponse(message, options)) {
    if (chunk.type === 'text') {
      fullResponse += chunk.content;
    } else if (chunk.type === 'error') {
      throw new Error(chunk.content);
    }
  }

  return fullResponse;
}
