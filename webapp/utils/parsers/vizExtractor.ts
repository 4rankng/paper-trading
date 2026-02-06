import { isJSONComplete } from './vizTokenizer';
import { autoFixVisualization } from './vizFixer';

/**
 * Detect if JSON appears to be truncated (LLM response cut off mid-generation)
 * Returns: { isTruncated, confidence, reason }
 */
export function detectTruncation(jsonStr: string): { isTruncated: boolean; confidence: number; reason?: string } {
  const trimmed = jsonStr.trim();

  // High confidence truncation patterns
  if (trimmed.endsWith(',')) {
    return { isTruncated: true, confidence: 0.9, reason: 'Ends with comma - more items expected' };
  }

  if (trimmed.endsWith('"')) {
    return { isTruncated: true, confidence: 0.7, reason: 'Ends with open quote' };
  }

  if (trimmed.match(/:\s*\[?\s*$/)) {
    return { isTruncated: true, confidence: 0.95, reason: 'Empty property value' };
  }

  if (trimmed.match(/\[\s*\{?[^}]*$/)) {
    return { isTruncated: true, confidence: 0.85, reason: 'Incomplete object in array' };
  }

  // Check for unbalanced brackets WITH substantial content
  const openBraces = (trimmed.match(/\{/g) || []).length;
  const closeBraces = (trimmed.match(/\}/g) || []).length;
  const openBrackets = (trimmed.match(/\[/g) || []).length;
  const closeBrackets = (trimmed.match(/\]/g) || []).length;

  const hasContent = trimmed.length > 50; // Substantial content but unbalanced

  if (hasContent && (openBraces > closeBraces || openBrackets > closeBrackets)) {
    return {
      isTruncated: true,
      confidence: 0.8,
      reason: `Unbalanced brackets (${openBraces - closeBraces} unclosed braces, ${openBrackets - closeBrackets} unclosed brackets) with ${trimmed.length} chars`
    };
  }

  return { isTruncated: false, confidence: 0 };
}

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
 * Extract JSON by balancing brackets, not by looking for literal )
 * This works even if LLM forgets the closing parenthesis
 */
export function extractJSON(text: string, startIndex: number, vizType?: string): { json: string | null; endIndex: number } | null {
  let braceDepth = 0; // Track { } depth
  let bracketDepth = 0; // Track [ ] depth
  let i = startIndex;
  let inString = false;
  let escapeNext = false;
  let firstChar = text.charAt(startIndex);

  // If we start with { or [, we're looking for balanced JSON
  if (firstChar !== '{' && firstChar !== '[') {
    return null; // Not JSON
  }

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
      if (char === '{') braceDepth++;
      else if (char === '}') braceDepth--;
      else if (char === '[') bracketDepth++;
      else if (char === ']') bracketDepth--;
      else if (char === ')') {
        // Found closing ) - extract JSON and auto-fix it
        let json = text.substring(startIndex, i);
        const fixResult = autoFixVisualization(json, vizType ?? 'unknown');
        if (isJSONComplete(fixResult.fixed)) {
          try {
            JSON.parse(fixResult.fixed);
            return { json: fixResult.fixed, endIndex: i + 1 };
          } catch {
            return { json: null, endIndex: i + 1 };
          }
        }
      }

      // Check if we've closed all braces and brackets - we found the end of JSON
      // (This handles cases where JSON is complete but no closing ) exists)
      if (braceDepth === 0 && bracketDepth === 0 && i > startIndex) {
        let json = text.substring(startIndex, i + 1);
        const fixResult = autoFixVisualization(json, vizType ?? 'unknown');
        if (isJSONComplete(fixResult.fixed)) {
          try {
            JSON.parse(fixResult.fixed);
            // Return the JSON, and point to after it (caller will skip the ) if it exists)
            return { json: fixResult.fixed, endIndex: i + 1 };
          } catch {
            return { json: null, endIndex: i + 1 };
          }
        }
      }
    }

    i++;
  }

  // If we reached end of text, try to salvage what we have and let auto-fixer balance it
  if (i > startIndex) {
    let json = text.substring(startIndex, i);
    const fixResult = autoFixVisualization(json, vizType ?? 'unknown');
    if (isJSONComplete(fixResult.fixed)) {
      try {
        JSON.parse(fixResult.fixed);
        return { json: fixResult.fixed, endIndex: i };
      } catch {
        return { json: null, endIndex: i };
      }
    }
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
 * For truncated visualizations, limits to the current line to avoid eating subsequent content
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

  // Find the end of the current line (don't eat subsequent content)
  const nextNewline = content.indexOf('\n', openParenIndex);
  if (nextNewline !== -1) {
    // Only go to end of current line, not include the newline itself
    return nextNewline;
  }

  // Last resort: limit to a reasonable amount (500 chars max)
  return Math.min(openParenIndex + 500, content.length);
}

/**
 * Check if a position range is already covered
 */
export function isCovered(start: number, end: number, coveredRanges: [number, number][]): boolean {
  return coveredRanges.some(([rangeStart, rangeEnd]) => {
    return start < rangeEnd && end > rangeStart;
  });
}
