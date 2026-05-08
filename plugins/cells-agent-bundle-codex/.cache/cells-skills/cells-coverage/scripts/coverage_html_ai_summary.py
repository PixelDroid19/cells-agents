import argparse
import html
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, TypedDict


class LineEntry(TypedDict):
    line: int
    coverage_html: str
    code_html: str
    code_text: str


class BlockSummary(TypedDict):
    owner: str
    start_line: int
    end_line: int
    kinds: List[str]
    priority: int
    action: str
    sample: str


class ReportSummary(TypedDict):
    source_file: str
    metrics: Dict[str, str]
    total_issues: int
    compact_blocks: List[BlockSummary]


class MutableBlock(TypedDict):
    owner: str
    start_line: int
    end_line: int
    kinds: List[str]
    samples: List[str]
    count: int


METRIC_PATTERNS = {
    "s": re.compile(r'<span class="strong">\s*([^<]+?)\s*</span>\s*<span class="quiet">Statements</span>', re.IGNORECASE),
    "b": re.compile(r'<span class="strong">\s*([^<]+?)\s*</span>\s*<span class="quiet">Branches</span>', re.IGNORECASE),
    "f": re.compile(r'<span class="strong">\s*([^<]+?)\s*</span>\s*<span class="quiet">Functions</span>', re.IGNORECASE),
    "l": re.compile(r'<span class="strong">\s*([^<]+?)\s*</span>\s*<span class="quiet">Lines</span>', re.IGNORECASE),
}

LINE_NUMBER_RE = re.compile(r"<a name='L(\d+)'></a><a href='#L\d+'>\d+</a>")
LINE_COVERAGE_CELL_RE = re.compile(r'(<span class="[^"]*".*?</span>)', re.DOTALL)
LINE_TABLE_RE = re.compile(
    r'<td class="line-count quiet">(?P<line_numbers>.*?)</td>\s*'
    r'<td class="line-coverage quiet">(?P<coverage>.*?)</td>\s*'
    r'<td class="text"><pre class="prettyprint [^"]*">(?P<code>.*?)</pre></td>',
    re.DOTALL,
)
TITLE_RE = re.compile(r'title="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")
FUNCTION_RE = re.compile(r"^(?:static\s+)?(?:async\s+)?(?:(?:get|set)\s+)?([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{?$")
GETTER_RE = re.compile(r"^(?:static\s+)?get\s+([A-Za-z_$][\w$]*)\s*\{?$")


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_tags(text: str) -> str:
    cleaned = TAG_RE.sub("", text)
    cleaned = html.unescape(cleaned)
    cleaned = cleaned.replace("\xa0", " ")
    return cleaned.rstrip()


def extract_metrics(raw_html: str) -> Dict[str, str]:
    metrics: Dict[str, str] = {}
    for key, pattern in METRIC_PATTERNS.items():
        match = pattern.search(raw_html)
        if match:
            metrics[key] = normalize_space(match.group(1)).replace(" ", "")
    return metrics


def extract_line_entries(raw_html: str) -> List[LineEntry]:
    table_match = LINE_TABLE_RE.search(raw_html)
    if not table_match:
        return []
    line_numbers = [int(value) for value in LINE_NUMBER_RE.findall(table_match.group("line_numbers"))]
    coverage_cells = LINE_COVERAGE_CELL_RE.findall(table_match.group("coverage"))
    code_lines_raw = table_match.group("code").splitlines()
    total = min(len(line_numbers), len(coverage_cells), len(code_lines_raw))

    entries: List[LineEntry] = []
    for index in range(total):
        code_html = code_lines_raw[index]
        entries.append(
            {
                "line": line_numbers[index],
                "coverage_html": coverage_cells[index],
                "code_html": code_html,
                "code_text": normalize_space(strip_tags(code_html)),
            }
        )
    return entries


def classify_issue(titles: List[str], code_text: str) -> str:
    merged = " | ".join(titles).lower()
    code = code_text.lower()
    if "else path not taken" in merged:
        return "else"
    if "branch not covered" in merged:
        return "branch"
    if "function not covered" in merged:
        if code.startswith("get ") or code.startswith("static get "):
            return "getter"
        if code.startswith("async "):
            return "async_fn"
        return "fn"
    if "statement not covered" in merged:
        if code.startswith("if "):
            return "cond"
        if code.startswith("return "):
            return "return"
        return "stmt"
    return "line"


def detect_owner(code_text: str) -> Optional[str]:
    stripped = code_text.strip()
    if not stripped.endswith("{") and not GETTER_RE.match(stripped):
        return None
    if re.match(r"^(if|for|while|switch|catch|return|else)\b", stripped):
        return None
    getter_match = GETTER_RE.match(code_text)
    if getter_match:
        return getter_match.group(1)
    function_match = FUNCTION_RE.match(code_text)
    if function_match:
        return function_match.group(1)
    return None


def choose_action(kinds: List[str], sample: str) -> str:
    kinds_set = set(kinds)
    if "else" in kinds_set or "branch" in kinds_set or "cond" in kinds_set:
        return "probar rutas true/false"
    if "getter" in kinds_set:
        return "invocar getter y validar retorno"
    if "async_fn" in kinds_set:
        return "llamar funcion async y esperar efectos"
    if "fn" in kinds_set:
        return "invocar metodo y validar efectos"
    if "return" in kinds_set:
        return "forzar flujo hasta el return"
    if "emitEvent(" in sample:
        return "espiar emitEvent y validar payload"
    if "querySelector(" in sample:
        return "simular DOM requerido"
    return "ejecutar flujo faltante"


def priority_for(kinds: List[str]) -> int:
    weights = {"else": 5, "branch": 5, "cond": 5, "fn": 4, "async_fn": 4, "getter": 3, "return": 2, "stmt": 1, "line": 1}
    return max(weights.get(kind, 1) for kind in kinds)


def group_blocks(entries: List[LineEntry]) -> List[BlockSummary]:
    current_owner = "global"
    owner_start = 1
    owner_last_line = 1
    blocks: Dict[str, MutableBlock] = {}

    for entry in entries:
        owner = detect_owner(entry["code_text"])
        if owner:
            current_owner = owner
            owner_start = entry["line"]
        owner_last_line = entry["line"]
        titles = TITLE_RE.findall(entry["coverage_html"] + entry["code_html"])
        if not titles:
            continue
        kind = classify_issue(titles, entry["code_text"])
        block = blocks.setdefault(
            current_owner,
            {
                "owner": current_owner,
                "start_line": owner_start,
                "end_line": owner_last_line,
                "kinds": [],
                "samples": [],
                "count": 0,
            },
        )
        block["end_line"] = owner_last_line
        block["count"] += 1
        if kind not in block["kinds"]:
            block["kinds"].append(kind)
        if entry["code_text"] and len(block["samples"]) < 2:
            block["samples"].append(entry["code_text"])

    result: List[BlockSummary] = []
    for raw_block in blocks.values():
        sample = raw_block["samples"][0] if raw_block["samples"] else ""
        kinds = raw_block["kinds"]
        result.append(
            {
                "owner": raw_block["owner"],
                "start_line": raw_block["start_line"],
                "end_line": raw_block["end_line"],
                "kinds": sorted(kinds),
                "priority": priority_for(kinds) * 100 + raw_block["count"],
                "action": choose_action(kinds, sample),
                "sample": sample[:120],
            }
        )
    result.sort(key=lambda item: (-item["priority"], item["start_line"]))
    return result


def parse_report(file_path: Path) -> ReportSummary:
    raw_html = file_path.read_text(encoding="utf-8", errors="ignore")
    entries = extract_line_entries(raw_html)
    source_match = re.search(r"Code coverage report for\s+([^<]+)", raw_html, re.IGNORECASE)
    source_file = normalize_space(html.unescape(source_match.group(1))) if source_match else file_path.stem
    total_issues = sum(1 for entry in entries if TITLE_RE.findall(entry["coverage_html"] + entry["code_html"]))
    return {
        "source_file": source_file,
        "metrics": extract_metrics(raw_html),
        "total_issues": total_issues,
        "compact_blocks": group_blocks(entries),
    }


def render_ai_text(summary: ReportSummary, max_blocks: int) -> str:
    metrics = summary["metrics"]
    metric_text = " ".join(f"{key}:{metrics[key]}" for key in ("s", "b", "f", "l") if metrics.get(key))
    lines = [f"FILE {summary['source_file']}", f"COV {metric_text}", f"MISS {summary['total_issues']}", "FIX:"]
    for block in summary["compact_blocks"][:max_blocks]:
        lines.append(f"- {block['owner']} L{block['start_line']}-{block['end_line']} | {','.join(block['kinds'])} | {block['action']}")
        if block["sample"]:
            lines.append(f"  eg: {block['sample']}")
    lines.append("RULE: prioriza bloques con branch/else/cond y luego fn/async_fn.")
    return "\n".join(lines)


def render_toon_text(summary: ReportSummary) -> str:
    metrics = summary["metrics"]
    lines = [
        f"f: {summary['source_file']}",
        f"cov: s={metrics.get('s', '?')} b={metrics.get('b', '?')} f={metrics.get('f', '?')} l={metrics.get('l', '?')}",
        f"miss: {summary['total_issues']}",
        f"blk[{len(summary['compact_blocks'])}]{{o,sl,el,k,a,s}}:",
    ]
    for block in summary["compact_blocks"]:
        lines.append(
            f"  {block['owner']},{block['start_line']},{block['end_line']},{'|'.join(block['kinds'])},{block['action']},{block['sample']}"
        )
    return "\n".join(lines)


def collect_input_files(path_value: str) -> List[Path]:
    base = Path(path_value).resolve()
    if base.is_file():
        return [base]
    if base.is_dir():
        return [file for file in sorted(base.rglob("*.html")) if file.exists() and file.is_file()]
    return [file.resolve() for file in Path(".").glob(path_value) if file.exists() and file.is_file()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrae un resumen compacto de HTML coverage para uso por IA.")
    parser.add_argument("path", help="Archivo HTML o carpeta con reportes")
    parser.add_argument("--contains", default="", help="Filtra por texto de ruta")
    parser.add_argument("--format", choices=["ai", "json", "toon"], default="toon")
    parser.add_argument("--max-blocks", type=int, default=8)
    parser.add_argument("--output", default="", help="Guarda la salida en un archivo")
    args = parser.parse_args()

    files = collect_input_files(args.path)
    if args.contains:
        files = [file for file in files if args.contains.lower() in str(file).lower()]
    files = [file for file in files if file.suffix == ".html" and file.name != "index.html"]
    if not files:
        raise SystemExit("No se encontraron reportes HTML para procesar.")

    summaries = [parse_report(file) for file in files]
    if args.format == "json":
        output = json.dumps(summaries if len(summaries) > 1 else summaries[0], ensure_ascii=False, separators=(",", ":"))
    elif args.format == "ai":
        output = "\n\n".join(render_ai_text(summary, args.max_blocks) for summary in summaries)
    else:
        output = "\n\n".join(render_toon_text(summary) for summary in summaries)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
