import re, pathlib

utils_path = pathlib.Path("/usr/local/lib/python3.10/site-packages/gradio_client/utils.py")
content = utils_path.read_text()

# Fix the broken line: `if "const" in schema:` fails when schema is a bool
old = '    if "const" in schema:'
new = '    if not isinstance(schema, dict): return "Any"\n    if "const" in schema:'

if old in content and new not in content:
    content = content.replace(old, new)
    utils_path.write_text(content)
    print("✅ gradio_client patched successfully")
else:
    print("ℹ️ Already patched or pattern not found")