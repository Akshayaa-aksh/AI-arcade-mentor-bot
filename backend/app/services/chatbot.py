import datetime
from app.services.groq_client import client
from app.services.memory import get_memory, save_memory, trim_memory
from app.config.personas import PERSONAS

def get_bot_response(user_message: str, persona_key: str, session_id: str) -> str:
    if not user_message.strip():
        return ""

    persona = PERSONAS[persona_key]
    history = get_memory(session_id, persona_key)

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