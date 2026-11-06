# Agent practice with Claude (Python)

Three short lessons that build up to a working agent.

| File | What you learn |
|---|---|
| `01_first_call.py` | One request/response with the Anthropic SDK |
| `02_manual_loop.py` | The agent loop by hand: tools, `stop_reason`, tool results |
| `03_tool_runner.py` | Same loop, driven by the SDK's tool runner; a file-notes agent |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # from console.anthropic.com
python 01_first_call.py
```

All lessons use `claude-opus-5-5`. They opt into server-side refusal fallbacks
(`fallbacks="default"`), so if a safety classifier declines, the API retries on a
suitable model automatically. Delete those two lines if you don't want that.

## Exercises

1. **Lesson 1:** change `effort` from `low` to `high` and compare answers and token counts.
2. **Lesson 2:** add a `get_weather(city)` tool that returns fake data. Ask about two cities and watch Claude call tools in parallel.
3. **Lesson 2:** make `calculator` fail (e.g. ask for the square root of 2, since `sqrt` is not allowed) and see how Claude recovers from the `is_error` result.
4. **Lesson 3:** add a `delete_note` tool that first asks for confirmation with `input("Delete? y/n")`, which is a human-in-the-loop approval gate.
5. **Lesson 3:** turn it into a chat: wrap it in a `while True: input()` loop and keep `messages` between turns.
6. **Stretch:** add the server-side web search tool (`{"type": "web_search_20260209", "name": "web_search"}`) and build a research agent that saves findings as notes.

Next steps: the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk) (Claude Code as a library, with built-in file/bash/web tools)
and Managed Agents (Anthropic hosts the loop and a sandbox).
