import { VizCommand, ParsedViz, VizType } from '@/types/visualizations';
import { autoFixVisualization, sanitizeLoneSurrogates } from './parsers/vizFixer';
import { parseMarkdownTable, extractJSON, findVisualizationEnd, isCovered } from './parsers/vizExtractor';

// Re-export for other modules
export { sanitizeLoneSurrogates, autoFixVisualization };

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

// Map chart type aliases
const CHART_TYPE_ALIASES: Record<string, 'line' | 'bar' | 'scatter'> = {
  'line': 'line',
  'bar': 'bar',
  'scatter': 'scatter',
};

/**
 * Main parsing function - find and parse all visualizations
 */
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

    try {
      const data = JSON.parse(jsonStr);
      const typeStrLower = typeStr.toLowerCase();

      if (Array.isArray(data)) {
        throw new Error('Data must be an object with "headers" and "rows" keys, not an array');
      }

      if (CHART_TYPE_ALIASES[typeStrLower]) {
        const typedData = data as Record<string, unknown>;
        const { type: _type, ...dataWithoutType } = typedData;
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
      });
      coveredRanges.push([startIndex, endIndex]);
    } catch (error: any) {
      // Try auto-fix
      const autoFixResult = autoFixVisualization(jsonStr, typeStr);

      if (autoFixResult.wasFixed) {
        try {
          const data = JSON.parse(autoFixResult.fixed);
          const typeStrLower = typeStr.toLowerCase();

          if (CHART_TYPE_ALIASES[typeStrLower]) {
            const typedData = data as Record<string, unknown>;
            const { type: _type, ...dataWithoutType } = typedData;
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
          // Fall through to error
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

/**
 * Replace visualizations with placeholders
 */
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

/**
 * Replace visualizations with error messages
 */
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

/**
 * Split text by visualization positions
 */
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
