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
// Captures the full table including header and separator rows
const MARKDOWN_TABLE_REGEX = /\|(?![\s\d-:]+\|)[^|\r\n]+(\|[^|\r\n]+)+\|[ \t]*\r?\n[ \t]*\|[\s\-:]+\|[\s\-:|]*\|[ \t]*\r?\n(?:[ \t]*\|(?![\s\-:]+)[^|\r\n]+(\|[^|\r\n]+)*\|[ \t]*\r?\n?)*/g;

/**
 * Parse a markdown table and convert to viz:table format
 * Returns { headers, rows, endIndex } or null if not a valid table
 */
function parseMarkdownTable(text: string, startIndex: number): {
  headers: string[];
  rows: string[][];
  endIndex: number;
} | null {
  const tableText = text.substring(startIndex);

  // Extract the full table
  let i = 0;
  let lineStart = 0;
  const lines: string[] = [];

  // Extract lines while they look like table rows
  while (i < tableText.length) {
    // Find next newline
    let lineEnd = tableText.indexOf('\n', i);
    if (lineEnd === -1) lineEnd = tableText.length;

    const line = tableText.substring(i, lineEnd);
    const trimmed = line.trim();

    // Check if this looks like a table row (starts and ends with |)
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      lines.push(trimmed);
      i = lineEnd + 1;
    } else {
      // Not a table row, stop
      break;
    }

    // Stop if we hit an empty line or double newline
    if (i < tableText.length && tableText[i] === '\n') {
      break;
    }
  }

  // Need at least header and separator rows
  if (lines.length < 2) return null;

  // First line is headers
  const headerLine = lines[0];
  const headers = headerLine
    .split('|')
    .slice(1, -1) // Remove empty first and last elements
    .map(h => h.trim())
    .filter(h => h.length > 0);

  // Second line is separator (skip)
  if (!lines[1].includes('---')) return null;

  // Remaining lines are data rows
  const rows: string[][] = [];
  for (let i = 2; i < lines.length; i++) {
    const row = lines[i]
      .split('|')
      .slice(1, -1)
      .map(cell => cell.trim())
      .filter(cell => cell.length > 0);

    // Only add row if it has data
    if (row.length > 0) {
      rows.push(row);
    }
  }

  // Calculate end index
  const endIndex = startIndex + lines.reduce((sum, line) => sum + line.length + 1, 0);

  return { headers, rows, endIndex };
}

/**
 * Pre-process JSON string to fix common LLM mistakes
 * - Removes duplicate keys (keeps last occurrence)
 * - Removes trailing commas
 * - Fixes malformed structures
 */
function preprocessJSON(jsonStr: string): string {
  let processed = jsonStr.trim();

  // Remove duplicate keys by keeping the last occurrence
  // This regex matches patterns like "key": value, ... "key": value2
  // and removes the first occurrence
  const keyPattern = /"([^"]+)"\s*:/g;
  const seenKeys = new Set<string>();
  const keysToRemove: Array<{ key: string; start: number; end: number }> = [];

  let match;
  while ((match = keyPattern.exec(processed)) !== null) {
    const key = match[1];
    const keyStart = match.index;
    const keyEnd = keyPattern.lastIndex;

    if (seenKeys.has(key)) {
      // Found duplicate - mark the first occurrence for removal
      keysToRemove.push({ key, start: keyStart, end: keyEnd });
    } else {
      seenKeys.add(key);
    }
  }

  // Remove duplicate key-value pairs from end to start (to preserve indices)
  // We need to find the complete value for each duplicate key
  for (const dup of keysToRemove.reverse()) {
    // Find the end of this key's value (comma or closing brace)
    let valueEnd = dup.end;
    let braceDepth = 0;
    let inString = false;
    let escapeNext = false;

    for (let i = dup.end; i < processed.length; i++) {
      const char = processed[i];

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
          braceDepth++;
        } else if (char === '}' || char === ']') {
          braceDepth--;
        } else if (braceDepth === 0 && (char === ',' || char === '}' || char === ']')) {
          valueEnd = i;
          break;
        }
      }
    }

    // Remove the duplicate key-value pair
    processed = processed.substring(0, dup.start) + processed.substring(valueEnd);
  }

  return processed;
}

/**
 * Check if JSON string appears to be complete
 * Detects common incomplete patterns during streaming
 */
function isJSONComplete(jsonStr: string): boolean {
  const trimmed = jsonStr.trim();

  // Quick check: must end with } or ]
  if (!trimmed.endsWith('}') && !trimmed.endsWith(']')) {
    return false;
  }

  // Check for incomplete string at the end
  // If we have an odd number of quotes, a string is likely unclosed
  let quoteCount = 0;
  let escapeNext = false;
  for (let i = 0; i < trimmed.length; i++) {
    const char = trimmed[i];
    if (escapeNext) {
      escapeNext = false;
      continue;
    }
    if (char === '\\') {
      escapeNext = true;
      continue;
    }
    if (char === '"') {
      quoteCount++;
    }
  }

  // Odd number of quotes means unclosed string
  if (quoteCount % 2 !== 0) {
    return false;
  }

  // Check for trailing comma (common LLM streaming artifact)
  if (/,\s*[,}\]]/.test(trimmed)) {
    return false;
  }

  // Check for incomplete patterns that suggest truncation
  // e.g., "value": ... (no closing quote or bracket)
  const incompletePatterns = [
    /"[^"]*:\s*"[^"]*$/,  // Unclosed string value
    /"[^"]*:\s*\{[^}]*$/, // Unclosed object value
    /"[^"]*:\s*\[[^\]]*$/, // Unclosed array value
  ];

  for (const pattern of incompletePatterns) {
    if (pattern.test(trimmed)) {
      return false;
    }
  }

  return true;
}

// Extract complete JSON by matching parentheses
// Returns { json, endIndex } on success, { json: null, endIndex } on error (to capture full range for error display)
function extractJSON(text: string, startIndex: number): { json: string | null; endIndex: number } | null {
  let parenCount = 1; // Start at 1 because we've already seen the opening (
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
          // Found matching closing parenthesis - validate JSON is complete
          let json = text.substring(startIndex, i);

          // Check if JSON appears complete before parsing (prevents parsing incomplete streaming data)
          if (!isJSONComplete(json)) {
            // JSON looks incomplete - don't try to parse yet, return null to wait for more data
            continue;
          }

          // Pre-process JSON to fix common LLM mistakes (duplicate keys, etc.)
          json = preprocessJSON(json);

          // Validate JSON is parseable before returning
          try {
            JSON.parse(json);
            return { json, endIndex: i + 1 };
          } catch {
            // JSON is complete but invalid - return with json=null to trigger error handling
            // but still provide endIndex for proper error message placement
            return { json: null, endIndex: i + 1 };
          }
        }
      }
    }

    i++;
  }

  // No matching closing parenthesis found or JSON incomplete
  // If we found at least one closing paren, use that for error display
  if (lastClosingParen > startIndex) {
    return { json: null, endIndex: lastClosingParen + 1 };
  }

  // No valid structure found - return null to indicate "not ready yet"
  return null;
}

// Map chart type aliases to 'chart' type
const CHART_TYPE_ALIASES: Record<string, 'line' | 'bar' | 'scatter'> = {
  'line': 'line',
  'bar': 'bar',
  'scatter': 'scatter',
};

/**
 * Attempt to auto-fix common LLM visualization syntax errors
 * Returns fixed JSON string or null if fix not possible
 */
function attemptAutoFix(
  jsonStr: string,
  typeStr: string
): { fixed: string; fixDescription: string } | null {
  const trimmed = jsonStr.trim();

  // Quick check: if JSON is incomplete (ends mid-value), don't try to fix
  // This handles streaming truncation
  if (trimmed.length > 0 && !trimmed.endsWith('}') && !trimmed.endsWith(']')) {
    return null;
  }

  // Pattern 1: Array-at-root + datasets (most common error)
  // Example: ["AAPL","MSFT"],"datasets":[{"label":"P/L %","data":[12.5,8.3]}]}}
  if (trimmed.startsWith('[') && trimmed.includes('"datasets"')) {
    try {
      // Try to parse and reconstruct the structure
      // Find the end of the labels array
      let depth = 0;
      let labelsEnd = -1;
      for (let i = 0; i < trimmed.length; i++) {
        if (trimmed[i] === '[' || trimmed[i] === '{') depth++;
        if (trimmed[i] === ']' || trimmed[i] === '}') depth--;
        if (depth === 0 && trimmed[i] === ']') {
          labelsEnd = i + 1;
          break;
        }
      }

      if (labelsEnd > 0) {
        const labelsPart = trimmed.substring(0, labelsEnd);
        const restPart = trimmed.substring(labelsEnd).trim();

        // Remove trailing comma if present
        const datasetsPart = restPart.startsWith(',') ? restPart.substring(1).trim() : restPart;

        // Try to parse labels
        const labels = JSON.parse(labelsPart);
        if (!Array.isArray(labels)) return null;

        // Try to parse datasets part
        let datasets;
        try {
          // Handle case where datasets might be wrapped in extra braces
          const cleanedDatasets = datasetsPart.replace(/^,*/, '').replace(/}*$/, '');
          datasets = JSON.parse(cleanedDatasets);
          if (!datasets.datasets && Array.isArray(datasets)) {
            // If it's an array, wrap it
            datasets = { datasets: [{ label: 'Value', data: datasets }] };
          }
        } catch {
          // Try to extract datasets object from malformed structure
          const datasetsMatch = datasetsPart.match(/"datasets"\s*:\s*\[[^\]]*\]/);
          if (datasetsMatch) {
            const datasetsObjStr = '{' + datasetsMatch[0] + '}';
            datasets = JSON.parse(datasetsObjStr);
          } else {
            return null;
          }
        }

        // Determine chart type from context
        let chartType = 'bar'; // Default
        if (typeStr === 'line') chartType = 'line';

        // Reconstruct proper structure
        const fixed = JSON.stringify({
          type: 'chart',
          chartType,
          data: {
            labels,
            ...datasets
          }
        });

        return {
          fixed,
          fixDescription: 'Fixed: Wrapped array data in proper chart structure with type, chartType, and data fields'
        };
      }
    } catch (e) {
      // Auto-fix failed, will return null below
    }
  }

  // Pattern 2: Missing "data" wrapper but has labels and datasets
  // Example: {"labels":["AAPL"],"datasets":[...]}
  if (!trimmed.startsWith('[') && (trimmed.includes('"labels"') && trimmed.includes('"datasets"'))) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed.labels && parsed.datasets && !parsed.data) {
        // Check if it already has type/chartType
        const fixed = {
          type: parsed.type || 'chart',
          chartType: parsed.chartType || (typeStr === 'line' ? 'line' : 'bar'),
          data: {
            labels: parsed.labels,
            datasets: parsed.datasets
          },
          options: parsed.options
        };
        return {
          fixed: JSON.stringify(fixed),
          fixDescription: 'Fixed: Wrapped labels/datasets in data object'
        };
      }
    } catch (e) {
      // Auto-fix pattern 2 failed
    }
  }

  // Pattern 3: Malformed table with mismatched brackets
  // Example: {"columns":["A","B"],["rows":[["x","y"]]} or {"headers":[...],["rows":[...]}
  if (typeStr === 'table' && trimmed.match(/^\{.*?\["/)) {
    try {
      // Try to fix by replacing ],[ with ," (malformed bracket pattern)
      const fixedStr = trimmed.replace(/\],\s*\[/g, ',"');

      // Try parsing the fixed version
      const parsed = JSON.parse(fixedStr);

      // Check if it now has valid structure
      if ((parsed.headers || parsed.columns) && parsed.rows) {
        // Normalize to standard format
        const fixed = {
          type: 'table',
          headers: parsed.headers || parsed.columns,
          rows: parsed.rows
        };
        return {
          fixed: JSON.stringify(fixed),
          fixDescription: 'Fixed: Corrected mismatched brackets in table structure'
        };
      }
    } catch (e) {
      // Auto-fix pattern 3 failed
    }
  }

  // Pattern 4: Table with columns/rows but using wrong key names
  // Example: {"columns":[...],"rows":[...]} instead of {"headers":[...],"rows":[...]}
  if (typeStr === 'table' && trimmed.includes('"columns"') && trimmed.includes('"rows"')) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed.columns && parsed.rows && !parsed.headers) {
        const fixed = {
          type: 'table',
          headers: parsed.columns,
          rows: parsed.rows
        };
        return {
          fixed: JSON.stringify(fixed),
          fixDescription: 'Fixed: Renamed "columns" to "headers" for table format'
        };
      }
    } catch (e) {
      // Auto-fix pattern 4 failed
    }
  }

  // Pattern 5: Trailing commas in objects or arrays (common LLM error)
  if (trimmed.includes(',}') || trimmed.includes(',]')) {
    try {
      const fixedStr = trimmed.replace(/,\s*}/g, '}').replace(/,\s*]/g, ']');
      const parsed = JSON.parse(fixedStr);

      // Re-wrap with proper structure if needed
      const fixed = typeStr === 'table' && parsed.headers && parsed.rows
        ? { type: 'table', headers: parsed.headers, rows: parsed.rows }
        : typeStr === 'chart' && parsed.data
        ? { type: 'chart', ...parsed }
        : typeStr === 'pie' && parsed.data
        ? { type: 'pie', options: parsed.options, data: parsed.data }
        : parsed;

      return {
        fixed: JSON.stringify(fixed),
        fixDescription: 'Fixed: Removed trailing commas'
      };
    } catch (e) {
      // Auto-fix pattern 5 failed
    }
  }

  // Pattern 6: Missing quotes around property names (common in Python-like syntax)
  // Example: {headers: [...], rows: [...]} instead of {"headers": [...], "rows": [...]}
  if (/^[a-zA-Z_][a-zA-Z0-9_]*\s*:/.test(trimmed)) {
    try {
      // Add quotes around unquoted property names
      const fixedStr = trimmed.replace(/([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g, '$1"$2":');
      const parsed = JSON.parse(fixedStr);

      // Wrap in proper structure
      const fixed = typeStr === 'table' && parsed.headers && parsed.rows
        ? { type: 'table', headers: parsed.headers, rows: parsed.rows }
        : parsed;

      return {
        fixed: JSON.stringify(fixed),
        fixDescription: 'Fixed: Added quotes around property names'
      };
    } catch (e) {
      // Auto-fix pattern 6 failed
    }
  }

  // Pattern 7: Single quotes instead of double quotes
  if (trimmed.includes("'") && !trimmed.includes('"')) {
    try {
      // Replace single quotes with double quotes, escaping properly
      const fixedStr = trimmed
        .replace(/'/g, '"')
        .replace(/"\s*:\s*"/g, '": "');  // Fix any double colons

      const parsed = JSON.parse(fixedStr);

      const fixed = typeStr === 'table' && parsed.headers && parsed.rows
        ? { type: 'table', headers: parsed.headers, rows: parsed.rows }
        : parsed;

      return {
        fixed: JSON.stringify(fixed),
        fixDescription: 'Fixed: Replaced single quotes with double quotes'
      };
    } catch (e) {
      // Auto-fix pattern 7 failed
    }
  }

  // Pattern 8: Wrong type in viz:chart (type="line" or type="bar" should be type="chart" with chartType)
  if ((trimmed.includes('"type":"line"') || trimmed.includes('"type":"bar"') || trimmed.includes('"type": "line"') || trimmed.includes('"type": "bar"')) && (trimmed.includes('"datasets"') || trimmed.includes('"labels"'))) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed.type === 'line' || parsed.type === 'bar') {
        const chartType = parsed.type;
        const { type, ...rest } = parsed;
        const fixed = {
          type: 'chart',
          chartType: chartType,
          ...rest
        };

        return {
          fixed: JSON.stringify(fixed),
          fixDescription: `Fixed: Changed type="${chartType}" to type="chart" with chartType="${chartType}"`
        };
      }
    } catch (e) {
      // Auto-fix pattern 8 failed
    }
  }

  return null;
}

/**
 * Check if a position range is already covered by existing visualizations
 */
function isCovered(start: number, end: number, coveredRanges: [number, number][]): boolean {
  return coveredRanges.some(([rangeStart, rangeEnd]) => {
    // Check for overlap
    return start < rangeEnd && end > rangeStart;
  });
}

export function parseVizCommands(text: string): { vizs: ParsedViz[]; errors: VizParseError[] } {
  const vizCommands: ParsedViz[] = [];
  const errors: VizParseError[] = [];

  // Track positions already covered by viz commands to avoid duplicates
  const coveredRanges: [number, number][] = [];

  // First, parse viz:table/viz:chart commands
  let match;
  VIZ_REGEX.lastIndex = 0;

  while ((match = VIZ_REGEX.exec(text)) !== null) {
    const typeStr = match[1];
    const startIndex = match.index;
    const openParenIndex = startIndex + match[0].length;

    // Extract JSON by matching parentheses
    const result = extractJSON(text, openParenIndex);

    if (!result) {
      // No valid structure found at all - likely incomplete/streaming
      errors.push({
        startIndex,
        endIndex: openParenIndex + 50, // Approximate end for error display
        type: typeStr,
        error: 'Could not find matching closing parenthesis',
        hint: 'Check that your JSON is properly closed with })',
      });
      continue;
    }

    const { json: jsonStr, endIndex } = result;

    // If json is null, we found closing paren but JSON is invalid
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

      // Validate that data is an object, not an array (common LLM mistake)
      if (Array.isArray(data)) {
        throw new Error('Data must be an object with "headers" and "rows" keys, not an array');
      }

      // Handle chart type aliases (bar, line, scatter -> chart)
      if (CHART_TYPE_ALIASES[typeStrLower]) {
        // Extract data but exclude 'type' field to prevent overwriting
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

      // Direct type match (chart, table, pie)
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
      // Attempt auto-fix for common LLM mistakes
      const autoFixResult = attemptAutoFix(jsonStr, typeStr);

      if (autoFixResult) {
        finalJsonStr = autoFixResult.fixed;
        wasAutoFixed = true;
        fixDescription = autoFixResult.fixDescription;

        // Try parsing again with fixed JSON
        try {
          const data = JSON.parse(finalJsonStr);
          const typeStrLower = typeStr.toLowerCase();

          // Handle chart type aliases
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
              fixDescription,
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
            fixDescription,
          });
          coveredRanges.push([startIndex, endIndex]);
          continue;
        } catch (retryError: any) {
          // Auto-fix didn't work, fall through to error handling
        }
      }

      // Parse error - create user-friendly error message

      // Create user-friendly error message
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

  // Second, detect and convert markdown tables
  MARKDOWN_TABLE_REGEX.lastIndex = 0;
  let tableMatch;
  while ((tableMatch = MARKDOWN_TABLE_REGEX.exec(text)) !== null) {
    const startIndex = tableMatch.index;

    // Skip if this range is already covered by a viz command
    if (isCovered(startIndex, startIndex + 100, coveredRanges)) {
      continue;
    }

    const parsedTable = parseMarkdownTable(text, startIndex);
    if (parsedTable) {
      const { headers, rows, endIndex } = parsedTable;

      // Skip if covered
      if (isCovered(startIndex, endIndex, coveredRanges)) {
        continue;
      }

      // Create viz:table command
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

export function replaceVizsWithErrors(
  text: string,
  errors: VizParseError[]
): string {
  let result = text;
  let errorCount = 0;

  // Replace from end to start to maintain correct indices
  errors
    .sort((a, b) => b.startIndex - a.startIndex)
    .forEach(({ startIndex, endIndex, type, error, hint }) => {
      const errorPlaceholder = `[⚠️ ${type} chart error: ${error}\n💡 Hint: ${hint}]`;
      result =
        result.substring(0, startIndex) + errorPlaceholder + result.substring(endIndex);
      errorCount++;
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
