# NeuraChat — Full Code Explanation

This document explains every part of the codebase in detail. Every file, every function, every decision.

---

## Project Structure

```
project/
  ├── app.py          # Python Flask backend — handles all AI requests
  ├── index.html      # Chat page — main UI
  └── tools.html      # Tools page — summarizer, story, code, quiz, email, debate
```

---

## app.py — Backend

### Imports

```python
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
```

- `Flask` — the web framework. Creates the server and handles routing.
- `request` — lets us read incoming POST request data (JSON body).
- `jsonify` — converts Python dictionaries into JSON responses.
- `send_from_directory` — serves static HTML files from the disk.
- `CORS` — Cross-Origin Resource Sharing. Without this, the browser blocks requests from the frontend to the backend because they are on different ports or domains.
- `Groq` — the official Groq Python SDK. Used to call AI models.

---

### App Initialization

```python
app = Flask(__name__, static_folder=".")
CORS(app)
client = Groq(api_key="your_api_key_here")
```

- `Flask(__name__, static_folder=".")` — creates the Flask app. The dot means it looks for static files (HTML) in the same folder as app.py.
- `CORS(app)` — enables CORS for every route so the browser does not block API calls.
- `Groq(api_key=...)` — creates one global Groq client used by every route.

---

### Valid Models List

```python
VALID_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen-qwq-32b",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]
```

A whitelist of allowed model names. This prevents users from sending arbitrary strings as model names which could cause unexpected errors or abuse.

---

### call_ai() — Core AI Function

```python
def call_ai(messages, model="llama-3.3-70b-versatile", max_tokens=2048, temperature=0.7):
    if model not in VALID_MODELS:
        model = "llama-3.3-70b-versatile"
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content, response.usage.total_tokens if response.usage else None
```

This is a shared helper used by every tool route. It avoids copy-pasting the same API call in every function.

- `messages` — a list of `{role, content}` dicts. Role is either `"system"`, `"user"`, or `"assistant"`.
- `model` — which AI model to use. Defaults to 70B if invalid.
- `max_tokens` — limits how long the AI response can be. Each tool passes a different limit based on expected output length.
- `temperature` — controls creativity. `0.0` is deterministic, `1.0` is most creative. Summarization uses `0.4` (factual), story uses `0.85` (creative).
- Returns a tuple: `(reply_text, total_tokens_used)`.

---

### handle_error() — Centralized Error Handler

```python
def handle_error(e):
    err = str(e)
    if "rate_limit" in err.lower():
        return jsonify({"error": "Rate limit reached..."}), 429
    elif "invalid_api_key" in err.lower():
        return jsonify({"error": "Invalid API key..."}), 401
    elif "model_not_found" in err.lower():
        return jsonify({"error": "Selected model is not available..."}), 400
    else:
        return jsonify({"error": f"AI error: {err}"}), 500
```

Instead of repeating try/except logic in every route, all errors go through here. It checks the error string for known patterns and returns a specific HTTP status code and human-readable message.

- `429` — Too Many Requests (rate limit)
- `401` — Unauthorized (bad API key)
- `400` — Bad Request (model not found)
- `500` — Internal Server Error (anything else)

---

### Page Routes

```python
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/tools")
def tools():
    return send_from_directory(".", "tools.html")
```

These serve the HTML files when the user visits the URLs. `send_from_directory(".", filename)` looks in the current directory for the file.

---

### /chat Route

```python
@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    ...
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    conversation_history.append({"role": "user", "content": user_message})
    reply, tokens = call_ai(conversation_history, model=model)
    conversation_history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply, "model": model, "tokens": tokens})
```

- `global conversation_history` — accesses the module-level list that persists across requests. This is what gives the chat its memory.
- The history is trimmed to the last 20 messages to prevent hitting token limits. Groq models have a fixed context window and sending too many messages will cause an error.
- The user message is added before the AI call. If the AI fails, it is removed (`conversation_history.pop()`) so the chat does not get stuck in a broken state.
- Returns `reply`, `model`, and `tokens` so the frontend can display token usage.

---

### /summarize Route

```python
style_prompts = {
    "concise":  "Summarize the following text in 3-5 concise sentences...",
    "detailed": "Write a detailed summary...",
    "bullet":   "Summarize the text as a clean bullet-point list...",
    "eli5":     "Explain the following text as simply as possible...",
}
```

The summarizer takes a `style` parameter and selects the appropriate system prompt from the dictionary. The system prompt is what tells the AI how to behave. The actual text is sent as the user message.

- `max_tokens=1024` — summaries do not need to be as long as stories.
- `temperature=0.4` — lower temperature keeps the summary factual and not creative.

---

### /story Route

```python
if continue_story:
    system_msg = f"...Continue the following story..."
    user_msg = f"Continue this story:\n\n{continue_story}"
else:
    system_msg = f"...Write an engaging {genre} story..."
    user_msg = f"Write a story about: {prompt}"
```

The story route handles two modes: new story and continuation. When continuing, the full existing story text is sent back to the AI as context so it knows where to pick up from.

- `temperature=0.85` — high temperature for creative and varied writing.
- `max_tokens=2048` — stories need more space than summaries.

---

### /explain-code Route

```python
mode_prompts = {
    "line-by-line": "Explain this code in detail, section by section...",
    "overview":     "Give a high-level overview...",
    "debug":        "Review this code carefully. Identify any bugs...",
    "complexity":   "Analyze the time and space complexity...",
}
```

Four analysis modes, each with a tailored system prompt. The language hint (`lang_hint`) is prepended to help the AI understand the syntax context even though it can usually detect the language automatically.

- `temperature=0.3` — very low temperature for accurate technical analysis.
- `max_tokens=1500` — code explanations can be long but not as long as stories.

---

### /quiz Route

```python
count = min(int(data.get("count", 5)), 15)
```

The count is capped at 15 to prevent the AI from generating extremely long responses that would exceed token limits. The `min()` ensures even if someone sends `count=100` it becomes 15.

The system prompt instructs the AI to number questions consistently and always include an Answer Key section at the end, making it easy to read and use.

---

### /email Route

```python
system_msg = f"""...
Include a suitable subject line on the first line prefixed with 'Subject:'.
Then write the full email body...
Do not add any commentary or explanation outside the email itself."""
```

The key instruction here is the last line. Without it, AI models often add things like "Here is your email:" before the content, which would break copy-paste usability. The instruction forces the model to output only the email itself.

---

### /debate Route

```python
if side == "for":
    system_msg = f"...argument IN FAVOR..."
elif side == "against":
    system_msg = f"...argument AGAINST..."
else:
    system_msg = f"...Structure in two sections: FOR and AGAINST..."
```

Three modes handled with simple conditionals. The balanced mode instructs the AI to end with a Conclusion section, which adds educational value by highlighting the core tension in the debate.

---

### /health and /models Routes

```python
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "history_length": len(conversation_history)})

@app.route("/models", methods=["GET"])
def models():
    return jsonify({"models": VALID_MODELS})
```

Utility routes. `/health` can be polled to check if the server is alive and how long the conversation history is. `/models` exposes the model list in case a frontend needs to populate a dynamic dropdown.

---

## index.html — Chat Page

### Design System (CSS Variables)

```css
:root {
  --bg: #000;
  --surface: #0a0a0a;
  --surface2: #111;
  --border: rgba(255,255,255,0.08);
  --text: #ededed;
  --text-muted: #888;
  --font: 'Inter', sans-serif;
}
```

All colors are defined as CSS variables. This means changing the theme requires editing only these values at the top. Every other style references these variables rather than hard-coded colors.

The background is pure black (`#000`) with progressively lighter surfaces (`#0a0a0a`, `#111`, `#1a1a1a`) for layering. Borders use white with very low opacity to create subtle separation without harsh lines. This is the core of the Vercel-style aesthetic.

---

### Layout

```css
.app {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  height: 100dvh;
}
```

The app uses CSS Grid with two columns: a fixed-width sidebar and a flexible main area. `100dvh` (dynamic viewport height) is used instead of `100vh` because on mobile browsers, `100vh` includes the address bar height which causes overflow. `dvh` accounts for this correctly.

---

### fmt() — Message Formatter

```javascript
function fmt(text) {
  const blocks = [];
  text = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const hl = lang && hljs.getLanguage(lang)
      ? hljs.highlight(code.trim(), { language: lang }).value
      : hljs.highlightAuto(code.trim()).value;
    blocks.push(`<pre>...${hl}...</pre>`);
    return `%%BLOCK_${blocks.length - 1}%%`;
  });
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
  text = text.replace(/\n/g, '<br>');
  text = text.replace(/%%BLOCK_(\d+)%%/g, (_, i) => blocks[i]);
  return text;
}
```

This is the most important frontend function. It converts raw AI markdown output into formatted HTML.

The critical pattern here is the placeholder system. Code blocks are extracted first and replaced with `%%BLOCK_0%%` tokens. Then the rest of the text is processed (newlines to `<br>`, bold, italic, inline code). Finally the code blocks are restored. This prevents the `<br>` replacement from running inside code blocks, which would break syntax highlighting by inserting HTML tags into the middle of code.

---

### sendMsg() — Message Sender

```javascript
async function sendMsg() {
  const text = input.value.trim();
  if (!text) return;
  if (text.length > MAX_CHARS) { showToast(...); return; }

  input.value = ''; input.style.height = 'auto';
  btn.disabled = true;

  if (window.innerWidth <= 700) input.blur();

  addMsg('user', text);
  addTyping();

  try {
    const res = await fetch(`${API}/chat`, { ... });
    const data = await res.json();
    removeTyping();
    if (!res.ok) { showToast(data.error); addMsg('ai', ...); setStatus(false); }
    else { addMsg('ai', data.reply); updateTokens(data.tokens); setStatus(true); }
  } catch {
    removeTyping();
    addMsg('ai', 'Cannot reach server...');
    setStatus(false);
  }

  btn.disabled = false;
  if (window.innerWidth <= 700) input.blur(); else input.focus();
}
```

Key decisions in this function:

- `input.blur()` on mobile is called immediately when sending. This dismisses the virtual keyboard right away so the user can see the AI response without the keyboard blocking the screen.
- The button is disabled during the request to prevent duplicate submissions.
- `addTyping()` shows the animated dots while waiting. `removeTyping()` removes them before adding the real response.
- The catch block handles network failures separately from API errors. A network failure means the server is unreachable. An API error means the server responded but the AI call failed.

---

### localStorage — Chat Persistence

```javascript
function saveToStorage() {
  try { localStorage.setItem('neurachat_log', JSON.stringify(chatLog.slice(-30))); } catch {}
}

function loadFromStorage() {
  try {
    const saved = localStorage.getItem('neurachat_log');
    if (!saved) return;
    const log = JSON.parse(saved);
    ...
  } catch {}
}
```

The last 30 messages are saved to `localStorage` on every new message. When the page loads, `loadFromStorage()` is called to restore previous messages. Both functions are wrapped in try/catch because localStorage can fail in private browsing mode or when storage is full.

Note: localStorage only persists in the browser. The Flask server's `conversation_history` is reset when the server restarts. This means the visual chat history is restored but the AI does not actually remember the previous conversation after a server restart.

---

### Mobile Keyboard Fix

```javascript
#msg { font-size: 16px; }
```

This single CSS rule is important. iOS Safari automatically zooms into any input field with a font size below 16px. Setting it to exactly 16px prevents the zoom without making the text visibly larger than the rest of the UI.

---

## tools.html — Tools Page

### switchTool() — Navigation

```javascript
function switchTool(name, el) {
  document.querySelectorAll('.tool-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.side-item').forEach(i => i.classList.remove('active'));
  document.querySelectorAll('.mob-tool-btn').forEach(i => i.classList.remove('active'));
  document.getElementById('tool-' + name).classList.add('active');
  el.classList.add('active');
  document.querySelectorAll('[data-tool="' + name + '"]').forEach(i => i.classList.add('active'));
  if (window.innerWidth <= 720) window.scrollTo({ top: 0, behavior: 'smooth' });
}
```

The tools page uses a single-page application pattern without a router. All tool panels exist in the DOM simultaneously, only one has the `active` class at a time. Switching tools just moves the `active` class.

The function syncs both the sidebar items and mobile toolbar buttons simultaneously using `data-tool` attributes, ensuring both navs stay in sync regardless of which one was clicked.

---

### callAPI() — Shared Fetch Helper

```javascript
async function callAPI(endpoint, body, loadingPrefix, btnId) {
  setLoading(loadingPrefix, true, btnId);
  document.getElementById(loadingPrefix + '-result').classList.remove('show');
  try {
    const res = await fetch(API + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...body, model: getModel() })
    });
    const data = await res.json();
    setLoading(loadingPrefix, false, btnId);
    if (!res.ok) { toast(data.error || 'An error occurred', 'err'); return null; }
    return data;
  } catch {
    setLoading(loadingPrefix, false, btnId);
    toast('Cannot reach server...', 'err');
    return null;
  }
}
```

All 6 tools share this function. The `loadingPrefix` pattern (`sum`, `story`, `code`, `quiz`, `email`, `debate`) maps to element IDs like `sum-loading`, `sum-result`, `sum-btn`. This avoids writing the same loading/error logic 6 times.

The model is injected via `{ ...body, model: getModel() }` — the spread operator merges the tool-specific body with the selected model, so individual tool functions do not need to think about the model.

---

### Story Continuation

```javascript
let storyFull = "";

async function runStory(isContinue) {
  ...
  storyFull = isContinue ? storyFull + '\n\n' + data.story : data.story;
  ...
}
```

The `storyFull` variable accumulates the story across multiple continuation requests. When continuing, it sends the full accumulated story to the backend, and appends the new segment to it. This creates a continuously growing narrative that the AI always has full context for.

---

### Mobile Toolbar

```html
<div class="mobile-toolbar" id="mobile-toolbar">
  <button class="mob-tool-btn active" data-tool="summarize" onclick="switchTool('summarize',this)">
    ...
  </button>
  ...
</div>
```

On screens wider than 720px, the sidebar is visible and the mobile toolbar is hidden (`display:none`). On mobile, the sidebar hides and the toolbar appears. Both use the same `data-tool` attributes and `switchTool()` function, so they are kept in sync automatically.

The toolbar uses `overflow-x: auto` with `scrollbar-width: none` to create a horizontally scrollable row that hides the scrollbar visually but remains scrollable via touch.

---

## Deployment — PythonAnywhere

### WSGI File

```python
import sys
path = '/home/yourusername'
if path not in sys.path:
    sys.path.append(path)
from app import app as application
```

PythonAnywhere uses WSGI (Web Server Gateway Interface) to run Flask. The WSGI file is the entry point the server calls. It adds the project directory to Python's module search path and imports the Flask `app` object as `application` which is the name PythonAnywhere expects.

### Why app.run() is Removed

```python
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)
```

`app.run()` is only used when running Flask directly via `python app.py`. On PythonAnywhere, the WSGI server manages starting and stopping the app. Leaving `app.run()` in could cause conflicts.

---

## Key Limitations of Current Architecture

- `conversation_history` is a single global list. If two users use the chat simultaneously, their conversations mix together. A production app would store history per session using `flask-session` or a database.
- There is no authentication. Anyone who knows the URL can use the API and consume your Groq credits.
- The API key is hardcoded in `app.py`. In production it should be stored as an environment variable using `os.environ.get("GROQ_API_KEY")`.
- Story continuation state (`storyFull`) is stored in the browser's JavaScript memory. If the page refreshes, the story is lost even though the visual output is gone too.
