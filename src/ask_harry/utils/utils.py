import logging
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

from ask_harry.config.settings import Config
from rich.console import Console

try:
    from spellchecker import SpellChecker
except ImportError:  # pragma: no cover - optional dependency fallback
    SpellChecker = None

console = Console()
_config = Config()

logging.basicConfig(
    level=getattr(logging, _config.log_level.upper(), logging.INFO),
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(_config.app_name)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

def format_citations(answer: str, id_map: dict) -> tuple[str, dict]:
    # Extract Ids from answer
    found_ids = re.findall(r"\[ID:\s*(\d+)\]", answer)
    logger.debug(f"Found IDs: {found_ids}")
    # extract unique source ids
    unique_ids = list(OrderedDict.fromkeys(int(i) for i in found_ids))
    logger.debug(f"Found UNIQUE IDs: {unique_ids}")

    citations = []
    seen_sources = set()
    for i in unique_ids:
        source = id_map.get(i)

        if source and source not in seen_sources:
            citations.append((i, source))
            seen_sources.add(source)

    citations.sort(key=lambda x: x[0])
    return answer, citations


def format_grouped_citations(answer: str, id_map: dict) -> tuple[str, dict]:
    # Extract Ids from answer
    found_ids = []
    matches = re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", answer)
    for m in matches:
        parts = m.split(",")
        for p in parts:
            found_ids.append(int(p.strip()))

    logger.debug(f"Found IDs: {found_ids}")
    # extract unique source ids
    unique_ids = list(OrderedDict.fromkeys(int(i) for i in found_ids))
    logger.debug(f"Found UNIQUE IDs: {unique_ids}")

    # group ids per source file
    source_to_ids = defaultdict(list)
    for i in unique_ids:
        source = id_map.get(i)
        if source:
            source_to_ids[source].append(i)
    logger.debug(f"Found GROUPED IDs: {source_to_ids}")

    citations = []
    for source, ids in source_to_ids.items():
        ids_sorted = sorted(ids)
        id_text = "".join(f"[{i}]" for i in ids_sorted)
        filename = Path(source).name
        citations.append((filename, id_text))

    citations.sort(key=lambda x: x[0].lower())
    return answer, citations

def clean_text(text):
    if SpellChecker is None:
        return text

    spell = SpellChecker()
    words = text.split()
    # Correct each word
    corrected = [spell.correction(w) or w for w in words]
    return " ".join(corrected)

def display_agent_response(response_text):
    console.print("\n[bold green]Harry:[/]")
    console.print((response_text))

def display_tool_call(name, args):
    content = f"[bold cyan]Tool:[/] {name}\n[bold cyan]Args:[/] {args}"
    #console.print(Panel(content, title="[bold yellow]Harry is acting", border_style="yellow"))
    console.print(content)
