from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

app = Flask(__name__, static_folder=".")
CORS(app)

load_dotenv()
api_key = os.getenv("GROK_API_KEY")
client = Groq(api_key=api_key)
conversation_history = []

VALID_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen-qwq-32b",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

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

def handle_error(e):
    err = str(e)
    if "rate_limit" in err.lower():
        return jsonify({"error": "Rate limit reached. Please wait a moment and try again."}), 429
    elif "invalid_api_key" in err.lower():
        return jsonify({"error": "Invalid API key. Check your Groq key in app.py."}), 401
    elif "model_not_found" in err.lower():
        return jsonify({"error": "Selected model is not available on your plan."}), 400
    else:
        return jsonify({"error": f"AI error: {err}"}), 500

# ── Pages ──
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/tools")
def tools():
    return send_from_directory(".", "tools.html")

# ── Chat ──
@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history
    data = request.json
    user_message = data.get("message", "").strip()
    model = data.get("model", "meta-llama/llama-4-scout-17b-16e-instruct")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]

    conversation_history.append({"role": "user", "content": user_message})
    try:
        reply, tokens = call_ai(conversation_history, model=model)
        conversation_history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply, "model": model, "tokens": tokens})
    except Exception as e:
        conversation_history.pop()
        return handle_error(e)

# ── Summarize ──
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    text  = data.get("text", "").strip()
    style = data.get("style", "concise")
    model = data.get("model", "llama-3.3-70b-versatile")

    if not text:
        return jsonify({"error": "No text provided"}), 400
    if len(text) > 15000:
        return jsonify({"error": "Text too long. Maximum 15,000 characters."}), 400

    style_prompts = {
        "concise":  "Summarize the following text in 3-5 concise sentences. Be clear and direct.",
        "detailed": "Write a detailed summary covering all key points, arguments, and conclusions in structured paragraphs.",
        "bullet":   "Summarize the text as a clean bullet-point list. Use a dash (-) as the bullet symbol. One key idea per bullet.",
        "eli5":     "Explain the following text as simply as possible, as if explaining to a 12-year-old. Use plain language and short sentences.",
    }

    try:
        reply, tokens = call_ai([
            {"role": "system", "content": style_prompts.get(style, style_prompts["concise"])},
            {"role": "user", "content": text}
        ], model=model, max_tokens=1024, temperature=0.4)
        return jsonify({"summary": reply, "tokens": tokens, "word_count": len(text.split())})
    except Exception as e:
        return handle_error(e)

# ── Story ──
@app.route("/story", methods=["POST"])
def story():
    data = request.json
    prompt        = data.get("prompt", "").strip()
    genre         = data.get("genre", "adventure")
    length        = data.get("length", "medium")
    tone          = data.get("tone", "neutral")
    protagonist   = data.get("protagonist", "")
    setting       = data.get("setting", "")
    model         = data.get("model", "llama-3.3-70b-versatile")
    continue_story = data.get("continue_story", "")

    if not prompt and not continue_story:
        return jsonify({"error": "Please provide a story prompt"}), 400

    length_map = {"short": "400-600 words", "medium": "700-1000 words", "long": "1200-1600 words"}
    word_target = length_map.get(length, "700-1000 words")
    extras = []
    if protagonist: extras.append(f"Main character: {protagonist}")
    if setting:     extras.append(f"Setting: {setting}")
    extra_str = ". ".join(extras) + "." if extras else ""

    if continue_story:
        system_msg = f"You are a creative writer. Continue the following story. Keep the same tone, style, and characters. Add {word_target}. Genre: {genre}. Tone: {tone}. {extra_str} Do NOT summarize — continue writing from where it left off."
        user_msg = f"Continue this story:\n\n{continue_story}"
    else:
        system_msg = f"You are a creative fiction writer. Write an engaging {genre} story. Length: {word_target}. Tone: {tone}. {extra_str} Structure: Hook, rising action, climax, resolution. Use vivid descriptions and strong dialogue."
        user_msg = f"Write a story about: {prompt}"

    try:
        reply, tokens = call_ai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ], model=model, max_tokens=2048, temperature=0.85)
        return jsonify({"story": reply, "tokens": tokens})
    except Exception as e:
        return handle_error(e)

# ── Code Explainer ──
@app.route("/explain-code", methods=["POST"])
def explain_code():
    data = request.json
    code    = data.get("code", "").strip()
    mode    = data.get("mode", "line-by-line")  # line-by-line | overview | debug | complexity
    lang    = data.get("language", "")
    model   = data.get("model", "llama-3.3-70b-versatile")

    if not code:
        return jsonify({"error": "No code provided"}), 400
    if len(code) > 10000:
        return jsonify({"error": "Code too long. Maximum 10,000 characters."}), 400

    lang_hint = f"The code is written in {lang}. " if lang else ""

    mode_prompts = {
        "line-by-line": f"{lang_hint}Explain this code in detail, section by section. For each logical block or important line, explain what it does and why. Use clear plain English. Format with clear section headings.",
        "overview":     f"{lang_hint}Give a high-level overview of what this code does. Explain its purpose, inputs, outputs, and overall logic in plain English. Keep it concise and beginner-friendly.",
        "debug":        f"{lang_hint}Review this code carefully. Identify any bugs, logical errors, edge cases, or potential issues. For each issue found, explain what is wrong and how to fix it. If the code looks correct, say so.",
        "complexity":   f"{lang_hint}Analyze the time and space complexity of this code. Explain Big-O notation for each function or block. Also suggest any performance improvements if applicable.",
    }

    try:
        reply, tokens = call_ai([
            {"role": "system", "content": mode_prompts.get(mode, mode_prompts["line-by-line"])},
            {"role": "user", "content": code}
        ], model=model, max_tokens=1500, temperature=0.3)
        return jsonify({"explanation": reply, "tokens": tokens})
    except Exception as e:
        return handle_error(e)

# ── Quiz Generator ──
@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.json
    topic      = data.get("topic", "").strip()
    count      = min(int(data.get("count", 5)), 15)
    difficulty = data.get("difficulty", "medium")  # easy | medium | hard
    qtype      = data.get("type", "mcq")            # mcq | true-false | short
    model      = data.get("model", "llama-3.3-70b-versatile")

    if not topic:
        return jsonify({"error": "Please provide a topic"}), 400

    type_instructions = {
        "mcq":        f"Generate {count} multiple choice questions. Each must have exactly 4 options labeled A, B, C, D and one correct answer.",
        "true-false": f"Generate {count} true/false questions. Each must clearly state whether the answer is True or False.",
        "short":      f"Generate {count} short answer questions. Each must include a concise model answer.",
    }

    system_msg = f"""You are an expert quiz maker. {type_instructions.get(qtype, type_instructions['mcq'])}
Difficulty: {difficulty}. Topic: {topic}.
Format each question clearly and consistently, numbered 1 to {count}.
After all questions, provide an Answer Key section with all correct answers listed clearly."""

    try:
        reply, tokens = call_ai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Generate a {difficulty} {qtype} quiz on: {topic}"}
        ], model=model, max_tokens=2000, temperature=0.5)
        return jsonify({"quiz": reply, "tokens": tokens})
    except Exception as e:
        return handle_error(e)

# ── Email Writer ──
@app.route("/email", methods=["POST"])
def email():
    data = request.json
    intent    = data.get("intent", "").strip()
    tone      = data.get("tone", "professional")     # professional | friendly | formal | assertive | apologetic
    recipient = data.get("recipient", "")
    sender    = data.get("sender", "")
    context   = data.get("context", "")
    length    = data.get("length", "medium")          # short | medium | detailed
    model     = data.get("model", "llama-3.3-70b-versatile")

    if not intent:
        return jsonify({"error": "Please describe the purpose of the email"}), 400

    length_map = {"short": "3-4 sentences", "medium": "2-3 short paragraphs", "detailed": "4-5 detailed paragraphs"}
    length_str = length_map.get(length, "2-3 short paragraphs")

    recipient_str = f"The email is addressed to: {recipient}. " if recipient else ""
    sender_str    = f"The sender's name is: {sender}. " if sender else ""
    context_str   = f"Additional context: {context}. " if context else ""

    system_msg = f"""You are a professional email writer. Write a complete, ready-to-send email.
Tone: {tone}. Length: {length_str}.
{recipient_str}{sender_str}{context_str}
Include a suitable subject line on the first line prefixed with 'Subject:'.
Then write the full email body with proper greeting, content, and sign-off.
Do not add any commentary or explanation outside the email itself."""

    try:
        reply, tokens = call_ai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Write an email to: {intent}"}
        ], model=model, max_tokens=1000, temperature=0.6)
        return jsonify({"email": reply, "tokens": tokens})
    except Exception as e:
        return handle_error(e)

# ── Debate Generator ──
@app.route("/debate", methods=["POST"])
def debate():
    data = request.json
    topic   = data.get("topic", "").strip()
    side    = data.get("side", "both")   # for | against | both
    depth   = data.get("depth", "standard")  # brief | standard | deep
    model   = data.get("model", "llama-3.3-70b-versatile")

    if not topic:
        return jsonify({"error": "Please provide a debate topic"}), 400

    depth_map = {"brief": "3 key points per side", "standard": "5 key points per side", "deep": "7 detailed points per side with supporting evidence"}
    depth_str = depth_map.get(depth, "5 key points per side")

    if side == "for":
        system_msg = f"You are an expert debater. Construct a strong, well-reasoned argument IN FAVOR of the following topic. Provide {depth_str}. Use evidence, logic, and persuasive language. Format clearly with numbered points."
    elif side == "against":
        system_msg = f"You are an expert debater. Construct a strong, well-reasoned argument AGAINST the following topic. Provide {depth_str}. Use evidence, logic, and persuasive language. Format clearly with numbered points."
    else:
        system_msg = f"""You are an expert debate analyst. Present a balanced, objective debate on the given topic.
Structure your response in two clearly labeled sections: FOR and AGAINST.
Provide {depth_str}. Use evidence, logic, and clear language.
End with a brief Conclusion section noting the key tension points of the debate."""

    try:
        reply, tokens = call_ai([
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Debate topic: {topic}"}
        ], model=model, max_tokens=2000, temperature=0.6)
        return jsonify({"debate": reply, "tokens": tokens})
    except Exception as e:
        return handle_error(e)

# ── Misc ──
@app.route("/clear", methods=["POST"])
def clear():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "cleared"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "history_length": len(conversation_history)})

@app.route("/models", methods=["GET"])
def models():
    return jsonify({"models": VALID_MODELS})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
