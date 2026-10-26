import os

def render(element, data):
    html_path = os.path.join(os.path.dirname(__file__), "pl-gdb-terminal.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()