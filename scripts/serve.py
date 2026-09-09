#!/usr/bin/env python3
"""Omega Engine Alpha — FastAPI server wrapping Ollama (port 8000)."""
import argparse
import json

import ollama
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


def make_app(model):
    @app.get("/health")
    def health():
        return {"status": "ok", "model": model}

    @app.post("/chat")
    def chat(body: dict):
        messages = body.get("messages", [{"role": "user", "content": body.get("prompt", "")}])
        stream = body.get("stream", True)

        def gen():
            for chunk in ollama.chat(model=model, messages=messages, stream=True):
                yield json.dumps({"delta": chunk["message"]["content"]}) + "\n"

        if stream:
            return StreamingResponse(gen(), media_type="application/x-ndjson")
        return ollama.chat(model=model, messages=messages, stream=False)

    app.add_api_route("/chat", chat, methods=["POST"], include_in_schema=False)

    return app


def main():
    ap = argparse.ArgumentParser(description="FastAPI wrapper around Ollama.")
    ap.add_argument("--model", default="phi4-mini")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    make_app(args.model)
    print(f"  Serving on http://localhost:{args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()