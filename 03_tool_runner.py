"""Lesson 3 - the same idea, but the SDK's tool runner drives the loop.

You write only the tool functions; type hints + docstrings become the schema.
This agent can read and write notes in a local ./notes folder.

Run:  python 03_tool_runner.py "Save a note called ideas.txt with 3 agent project ideas, then list my notes"
"""
import sys
from pathlib import Path

import anthropic
from anthropic import beta_tool

MODEL = "claude-opus-5-5"
NOTES = Path(__file__).parent / "notes"
NOTES.mkdir(exist_ok=True)
client = anthropic.Anthropic()


def _safe(name: str) -> Path:
    path = (NOTES / name).resolve()
    if path.parent != NOTES.resolve():
        raise ValueError("Note names must be plain file names, no folders")
    return path


@beta_tool
def list_notes() -> str:
    """List the names of all saved notes."""
    return "\n".join(p.name for p in sorted(NOTES.iterdir())) or "(no notes yet)"


@beta_tool
def read_note(name: str) -> str:
    """Read a saved note.

    Args:
        name: File name of the note, e.g. "ideas.txt".
    """
    return _safe(name).read_text()


@beta_tool
def write_note(name: str, content: str) -> str:
    """Create or overwrite a note.

    Args:
        name: File name of the note, e.g. "ideas.txt".
        content: Full text to save.
    """
    _safe(name).write_text(content)
    return f"Saved {name} ({len(content)} chars)"


task = " ".join(sys.argv[1:]) or "List my notes, then save one called hello.txt saying hi."

runner = client.beta.messages.tool_runner(
    model=MODEL,
    max_tokens=16000,
    output_config={"effort": "medium"},
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
    system="You are a note-keeping assistant. Use the tools to manage the user's notes.",
    tools=[list_notes, read_note, write_note],
    messages=[{"role": "user", "content": task}],
)

for message in runner:  # one iteration per model response
    for block in message.content:
        if block.type == "tool_use":
            print(f"  -> {block.name}({block.input})")
        elif block.type == "text":
            print(block.text)
    if message.stop_reason == "refusal":
        print("Claude declined this request.")
