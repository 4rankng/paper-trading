import { isJSONComplete } from './vizTokenizer';
import { autoFixVisualization } from './vizFixer';

/**
 * Parse a markdown table and convert to viz:table format
 */
export function parseMarkdownTable(text: string, startIndex: number): {
  headers: string[];
  rows: string[][];
  endIndex: number;
} | null {
  const tableText = text.substring(startIndex);

  let i = 0;
  const lines: string[] = [];

  while (i < tableText.length) {
    let lineEnd = tableText.indexOf('\n', i);
    if (lineEnd === -1) lineEnd = tableText.length;

    const line = tableText.substring(i, lineEnd);
    const trimmed = line.trim();

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      lines.push(trimmed);
      i = lineEnd + 1;
    } else {
      break;
    }

    if (i < tableText.length && tableText[i] === '\n') {
      break;
    }
  }

  if (lines.length < 2) return null;

  const headerLine = lines[0];
  const headers = headerLine
    .split('|')
    .slice(1, -1)
    .map(h => h.trim())
    .filter(h => h.length > 0);

  if (!lines[1].includes('---')) return null;

  const rows: string[][] = [];
  for (let i = 2; i < lines.length; i++) {
    const row = lines[i]
      .split('|')
      .slice(1, -1)
      .map(cell => cell.trim())
      .filter(cell => cell.length > 0);

    if (row.length > 0) {
      rows.push(row);
    }
  }

  const endIndex = startIndex + lines.reduce((sum, line) => sum + line.length + 1, 0);

  return { headers, rows, endIndex };
}

/**
 * Extract complete JSON by matching parentheses
 */
export function extractJSON(text: string, startIndex: number): { json: string | null; endIndex: number } | null {
  let parenCount = 1;
  let i = startIndex;
  let inString = false;
  let escapeNext = false;
  let lastClosingParen = -1;

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
        lastClosingParen = i;

        if (parenCount === 0) {
          let json = text.substring(startIndex, i);

          if (!isJSONComplete(json)) {
            continue;
          }

          const fixResult = autoFixVisualization(json, 'unknown');

          try {
            JSON.parse(fixResult.fixed);
            return { json: fixResult.fixed, endIndex: i + 1 };
          } catch {
            return { json: null, endIndex: i + 1 };
          }
        }
      }
    }

    i++;
  }

  if (lastClosingParen > startIndex) {
    return { json: null, endIndex: lastClosingParen + 1 };
  }

  return null;
}

/**
 * Find proper closing parenthesis
 */
export function findProperClosingParen(content: string, openParenIndex: number): number {
  let braceCount = 0;
  let inString = false;
  let escapeNext = false;

  for (let i = openParenIndex + 1; i < content.length; i++) {
    const char = content[i];

    if (escapeNext) {
      escapeNext = false;
      continue;
    }

    if (char === '\\') {
      escapeNext = true;
      continue;
    }

    if (char === '"') {
      inString = !inString;
      continue;
    }

    if (!inString) {
      if (char === '{' || char === '[') {
        braceCount++;
      } else if (char === '}' || char === ']') {
        braceCount--;
      } else if (char === ')' && braceCount === 0) {
        return i;
      }
    }
  }

  return -1;
}

/**
 * Find the end of a visualization
 */
export function findVisualizationEnd(content: string, openParenIndex: number): number {
  const properEnd = findProperClosingParen(content, openParenIndex);
  if (properEnd !== -1) {
    return properEnd;
  }

  const nextViz = content.indexOf('![viz:', openParenIndex + 1);
  if (nextViz !== -1) {
    return nextViz;
  }

  const nextNewline = content.indexOf('\n', openParenIndex);
  if (nextNewline !== -1) {
    return nextNewline;
  }

  return Math.min(openParenIndex + 1000, content.length);
}

/**
 * Check if a position range is already covered
 */
export function isCovered(start: number, end: number, coveredRanges: [number, number][]): boolean {
  return coveredRanges.some(([rangeStart, rangeEnd]) => {
    return start < rangeEnd && end > rangeStart;
  });
}
