import { VizCommand, ParsedViz, VizType } from '@/types/visualizations';

// Match viz markdown: ![viz:type](...)
const VIZ_REGEX = /!\[viz:(\w+)\]\(/g;

// Extract complete JSON by matching parentheses
function extractJSON(text: string, startIndex: number): { json: string; endIndex: number } | null {
  let parenCount = 1; // Start at 1 because we've already seen the opening (
  let i = startIndex;
  let inString = false;
  let escapeNext = false;

  while (i < text.length) {
    const char = text[i];

    if (escapeNext) {
      escapeNext = false;
      i++;
      continue;
    }

    if (char === '\\') {
      escapeNext = true;
      i++;
      continue;
    }

    if (char === '"') {
      inString = !inString;
      i++;
      continue;
    }

    if (!inString) {
      if (char === '(') {
        parenCount++;
      } else if (char === ')') {
        parenCount--;
        if (parenCount === 0) {
          // Found matching closing parenthesis
          const json = text.substring(startIndex, i);
          return { json, endIndex: i + 1 };
        }
      }
    }

    i++;
  }

  // No matching closing parenthesis found
  return null;
}

// Map chart type aliases to 'chart' type
const CHART_TYPE_ALIASES: Record<string, 'line' | 'bar' | 'scatter'> = {
  'line': 'line',
  'bar': 'bar',
  'scatter': 'scatter',
};

export function parseVizCommands(text: string): ParsedViz[] {
  const vizCommands: ParsedViz[] = [];
  let match;

  // Reset regex for new search
  VIZ_REGEX.lastIndex = 0;

  while ((match = VIZ_REGEX.exec(text)) !== null) {
    const typeStr = match[1];
    const startIndex = match.index;
    const openParenIndex = startIndex + match[0].length;

    // Extract JSON by matching parentheses
    const result = extractJSON(text, openParenIndex);

    if (!result) {
      console.log('[viz-parser] No matching closing parenthesis found for viz at', startIndex);
      continue;
    }

    const { json: jsonStr, endIndex } = result;

    try {
      const data = JSON.parse(jsonStr);
      const typeStrLower = typeStr.toLowerCase();

      // Handle chart type aliases (bar, line, scatter -> chart)
      if (CHART_TYPE_ALIASES[typeStrLower]) {
        const command: VizCommand = {
          type: 'chart',
          ...data,
          chartType: CHART_TYPE_ALIASES[typeStrLower],
        } as VizCommand;

        vizCommands.push({
          command,
          startIndex,
          endIndex,
        });
        console.log('[viz-parser] Parsed chart alias:', typeStr, 'at', startIndex, '-', endIndex);
        continue;
      }

      const type = typeStrLower as VizType;

      const command: VizCommand = {
        type,
        ...data,
      } as VizCommand;

      vizCommands.push({
        command,
        startIndex,
        endIndex,
      });
      console.log('[viz-parser] Parsed viz:', type, 'at', startIndex, '-', endIndex);
    } catch (error) {
      // Silently skip incomplete JSON during streaming - this is expected
      // Only log actual parsing errors, not incomplete chunks
      if (!(error instanceof SyntaxError)) {
        console.error('Failed to parse visualization command:', error);
      } else {
        console.log('[viz-parser] Incomplete JSON, skipping...');
      }
    }
  }

  console.log('[viz-parser] Total viz commands found:', vizCommands.length);
  return vizCommands;
}

export function replaceVizsWithPlaceholders(
  text: string,
  parsedVizs: ParsedViz[]
): string {
  let result = text;

  // Replace from end to start to maintain correct indices
  parsedVizs
    .sort((a, b) => b.startIndex - a.startIndex)
    .forEach(({ startIndex, endIndex }, index) => {
      const placeholder = `__VIZ_${index}__`;
      result =
        result.substring(0, startIndex) + placeholder + result.substring(endIndex);
    });

  return result;
}

export function splitTextByVizs(
  text: string,
  parsedVizs: ParsedViz[]
): Array<{ type: 'text' | 'viz'; content: string; index?: number }> {
  const parts: Array<{ type: 'text' | 'viz'; content: string; index?: number }> = [];
  let lastIndex = 0;

  const sortedVizs = [...parsedVizs].sort((a, b) => a.startIndex - b.startIndex);

  sortedVizs.forEach((viz, i) => {
    if (viz.startIndex > lastIndex) {
      parts.push({
        type: 'text',
        content: text.substring(lastIndex, viz.startIndex),
      });
    }
    parts.push({
      type: 'viz',
      content: '',
      index: i,
    });
    lastIndex = viz.endIndex;
  });

  if (lastIndex < text.length) {
    parts.push({
      type: 'text',
      content: text.substring(lastIndex),
    });
  }

  return parts;
}
