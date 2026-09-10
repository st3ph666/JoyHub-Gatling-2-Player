#!/usr/bin/env python3
from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "JoyHub-Gatling-2-Player.py"
PACKAGE = ROOT / "src" / "joyhub_gatling2"
README = ROOT / "README.md"
REQUIREMENTS = ROOT / "requirements.txt"
PYPROJECT = ROOT / "pyproject.toml"
LAUNCHER = ROOT / "JoyHub-Gatling-2-Player-v1.3.5.py"
OLD_VERSION = "v1.3.4"
NEW_VERSION = "v1.3.5"

FRENCH = re.compile(r"[àâçéèêëîïôûùüÿœ]|\b(afin|ajoute|aucun|avec|avant|choisir|commande|connexion|dossier|début|défile|écran|fichier|fenêtre|grille|lancement|lecture|même|moteur|nom|pour|priorité|retourne|script|sélection|supprime|uniquement|vidéo|vibration|lorsque|automatique|arrêt|réglage|langue|rotation|pompage|vitesse|puissance|niveau|convertit|conversion)\b", re.I)


def src(lines, node):
    end = getattr(node, "end_lineno", node.lineno)
    return "".join(lines[node.lineno - 1:end]).rstrip() + "\n"


def clean_comments_and_docstrings(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    ranges = []
    def visit(body):
        if body and isinstance(body[0], ast.Expr):
            val = body[0].value
            if isinstance(val, ast.Constant) and isinstance(val.value, str) and FRENCH.search(val.value):
                ranges.append((body[0].lineno, body[0].end_lineno or body[0].lineno))
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(node.body)
    visit(tree.body)
    for start, end in sorted(ranges, reverse=True):
        for i in range(start - 1, end):
            lines[i] = "\n" if lines[i].endswith("\n") else ""
    text = "".join(lines)
    tokens = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT and not tok.string.startswith("#!") and FRENCH.search(tok.string):
            tok = tokenize.TokenInfo(tok.type, "", tok.start, tok.end, tok.line)
        tokens.append(tok)
    return tokenize.untokenize(tokens)


def read_dependencies() -> list[str]:
    if not REQUIREMENTS.exists():
        return []
    return [line.strip() for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def update_readme(text: str) -> str:
    text = text.replace(OLD_VERSION, NEW_VERSION)
    block = '''\n## uv deployment\n\nThe recommended deployment method is [`uv`](https://docs.astral.sh/uv/). The project is configured to use the system Python so Tkinter remains provided by the Linux distribution.\n\n### Debian / Ubuntu\n\n```bash\nsudo apt update\nsudo apt install -y python3 python3-tk mpv bluetooth bluez\n```\n\nInstall `uv` using its official installation method, then:\n\n```bash\ngit clone https://github.com/st3ph666/JoyHub-Gatling-2-Player.git\ncd JoyHub-Gatling-2-Player\nuv sync\nuv run python JoyHub-Gatling-2-Player-v1.3.5.py\n```\n\nPython dependencies are installed automatically by `uv sync`. Do not run `uv sync` with `sudo`.\n\n### Update\n\n```bash\ngit pull\nuv sync\nuv run python JoyHub-Gatling-2-Player-v1.3.5.py\n```\n\n## Source architecture\n\n```text\nJoyHub-Gatling-2-Player-v1.3.5.py  # Compatibility launcher\nsrc/joyhub_gatling2/\n├── __init__.py                   # Version metadata\n├── settings.py                   # Paths, translations, patterns and UI constants\n├── app.py                        # BLE engine bundle, helpers and Tkinter application\n└── main.py                       # Application entry point\n```\n\nSource-code comments are maintained in **English only**. French and English user-interface strings are preserved.\n\n'''
    if "## uv deployment" not in text:
        text += block
    return text


def main():
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    upper_assignments = []
    app_nodes = []
    main_node = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_node = node
            continue
        if isinstance(node, ast.If):
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if names and all(name.isupper() for name in names) and "ENGINE_BUNDLE" not in names and "LANGUAGE" not in names:
                upper_assignments.append(node)
                continue
        app_nodes.append(node)

    if main_node is None:
        raise RuntimeError("main() not found")

    PACKAGE.mkdir(parents=True, exist_ok=True)

    import_text = "".join(src(lines, n) for n in imports)
    settings = '"""Paths, translations, patterns, and UI constants."""\n\n' + import_text + "\n"
    settings += "\n".join(src(lines, n) for n in upper_assignments)
    settings = settings.replace(OLD_VERSION, NEW_VERSION)

    app = '"""JoyHub Gatling 2 application and embedded BLE engine."""\n\n' + import_text + "\nfrom .settings import *  # noqa: F403,F401\n\n"
    app += "\n".join(src(lines, n) for n in app_nodes)
    app = clean_comments_and_docstrings(app)

    main_code = '"""Application entry point."""\n\nfrom .app import *  # noqa: F403,F401\n\n' + src(lines, main_node) + '\nif __name__ == "__main__":\n    raise SystemExit(main())\n'
    launcher = '''#!/usr/bin/env python3\n"""Compatibility launcher for JoyHub Gatling 2 Player v1.3.5."""\n\nfrom pathlib import Path\nimport sys\n\nROOT = Path(__file__).resolve().parent\nSRC = ROOT / "src"\nif str(SRC) not in sys.path:\n    sys.path.insert(0, str(SRC))\n\nfrom joyhub_gatling2.main import main\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'''

    (PACKAGE / "__init__.py").write_text('"""JoyHub Gatling 2 Player package."""\n\n__version__ = "1.3.5"\n', encoding="utf-8")
    (PACKAGE / "settings.py").write_text(clean_comments_and_docstrings(settings), encoding="utf-8")
    (PACKAGE / "app.py").write_text(app, encoding="utf-8")
    (PACKAGE / "main.py").write_text(main_code, encoding="utf-8")
    LAUNCHER.write_text(launcher, encoding="utf-8")
    LAUNCHER.chmod(0o755)

    deps = read_dependencies()
    dep_lines = "\n".join(f'    "{d}",' for d in deps)
    PYPROJECT.write_text(f'''[project]\nname = "joyhub-gatling-2-player"\nversion = "1.3.5"\ndescription = "Linux BLE funscript player for JoyHub Gatling 2"\nrequires-python = ">=3.11"\ndependencies = [\n{dep_lines}\n]\n\n[tool.uv]\npackage = false\npython-preference = "only-system"\n''', encoding="utf-8")

    if README.exists():
        README.write_text(update_readme(README.read_text(encoding="utf-8")), encoding="utf-8")
    SOURCE.unlink()


if __name__ == "__main__":
    main()
