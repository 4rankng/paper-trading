import { VizCommand, ParsedViz, VizType } from '@/types/visualizations';

// Export error type for UI display
export interface VizParseError {
  startIndex: number;
  endIndex: number;
  type: string;
  error: string;
  hint: string;
}

// Match viz markdown: ![viz:type](...)
const VIZ_REGEX = /!\[viz:(\w+)\]\(/g;

// Match markdown tables: | Header | Header |
const MARKDOWN_TABLE_REGEX = /\|(?![\s\d-:]+\|)[^|\r\n]+(\|[^|\r\n]+)+\|[ \t]*\r?\n[ \t]*\|[\s\-:]+\|[\s\-:|]*\|[ \t]*\r?\n(?:[ \t]*\|(?![\s\-:]+)[^|\r\n]+(\|[^|\r\n]+)*\|[ \t]*\r?\n?)*/g;

// ============================================================================
// MULTI-PASS FIX SYSTEM
// ============================================================================

interface FixResult {
  fixed: string;
  wasFixed: boolean;
  warnings: string[];
}

interface Fix {
  index: number;
  action: 'add' | 'remove' | 'replace';
  char: string;
  length?: number;
}

/**
 * Sanitize string by removing lone surrogate characters that can't be encoded to UTF-8
 * Exported for use in other modules
 */
export function sanitizeLoneSurrogates(str: string): string {
  // Use Array.from to properly iterate by Unicode code points
  return Array.from(str)
    .filter(char => {
      const code = char.codePointAt(0)!;
      return code < 0xD800 || code > 0xDFFF;
    })
    .join('');
}

/**
 * Fix 1: Remove lone surrogate characters
 */
function fixSurrogateCharacters(json: string): FixResult {
  const warnings: string[] = [];
  const original = json;
  let fixed = sanitizeLoneSurrogates(json);

  if (fixed !== original) {
    // Count how many were removed
    const removed = original.length - fixed.length;
    warnings.push(`Removed ${removed} lone surrogate character(s)`);
  }

  return { fixed, wasFixed: fixed !== original, warnings };
}

/**
 * Fix 2: Remove trailing commas from objects and arrays
 */
function removeTrailingCommas(json: string): FixResult {
  const warnings: string[] = [];
  const fixed = json.replace(/,\s*}/g, '}').replace(/,\s*]/g, ']');
  const wasFixed = fixed !== json;
  if (wasFixed) warnings.push('Removed trailing commas');
  return { fixed, wasFixed, warnings };
}

/**
 * Fix 3: Remove duplicate keys (keeps last occurrence)
 * Uses regex-based approach for unparseable JSON
 */
function removeDuplicateKeys(json: string): FixResult {
  const warnings: string[] = [];
  const keyPattern = /"([^"]+)"\s*:/g;
  const seenKeys = new Map<string, { start: number; end: number }>();
  const duplicates: Array<{ start: number; end: number }> = [];

  let match;
  while ((match = keyPattern.exec(json)) !== null) {
    const key = match[1];
    const start = match.index;
    const end = keyPattern.lastIndex;

    if (seenKeys.has(key)) {
      // Mark earlier occurrence for removal
      duplicates.push(seenKeys.get(key)!);
    }
    seenKeys.set(key, { start, end });
  }

  if (duplicates.length === 0) {
    return { fixed: json, wasFixed: false, warnings };
  }

  // Find complete key-value pairs to remove (from end to start)
  const toRemove: Array<{ start: number; end: number }> = [];
  for (const dup of duplicates) {
    let braceDepth = 0;
    let inString = false;
    let escapeNext = false;

    for (let i = dup.end; i < json.length; i++) {
      const char = json[i];

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
        if (char === '{' || char === '[') braceDepth++;
        else if (char === '}' || char === ']') braceDepth--;
        else if (braceDepth === 0 && (char === ',' || char === '}' || char === ']')) {
          toRemove.push({ start: dup.start, end: i });
          break;
        }
      }
    }
  }

  // Apply removals from end to start
  let fixed = json;
  toRemove.sort((a, b) => b.end - a.end);
  for (const rem of toRemove) {
    fixed = fixed.substring(0, rem.start) + fixed.substring(rem.end);
  }

  warnings.push(`Removed ${toRemove.length} duplicate key(s)`);
  return { fixed, wasFixed: true, warnings };
}

/**
 * Fix 4: Escape unescaped quotes in strings
 */
function escapeQuotes(json: string): FixResult {
  const warnings: string[] = [];
  const fixed: string[] = [];
  let inString = false;
  let escapeNext = false;
  let wasFixed = false;

  for (let i = 0; i < json.length; i++) {
    const char = json[i];

    if (escapeNext) {
      fixed.push(char);
      escapeNext = false;
      continue;
    }

    if (char === '\\') {
      fixed.push(char);
      escapeNext = true;
      continue;
    }

    if (char === '"') {
      // Check if this quote needs escaping
      const prevChar = i > 0 ? json[i - 1] : '';
      const nextChar = i < json.length - 1 ? json[i + 1] : '';

      // Quote after : or { or , is opening string
      if (inString) {
        // Closing quote - should be preceded by non-backslash or even number of backslashes
        if (prevChar === '\\' && json[i - 2] !== '\\\\') {
          // Already escaped properly
          fixed.push(char);
        } else {
          fixed.push(char);
        }
        inString = false;
      } else {
        // Opening quote
        fixed.push(char);
        inString = true;
      }
    } else {
      fixed.push(char);
    }
  }

  return { fixed: fixed.join(''), wasFixed, warnings };
}

/**
 * Fix 5: Balance brackets by tracking them properly
 */
function balanceBrackets(json: string): FixResult {
  const warnings: string[] = [];
  const stack: Array<{ char: string; index: number }> = [];
  const fixes: Fix[] = [];
  let inString = false;
  let escapeNext = false;

  for (let i = 0; i < json.length; i++) {
    const char = json[i];

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
    if (inString) continue;

    if (char === '{' || char === '[') {
      stack.push({ char, index: i });
    } else if (char === '}' || char === ']') {
      const expected = char === '}' ? '{' : '[';

      if (stack.length === 0) {
        fixes.push({ index: i, action: 'remove', char });
      } else if (stack[stack.length - 1].char !== expected) {
        fixes.push({ index: i, action: 'remove', char });
        const correctCloser = stack[stack.length - 1].char === '{' ? '}' : ']';
        fixes.push({ index: i, action: 'add', char: correctCloser });
        stack.pop();
      } else {
        stack.pop();
      }
    }
  }

  // Add missing closers at end
  while (stack.length > 0) {
    const open = stack.pop()!;
    const closer = open.char === '{' ? '}' : ']';
    fixes.push({ index: json.length, action: 'add', char: closer });
  }

  if (fixes.length === 0) {
    return { fixed: json, wasFixed: false, warnings };
  }

  const result = applyFixes(json, fixes);
  warnings.push(`Fixed ${fixes.length} bracket imbalance(s)`);
  return { fixed: result.fixed, wasFixed: true, warnings: [...warnings, ...result.warnings] };
}

/**
 * Fix 6: Add missing commas between values
 */
function addMissingCommas(json: string): FixResult {
  const warnings: string[] = [];
  const fixes: Fix[] = [];
  let inString = false;
  let escapeNext = false;
  let braceDepth = 0;
  let bracketDepth = 0;

  for (let i = 0; i < json.length - 1; i++) {
    const char = json[i];
    const nextChar = json[i + 1];

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
    if (inString) continue;

    if (char === '{') braceDepth++;
    if (char === '}') braceDepth--;
    if (char === '[') bracketDepth++;
    if (char === ']') bracketDepth--;

    // Check for missing comma: value followed by " or { or [
    if (braceDepth > 0 || bracketDepth > 0) {
      if ((char === '"' || char === '}' || char === ']') &&
          (nextChar === '"' || nextChar === '{' || nextChar === '[')) {
        // Need a comma
        fixes.push({ index: i + 1, action: 'add', char: ',' });
      }
    }
  }

  if (fixes.length === 0) {
    return { fixed: json, wasFixed: false, warnings };
  }

  const result = applyFixes(json, fixes);
  warnings.push(`Added ${fixes.length} missing comma(s)`);
  return { fixed: result.fixed, wasFixed: true, warnings: [...warnings, ...result.warnings] };
}

/**
 * Apply fixes from end to start to avoid index drift
 */
function applyFixes(json: string, fixes: Fix[]): FixResult {
  const sorted = [...fixes].sort((a, b) => b.index - a.index);
  const warnings: string[] = [];

  let result = json;
  for (const fix of sorted) {
    if (fix.action === 'remove') {
      result = result.slice(0, fix.index) + result.slice(fix.index + 1);
    } else if (fix.action === 'add') {
      result = result.slice(0, fix.index) + fix.char + result.slice(fix.index);
    } else if (fix.action === 'replace') {
      result = result.slice(0, fix.index) + fix.char + result.slice(fix.index + (fix.length || 1));
    }
  }

  return { fixed: result, wasFixed: true, warnings };
}

/**
 * Fix 7: Schema-aware fixes for specific viz types
 */
function fixSchemaIssues(json: string, vizType: string): FixResult {
  const warnings: string[] = [];

  try {
    const obj = JSON.parse(json);
    const fixed = { ...obj };

    // Fix chart type mistakes
    if (vizType === 'chart' || vizType === 'line' || vizType === 'bar') {
      if (fixed.type === 'line' || fixed.type === 'bar') {
        const chartType = fixed.type;
        delete fixed.type;
        fixed.chartType = chartType;
        if (!fixed.type) fixed.type = 'chart';
        warnings.push(`Converted type:"${chartType}" to chartType:"${chartType}"`);
      }
      if (!fixed.type) fixed.type = 'chart';
    }

    // Ensure required fields for tables
    if (vizType === 'table') {
      if (!fixed.type) fixed.type = 'table';
      if (fixed.columns && !fixed.headers) {
        fixed.headers = fixed.columns;
        delete fixed.columns;
        warnings.push('Renamed "columns" to "headers"');
      }
      if (!fixed.headers) {
        fixed.headers = [];
        warnings.push('Added empty headers array');
      }
      if (!fixed.rows) {
        fixed.rows = [];
        warnings.push('Added empty rows array');
      }
    }

    // Ensure required fields for charts
    if (fixed.type === 'chart') {
      if (!fixed.chartType) {
        fixed.chartType = 'bar';
        warnings.push('Added default chartType: "bar"');
      }
      if (!fixed.data) {
        fixed.data = {};
        warnings.push('Added empty data object');
      }
    }

    return {
      fixed: JSON.stringify(fixed),
      wasFixed: warnings.length > 0,
      warnings
    };
  } catch {
    return { fixed: json, wasFixed: false, warnings };
  }
}

/**
 * Main multi-pass auto-fix function
 */
function autoFixVisualization(jsonStr: string, vizType: string): FixResult {
  const allWarnings: string[] = [];
  let current = jsonStr;
  let wasFixed = false;

  // Define passes in order
  const passes: Array<{ name: string; fn: (s: string) => FixResult }> = [
    { name: 'surrogate-chars', fn: fixSurrogateCharacters },
    { name: 'trailing-commas', fn: removeTrailingCommas },
    { name: 'duplicate-keys', fn: removeDuplicateKeys },
    { name: 'bracket-balance', fn: balanceBrackets },
    { name: 'missing-commas', fn: addMissingCommas },
    { name: 'schema-validation', fn: (s: string) => fixSchemaIssues(s, vizType) },
  ];

  // Run each pass
  for (const pass of passes) {
    try {
      const result = pass.fn(current);
      if (result.wasFixed) {
        wasFixed = true;
        current = result.fixed;
        allWarnings.push(`[${pass.name}] ${result.warnings.join(', ')}`);
      }
      allWarnings.push(...result.warnings);
    } catch (e) {
      allWarnings.push(`[${pass.name}] Pass failed: ${(e as Error).message}`);
    }
  }

  // Final validation
  try {
    JSON.parse(current);
  } catch (e) {
    allWarnings.push(`Validation failed: ${(e as Error).message}`);
  }

  return { fixed: current, wasFixed, warnings: allWarnings };
}

// ============================================================================
// TOKEN-BASED JSON COMPLETION CHECK
// ============================================================================

interface Token {
  type: 'bracket' | 'punctuation' | 'string' | 'literal' | 'whitespace';
  value: string;
  index: number;
}

/**
 * Tokenize JSON for more accurate analysis
 */
function tokenizeJSON(json: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;

  while (i < json.length) {
    const char = json[i];

    if (/\s/.test(char)) {
      const start = i;
      while (i < json.length && /\s/.test(json[i])) i++;
      tokens.push({ type: 'whitespace', value: json.substring(start, i), index: start });
      continue;
    }

    if (char === '"') {
      const start = i;
      i++; // Skip opening quote
      let escapeNext = false;
      while (i < json.length) {
        if (escapeNext) {
          escapeNext = false;
          i++;
          continue;
        }
        if (json[i] === '\\') {
          escapeNext = true;
          i++;
          continue;
        }
        if (json[i] === '"') {
          i++;
          break;
        }
        i++;
      }
      tokens.push({ type: 'string', value: json.substring(start, i), index: start });
      continue;
    }

    if (char === '{' || char === '[' || char === '}' || char === ']') {
      tokens.push({ type: 'bracket', value: char, index: i });
      i++;
      continue;
    }

    if (char === ':' || char === ',') {
      tokens.push({ type: 'punctuation', value: char, index: i });
      i++;
      continue;
    }

    // Literal (number, boolean, null)
    const start = i;
    while (i < json.length && /[^\s{}[\]:,"]/.test(json[i])) i++;
    tokens.push({ type: 'literal', value: json.substring(start, i), index: start });
  }

  return tokens;
}

/**
 * Check if JSON appears complete using token-based analysis
 */
function isJSONComplete(jsonStr: string): boolean {
  const trimmed = jsonStr.trim();

  // Quick check: must end with } or ]
  if (!trimmed.endsWith('}') && !trimmed.endsWith(']')) {
    return false;
  }

  const tokens = tokenizeJSON(trimmed);

  // Check bracket balance
  let braceCount = 0;
  let bracketCount = 0;
  for (const token of tokens) {
    if (token.type === 'bracket') {
      if (token.value === '{') braceCount++;
      if (token.value === '}') braceCount--;
      if (token.value === '[') bracketCount++;
      if (token.value === ']') bracketCount--;
    }
  }
  if (braceCount !== 0 || bracketCount !== 0) return false;

  // Check string balance (even number of unescaped quotes)
  let stringCount = 0;
  for (const token of tokens) {
    if (token.type === 'string') stringCount++;
  }
  if (stringCount % 2 !== 0) return false;

  // Check for trailing comma (last non-whitespace before } or ] shouldn't be ,)
  const nonWsTokens = tokens.filter(t => t.type !== 'whitespace');
  if (nonWsTokens.length >= 2) {
    const lastToken = nonWsTokens[nonWsTokens.length - 1];
    const secondLast = nonWsTokens[nonWsTokens.length - 2];
    if ((lastToken.value === '}' || lastToken.value === ']') && secondLast.value === ',') {
      return false;
    }
  }

  return true;
}

// ============================================================================
// ORIGINAL PARSING FUNCTIONS (Enhanced)
// ============================================================================

/**
 * Parse a markdown table and convert to viz:table format
 */
function parseMarkdownTable(text: string, startIndex: number): {
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
function extractJSON(text: string, startIndex: number): { json: string | null; endIndex: number } | null {
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

          // Apply multi-pass auto-fix
          const fixResult = autoFixVisualization(json, 'unknown');

          // Try to validate
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

// Map chart type aliases
const CHART_TYPE_ALIASES: Record<string, 'line' | 'bar' | 'scatter'> = {
  'line': 'line',
  'bar': 'bar',
  'scatter': 'scatter',
};

/**
 * Check if a position range is already covered
 */
function isCovered(start: number, end: number, coveredRanges: [number, number][]): boolean {
  return coveredRanges.some(([rangeStart, rangeEnd]) => {
    return start < rangeEnd && end > rangeStart;
  });
}

/**
 * Find the end of a visualization
 */
function findVisualizationEnd(content: string, openParenIndex: number): number {
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
 * Find proper closing parenthesis
 */
function findProperClosingParen(content: string, openParenIndex: number): number {
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

export function parseVizCommands(text: string): { vizs: ParsedViz[]; errors: VizParseError[] } {
  const vizCommands: ParsedViz[] = [];
  const errors: VizParseError[] = [];
  const coveredRanges: [number, number][] = [];

  let match;
  VIZ_REGEX.lastIndex = 0;

  while ((match = VIZ_REGEX.exec(text)) !== null) {
    const typeStr = match[1];
    const startIndex = match.index;
    const openParenIndex = startIndex + match[0].length;

    const result = extractJSON(text, openParenIndex);

    if (!result) {
      const endIndex = findVisualizationEnd(text, openParenIndex);

      errors.push({
        startIndex,
        endIndex,
        type: typeStr,
        error: 'Could not find matching closing parenthesis',
        hint: 'Check that your JSON is properly closed with })',
      });
      continue;
    }

    const { json: jsonStr, endIndex } = result;

    if (jsonStr === null) {
      errors.push({
        startIndex,
        endIndex,
        type: typeStr,
        error: 'Invalid JSON syntax',
        hint: 'Check for missing quotes, commas, or mismatched brackets',
      });
      continue;
    }

    let finalJsonStr = jsonStr;
    let wasAutoFixed = false;
    let fixDescription = '';

    try {
      const data = JSON.parse(jsonStr);
      const typeStrLower = typeStr.toLowerCase();

      if (Array.isArray(data)) {
        throw new Error('Data must be an object with "headers" and "rows" keys, not an array');
      }

      if (CHART_TYPE_ALIASES[typeStrLower]) {
        const { type, ...dataWithoutType } = data as any;
        const command: VizCommand = {
          type: 'chart',
          ...dataWithoutType,
          chartType: CHART_TYPE_ALIASES[typeStrLower],
        } as VizCommand;

        vizCommands.push({
          command,
          startIndex,
          endIndex,
        });
        coveredRanges.push([startIndex, endIndex]);
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
        autoFixed: wasAutoFixed,
        fixDescription: wasAutoFixed ? fixDescription : undefined,
      });
      coveredRanges.push([startIndex, endIndex]);
    } catch (error: any) {
      // Try auto-fix with new multi-pass system
      const autoFixResult = autoFixVisualization(jsonStr, typeStr);

      if (autoFixResult.wasFixed) {
        try {
          const data = JSON.parse(autoFixResult.fixed);
          const typeStrLower = typeStr.toLowerCase();

          if (CHART_TYPE_ALIASES[typeStrLower]) {
            const { type, ...dataWithoutType } = data as any;
            const command: VizCommand = {
              type: 'chart',
              ...dataWithoutType,
              chartType: CHART_TYPE_ALIASES[typeStrLower],
            } as VizCommand;

            vizCommands.push({
              command,
              startIndex,
              endIndex,
              autoFixed: true,
              fixDescription: autoFixResult.warnings.join('; '),
            });
            coveredRanges.push([startIndex, endIndex]);
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
            autoFixed: true,
            fixDescription: autoFixResult.warnings.join('; '),
          });
          coveredRanges.push([startIndex, endIndex]);
          continue;
        } catch (retryError: any) {
          fixDescription = autoFixResult.warnings.join('; ');
        }
      }

      let hint = 'Check JSON syntax';
      if (error.message.includes('array')) {
        hint = 'The "rows" key should be inside the object: {"headers":[...],"rows":[[...]]}';
      } else if (error.message.includes('JSON')) {
        hint = 'Check for missing quotes, commas, or brackets';
      }

      errors.push({
        startIndex,
        endIndex,
        type: typeStr,
        error: error.message,
        hint,
      });
    }
  }

  // Parse markdown tables
  MARKDOWN_TABLE_REGEX.lastIndex = 0;
  let tableMatch;
  while ((tableMatch = MARKDOWN_TABLE_REGEX.exec(text)) !== null) {
    const startIndex = tableMatch.index;

    if (isCovered(startIndex, startIndex + 100, coveredRanges)) {
      continue;
    }

    const parsedTable = parseMarkdownTable(text, startIndex);
    if (parsedTable) {
      const { headers, rows, endIndex } = parsedTable;

      if (isCovered(startIndex, endIndex, coveredRanges)) {
        continue;
      }

      const command: VizCommand = {
        type: 'table',
        headers,
        rows,
      } as VizCommand;

      vizCommands.push({
        command,
        startIndex,
        endIndex,
        autoFixed: true,
        fixDescription: 'Auto-converted from markdown table to viz:table',
      });
      coveredRanges.push([startIndex, endIndex]);
    }
  }

  return { vizs: vizCommands, errors };
}

export function replaceVizsWithPlaceholders(
  text: string,
  parsedVizs: ParsedViz[]
): string {
  let result = text;

  parsedVizs
    .sort((a, b) => b.startIndex - a.startIndex)
    .forEach(({ startIndex, endIndex }, index) => {
      const placeholder = `__VIZ_${index}__`;
      result =
        result.substring(0, startIndex) + placeholder + result.substring(endIndex);
    });

  return result;
}

export function replaceVizsWithErrors(
  text: string,
  errors: VizParseError[]
): string {
  let result = text;

  errors
    .sort((a, b) => b.startIndex - a.startIndex)
    .forEach(({ startIndex, endIndex, type, error, hint }) => {
      const errorPlaceholder = `[⚠️ ${type} chart error: ${error}\n💡 Hint: ${hint}]`;
      result =
        result.substring(0, startIndex) + errorPlaceholder + result.substring(endIndex);
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
