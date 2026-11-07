import html
import json
import os
import lxml.html
import prairielearn as pl

OPTIONAL = ["input-program", "vulnerable-program", "enable-aslr", "enable-canary",
            "enable-non-exec-pages", "enable-interact", "width",
            "shellcode-in-environ-var", "vulnerable-source-file",
            "autostart-iframe"]

XTERM_VERSION = "5.3.0"
CDN = f"https://cdn.jsdelivr.net/npm/xterm@{XTERM_VERSION}"


def xterm_urls(data):
    """Return (css_url, js_url) for xterm.js.

    If scripts/vendor_xterm.sh has copied the files into this element's
    clientFilesElement/ folder, serve them from PrairieLearn itself (no third-party
    CDN at runtime). Otherwise fall back to the CDN.
    """
    base = data["options"].get("client_files_element_url")
    local = os.path.join(os.path.dirname(__file__), "clientFilesElement")
    if base and all(os.path.exists(os.path.join(local, f)) for f in ("xterm.js", "xterm.css")):
        base = base.rstrip("/")
        return f"{base}/xterm.css", f"{base}/xterm.js"
    return f"{CDN}/css/xterm.css", f"{CDN}/lib/xterm.js"


NO_WORKSPACE = (
    '<div class="alert alert-warning">pl-gdb-terminal needs a workspace: add '
    '<code>workspaceOptions</code> (and <code>"singleVariant": true</code>) to this '
    'question\'s info.json and a <code>&lt;pl-workspace&gt;</code> to question.html.</div>'
)


def render(element_html, data):
    # PrairieLearn calls render() once for every panel (question, submission,
    # answer). Only the question panel should open a terminal; otherwise a
    # graded question ends up with several terminals and websockets.
    if data["panel"] != "question":
        return ""

    element = lxml.html.fragment_fromstring(element_html)
    pl.check_attribs(element, [], OPTIONAL)

    # PrairieLearn gives every workspace question a per-student URL such as
    # /pl/workspace/1. The workspace container (our backend) is proxied
    # beneath it, on the same origin as this page: no CORS, no tokens, and
    # PrairieLearn's own login protects it.
    workspace_url = data["options"].get("workspace_url")
    if not workspace_url:
        return NO_WORKSPACE

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
        "workspaceUrl": workspace_url,
        "base": workspace_url.rstrip("/") + "/container/",
        # Experimental: load the workspace page in a hidden iframe so the
        # container starts without the student clicking "Open workspace".
        "autostart": pl.get_boolean_attrib(element, "autostart-iframe", False),
    }
    css_url, js_url = xterm_urls(data)
    html_path = os.path.join(os.path.dirname(__file__), "pl-gdb-terminal.html")
    with open(html_path, "r", encoding="utf-8") as f:
        page = f.read()
    return (page
            .replace("__GDB_CONFIG__", html.escape(json.dumps(config), quote=True))
            .replace("__XTERM_CSS__", html.escape(css_url, quote=True))
            .replace("__XTERM_JS__", html.escape(js_url, quote=True)))
