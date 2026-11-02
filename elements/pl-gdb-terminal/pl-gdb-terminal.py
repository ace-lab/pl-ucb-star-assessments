import os


def render(element, data):
    # PrairieLearn calls render() once for every panel (question, submission,
    # answer). Only the question panel should open a terminal; otherwise a
    # graded question ends up with several terminals and websockets.
    if data["panel"] != "question":
        return ""
    html_path = os.path.join(os.path.dirname(__file__), "pl-gdb-terminal.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
