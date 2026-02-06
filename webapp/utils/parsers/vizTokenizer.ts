// Token-based JSON completion check

interface Token {
  type: 'bracket' | 'punctuation' | 'string' | 'literal' | 'whitespace';
  value: string;
  index: number;
}

/**
 * Tokenize JSON for more accurate analysis
 */
export function tokenizeJSON(json: string): Token[] {
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
      i++;
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

    const start = i;
    while (i < json.length && /[^\s{}[\]:,"]/.test(json[i])) i++;
    tokens.push({ type: 'literal', value: json.substring(start, i), index: start });
  }

  return tokens;
}

/**
 * Check if JSON appears complete using token-based analysis
 */
export function isJSONComplete(jsonStr: string): boolean {
  const trimmed = jsonStr.trim();

  if (!trimmed.endsWith('}') && !trimmed.endsWith(']')) {
    return false;
  }

  const tokens = tokenizeJSON(trimmed);

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
