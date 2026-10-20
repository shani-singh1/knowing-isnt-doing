"""Check the body of paper.tex against the writing rules: banned words and phrases, em dashes, task or question IDs
in the body, sentences under six words, and the hedging words allowed only in the limitations paragraph.

    python scripts/lint_prose.py

Prints each hit with its line number and exits non-zero if there is any. The bibliography and the appendices are
excluded from the ID rule (task IDs belong in the appendix).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNED = ["it is worth noting", "importantly", "notably", "crucially", "this suggests that", "in other words",
          "interestingly", "delve", "landscape", "novel", "latent state", "flips"]
ROBUST_OK = re.compile(r"robust(ness)? (standard error|estimator|regression)", re.I)
HEDGES = ["may ", "might ", "could ", "perhaps", "possibly", "seems", "appears to"]


def body(tex: str) -> tuple[list[tuple[int, str]], int]:
    end = tex.index("\\begin{thebibliography}")
    app = tex.find("\\appendix")
    lines = tex[:end].split("\n")
    return list(enumerate(lines, 1)), tex[:app].count("\n") + 1 if app > 0 else len(lines)


def plain(s: str) -> str:
    s = re.sub(r"%.*", "", s)
    s = re.sub(r"\\(cite[pt]?|ref|sref|figref|tabref|label|url|includegraphics)\{[^}]*\}", "X", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s)
    return s.replace("{", "").replace("}", "")


COUNT = re.compile(r"\d[\d,]*(?:\.\d+)?(?:\s+(?:of|to|and|against)\s+\d[\d,]*(?:\.\d+)?)?")


def paragraph_rules(tex: str) -> list[tuple[int, str]]:
    """Main-text body paragraphs (abstract to the data statement, floats and section commands removed): at most three
    figures per paragraph (a count such as "10 of 78" or a range "58 to 60" is one figure), no semicolons, no sentence
    over 35 words."""
    body = tex[tex.index("\\end{abstract}"):tex.index("\\section*{Data and code availability}")]
    body = re.sub(r"GPT-6(\.1)?|V4\.1|(Haiku|Sonnet|Opus) 5\.5|BixBench3|\d+\s?(hours|minutes|October)|``[^']*''", " ", body)
    body = re.sub(r"\\begin\{(figure|table)\}.*?\\end\{\1\}", "", body, flags=re.S)
    out = []
    for para in re.split(r"\n\s*\n|\\item\b", body):
        if re.match(r"\s*\\(section|subsection|begin\{(enumerate|itemize)\})", para) and len(para) < 120:
            continue
        s = plain(re.sub(r"\\(section|subsection)\*?\{[^}]*\}(\\label\{[^}]*\})?", " ", para))
        s = re.sub(r"\$[^$]*\$", " X ", s)
        nums = [m for m in COUNT.findall(s)]
        head = " ".join(s.split())[:70]
        if len(nums) > 3:
            out.append((0, f"{len(nums)} numbers in paragraph: {head!r}"))
        if ";" in s:
            out.append((0, f"semicolon in paragraph: {head!r}"))
        for sent in re.split(r"(?<=[.!?])\s+", " ".join(s.split())):
            if len(sent.split()) > 35:
                out.append((0, f"sentence of {len(sent.split())} words: {sent[:70]!r}"))
    return out


def main() -> int:
    tex = (ROOT / "paper.tex").read_text(encoding="utf-8")
    lines, app_line = body(tex)
    hits = []
    in_limits = False
    for n, raw in lines:
        if "\\label{sec:limits}" in raw or "Limitations." in raw:
            in_limits = True
        if in_limits and ("\\paragraph{Conclusion" in raw or "\\label{sec:conclusion}" in raw):
            in_limits = False
        s = plain(raw)
        low = s.lower()
        for w in BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                hits.append((n, f"banned: {w}"))
        if "robust" in low and not ROBUST_OK.search(s):
            hits.append((n, "robust outside its statistical sense"))
        if "\u2014" in raw or "---" in raw:
            hits.append((n, "em dash"))
        if n < app_line and re.search(r"\btask\s?~?\d+|\bT\d+\b|bb3t\d+|_t\d\b", raw) and "\\caption" not in raw:
            hits.append((n, "task or question ID in the body"))
        if not in_limits and n < app_line:
            for h in HEDGES:
                if h in low and not raw.lstrip().startswith("%"):
                    hits.append((n, f"hedge outside limitations: {h.strip()}"))
    # short sentences in running text (main text only)
    text = plain("\n".join(r for n, r in lines if n < app_line and not r.lstrip().startswith(("\\", "%", "&"))))
    for sent in re.split(r"(?<=[.!?])\s+", text):
        w = re.findall(r"[A-Za-z0-9]+", sent)
        if 0 < len(w) < 6 and sent.strip().endswith((".", "!", "?")) and not re.match(r"^\s*(\(|[A-Z]\d|Fig|Tab|e\.g)", sent):
            hits.append((0, f"short sentence: {sent.strip()[:80]!r}"))
    hits += paragraph_rules(tex)
    for n, h in hits:
        print(f"line {n}: {h}")
    print(f"{len(hits)} hits")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
