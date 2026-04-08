import gradio as gr
import uuid
import json

from app.services.chatbot import get_bot_response
from app.services.memory import memory_stats, clear_all_memory
from app.config.personas import PERSONAS, PERSONA_KEYS
from app.ui.styles import CSS

def process_message(user_message, chat_history, persona_key, session_id):
    """Process user message and get bot response"""
    if not user_message.strip():
        return chat_history, "", memory_stats(session_id)

    # Get bot response (this also saves to memory)
    bot_reply = get_bot_response(user_message, persona_key, session_id)

    # Update chat history with proper format
    updated = chat_history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_reply}
    ]
    
    return updated, "", memory_stats(session_id)


def clear_session(session_id):
    """Clear all memory for current session"""
    clear_all_memory(session_id)
    return [], "", "✨ Session cleared!"


def on_persona_change(persona_key, session_id):
    """Update memory display when persona changes"""
    return memory_stats(session_id)


def build_ui():
    with gr.Blocks() as demo:
        # Initialize session with a unique ID
        session_id = gr.State(value=str(uuid.uuid4()))
        
        # Header
        with gr.Group(elem_classes="header-block"):
            gr.Markdown(
                """
                # 🎯 AI Arcade Mentor Bot
                **Learn from AI experts** — Choose your mentor and start chatting. Your conversations are remembered! 🧠
                """
            )

        # Main layout: Sidebar + Chat
        with gr.Row():
            # SIDEBAR
            with gr.Column(scale=1, min_width=280, elem_classes="sidebar"):
                gr.Markdown("### 👤 Select Your Mentor")
                
                persona_selector = gr.Radio(
                    choices=PERSONA_KEYS,
                    value=PERSONA_KEYS[0],
                    interactive=True,
                    elem_classes="persona-radio"
                )

                gr.Markdown("### 💡 Try These Questions")
                
                # Examples - will update based on persona
                example_1_btn = gr.Button(
                    value=PERSONAS[PERSONA_KEYS[0]]["examples"][0],
                    size="sm",
                    elem_classes="example-btn",
                    variant="secondary"
                )
                example_2_btn = gr.Button(
                    value=PERSONAS[PERSONA_KEYS[0]]["examples"][1],
                    size="sm",
                    elem_classes="example-btn",
                    variant="secondary"
                )
                example_3_btn = gr.Button(
                    value=PERSONAS[PERSONA_KEYS[0]]["examples"][2],
                    size="sm",
                    elem_classes="example-btn",
                    variant="secondary"
                )

                # Memory stats
                gr.Markdown("### 📊 Session Memory")
                memory_display = gr.Textbox(
                    value="No memory yet.",
                    interactive=False,
                    label="Conversation Turns",
                    lines=4,
                    elem_classes="memory-bar"
                )

                # Clear buttons
                with gr.Row():
                    clear_all_btn = gr.Button("🔄 Reset All", size="sm", elem_classes="clear-btn")

            # CHAT AREA
            with gr.Column(scale=3, elem_classes="chat-container"):
                gr.Markdown("### 💬 Conversation")
                
                chatbot = gr.Chatbot(
                    value=[],
                    label="Chat History",
                    show_label=False,
                    height=500
                )

                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Ask me anything...",
                        label="Your Message",
                        lines=2,
                        elem_classes="user-input",
                        show_label=False
                    )
                    send_btn = gr.Button("✨ Send", size="lg", elem_classes="send-btn")

        # Event handlers
        def update_examples(persona_key):
            """Update example buttons when persona changes"""
            examples = PERSONAS[persona_key]["examples"]
            return (
                examples[0],
                examples[1],
                examples[2]
            )

        def insert_example(example_text):
            """Insert example text into input"""
            return example_text

        # Persona change handler - update examples and memory display
        persona_selector.change(
            update_examples,
            inputs=[persona_selector],
            outputs=[example_1_btn, example_2_btn, example_3_btn]
        ).then(
            on_persona_change,
            inputs=[persona_selector, session_id],
            outputs=[memory_display]
        )

        # Send message
        send_btn.click(
            process_message,
            inputs=[user_input, chatbot, persona_selector, session_id],
            outputs=[chatbot, user_input, memory_display]
        )

        # Clear all memory
        clear_all_btn.click(
            clear_session,
            inputs=[session_id],
            outputs=[chatbot, user_input, memory_display]
        )

        # Example buttons - insert text into input
        example_1_btn.click(
            insert_example,
            inputs=[example_1_btn],
            outputs=[user_input]
        )
        example_2_btn.click(
            insert_example,
            inputs=[example_2_btn],
            outputs=[user_input]
        )
        example_3_btn.click(
            insert_example,
            inputs=[example_3_btn],
            outputs=[user_input]
        )

    return demo