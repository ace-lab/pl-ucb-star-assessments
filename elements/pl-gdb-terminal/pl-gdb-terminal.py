import html
import json 
import os
import re
import lxml.html
import prairielearn as pl

OPTIONAL = ["input-program", "vulnerable-program", "enable-aslr", "enable-canary",
            "enable-non-exec-pages", "enable-interact", "width", "shellcode-in-environ-var"]


# def prepare(element_html, data):
#     element = lxml.html.fragment_fromstring(element_html)
#     pl.check_attribs(element, [], OPTIONAL)
#     if not re.fullmatch(r"[A-Za-z0-9_-]+", pl.get_string_attrib(element, "vulnerable-program", "demo")):
#         raise ValueError("vulnerable-program must be a plain name")


def render(element_html, data):
    # PrairieLearn calls render() once for every panel (question, submission,
    # answer). Only the question panel should open a terminal; otherwise a
    # graded question ends up with several terminals and websockets.
    if data["panel"] != "question":
        return ""

    element = lxml.html.fragment_fromstring(element_html)
    pl.check_attribs(element, [], OPTIONAL)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", pl.get_string_attrib(element, "vulnerable-program", "demo")):
        raise ValueError("vulnerable-program must be a plain name")

    config = {
        # "program": pl.get_string_attrib(element, "vulnerable-program", "demo"),
        "aslr": pl.get_boolean_attrib(element, "enable-aslr", False),
        "canary": pl.get_boolean_attrib(element, "enable-canary", False),
        "nx": pl.get_boolean_attrib(element, "enable-non-exec-pages", False),
        # "interact": pl.get_boolean_attrib(element, "enable-interact", False),
        # "shellcode_env": pl.get_boolean_attrib(element, "shellcode-in-environ-var", False),
        # "width": pl.get_integer_attrib(element, "width", 500),
    }
    html_path = os.path.join(os.path.dirname(__file__), "pl-gdb-terminal.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read().replace("__GDB_CONFIG__", html.escape(json.dumps(config), quote=True))
