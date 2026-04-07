import os
import uuid
import json
import datetime

os.environ.pop("SSL_CERT_FILE", None)
os.environ.pop("REQUESTS_CA_BUNDLE", None)

try:
    exec(open("./fix_gradio.py", encoding="utf-8").read())
except Exception as e:
    print(f"⚠️ Patch failed (will continue): {e}")

import gradio as gr
from groq import Groq

# Detect Gradio major version for compatibility
_GR_MAJOR = int(gr.__version__.split(".")[0])
# Gradio 6+ uses messages format by default; Gradio 4/5 needs type="messages" or tuples
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=api_key)

# ── Persona definitions ────────────────────────────────────────────────────────

PERSONAS = {
    "🤖 Maya — ML Engineer": {
        "name": "Maya",
        "system_prompt": (
            "You are Maya, an expert Machine Learning Engineer mentor. "
            "You specialize in teaching ML concepts clearly: supervised/unsupervised learning, "
            "neural networks, model training, evaluation metrics, overfitting, regularization, "
            "transformers, and ML pipelines. You give practical, example-driven answers. "
            "Keep responses concise (3-5 sentences) unless a deeper explanation is explicitly requested. "
            "You use analogies to make complex ideas accessible. "
            "You remember the user's previous questions in this session and build on them naturally. "
            "Do NOT answer questions outside ML/AI topics — politely redirect the user."
        ),
        "examples": [
            "What is overfitting and how do I fix it?",
            "Explain gradient descent simply.",
            "What's the difference between bagging and boosting?",
        ],
    },
    "🐍 Leo — Python Coach": {
        "name": "Leo",
        "system_prompt": (
            "You are Leo, a friendly and sharp Python coding coach. "
            "You help learners understand Python fundamentals, data structures, OOP, "
            "decorators, generators, list comprehensions, pandas, numpy, and writing clean Pythonic code. "
            "Always include short code snippets in your answers when relevant. "
            "Keep responses concise (3-5 sentences + code block) unless asked to elaborate. "
            "You remember the user's previous questions in this session and build on them naturally. "
            "Do NOT answer questions outside Python/coding topics — politely redirect the user."
        ),
        "examples": [
            "Explain list comprehensions with an example.",
            "What are Python decorators?",
            "How do I use *args and **kwargs?",
        ],
    },
    "✨ Aria — AI Concepts Guide": {
        "name": "Aria",
        "system_prompt": (
            "You are Aria, a knowledgeable AI concepts guide and quiz master. "
            "You explain AI fundamentals: generative AI, LLMs, prompt engineering, embeddings, "
            "RAG, fine-tuning, RLHF, and AI ethics. You also love testing knowledge with quick quizzes. "
            "Keep responses concise (3-5 sentences) unless a deeper explanation is explicitly requested. "
            "When the user says 'quiz me', generate a multiple-choice question on an AI topic. "
            "You remember the user's previous questions in this session and build on them naturally. "
            "Do NOT answer questions outside AI concepts — politely redirect the user."
        ),
        "examples": [
            "What is RAG and why is it useful?",
            "Explain prompt engineering.",
            "Quiz me on AI!",
        ],
    },
}

PERSONA_KEYS = list(PERSONAS.keys())

# ── Per-user memory store ─────────────────────────────────────────────────────
# Structure: { session_id: { persona_key: [ {role, content, ts}, ... ] } }
USER_MEMORY: dict = {}
MAX_MEMORY_TURNS = 20  # keep last N user+assistant pairs per persona


def get_memory(session_id: str, persona_key: str) -> list:
    return USER_MEMORY.get(session_id, {}).get(persona_key, [])


def save_memory(session_id: str, persona_key: str, messages: list):
    if session_id not in USER_MEMORY:
        USER_MEMORY[session_id] = {}
    USER_MEMORY[session_id][persona_key] = messages


def trim_memory(messages: list) -> list:
    max_items = MAX_MEMORY_TURNS * 2
    return messages[-max_items:] if len(messages) > max_items else messages


def memory_stats(session_id: str) -> str:
    if session_id not in USER_MEMORY:
        return "No memory yet."
    lines = []
    for pk, msgs in USER_MEMORY[session_id].items():
        name = PERSONAS[pk]["name"]
        pairs = len(msgs) // 2
        if pairs:
            lines.append(f"{name}: {pairs} turn(s)")
    return " | ".join(lines) if lines else "No memory yet."


# ── Core chat logic ───────────────────────────────────────────────────────────

def get_bot_response(user_message: str, persona_key: str, session_id: str) -> str:
    if not user_message.strip():
        return ""

    persona = PERSONAS[persona_key]
    history = get_memory(session_id, persona_key)

    # Build messages: system prompt + full history + new user message
    groq_messages = [{"role": "system", "content": persona["system_prompt"]}]
    for msg in history:
        groq_messages.append({"role": msg["role"], "content": msg["content"]})
    groq_messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    history.append({"role": "user", "content": user_message, "ts": ts})
    history.append({"role": "assistant", "content": reply, "ts": ts})
    history = trim_memory(history)
    save_memory(session_id, persona_key, history)

    return reply


def process_message(user_message, chat_history, persona_key, session_id):
    if not user_message.strip():
        return chat_history, chat_history, "", memory_stats(session_id)

    bot_reply = get_bot_response(user_message, persona_key, session_id)
    updated = chat_history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_reply},
    ]
    return updated, updated, "", memory_stats(session_id)


def clear_chat(session_id, persona_key):
    if session_id in USER_MEMORY and persona_key in USER_MEMORY[session_id]:
        USER_MEMORY[session_id][persona_key] = []
    return [], [], "", memory_stats(session_id)


def clear_all_memory(session_id):
    if session_id in USER_MEMORY:
        USER_MEMORY[session_id] = {}
    return [], [], "", "All memory cleared."


def update_examples_on_change(persona_key, session_id, _chat_history):
    persona_history = get_memory(session_id, persona_key)
    internal = [{"role": m["role"], "content": m["content"]} for m in persona_history]
    ex = PERSONAS[persona_key]["examples"]
    return (
        gr.update(value=ex[0]),
        gr.update(value=ex[1]),
        gr.update(value=ex[2]),
        internal,
        internal,
        memory_stats(session_id),
    )


def handle_example(example_text, history, persona, session_id):
    return process_message(example_text, history, persona, session_id)


def export_memory(session_id):
    data = USER_MEMORY.get(session_id, {})
    if not data:
        return "No memory to export."
    export = {}
    for pk, msgs in data.items():
        export[PERSONAS[pk]["name"]] = [
            {"role": m["role"], "content": m["content"], "time": m.get("ts", "")}
            for m in msgs
        ]
    return json.dumps(export, indent=2, ensure_ascii=False)


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0f0f13;
    --surface: #18181f;
    --surface2: #22222d;
    --border: #2e2e3d;
    --accent: #7c3aed;
    --accent2: #a78bfa;
    --text: #e8e8f0;
    --muted: #6b6b85;
    --green: #4ade80;
    --radius: 14px;
    --font: 'Space Grotesk', sans-serif;
    --mono: 'JetBrains Mono', monospace;
}

body, .gradio-container {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

.gradio-container { max-width: 1280px !important; margin: 0 auto !important; }

.header-block {
    background: linear-gradient(135deg, #1a0a2e 0%, #16082a 50%, #0f0f13 100%);
    border: 1px solid #3d1f7a;
    border-radius: var(--radius);
    padding: 28px 36px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.header-block::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, #7c3aed33 0%, transparent 70%);
    pointer-events: none;
}

.sidebar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
}

.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
}

.section-label {
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 8px; margin-top: 14px;
}

/* Radio */
.persona-radio label {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-bottom: 6px !important;
    cursor: pointer; font-weight: 500;
    transition: all 0.18s ease;
}
.persona-radio label:hover { border-color: var(--accent2) !important; }

/* Example buttons */
.example-btn {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
    margin-bottom: 6px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.15s ease;
}
.example-btn:hover {
    border-color: var(--accent2) !important;
    transform: translateX(3px);
}

/* Send button */
.send-btn {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    border: none !important; border-radius: 10px !important;
    color: white !important; font-family: var(--font) !important;
    font-weight: 600 !important; transition: all 0.2s ease !important;
}
.send-btn:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px #7c3aed55 !important;
}

/* Clear buttons */
.clear-btn {
    background: #2a1010 !important;
    border: 1px solid #5a1f1f !important;
    border-radius: 8px !important;
    color: #f87171 !important;
    font-family: var(--font) !important;
    font-size: 12px !important;
    transition: all 0.15s ease;
}
.clear-btn:hover { background: #3d1515 !important; border-color: #ef4444 !important; }

/* Memory display */
.memory-bar textarea {
    background: #0d1f0d !important;
    border: 1px solid #1a4a1a !important;
    border-radius: 8px !important;
    color: var(--green) !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
}

/* Export box */
.export-box textarea {
    background: #0d0d14 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--green) !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
}

/* Input */
.user-input textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
    resize: none !important;
}
.user-input textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px #7c3aed22 !important;
    outline: none !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: #3d2d7a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
"""

# ── Layout ────────────────────────────────────────────────────────────────────

with gr.Blocks(title="🎓 AI Arcade Mentor Bot") as demo:

    session_id = gr.State(lambda: str(uuid.uuid4()))
    chat_history = gr.State([])

    with gr.Column(elem_classes="header-block"):
        gr.HTML("""
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="font-size:44px;line-height:1;">🎓</div>
            <div>
                <h1 style="margin:0;font-size:26px;font-weight:700;
                    background:linear-gradient(90deg,#a78bfa,#60a5fa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    AI Arcade Mentor Bot
                </h1>
                <p style="margin:4px 0 0;color:#9999bb;font-size:14px;">
                    Pick your mentor · Ask anything · Memory persists per mentor across your session
                </p>
            </div>
        </div>
        """)

    with gr.Row(equal_height=False):

        # ── Sidebar ───────────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=240, elem_classes="sidebar"):

            gr.HTML('<div class="section-label">👤 Select Mentor</div>')
            persona_selector = gr.Radio(
                choices=PERSONA_KEYS,
                value=PERSONA_KEYS[0],
                label="",
                elem_classes="persona-radio",
            )

            gr.HTML('<div class="section-label">💡 Quick Examples</div>')
            init_ex = PERSONAS[PERSONA_KEYS[0]]["examples"]
            ex1 = gr.Button(init_ex[0], size="sm", elem_classes="example-btn")
            ex2 = gr.Button(init_ex[1], size="sm", elem_classes="example-btn")
            ex3 = gr.Button(init_ex[2], size="sm", elem_classes="example-btn")

            gr.HTML('<div class="section-label">🧠 Session Memory</div>')
            memory_display = gr.Textbox(
                value="No memory yet.",
                interactive=False,
                label="",
                lines=2,
                elem_classes="memory-bar",
            )

            gr.HTML('<div class="section-label">⚙️ Actions</div>')
            clear_btn = gr.Button("🗑️ Clear This Chat", size="sm", elem_classes="clear-btn")
            clear_all_btn = gr.Button("💣 Clear ALL Memory", size="sm", elem_classes="clear-btn")

            gr.HTML('<div class="section-label">📤 Export Memory</div>')
            export_btn = gr.Button("Export as JSON", size="sm", elem_classes="example-btn")
            export_box = gr.Textbox(
                label="",
                lines=6,
                interactive=False,
                placeholder="Click Export to see your session memory…",
                elem_classes="export-box",
            )

        # ── Chat area ─────────────────────────────────────────────────────────
        with gr.Column(scale=3, elem_classes="chat-container"):

            _chatbot_kwargs = dict(label="", height=520, show_label=False)
            if _GR_MAJOR < 6:
                _chatbot_kwargs["type"] = "messages"
            chatbot = gr.Chatbot(**_chatbot_kwargs)

            with gr.Row():
                user_input = gr.Textbox(
                    placeholder="Type your question and press Enter or click Send…",
                    lines=3,
                    scale=5,
                    label="",
                    show_label=False,
                    elem_classes="user-input",
                )
                send_btn = gr.Button(
                    "Send ➤",
                    variant="primary",
                    scale=1,
                    min_width=110,
                    elem_classes="send-btn",
                )

    # ── Wiring ────────────────────────────────────────────────────────────────

    send_btn.click(
        process_message,
        inputs=[user_input, chat_history, persona_selector, session_id],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    user_input.submit(
        process_message,
        inputs=[user_input, chat_history, persona_selector, session_id],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    clear_btn.click(
        clear_chat,
        inputs=[session_id, persona_selector],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    clear_all_btn.click(
        clear_all_memory,
        inputs=[session_id],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    persona_selector.change(
        update_examples_on_change,
        inputs=[persona_selector, session_id, chat_history],
        outputs=[ex1, ex2, ex3, chatbot, chat_history, memory_display],
    )
    ex1.click(
        handle_example,
        inputs=[ex1, chat_history, persona_selector, session_id],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    ex2.click(
        handle_example,
        inputs=[ex2, chat_history, persona_selector, session_id],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    ex3.click(
        handle_example,
        inputs=[ex3, chat_history, persona_selector, session_id],
        outputs=[chatbot, chat_history, user_input, memory_display],
    )
    export_btn.click(
        export_memory,
        inputs=[session_id],
        outputs=[export_box],
    )

# ── Launch ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import socket

    def find_available_port(start_port=7860):
        for port in range(start_port, start_port + 100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(("127.0.0.1", port))
                sock.close()
                return port
            except OSError:
                continue
        return start_port

    port = find_available_port(7860)
    print("\n" + "=" * 60)
    print("🎓 AI Arcade Mentor Bot (with Memory) is starting...")
    print(f"📱 Open your browser: http://localhost:{port}")
    print("=" * 60 + "\n")

    demo.launch(server_name="127.0.0.1", server_port=port, share=False, css=CSS)