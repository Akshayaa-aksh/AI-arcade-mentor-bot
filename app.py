import os
os.environ.pop("SSL_CERT_FILE", None)
os.environ.pop("REQUESTS_CA_BUNDLE", None)

# ── Nuclear patch: stop gradio from crashing on api_info ──
import gradio.routes as _gr_routes
_original_api_info = _gr_routes.api_info

def _safe_api_info(*args, **kwargs):
    try:
        return _original_api_info(*args, **kwargs)
    except Exception:
        pass

_gr_routes.api_info = _safe_api_info
# ── End patch ──────────────────────────────────────────────

import gradio as gr
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)

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
            "Do NOT answer questions outside ML/AI topics — politely redirect the user."
        ),
        "examples": [
            "What is overfitting and how do I fix it?",
            "Explain gradient descent simply.",
            "What's the difference between bagging and boosting?",
        ]
    },
    "🐍 Leo — Python Coach": {
        "name": "Leo",
        "system_prompt": (
            "You are Leo, a friendly and sharp Python coding coach. "
            "You help learners understand Python fundamentals, data structures, OOP, "
            "decorators, generators, list comprehensions, pandas, numpy, and writing clean Pythonic code. "
            "Always include short code snippets in your answers when relevant. "
            "Keep responses concise (3-5 sentences + code block) unless asked to elaborate. "
            "Do NOT answer questions outside Python/coding topics — politely redirect the user."
        ),
        "examples": [
            "Explain list comprehensions with an example.",
            "What are Python decorators?",
            "How do I use *args and **kwargs?",
        ]
    },
    "✨ Aria — AI Concepts Guide": {
        "name": "Aria",
        "system_prompt": (
            "You are Aria, a knowledgeable AI concepts guide and quiz master. "
            "You explain AI fundamentals: generative AI, LLMs, prompt engineering, embeddings, "
            "RAG, fine-tuning, RLHF, and AI ethics. You also love testing knowledge with quick quizzes. "
            "Keep responses concise (3-5 sentences) unless a deeper explanation is explicitly requested. "
            "When the user says 'quiz me', generate a multiple-choice question on an AI topic. "
            "Do NOT answer questions outside AI concepts — politely redirect the user."
        ),
        "examples": [
            "What is RAG and why is it useful?",
            "Explain prompt engineering.",
            "Quiz me on AI!",
        ]
    },
}

PERSONA_KEYS = list(PERSONAS.keys())

def chat(user_message, history, persona_key):
    if not user_message.strip():
        return history, ""
    persona = PERSONAS[persona_key]
    groq_messages = [{"role": "system", "content": persona["system_prompt"]}]
    for human, assistant in history:
        groq_messages.append({"role": "user", "content": human})
        groq_messages.append({"role": "assistant", "content": assistant})
    groq_messages.append({"role": "user", "content": user_message})
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        bot_reply = completion.choices[0].message.content
    except Exception as e:
        bot_reply = f"⚠️ Error: {str(e)}"
    history = history + [(user_message, bot_reply)]
    return history, ""

def clear_chat():
    return [], ""

def send_example(idx, history, persona_key):
    text = PERSONAS[persona_key]["examples"][idx]
    return chat(text, history, persona_key)

def update_examples(persona_key):
    ex = PERSONAS[persona_key]["examples"]
    return gr.update(value=ex[0]), gr.update(value=ex[1]), gr.update(value=ex[2])

with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        font=gr.themes.GoogleFont("DM Sans"),
    ),
    title="AI Arcade Mentor Bot",
    css="""
        #title  { text-align: center; }
        #subtitle { text-align: center; color: #6b7280; font-size: 14px; margin-bottom: 10px; }
        footer  { display: none !important; }
    """
) as demo:

    gr.Markdown("# 🎓 AI Arcade Mentor Bot", elem_id="title")
    gr.Markdown(
        "Pick a mentor and start learning. Each expert stays in their lane.",
        elem_id="subtitle",
    )

    with gr.Row():
        with gr.Column(scale=1):
            persona_selector = gr.Radio(
                choices=PERSONA_KEYS,
                value=PERSONA_KEYS[0],
                label="👤 Choose Your Mentor",
            )
            gr.Markdown("### 💡 Quick Questions:")
            init_ex = PERSONAS[PERSONA_KEYS[0]]["examples"]
            ex1 = gr.Button(init_ex[0])
            ex2 = gr.Button(init_ex[1])
            ex3 = gr.Button(init_ex[2])
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="", height=460, show_label=False)
            with gr.Row():
                user_input = gr.Textbox(
                    placeholder="Ask your mentor something... (Enter to send)",
                    label="",
                    lines=2,
                    scale=5,
                    show_label=False,
                )
                send_btn = gr.Button("Send ➤", variant="primary", scale=1)

    history_state = gr.State([])

    def do_send(msg, hist, persona):
        return chat(msg, hist, persona)

    send_btn.click(do_send, [user_input, history_state, persona_selector], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])
    user_input.submit(do_send, [user_input, history_state, persona_selector], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])
    clear_btn.click(clear_chat, [], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])
    persona_selector.change(update_examples, [persona_selector], [ex1, ex2, ex3])
    persona_selector.change(clear_chat, [], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])
    ex1.click(lambda h, p: send_example(0, h, p), [history_state, persona_selector], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])
    ex2.click(lambda h, p: send_example(1, h, p), [history_state, persona_selector], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])
    ex3.click(lambda h, p: send_example(2, h, p), [history_state, persona_selector], [history_state, user_input]).then(
        lambda h: h, [history_state], [chatbot])

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    show_api=False,
    share=False,
)