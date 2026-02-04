export interface Theme {
  name: string;
  colors: {
    background: string;
    foreground: string;
    cursor: string;
    cursorAccent: string;
    selectionBackground: string;
    black: string;
    red: string;
    green: string;
    yellow: string;
    blue: string;
    magenta: string;
    cyan: string;
    white: string;
    brightBlack: string;
    brightRed: string;
    brightGreen: string;
    brightYellow: string;
    brightBlue: string;
    brightMagenta: string;
    brightCyan: string;
    brightWhite: string;
  };
  cssVars: {
    bgPrimary: string;
    bgSecondary: string;
    bgTertiary: string;
    textPrimary: string;
    textSecondary: string;
    textDim: string;
    accentBlue: string;
    accentPurple: string;
    accentCyan: string;
    borderColor: string;
    borderLight: string;
    error: string;
    success: string;
    warning: string;
    info: string;
  };
}

export const themes: Record<string, Theme> = {
  oneDark: {
    name: 'One Dark',
    colors: {
      background: '#1E1E1E',
      foreground: '#E0E0E0',
      cursor: '#5C6AC4',
      cursorAccent: '#1E1E1E',
      selectionBackground: 'rgba(92, 106, 196, 0.4)',
      black: '#1E1E1E',
      red: '#F48771',
      green: '#89D185',
      yellow: '#DCDCAA',
      blue: '#5C6AC4',
      magenta: '#BB86FC',
      cyan: '#4FC1FF',
      white: '#E0E0E0',
      brightBlack: '#858585',
      brightRed: '#F48771',
      brightGreen: '#89D185',
      brightYellow: '#DCDCAA',
      brightBlue: '#75BEFF',
      brightMagenta: '#BB86FC',
      brightCyan: '#4FC1FF',
      brightWhite: '#FFFFFF',
    },
    cssVars: {
      bgPrimary: '#1E1E1E',
      bgSecondary: '#252526',
      bgTertiary: '#2D2D2D',
      textPrimary: '#E0E0E0',
      textSecondary: '#B3B3B3',
      textDim: '#858585',
      accentBlue: '#5C6AC4',
      accentPurple: '#BB86FC',
      accentCyan: '#4FC1FF',
      borderColor: '#333333',
      borderLight: '#3E3E42',
      error: '#F48771',
      success: '#89D185',
      warning: '#DCDCAA',
      info: '#75BEFF',
    },
  },
  dracula: {
    name: 'Dracula',
    colors: {
      background: '#282A36',
      foreground: '#F8F8F2',
      cursor: '#BD93F9',
      cursorAccent: '#282A36',
      selectionBackground: 'rgba(189, 147, 249, 0.4)',
      black: '#282A36',
      red: '#FF5555',
      green: '#50FA7B',
      yellow: '#F1FA8C',
      blue: '#BD93F9',
      magenta: '#FF79C6',
      cyan: '#8BE9FD',
      white: '#F8F8F2',
      brightBlack: '#6272A4',
      brightRed: '#FF6E6E',
      brightGreen: '#69FF94',
      brightYellow: '#FFFFA5',
      brightBlue: '#D6ACFF',
      brightMagenta: '#FF92DF',
      brightCyan: '#A4FFFF',
      brightWhite: '#FFFFFF',
    },
    cssVars: {
      bgPrimary: '#282A36',
      bgSecondary: '#21222C',
      bgTertiary: '#343746',
      textPrimary: '#F8F8F2',
      textSecondary: '#B3B3B3',
      textDim: '#6272A4',
      accentBlue: '#BD93F9',
      accentPurple: '#FF79C6',
      accentCyan: '#8BE9FD',
      borderColor: '#44475A',
      borderLight: '#6272A4',
      error: '#FF5555',
      success: '#50FA7B',
      warning: '#F1FA8C',
      info: '#8BE9FD',
    },
  },
  githubDark: {
    name: 'GitHub Dark',
    colors: {
      background: '#0D1117',
      foreground: '#C9D1D9',
      cursor: '#58A6FF',
      cursorAccent: '#0D1117',
      selectionBackground: 'rgba(88, 166, 255, 0.4)',
      black: '#0D1117',
      red: '#FF7B72',
      green: '#7EE787',
      yellow: '#FFA657',
      blue: '#58A6FF',
      magenta: '#D2A8FF',
      cyan: '#79C0FF',
      white: '#C9D1D9',
      brightBlack: '#484F58',
      brightRed: '#FFA198',
      brightGreen: '#56D364',
      brightYellow: '#E3B341',
      brightBlue: '#79C0FF',
      brightMagenta: '#D2A8FF',
      brightCyan: '#79C0FF',
      brightWhite: '#FFFFFF',
    },
    cssVars: {
      bgPrimary: '#0D1117',
      bgSecondary: '#161B22',
      bgTertiary: '#21262D',
      textPrimary: '#C9D1D9',
      textSecondary: '#8B949E',
      textDim: '#484F58',
      accentBlue: '#58A6FF',
      accentPurple: '#A371F7',
      accentCyan: '#79C0FF',
      borderColor: '#30363D',
      borderLight: '#484F58',
      error: '#FF7B72',
      success: '#7EE787',
      warning: '#FFA657',
      info: '#58A6FF',
    },
  },
};

export const defaultTheme = 'oneDark';

export function applyTheme(themeName: string) {
  const theme = themes[themeName] || themes[defaultTheme];
  const root = document.documentElement;

  Object.entries(theme.cssVars).forEach(([key, value]) => {
    const cssVar = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    root.style.setProperty(`--${cssVar}`, value);
  });

  return theme;
}

export function getXtermTheme(themeName: string) {
  const theme = themes[themeName] || themes[defaultTheme];
  return {
    background: theme.colors.background,
    foreground: theme.colors.foreground,
    cursor: theme.colors.cursor,
    cursorAccent: theme.colors.cursorAccent,
    selectionBackground: theme.colors.selectionBackground,
    black: theme.colors.black,
    red: theme.colors.red,
    green: theme.colors.green,
    yellow: theme.colors.yellow,
    blue: theme.colors.blue,
    magenta: theme.colors.magenta,
    cyan: theme.colors.cyan,
    white: theme.colors.white,
    brightBlack: theme.colors.brightBlack,
    brightRed: theme.colors.brightRed,
    brightGreen: theme.colors.brightGreen,
    brightYellow: theme.colors.brightYellow,
    brightBlue: theme.colors.brightBlue,
    brightMagenta: theme.colors.brightMagenta,
    brightCyan: theme.colors.brightCyan,
    brightWhite: theme.colors.brightWhite,
  };
}
