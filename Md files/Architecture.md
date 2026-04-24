# NeuraChat — Website Architecture

This document is a complete specification of the NeuraChat website. It covers every visual element, every feature, every API contract, and every design decision. Use this file to rebuild the entire project in any framework or language.

---

## Overview

NeuraChat is a two-page AI web application. Page one is a real-time chat interface. Page two is a tools dashboard with six distinct AI-powered utilities. The backend is a REST API that proxies requests to Groq's LLM inference platform.

**Live URL:** `https://muneer.pythonanywhere.com`

---

## Design System

### Color Palette

All colors follow a pure black base with white text and white-opacity borders. There are no accent colors. The aesthetic is identical to Vercel's dashboard.

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#000000` | Page background |
| `--surface` | `#0a0a0a` | Sidebar, nav background |
| `--surface2` | `#111111` | Cards, input fields, bubbles |
| `--surface3` | `#1a1a1a` | Hover states, code blocks |
| `--surface4` | `#222222` | Deep nested elements |
| `--border` | `rgba(255,255,255,0.08)` | Default borders |
| `--border-mid` | `rgba(255,255,255,0.12)` | Input borders |
| `--border-bright` | `rgba(255,255,255,0.22)` | Focus states, active borders |
| `--text` | `#ededed` | Primary text |
| `--text-muted` | `#888888` | Labels, placeholders, secondary text |
| `--text-dim` | `#333333` or `#3a3a3a` | Disabled, hints |
| `--green` | `#4ade80` or `#22c55e` | Success states, live dot |
| `--red` | `#f87171` or `#ef4444` | Errors, offline dot |
| `--yellow` | `#facc15` or `#eab308` | Warnings, token bar overflow |

### Typography

| Font | Usage | Import |
|---|---|---|
| Inter | All body text, UI labels, buttons | Google Fonts |
| Geist Mono | Code blocks, token counters, monospace data | Google Fonts |

Font sizes used:
- Page titles: `20-24px`, weight `600`
- Section labels: `10-11px`, weight `600`, uppercase, letter-spacing `0.6-1px`
- Body text / messages: `13.5-14px`, weight `400`
- Small labels / hints: `10-11px`, weight `400-500`
- Button text: `13px`, weight `500`

### Border Radius

| Token | Value |
|---|---|
| `--radius` | `12px` — cards, message bubbles, input boxes |
| `--radius-sm` | `7-8px` — buttons, selects, small elements |
| `100px` | pill buttons, status badges |

### Spacing

Consistent spacing units: `4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `28px`, `32px`, `40px`.

### Favicon

SVG inline favicon, white triangle on transparent background:
```html
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><polygon points='12,2 2,19.5 22,19.5' fill='white'/></svg>">
```

---

## Page 1 — Chat (`/`)

### Layout

Two-column CSS Grid:
- Left column: fixed `240px` sidebar
- Right column: flexible `1fr` main area
- Full viewport height using `100dvh`

### Sidebar

**Top section — Logo**
- White `28x28px` rounded square (`6px` radius) containing a white triangle SVG (Vercel-style logo mark)
- Logo text "NeuraChat", `14px`, weight `600`, color `#fff`, letter-spacing `-0.3px`
- Bottom border separates from body

**Body section**
- "New conversation" button — full width, ghost style, left-aligned with `+` SVG icon, clears chat and resets server history on click
- Section label "MODEL" in uppercase dimmed text
- Model list — 6 clickable rows, each with model name and a tag badge
  - Llama 4 Scout — tag: "New"
  - Llama 3.3 70B — tag: "Smart"
  - Qwen QwQ 32B — tag: "Reasoning"
  - Mixtral 8x7B — tag: "Code"
  - Gemma 2 9B — tag: "Google"
  - Llama 3.1 8B — tag: "Fast"
  - Active model has `border-bright` border and white text
  - Clicking a model updates `selectedModel` variable, header badge, status bar text, shows toast
- Token usage box (hidden until first message)
  - Shows "Tokens used" label, number in mono font
  - Progress bar: white below 60%, yellow 60-80%, red above 80%
  - Max reference: 8000 tokens

**Footer section**
- "AI Tools" link with grid icon — navigates to `/tools`
- Status row: animated dot (green = online, red = error) + model name + "· Groq"

### Header

Sticky top bar:
- Left: hamburger menu button (mobile only, hidden on desktop), "Assistant" label, model name badge (truncated with ellipsis)
- Right: export button (download icon), clear button (trash icon)
- Both icon buttons are `30x30px` ghost style

### Chat Area

Scrollable flex container:
- Max width `680px`, centered with `margin: 0 auto`
- Padding `32px 20px`
- Custom scrollbar: `3px` wide, `surface3` color

**Empty state** (shown when no messages):
- Centered vertically in the chat area
- Icon box: `46x46px`, bordered, rounded, with chat bubble SVG
- Title: "What can I help with?", `20px`, weight `600`
- Subtitle: smaller muted text
- Suggestion grid: 2 columns, 4 cards
  - Each card has a bold title line and a dimmer example text
  - Clicking a card fills the input and sends immediately

**Message bubbles:**
- Each message is a flex row with avatar and content column
- User messages: `row-reverse` (right-aligned)
- AI messages: left-aligned
- Avatar: `27x28px` rounded square
  - AI: white background, black triangle SVG
  - User: `surface2` background, bordered, "U" text
- Bubble: padded box with `surface` background and `border` for AI, `surface2` and `border-mid` for user
- Top corner radius: `3px` on the side closest to the avatar (chat bubble effect)
- Below each bubble: timestamp (HH:MM format) + "Copy" text button
- Typing indicator: three animated dots when AI is processing
- All messages animate in with `fadeUp` keyframe

**Code blocks inside messages:**
- Header bar with language label (left) and Copy button (right)
- Copy button shows checkmark and "Copied" for 2 seconds after click
- Code rendered with `highlight.js` using `atom-one-dark` theme
- Font: Geist Mono, `12.5px`

### Input Area

Fixed to bottom of page:
- Input box: flex row, `surface` background, `border-mid` border, `12px` radius
- Textarea: auto-resizing, max height `120px`, placeholder "Message NeuraChat...", `16px` font on mobile
- Send button: `32x32px`, white background, black arrow SVG, `7px` radius, scales up on hover
- Below input: left hint text ("Enter to send · Shift+Enter for new line"), right character counter (shows only above 75% of 4000 char limit, turns yellow at limit)

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Enter` | Send message |
| `Shift+Enter` | New line in input |
| `Ctrl+K` | Focus input |
| `Ctrl+Shift+Delete` | Clear chat |
| `Escape` | Close sidebar (mobile) |

### Features

- **Chat memory**: conversation history maintained server-side, trimmed to last 20 messages
- **LocalStorage persistence**: last 30 messages saved to browser, restored on page reload
- **Export chat**: downloads full conversation as `.txt` file with timestamps
- **Token tracking**: cumulative token count shown in sidebar with visual bar
- **Status indicator**: dot turns red on server error, green on success
- **Model switching**: switch models mid-conversation, toast confirms change
- **Mobile sidebar**: overlay + slide-in drawer on screens below `700px`

---

## Page 2 — Tools (`/tools`)

### Layout

Three-part vertical stack:
1. Sticky top navigation bar
2. Horizontally scrollable mobile toolbar (hidden on desktop)
3. Mobile model selector bar (hidden on desktop)
4. Two-column layout: `220px` sidebar + flexible content area

On mobile (below `720px`): sidebar hides, mobile toolbar and model bar show.

### Navigation Bar

Height `54px`, sticky, blurred background:
- Left: logo (same as chat page) + vertical separator + nav links ("Chat", "Tools")
- Active page link has white text
- Padding `0 32px` desktop, `0 14px` mobile

### Desktop Sidebar

Width `220px`, sticky, full height:
- Section label "TOOLS"
- 6 navigation items, each with SVG icon and label text
- Active item: white text, `2px` left white border, `surface2` background
- Section divider
- Section label "MODEL"
- Single model `<select>` dropdown, same 5 options as chat page

### Mobile Toolbar

Horizontal scrollable row, `display:none` on desktop:
- 6 pill buttons, each with small SVG icon and short label
- Active pill: white background, black text
- Scrolls horizontally with touch, scrollbar hidden visually

### Mobile Model Bar

Thin bar below toolbar with "MODEL" label and full-width select dropdown.

### Tool Panels

All 6 panels exist in the DOM. Only one has `active` class and is visible at a time. Switching is instant with no network request.

---

### Tool 1 — Document Summarizer

**Inputs:**
- Large textarea: paste text, up to 15,000 characters, with character counter
- Format pills: Concise / Detailed / Bullet Points / Plain English

**Output:**
- Stats row: 4 cells showing Input Words, Summary Words, Reduction %, Tokens Used
- Result box with summary text
- Footer: word count + token count
- Copy and Download buttons

**API:** `POST /summarize`

Request body:
```json
{
  "text": "string (required, max 15000 chars)",
  "style": "concise | detailed | bullet | eli5",
  "model": "string"
}
```

Response:
```json
{
  "summary": "string",
  "tokens": "number",
  "word_count": "number"
}
```

---

### Tool 2 — Story Generator

**Inputs:**
- Textarea: story concept/prompt
- 3 selects: Genre (9 options), Tone (6 options), Length (3 options)
- 2 text inputs: Protagonist (optional), Setting (optional)

**Genres:** Adventure, Science Fiction, Fantasy, Horror, Romance, Mystery, Thriller, Comedy, Drama

**Tones:** Neutral, Dark, Comedic, Romantic, Suspenseful, Epic

**Lengths:** Short (~500 words), Medium (~800 words), Long (~1400 words)

**Output:**
- Story text, word count, token count
- "Continue Story" button appears after first generation, allows extending the story

**Loading state:** Rotating messages: "Writing your story...", "Developing characters...", "Building the world...", "Crafting the climax..."

**API:** `POST /story`

Request body:
```json
{
  "prompt": "string",
  "genre": "string",
  "tone": "string",
  "length": "short | medium | long",
  "protagonist": "string (optional)",
  "setting": "string (optional)",
  "model": "string",
  "continue_story": "string (empty for new, full story text for continuation)"
}
```

Response:
```json
{
  "story": "string",
  "tokens": "number"
}
```

---

### Tool 3 — Code Explainer

**Inputs:**
- Text input: language name (optional, e.g. "Python")
- Select: Analysis Mode (Line by Line / Overview / Bug Detection / Complexity Analysis)
- Textarea with monospace font: paste code, up to 10,000 characters

**Analysis modes:**
- Line by Line: explains each logical block in plain English with section headings
- Overview: high-level purpose, inputs, outputs
- Bug Detection: identifies errors, edge cases, and potential issues with fixes
- Complexity Analysis: Big-O notation for each function with optimization suggestions

**API:** `POST /explain-code`

Request body:
```json
{
  "code": "string (required, max 10000 chars)",
  "mode": "line-by-line | overview | debug | complexity",
  "language": "string (optional)",
  "model": "string"
}
```

Response:
```json
{
  "explanation": "string",
  "tokens": "number"
}
```

---

### Tool 4 — Quiz Generator

**Inputs:**
- Textarea: topic or source material to quiz on
- 3 controls: Question Type (MCQ / True-False / Short Answer), Difficulty (Easy / Medium / Hard), Number of Questions (number input, 3-15, capped at 15)

**Output format:**
- Questions numbered 1 to N
- MCQ: 4 options labeled A, B, C, D
- True/False: statement + True or False answer
- Short Answer: question + model answer
- Answer Key section at the bottom

**API:** `POST /quiz`

Request body:
```json
{
  "topic": "string (required)",
  "type": "mcq | true-false | short",
  "difficulty": "easy | medium | hard",
  "count": "number (3-15)",
  "model": "string"
}
```

Response:
```json
{
  "quiz": "string",
  "tokens": "number"
}
```

---

### Tool 5 — Email Writer

**Inputs:**
- Textarea: purpose/intent of the email
- 2 text inputs: Recipient, Sender name
- 3 selects: Tone, Length, Additional context (optional text input)

**Tones:** Professional, Formal, Friendly, Assertive, Apologetic

**Lengths:** Short (3-4 sentences), Medium (2-3 paragraphs), Detailed (4-5 paragraphs)

**Output format:**
- First line: `Subject: [subject line]`
- Full email body with greeting, content, sign-off
- No preamble or explanation outside the email text

**API:** `POST /email`

Request body:
```json
{
  "intent": "string (required)",
  "recipient": "string (optional)",
  "sender": "string (optional)",
  "tone": "professional | formal | friendly | assertive | apologetic",
  "length": "short | medium | detailed",
  "context": "string (optional)",
  "model": "string"
}
```

Response:
```json
{
  "email": "string",
  "tokens": "number"
}
```

---

### Tool 6 — Debate Generator

**Inputs:**
- Textarea: the debate topic or statement
- 2 selects: Perspective (Both Sides / For / Against), Depth (Brief 3pts / Standard 5pts / Deep 7pts)

**Output structure (Both Sides mode):**
- FOR section with numbered points
- AGAINST section with numbered points
- Conclusion section summarizing key tensions

**Single side mode:** numbered argument points only, no opposing section.

**API:** `POST /debate`

Request body:
```json
{
  "topic": "string (required)",
  "side": "both | for | against",
  "depth": "brief | standard | deep",
  "model": "string"
}
```

Response:
```json
{
  "debate": "string",
  "tokens": "number"
}
```

---

## Shared UI Patterns

### Buttons

**Primary button** — white background, black text, `7-8px` radius
- Hover: `#e2e2e2` background
- Disabled: `opacity 0.25`
- Contains SVG icon left of text

**Outline/Ghost button** — transparent background, `border-mid` border, muted text
- Hover: `surface3` background, `border-bright` border, white text

### Form Fields

All inputs and selects:
- Background: `surface2`
- Border: `border-mid` default, `border-bright` on focus
- Font: Inter, `13.5px` desktop, `16px` mobile (prevents iOS zoom)
- `8px` padding, `7px` radius

Select dropdowns have a custom chevron SVG as background-image, `appearance: none` to remove OS styling.

### Loading State

Each tool has a loading row with:
- `15x15px` spinning circle (CSS border animation)
- Text label describing the action

Shown by adding `show` class which changes `display` from `none` to `flex`.

### Result Box

- `surface2` background, `border` border, `7-8px` radius
- `pre-wrap` white-space to preserve newlines
- Max height `500px` with overflow scroll
- Custom `3px` scrollbar
- Header row: left label + right action buttons (Copy, Download)
- Footer row: word count left, token count right

### Toast Notifications

Fixed position, bottom-right:
- Default: `surface2` background, `border-mid` border
- Success (`.ok`): green border and text
- Error (`.err`): red border and text
- Auto-dismisses after `2500ms`
- On mobile: spans full width, centered

### Stats Row (Summarizer)

Horizontal flex row with no-gap cells, each cell bordered:
- 4 cells: Input Words, Summary Words, Reduction %, Tokens Used
- Each cell has a large number in mono font and a small uppercase label below
- On mobile: wraps to 2-column grid

---

## Backend API — Complete Reference

Base URL: `https://muneer.pythonanywhere.com`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serves `index.html` |
| GET | `/tools` | Serves `tools.html` |
| POST | `/chat` | Chat with conversation memory |
| POST | `/summarize` | Document summarization |
| POST | `/story` | Story generation and continuation |
| POST | `/explain-code` | Code analysis |
| POST | `/quiz` | Quiz generation |
| POST | `/email` | Email drafting |
| POST | `/debate` | Debate argument generation |
| POST | `/clear` | Reset conversation history |
| GET | `/health` | Server health check |
| GET | `/models` | List valid model names |

All POST routes accept and return `application/json`. All error responses follow the format:
```json
{ "error": "Human readable error message" }
```

HTTP status codes used: `200`, `400`, `401`, `429`, `500`.

---

## AI Models Available

All models are accessed via Groq API (base URL: `https://api.groq.com`).

| Model String | Description | Best For |
|---|---|---|
| `meta-llama/llama-4-scout-17b-16e-instruct` | Llama 4 Scout | General chat, default |
| `llama-3.3-70b-versatile` | Llama 3.3 70B | Tools, detailed tasks |
| `llama-3.1-8b-instant` | Llama 3.1 8B | Fast responses |
| `qwen-qwq-32b` | Qwen QwQ 32B | Reasoning tasks |
| `gemma2-9b-it` | Gemma 2 9B | Google model |
| `mixtral-8x7b-32768` | Mixtral 8x7B | Code tasks |

---

## TypeScript Rebuild Guide

### Recommended Stack

```
Frontend:  Next.js 14 (App Router) + TypeScript
Styling:   Tailwind CSS
AI:        Vercel AI SDK or direct fetch to Groq API
Hosting:   Vercel (frontend + API routes in one)
```

### Folder Structure

```
neurachat/
  ├── app/
  │   ├── page.tsx              # Chat page (index.html equivalent)
  │   ├── tools/
  │   │   └── page.tsx          # Tools page
  │   ├── layout.tsx            # Root layout with nav
  │   └── api/
  │       ├── chat/route.ts     # POST /api/chat
  │       ├── summarize/route.ts
  │       ├── story/route.ts
  │       ├── explain-code/route.ts
  │       ├── quiz/route.ts
  │       ├── email/route.ts
  │       └── debate/route.ts
  ├── components/
  │   ├── chat/
  │   │   ├── ChatArea.tsx
  │   │   ├── Message.tsx
  │   │   ├── InputBar.tsx
  │   │   ├── Sidebar.tsx
  │   │   └── TypingIndicator.tsx
  │   ├── tools/
  │   │   ├── Summarizer.tsx
  │   │   ├── StoryGenerator.tsx
  │   │   ├── CodeExplainer.tsx
  │   │   ├── QuizGenerator.tsx
  │   │   ├── EmailWriter.tsx
  │   │   └── DebateGenerator.tsx
  │   └── ui/
  │       ├── Button.tsx
  │       ├── Textarea.tsx
  │       ├── Select.tsx
  │       ├── PillGroup.tsx
  │       ├── ResultBox.tsx
  │       ├── Toast.tsx
  │       └── StatsRow.tsx
  ├── lib/
  │   ├── groq.ts               # Groq client setup
  │   ├── models.ts             # VALID_MODELS list + types
  │   └── storage.ts            # localStorage helpers
  ├── hooks/
  │   ├── useChat.ts            # Chat state and send logic
  │   ├── useToast.ts           # Toast state
  │   └── useMobile.ts          # window.innerWidth hook
  └── types/
      └── index.ts              # All TypeScript interfaces
```

### Key TypeScript Interfaces

```typescript
// types/index.ts

export interface Message {
  role: 'user' | 'ai';
  content: string;
  time: string;
}

export interface ChatResponse {
  reply: string;
  model: string;
  tokens: number | null;
}

export interface SummarizeRequest {
  text: string;
  style: 'concise' | 'detailed' | 'bullet' | 'eli5';
  model: string;
}

export interface SummarizeResponse {
  summary: string;
  tokens: number | null;
  word_count: number;
}

export interface StoryRequest {
  prompt: string;
  genre: string;
  tone: string;
  length: 'short' | 'medium' | 'long';
  protagonist?: string;
  setting?: string;
  model: string;
  continue_story?: string;
}

export interface CodeRequest {
  code: string;
  mode: 'line-by-line' | 'overview' | 'debug' | 'complexity';
  language?: string;
  model: string;
}

export interface QuizRequest {
  topic: string;
  type: 'mcq' | 'true-false' | 'short';
  difficulty: 'easy' | 'medium' | 'hard';
  count: number;
  model: string;
}

export interface EmailRequest {
  intent: string;
  recipient?: string;
  sender?: string;
  tone: 'professional' | 'formal' | 'friendly' | 'assertive' | 'apologetic';
  length: 'short' | 'medium' | 'detailed';
  context?: string;
  model: string;
}

export interface DebateRequest {
  topic: string;
  side: 'both' | 'for' | 'against';
  depth: 'brief' | 'standard' | 'deep';
  model: string;
}

export type ToolName = 'summarize' | 'story' | 'code' | 'quiz' | 'email' | 'debate';

export type ModelId =
  | 'meta-llama/llama-4-scout-17b-16e-instruct'
  | 'llama-3.3-70b-versatile'
  | 'llama-3.1-8b-instant'
  | 'qwen-qwq-32b'
  | 'gemma2-9b-it'
  | 'mixtral-8x7b-32768';

export interface ModelOption {
  id: ModelId;
  name: string;
  tag: string;
}
```

### Environment Variables

```bash
# .env.local
GROQ_API_KEY=gsk_your_key_here
NEXT_PUBLIC_APP_URL=https://your-domain.vercel.app
```

### Groq Client Setup

```typescript
// lib/groq.ts
import Groq from 'groq-sdk';

export const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

export async function callAI(
  messages: Array<{ role: string; content: string }>,
  model = 'llama-3.3-70b-versatile',
  maxTokens = 2048,
  temperature = 0.7
) {
  const response = await groq.chat.completions.create({
    model,
    messages,
    max_tokens: maxTokens,
    temperature,
  });
  return {
    content: response.choices[0].message.content,
    tokens: response.usage?.total_tokens ?? null,
  };
}
```

### Chat State with useChat Hook

```typescript
// hooks/useChat.ts
// Store messages in useState
// Store conversation history (for API) separately
// On send: add user message, call /api/chat, add AI response
// Persist to localStorage on every new message
// Load from localStorage on mount
```

### Important Behavior to Replicate

1. Conversation history is server-side state, trimmed to 20 messages. In Next.js API routes, use a module-level variable or Redis for multi-user support.
2. `fmt()` function must extract code blocks before processing newlines to avoid breaking syntax highlighting.
3. Input font-size must be `16px` on mobile to prevent iOS Safari zoom.
4. Use `100dvh` not `100vh` for full-height mobile layouts.
5. Blur the textarea on mobile immediately when sending, not after the AI responds.
6. Story continuation accumulates the full story client-side and sends it with each continuation request.
7. Model selection syncs between sidebar (desktop) and toolbar (mobile) using shared state.
8. Toast messages auto-dismiss after 2500ms.
9. All tool panels are rendered in the DOM simultaneously, toggled with CSS display/visibility not routing.

---

## Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| Above `720px` | Desktop: sidebar visible, mobile toolbar hidden |
| Below `720px` | Mobile: sidebar hidden, mobile toolbar shown, grids collapse to 1 column |
| Below `700px` | Chat page mobile: slide-in sidebar drawer, input blur on send |
| Below `380px` | Hide nav links and model badge in header |
