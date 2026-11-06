"""Lesson 2 - an agent loop written by hand.

An "agent" is just this loop:
  1. send the conversation + tool definitions to Claude
  2. if Claude asks to use tools, run them and send the results back
  3. repeat until Claude answers without calling a tool

Run:  python 02_manual_loop.py "What is 17% of 2340, and what time is it in UTC?"
"""
import json
import sys
from datetime import datetime, timezone

import anthropic

MODEL = "claude-opus-5-5"
client = anthropic.Anthropic()


# ---- 1. Tools: plain Python functions -------------------------------------
def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). %")
    if not set(expression) <= allowed:
        raise ValueError("Only numbers and + - * / ( ) . % are allowed")
    return str(eval(expression, {"__builtins__": {}}))  # restricted on purpose


def current_time() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


TOOL_FUNCS = {"calculator": calculator, "current_time": current_time}

# ---- 2. Tool definitions: what Claude sees --------------------------------
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression, e.g. '2340 * 0.17'.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
            "additionalProperties": False,
        },
    },
    {
        "name": "current_time",
        "description": "Get the current date and time in UTC (ISO 8601).",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
    },
]


def run_tool(name: str, args: dict) -> dict:
    """Run one tool; errors go back to Claude so it can recover."""
    try:
        return {"content": TOOL_FUNCS[name](**args)}
    except Exception as e:  # noqa: BLE001 - report any tool failure to the model
        return {"content": f"Error: {e}", "is_error": True}


# ---- 3. The loop -----------------------------------------------------------
def run_agent(task: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": task}]
    for turn in range(max_turns):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system="You are a helpful assistant. Use tools for math and time instead of guessing.",
            tools=TOOLS,
            messages=messages,
        )
        # Always append the full content (not just text) so history stays valid.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            return "Claude declined this request."
        if response.stop_reason == "max_tokens":
            return "Stopped: hit max_tokens."
        if response.stop_reason == "pause_turn":
            continue
        if response.stop_reason != "tool_use":  # end_turn: we're done
            return "".join(b.text for b in response.content if b.type == "text")

        # Run every requested tool, return ALL results in ONE user message.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                out = run_tool(block.name, block.input)
                print(f"  [turn {turn + 1}] {block.name}({json.dumps(block.input)}) -> {out['content']}")
                results.append({"type": "tool_result", "tool_use_id": block.id, **out})
        messages.append({"role": "user", "content": results})

    return "Stopped: too many turns."


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) or "What is 17% of 2340, and what time is it in UTC?"
    print(run_agent(task))
