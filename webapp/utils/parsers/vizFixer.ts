// Multi-pass auto-fix system for visualization JSON

interface Fix {
  index: number;
  action: 'add' | 'remove' | 'replace';
  char: string;
  length?: number;
}

interface FixResult {
  fixed: string;
  wasFixed: boolean;
  warnings: string[];
}

/**
 * Sanitize string by removing lone surrogate characters
 */
export function sanitizeLoneSurrogates(str: string): string {
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
      duplicates.push(seenKeys.get(key)!);
    }
    seenKeys.set(key, { start, end });
  }

  if (duplicates.length === 0) {
    return { fixed: json, wasFixed: false, warnings };
  }

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

  let fixed = json;
  toRemove.sort((a, b) => b.end - a.end);
  for (const rem of toRemove) {
    fixed = fixed.substring(0, rem.start) + fixed.substring(rem.end);
  }

  warnings.push(`Removed ${toRemove.length} duplicate key(s)`);
  return { fixed, wasFixed: true, warnings };
}

/**
 * Fix 4: Balance brackets
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
 * Fix 5: Add missing commas
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

    if ((braceDepth > 0 || bracketDepth > 0) &&
        (char === '"' || char === '}' || char === ']') &&
        (nextChar === '"' || nextChar === '{' || nextChar === '[')) {
      fixes.push({ index: i + 1, action: 'add', char: ',' });
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
 * Fix 6: Schema-aware fixes for specific viz types
 */
function fixSchemaIssues(json: string, vizType: string): FixResult {
  const warnings: string[] = [];

  try {
    const obj = JSON.parse(json);
    const fixed = { ...obj };

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
export function autoFixVisualization(jsonStr: string, vizType: string): FixResult {
  const allWarnings: string[] = [];
  let current = jsonStr;
  let wasFixed = false;

  const passes: Array<{ name: string; fn: (s: string) => FixResult }> = [
    { name: 'surrogate-chars', fn: fixSurrogateCharacters },
    { name: 'trailing-commas', fn: removeTrailingCommas },
    { name: 'duplicate-keys', fn: removeDuplicateKeys },
    { name: 'bracket-balance', fn: balanceBrackets },
    { name: 'missing-commas', fn: addMissingCommas },
    { name: 'schema-validation', fn: (s: string) => fixSchemaIssues(s, vizType) },
  ];

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

  try {
    JSON.parse(current);
  } catch (e) {
    allWarnings.push(`Validation failed: ${(e as Error).message}`);
  }

  return { fixed: current, wasFixed, warnings: allWarnings };
}
