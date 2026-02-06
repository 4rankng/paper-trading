import { VizParseError, parseVizCommands, sanitizeLoneSurrogates } from '@/utils/viz-parser';
import { ParsedViz } from '@/types/visualizations';

export interface VizValidationResult {
  isValid: boolean;
  fixedText: string;
  errors: VizParseError[];
  autoFixedCount: number;
}

// Re-export for backward compatibility
export { sanitizeLoneSurrogates };

/**
 * Validate and auto-fix visualizations in LLM response
 * Called server-side before sending to client
 */
export function validateAndFixVisualizations(text: string): VizValidationResult {
  const { vizs, errors } = parseVizCommands(text);

  // Check if any errors couldn't be auto-fixed
  const hasUnfixableErrors = errors.length > 0;

  // Count successful auto-fixes
  const autoFixedCount = vizs.filter(v => v.autoFixed).length;

  // If there are errors, we need to extract the fixed portions
  // For now, return the original text if there are unfixable errors
  // The calling code will handle regeneration
  let fixedText = text;
  if (!hasUnfixableErrors) {
    // All visualizations were parsed successfully (with or without auto-fix)
    // We can stream this to the client
    fixedText = text;
  }

  return {
    isValid: !hasUnfixableErrors,
    fixedText,
    errors,
    autoFixedCount,
  };
}

/**
 * Generate a prompt for LLM to regenerate visualizations with specific error feedback
 * Only asks to regenerate the broken visualizations, not the entire response
 */
export function generateRegenerationPrompt(originalText: string, errors: VizParseError[]): string {
  const errorSummary = errors.map((err, i) => {
    return `Error ${i + 1}: ${err.type} visualization - ${err.error}\n  Hint: ${err.hint}`;
  }).join('\n\n');

  // Extract the broken visualization snippets from the original text
  const brokenVizs = errors.map(err => {
    const snippet = originalText.substring(err.startIndex, Math.min(err.endIndex, err.startIndex + 200));
    // Sanitize to remove lone surrogates that can cause UTF-8 encoding errors
    return `  ${sanitizeLoneSurrogates(snippet.trim())}`;
  }).join('\n\n');

  return `Some visualizations in your response have JSON syntax errors that couldn't be auto-fixed.

ERRORS FOUND:
${errorSummary}

BROKEN VISUALIZATIONS:
${brokenVizs}

COMMON FIXES:
1. For charts: Use type="chart" with chartType="line" or chartType="bar" inside
   ✅ CORRECT: ![viz:chart]({"type":"chart","chartType":"line","data":{...}})
   ❌ WRONG: ![viz:line]({"data":{...}})

2. For tables: Ensure all JSON is properly closed with })
   ✅ CORRECT: ![viz:table]({"headers":["A","B"],"rows":[["x","y"]]})
   ❌ WRONG: ![viz:table]({"headers":["A","B"],"rows":[["x","y"]

3. Check for:
   - Mismatched brackets [ instead of {
   - Missing closing quotes
   - Trailing commas
   - Duplicate keys

Please provide ONLY the corrected visualizations (one per line), not the entire response:

Format your response as a JSON array:
[
  {"index": 0, "corrected": "![viz:table]({...})"},
  {"index": 1, "corrected": "![viz:chart]({...})"},
  ...
]`;
}

/**
 * Extract corrected visualizations from LLM regeneration response
 * Returns array of corrected viz strings
 */
export function extractCorrectedVisualizations(regenerationResponse: string): string[] {
  try {
    // Try to parse as JSON array
    const corrected = JSON.parse(regenerationResponse);
    if (Array.isArray(corrected)) {
      return corrected.map((item: any) => item.corrected).filter(Boolean);
    }
  } catch {
    // Fallback: extract all viz syntax from the response
    const vizMatches = regenerationResponse.match(/!\[viz:\w+\]\([^)]+\)/g);
    return vizMatches || [];
  }
  return [];
}
