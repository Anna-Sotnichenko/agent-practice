"""Lesson 1 - a single call to Claude (no tools, no loop).

Run:  python 01_first_call.py "Explain what an AI agent is in 3 sentences"
"""
import sys

import anthropic

MODEL = "claude-opus-5-5"
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

prompt = " ".join(sys.argv[1:]) or "Explain what an AI agent is in 3 sentences."

response = client.beta.messages.create(
    model=MODEL,
    max_tokens=16000,
    output_config={"effort": "low"},  # low | medium | high | xhigh | max
    # If a safety classifier declines, the API retries on a suitable model for you.
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
    system="You are a concise, friendly tutor.",
    messages=[{"role": "user", "content": prompt}],
)

if response.stop_reason == "refusal":
    print("Claude declined this request.")
else:
    for block in response.content:
        if block.type == "text":
            print(block.text)

print(f"\n[tokens in={response.usage.input_tokens} out={response.usage.output_tokens}]")
