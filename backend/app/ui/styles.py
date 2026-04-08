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