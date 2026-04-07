import re, pathlib, sys, importlib.util

# Find gradio_client utils.py dynamically across platforms
try:
    spec = importlib.util.find_spec("gradio_client")
    if spec and spec.origin:
        gradio_client_dir = pathlib.Path(spec.origin).parent
        utils_path = gradio_client_dir / "utils.py"
        
        if utils_path.exists():
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
        else:
            print(f"⚠️ Utils file not found at {utils_path}")
    else:
        print("⚠️ Could not locate gradio_client")
except Exception as e:
    print(f"⚠️ Patch attempt failed: {e}")