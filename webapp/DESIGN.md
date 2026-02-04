# TermAI Explorer - Design Documentation

## Overview

TermAI Explorer is a modern, web-based terminal emulator powered by xterm.js with a sleek, contemporary UI inspired by Warp and Hyper terminals. It provides an intelligent AI assistant interface with real-time streaming responses and interactive data visualizations.

## Architecture

### Hybrid Approach

The application uses a **hybrid architecture** similar to Warp terminal:

- **xterm.js**: Terminal emulator for command input/output rendering
- **React panels**: Title bar, tabs, status bar, and visualizations sidebar
- **Seamless integration**: Text streams to terminal, visualizations render in React panels

### Technology Stack

- **Frontend**: Next.js 14 with React 18
- **Terminal**: xterm.js 5.3.0 with FitAddon and WebLinksAddon
- **State Management**: Zustand
- **Visualizations**: Chart.js with react-chartjs-2
- **Styling**: Tailwind CSS with custom theme variables
- **Font**: Fira Code (monospace)

## Component Architecture

```
app/
├── page.tsx                    # Main layout with shell structure
├── globals.css                 # Modern One Dark color scheme
├── layout.tsx                  # Root layout with font imports
└── api/                        # API routes (chat, session, RAG)

components/
├── terminal/
│   ├── XtermTerminal.tsx      # xterm.js terminal emulator
│   ├── TitleBar.tsx           # Window controls and session status
│   ├── TabBar.tsx             # Multi-session tab management
│   ├── StatusBar.tsx          # Session info, actions, clock
│   └── VizPanel.tsx           # Visualization sidebar
├── visualizations/
│   ├── VizRenderer.tsx        # Visualization router
│   ├── Chart.tsx              # Line/bar/scatter charts
│   ├── Table.tsx              # Data tables
│   └── PieChart.tsx           # Pie charts
└── ui/
    └── ErrorBoundary.tsx      # Error handling

lib/
├── themes.ts                  # Theme configurations (One Dark, Dracula, GitHub Dark)
├── viz-parser.ts              # Visualization syntax parser
├── storage.ts                 # Session persistence
└── data-access.ts             # File I/O utilities

store/
└── useTerminalStore.ts        # Zustand state management

types/
├── index.ts                   # Message, Session, TerminalState
└── visualizations.ts          # VizCommand types
```

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Title Bar (40px)                                            │
│ [● ● ●]  TermAI Explorer                            Connected│
├─────────────────────────────────────────────────────────────┤
│ Tab Bar (36px)                                              │
│ [Session 1] [Session 2] [+]                                 │
├──────────────────────────────────┬──────────────────────────┤
│                                  │ VizPanel (384px)         │
│                                  │ ┌────────────────────┐   │
│                                  │ │ Visualizations     │   │
│                                  │ ├────────────────────┤   │
│                                  │ │ [Chart 1]          │   │
│ Xterm Terminal                   │ │ [Table 2]          │   │
│ (flexible)                       │ │ [Pie 3]            │   │
│                                  │ └────────────────────┘   │
│                                  │                          │
│                                  │ 3 vizs | Scroll ↓       │
├──────────────────────────────────┴──────────────────────────┤
│ Status Bar (24px)                                            │
│ Session: abc12345 | 12 messages | Clear | Settings | Ready │
└─────────────────────────────────────────────────────────────┘
```

## Color Scheme (One Dark Theme)

```css
/* Primary Colors */
--bg-primary: #1E1E1E;      /* Deep gray background */
--bg-secondary: #252526;    /* Slightly lighter for panels */
--bg-tertiary: #2D2D2D;     /* Hover states */

/* Text Colors */
--text-primary: #E0E0E0;    /* Soft white */
--text-secondary: #B3B3B3;  /* Muted text */
--text-dim: #858585;        /* Dimmed text */

/* Accent Colors */
--accent-blue: #5C6AC4;     /* Primary accent */
--accent-purple: #BB86FC;   /* Secondary accent */
--accent-cyan: #4FC1FF;     /* Tertiary accent */

/* UI Elements */
--border-color: #333333;    /* Subtle borders */
--border-light: #3E3E42;    /* Lighter borders */

/* Status Colors */
--error: #F48771;           /* Modern error red */
--success: #89D185;         /* Modern success green */
--warning: #DCDCAA;         /* Warning yellow */
--info: #75BEFF;            /* Info blue */
```

## Typography

- **Primary Font**: Fira Code
- **Fallbacks**: Source Code Pro, Monaco, Courier New
- **Terminal Size**: 14px
- **UI Size**: 13-14px
- **Anti-aliasing**: Enabled (-webkit-font-smoothing: antialiased)

## Terminal Features

### Command Input

- Real-time character input rendering
- Command history navigation (Up/Down arrows)
- Backspace handling
- Ctrl+C to cancel current input
- Custom prompt: `➜ user@termai:~$`

### Streaming Responses

- Server-Sent Events (SSE) for real-time streaming
- Text renders in dim color during streaming
- Visualizations automatically extracted and routed to sidebar
- Placeholder indicators: `[Visualization → panel]`

### xterm.js Configuration

```typescript
{
  theme: getXtermTheme('oneDark'),
  fontFamily: 'Fira Code',
  fontSize: 14,
  lineHeight: 1.2,
  cursorBlink: true,
  cursorStyle: 'block',
  scrollback: 1000,
  tabStopWidth: 4
}
```

## Visualization System

### Syntax

Visualizations use markdown-like syntax in AI responses:

```
![viz:chart]({"type":"chart","data":{...},"chartType":"line"})
![viz:table]({"type":"table","headers":[...],"rows":[...]})
![viz:pie]({"type":"pie","data":[...],"options":{...}})
```

### Detection & Routing

1. **Parser** (`lib/viz-parser.ts`) extracts viz commands from text
2. **Store** tracks visualizations in Zustand state
3. **Terminal** shows placeholder: `[Visualization → panel]`
4. **VizPanel** renders actual Chart.js components

### VizPanel Features

- Collapsible sidebar (384px wide)
- Render charts, tables, pie charts via VizRenderer
- Empty state with helpful message
- Visualization counter in footer
- Can be completely closed (floating reopen button appears)
- Smooth animations and transitions

## State Management

### Zustand Store Structure

```typescript
interface TerminalStore {
  // Session state
  sessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // Command history
  commandHistory: string[];
  commandIndex: number;

  // Visualizations
  visualizations: VizCommand[];

  // Theme
  currentTheme: string;

  // Actions
  setSessionId(id: string): void;
  addMessage(message: Message): void;
  setLoading(loading: boolean): void;
  setError(error: string | null): void;
  addToCommandHistory(command: string): void;
  navigateCommandHistory(direction: 'up' | 'down'): void;
  clearMessages(): void;
  addVisualization(viz: VizCommand): void;
  clearVisualizations(): void;
  setTheme(theme: string): void;
}
```

## Theme System

### Available Themes

1. **One Dark** (default)
   - VS Code-inspired dark theme
   - Blue accent (#5C6AC4)
   - Balanced contrast

2. **Dracula**
   - Purple/pink aesthetic
   - Higher contrast
   - Popular in developer community

3. **GitHub Dark**
   - GitHub's dark mode colors
   - Subtle, professional
   - Great for long sessions

### Theme Switching

Themes can be switched via:
- Settings menu (planned)
- Programmatic `setTheme()` store action
- Direct `applyTheme(themeName)` function call

## API Integration

### Chat Endpoint

**POST** `/api/chat`

```typescript
{
  message: string;
  session_id: string;
}
```

Returns SSE stream with chunks:
```
data: {"text": "Hello"}
data: {"text": " world"}
data: [DONE]
```

### Session Endpoint

**GET/POST** `/api/session`

Creates or retrieves session ID from localStorage.

### RAG Endpoints

- **POST** `/api/rag/query` - Semantic search
- **POST** `/api/rag/store` - Store message embeddings

## Performance Optimizations

### Dynamic Imports

XtermTerminal is dynamically imported with SSR disabled to prevent xterm.js server-side issues:

```typescript
const XtermTerminal = dynamic(
  () => import('@/components/terminal/XtermTerminal'),
  { ssr: false }
);
```

### useEffect Dependencies

Terminal initialization only runs once using refs to track initialization state:

```typescript
useEffect(() => {
  if (!terminalRef.current || xtermRef.current) return;
  // Initialize xterm.js
}, []);
```

### Resize Handling

FitAddon automatically adjusts terminal size on window resize with debouncing.

## Responsive Design

- Mobile: VizPanel stacks below terminal, tabs become scrollable
- Tablet: Side-by-side layout with narrower VizPanel (300px)
- Desktop: Full 384px VizPanel side-by-side

## Accessibility

- Keyboard navigation for tabs (Tab/Shift+Tab)
- Aria labels on all buttons
- Focus indicators on interactive elements
- Screen reader friendly text alternatives

## Future Enhancements

### Planned Features

1. **Command Palette** (Ctrl+Shift+P)
   - Fuzzy search through commands
   - Recent commands history
   - Quick action shortcuts

2. **Split Panes**
   - Multiple terminals side-by-side
   - Independent sessions per pane
   - CSS Grid layout

3. **Autocomplete**
   - Tab completion for commands
   - Suggestions from history
   - Dropdown with matches

4. **Settings Panel**
   - Theme switcher UI
   - Font size controls
   - Keybinding customization
   - Terminal preferences

5. **Command History Sidebar**
   - Full command history list
   - Search and filter
   - Click to re-execute

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Supported with responsive layout

## Development

### Run Dev Server

```bash
npm run dev
# Opens http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

### Type Checking

```typescript
# All components fully typed
npm run lint
```

## Design Principles

1. **Modern Aesthetic**: Clean, contemporary design inspired by popular terminals
2. **Hybrid Architecture**: Best of both xterm.js and React worlds
3. **Performance**: Fast rendering with efficient state management
4. **Accessibility**: Keyboard-first design with screen reader support
5. **Extensibility**: Easy to add new visualizations and features
6. **Developer Experience**: Well-typed, documented codebase

## Resources

- [xterm.js Documentation](https://xtermjs.org/)
- [Warp Terminal](https://www.warp.dev/) - Design inspiration
- [Hyper Terminal](https://hyper.is/) - UI component inspiration
- [Chart.js](https://www.chartjs.org/) - Visualization library
- [Zustand](https://zustand-demo.pmnd.rs/) - State management
