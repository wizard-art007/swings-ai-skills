# Moat: Lightweight LLM Router Proxy

Moat is a minimal Python proxy designed to act as a fallback router for LLM API calls. It intercepts incoming requests and attempts to route them to a local primary provider (e.g., Ollama). If the local provider is unreachable, it automatically flips the request to a cloud provider (e.g., OpenAI).

## How it works
- Uses `http.server` to listen for incoming POST requests.
- Uses `requests` to forward the payload.
- Implements a simple try-except block to handle fallback switching.

## Running
1. `python3 -c "from src.moat import run; run()"`
2. Point your LLM client (like an IDE plugin) to `http://localhost:8080`.

## What was learned
- Standard library `http.server` is sufficient for building minimal API gateways.
- Fault tolerance in AI workflows can be achieved with very little code by wrapping API calls in proxy layers.
- Localized alternatives reduce dependency on single-vendor uptime for critical development tasks.
