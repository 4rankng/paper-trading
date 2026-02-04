# TermAI Explorer - Design Specification

## Product Vision

TermAI Explorer is a **modern AI-native terminal interface** that reimagines the command line for the age of intelligent assistants. It combines the power and efficiency of CLI workflows with the intelligence of Claude AI, featuring **inline visualizations that render directly in the terminal output stream**.

**Target Users**: Developers, data scientists, AI researchers, and power users who live in the terminal but want modern AI capabilities without leaving their workflow.

**Core Value Proposition**:
- **Seamless AI Integration**: Chat with Claude directly in your terminal
- **Native Visualizations**: Charts, tables, and data render inline within the message flow
- **Persistent Knowledge**: RAG-powered conversation history that builds context over time
- **Modern UX**: Smooth animations, keyboard-first navigation, dark/light modes
- **Privacy-First**: Local-first storage with optional cloud sync

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     TermAI Explorer                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer          │  Backend Layer                   │
│  ──────────────          │  ─────────────                   │
│  • Next.js 14 App Router │  • Next.js API Routes            │
│  • React Server Comp     │  • Claude API Integration        │
│  • Hybrid Terminal UI    │  • Ollama (Local Embeddings)     │
│  • Tailwind CSS          │  • ChromaDB Vector Store         │
│  • TypeScript            │  • File System Storage           │
└─────────────────────────────────────────────────────────────┘
```

**Monorepo Structure**:
```
paper-trading/
├── webapp/                 # Next.js application
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   │   ├── terminal/      # Terminal components
│   │   │   ├── HybridTerminal.tsx  # Main terminal (input + inline viz)
│   │   │   ├── TerminalOutput.tsx  # Message renderer with viz
│   │   │   ├── TitleBar.tsx        # Window controls
│   │   │   ├── TabBar.tsx          # Session tabs
│   │   │   └── StatusBar.tsx       # Session info
│   │   └── visualizations/ # Inline viz components
│   │       ├── Chart.tsx          # Line/bar/scatter charts
│   │       ├── Table.tsx          # Data tables
│   │       ├── PieChart.tsx       # Pie charts
│   │       └── VizRenderer.tsx    # Viz router
│   ├── lib/               # Utilities, API clients
│   │   ├── themes.ts      # Theme configurations
│   │   ├── viz-parser.ts  # Visualization syntax parser
│   │   ├── storage.ts     # Session persistence
│   │   └── data-access.ts # File I/O utilities
│   ├── store/             # State management
│   │   └── useTerminalStore.ts    # Zustand store
│   └── types/             # TypeScript definitions
├── filedb/                # Persistent data storage
│   ├── embeddings/        # Vector embeddings
│   ├── sessions/          # Conversation history
│   └── cache/             # Response cache
├── Makefile               # Dev orchestration
└── DESIGN.md              # This file
```

---

## UI Layout (Inline Visualization Design)

```
┌─────────────────────────────────────────────────────────────┐
│ Title Bar (40px)                                            │
│ [● ● ●]  TermAI Explorer                            [⚙] [☀] │
├─────────────────────────────────────────────────────────────┤
│ Tab Bar (36px)                                              │
│ [Session 1] [Session 2] [+]                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Message Output Area (flex-1, scrollable)              │ │
│  │                                                        │ │
│  │ ┌──────────────────────────────────────────────────┐  │ │
│  │ │ ➜ user@termai:~$ analyze AAPL                    │  │ │
│  │ └──────────────────────────────────────────────────┘  │ │
│  │ ┌──────────────────────────────────────────────────┐  │ │
│  │ │ → assistant: Analyzing Apple Inc...              │  │ │
│  │ │                                                  │  │ │
│  │ │ Based on recent data...                          │  │ │
│  │ │                                                  │  │ │
│  │ │ ┌────────────────────────────────────────────┐   │  │ │
│  │ │ │ 📊 Price Chart (inline)                   │   │  │ │
│  │ │ │ [Chart.js canvas rendered here]           │   │  │ │
│  │ │ └────────────────────────────────────────────┘   │  │ │
│  │ │                                                  │  │ │
│  │ │ ┌────────────────────────────────────────────┐   │  │ │
│  │ │ │ 📋 Financial Metrics (inline)             │   │  │ │
│  │ │ │ [Table with sortable columns]             │   │  │ │
│  │ │ └────────────────────────────────────────────┘   │  │ │
│  │ │                                                  │  │ │
│  │ └──────────────────────────────────────────────────┘  │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ Terminal Input Area (80px)                                   │
│ [xterm.js terminal instance - 3 rows]                       │
│ ➜ user@termai:~$ █                                          │
├─────────────────────────────────────────────────────────────┤
│ Status Bar (24px)                                            │
│ Session: abc12345 | 12 messages | Clear | Settings | Ready │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Single Column Layout**: No sidebar, no separate panels. Everything flows vertically.
2. **Inline Visualizations**: Charts and tables appear directly in the message stream, mixed with text.
3. **Native Terminal Feel**: Input area uses xterm.js for authentic terminal behavior.
4. **Hybrid Rendering**: Text content rendered via React (for markdown + viz), input via xterm.js.

---

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router, Server Components)
- **UI Library**: React 18 + Tailwind CSS v3
- **Terminal**: xterm.js 5.3.0 (for input only)
- **Visualizations**: Chart.js with react-chartjs-2
- **State**: Zustand (lightweight, TypeScript-first)
- **Icons**: Lucide React (consistent, tree-shakeable)

### Backend
- **API**: Next.js Route Handlers
- **AI SDK**: Anthropic Claude SDK (@anthropic-ai/sdk)
- **Vector DB**: ChromaDB (persistent, local-first)
- **Embeddings**: Ollama (nomic-embed-text model)
- **Storage**: JSON file system (./filedb/)

### Developer Experience
- **Language**: TypeScript 5.3+ (strict mode)
- **Linting**: ESLint + Prettier
- **Testing**: Vitest + Playwright
- **CLI**: Turbo (monorepo orchestration)

---

## Component Architecture

### HybridTerminal - Main Terminal Component

**Purpose**: Combines xterm.js input with React-based message output.

**Architecture**:
```
HybridTerminal
├── [Scrollable Message Output]
│   └── TerminalOutput
│       └── MessageContent
│           ├── Text (ReactMarkdown)
│           └── Visualizations (VizRenderer)
│               ├── Chart.tsx
│               ├── Table.tsx
│               └── PieChart.tsx
│
└── [xterm.js Input Area]
    └── 3-row terminal for authentic typing
```

**Key Features**:
- xterm.js configured with `scrollback: 0`, `rows: 3` (input only)
- Messages rendered in React scrollable container above input
- Auto-scroll to bottom on new messages
- Real-time streaming updates

**Props**:
```typescript
interface HybridTerminalProps {
  className?: string;
}
```

### TerminalOutput - Message Renderer

**Purpose**: Renders messages with inline visualizations.

**Flow**:
1. Parse message content for visualization markers
2. Split content into text and visualization parts
3. Render text with ReactMarkdown
4. Render visualizations inline via VizRenderer

**Example Output**:
```
→ assistant: Here's your analysis

Based on recent data, AAPL shows...

┌─────────────────────────────────────────┐
│ 📊 AAPL Price History (Last 30 Days)   │
│ [Chart.js Line Chart]                   │
└─────────────────────────────────────────┘

Key metrics:

┌─────────────────────────────────────────┐
│ 📋 Financial Data                       │
│ ┌───────┬──────┬───────┐               │
│ │ Metric│ Value │ Change│               │
│ ├───────┼──────┼───────┤               │
│ │ Price │ $178  │ +2.3% │               │
│ └───────┴──────┴───────┘               │
└─────────────────────────────────────────┘

Recommendation: BUY at $175-180
```

### VizRenderer - Visualization Router

**Purpose**: Routes visualization commands to appropriate components.

**Supported Types**:
- `chart`: Line, bar, scatter, area charts
- `table`: Sortable data tables
- `pie`: Pie/donut charts

---

## Visualization Syntax

### Markdown-like Syntax

Visualizations use special markdown-like syntax in AI responses:

```markdown
Analyzing AAPL stock performance...

![viz:chart]({"type":"chart","chartType":"line","data":{"labels":["1/1","1/2","1/3"],"datasets":[{"label":"Price","data":[175,178,180]}]},"options":{"plugins":{"title":{"display":true,"text":"AAPL Price"}}}})

Key metrics:

![viz:table]({"type":"table","headers":["Metric","Value","Change"],"rows":[["Price","$178","+2.3%"],["Volume","45M","-5%"]],"options":{"caption":"Financial Metrics","sortable":true}})

Recommendation: Buy at $175-180
```

### Parsing & Rendering

1. **Parser** (`lib/viz-parser.ts`) extracts viz commands from text
2. **Split**: Content split into text and viz parts
3. **Render**: Text → ReactMarkdown, Viz → VizRenderer
4. **Inline**: Visualizations render directly in message flow

---

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

---

## Typography

- **Primary Font**: Fira Code (monospace)
- **Fallbacks**: Source Code Pro, Monaco, Courier New
- **Terminal Size**: 14px
- **UI Size**: 13-14px
- **Anti-aliasing**: Enabled (-webkit-font-smoothing: antialiased)

---

## Terminal Features

### Command Input (xterm.js)

- Real-time character input rendering
- Command history navigation (Up/Down arrows)
- Backspace handling
- Ctrl+C to cancel current input
- Custom prompt: `➜ user@termai:~$`

### Configuration

```typescript
const terminal = new Terminal({
  theme: getXtermTheme('oneDark'),
  fontFamily: 'Fira Code',
  fontSize: 14,
  lineHeight: 1.2,
  cursorBlink: true,
  cursorStyle: 'block',
  scrollback: 0,        // No scrollback - output in React
  rows: 3,              // Just enough for input
  tabStopWidth: 4
});
```

### Streaming Responses

- Server-Sent Events (SSE) for real-time streaming
- Messages render in React container (not terminal)
- Visualizations extracted and rendered inline
- Auto-scroll to latest message

---

## State Management (Zustand)

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
  setTheme(theme: string): void;
}
```

**Note**: Visualizations are stored within messages (`message.visualizations: VizCommand[]`), not as separate state.

---

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

```typescript
// Via store action
useTerminalStore.getState().setTheme('dracula');

// Via direct function
applyTheme('githubDark');
```

---

## API Integration

### Chat Endpoint

**POST** `/api/chat`

```typescript
{
  message: string;
  session_id: string;
}
```

Returns SSE stream:
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

---

## Performance Optimizations

### Dynamic Imports

xterm.js components are dynamically imported with SSR disabled:

```typescript
const HybridTerminal = dynamic(
  () => import('@/components/terminal/HybridTerminal'),
  { ssr: false }
);
```

### useEffect Dependencies

Terminal initialization only runs once using refs:

```typescript
useEffect(() => {
  if (!terminalRef.current || xtermRef.current) return;
  // Initialize xterm.js
}, []);
```

### Resize Handling

FitAddon automatically adjusts terminal size on window resize with debouncing.

---

## Responsive Design

- **Mobile**: Full-width input, messages take 100% width
- **Tablet**: Same layout, optimized touch targets
- **Desktop**: Max-width container (1200px) centered

**Visualizations** adapt to container width automatically via Chart.js `responsive: true`.

---

## Accessibility

- Keyboard navigation for tabs (Tab/Shift+Tab)
- Aria labels on all buttons
- Focus indicators on interactive elements
- Screen reader friendly text alternatives
- Tables have proper headers for navigation

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Submit command |
| `Shift + Enter` | New line (multiline input) |
| `↑ / ↓` | Navigate command history |
| `Ctrl + C` | Cancel input |
| `Ctrl + L` | Clear messages (planned) |

---

## Development Workflow

### Makefile Commands

```makefile
# Start development environment
dev:
	@mkdir -p filedb/{embeddings,sessions,cache}
	@cd webapp && npm run dev

# Build for production
build:
	@cd webapp && npm run build

# Run tests
test:
	@cd webapp && npm run test

# Lint code
lint:
	@cd webapp && npm run lint

# Clean artifacts
clean:
	@rm -rf webapp/.next webapp/node_modules
```

### Environment Variables

```bash
# .env.local
ANTHROPIC_API_KEY=sk-ant-xxx
NEXT_PUBLIC_APP_URL=http://localhost:3000
OLLAMA_BASE_URL=http://localhost:11434
CHROMADB_PATH=./filedb/embeddings
```

---

## Design Principles

1. **Content First**: UI recedes, conversation takes center stage
2. **Native Visualizations**: Charts/tables inline, not in separate panels
3. **Terminal Authenticity**: Real xterm.js for input, not a fake input field
4. **Performance**: Fast rendering with efficient state management
5. **Accessibility**: Keyboard-first, screen reader friendly
6. **Extensibility**: Easy to add new visualization types

---

## Roadmap

### Phase 1: MVP ✅
- [x] Hybrid terminal with xterm.js input + React output
- [x] Claude integration with streaming
- [x] Session persistence (JSON)
- [x] Inline visualizations (chart, table, pie)
- [x] Dark mode (One Dark theme)

### Phase 2: Enhanced 🚧
- [ ] RAG with ChromaDB + Ollama embeddings
- [ ] Light/dark mode toggle
- [ ] Multi-session management
- [ ] Export sessions (Markdown, JSON)
- [ ] Command palette (Cmd+K)

### Phase 3: Advanced 🔮
- [ ] Multi-model support (GPT-4, Claude 3.5)
- [ ] Voice input (Web Speech API)
- [ ] Session sharing (public/private links)
- [ ] More visualization types (heatmaps, treemaps)
- [ ] Custom themes system

### Phase 4: Platform 🌟
- [ ] Cloud sync (optional)
- [ ] Team workspaces
- [ ] API access (webhooks)
- [ ] Analytics dashboard
- [ ] Self-hosted option

---

## Key Differences from Original Design

| Aspect | Old Design (VizPanel) | New Design (Inline) |
|--------|----------------------|---------------------|
| Layout | Split pane (terminal + sidebar) | Single column |
| Viz Placement | Separate 384px sidebar | Inline in message flow |
| Terminal Usage | xterm.js for input + output | xterm.js for input only |
| Message Rendering | xterm.js text stream | React components |
| UX Flow | Text → placeholder → panel | Text + viz mixed naturally |

---

## Resources

- [xterm.js Documentation](https://xtermjs.org/)
- [Next.js 14 App Router](https://nextjs.org/docs/app)
- [Chart.js](https://www.chartjs.org/) - Visualization library
- [Zustand](https://zustand-demo.pmnd.rs/) - State management
- [Tailwind CSS](https://tailwindcss.com/) - Styling
