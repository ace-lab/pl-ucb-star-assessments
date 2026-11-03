import html
import json
import os
import lxml.html
import prairielearn as pl

OPTIONAL = ["input-program", "vulnerable-program", "enable-aslr", "enable-canary",
            "enable-non-exec-pages", "enable-interact", "width",
            "shellcode-in-environ-var", "vulnerable-source-file"]


def render(element_html, data):
    # PrairieLearn calls render() once for every panel (question, submission,
    # answer). Only the question panel should open a terminal; otherwise a
    # graded question ends up with several terminals and websockets.
    if data["panel"] != "question":
        return ""

    element = lxml.html.fragment_fromstring(element_html)
    pl.check_attribs(element, [], OPTIONAL)

    # The vulnerable C source lives in the question's own folder (same
    # convention as egg.py) so instructors never touch this element or the
    # backend to add a new challenge. Defaults to "vuln.c".
    src_name = pl.get_string_attrib(element, "vulnerable-source-file", "vuln.c")
    src_path = os.path.join(data["options"]["question_path"], src_name)
    with open(src_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    config = {
        "aslr": pl.get_boolean_attrib(element, "enable-aslr", False),
        "canary": pl.get_boolean_attrib(element, "enable-canary", False),
        "nx": pl.get_boolean_attrib(element, "enable-non-exec-pages", False),
        "source": source_code,
    }
    html_path = os.path.join(os.path.dirname(__file__), "pl-gdb-terminal.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read().replace("__GDB_CONFIG__", html.escape(json.dumps(config), quote=True))
