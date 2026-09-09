#!/usr/bin/env python3
"""Omega Engine Alpha — interactive streaming chatbot."""
import argparse
import sys

import ollama


def main():
    ap = argparse.ArgumentParser(description="Streaming chatbot backed by Ollama.")
    ap.add_argument("--model", default="phi4-mini")
    args = ap.parse_args()

    msgs = [{"role": "system", "content": "You are a helpful assistant. Be concise."}]
    print(f"Chatting with {args.model} (type /bye to exit)")
    while True:
        try:
            q = input(">>> ")
        except EOFError:
            break
        if q.strip() in ("/bye", "/quit", "/exit"):
            break
        msgs.append({"role": "user", "content": q})
        reply = ""
        try:
            for chunk in ollama.chat(model=args.model, messages=msgs, stream=True):
                t = chunk["message"]["content"]
                print(t, end="", flush=True)
                reply += t
        except Exception as exc:
            print(f"\n(error: {exc})")
            break
        print()
        msgs.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()