USER_MEMORY: dict = {}
MAX_MEMORY_TURNS = 20

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
        from app.config.personas import PERSONAS
        name = PERSONAS[pk]["name"]
        pairs = len(msgs) // 2
        if pairs:
            lines.append(f"{name}: {pairs} turn(s)")
    return " | ".join(lines) if lines else "No memory yet."


def clear_chat(session_id, persona_key):
    if session_id in USER_MEMORY and persona_key in USER_MEMORY[session_id]:
        USER_MEMORY[session_id][persona_key] = []
    return [], [], "", memory_stats(session_id)


def clear_all_memory(session_id):
    if session_id in USER_MEMORY:
        USER_MEMORY[session_id] = {}
    return [], [], "", "All memory cleared."