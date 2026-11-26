# Moat: OpenRouter Replacement

Moat is a lightweight, open-source LLM API router and proxy written in Python. It provides a unified OpenAI-compatible endpoint that intelligently routes requests across multiple underlying LLM providers (e.g., Anthropic, OpenAI, local Ollama models) based on configurable routing strategies (fallback, round-robin, or cost-optimized).

## How It Works
1. **Unified API**: Exposes standard `/v1/chat/completions` endpoints.
2. **Provider Adapters**: Translates OpenAI-format requests to provider-specific formats (or passes through for OpenAI-compatible providers).
3. **Router Strategies**:
   - **Fallback**: Tries providers in sequence until one succeeds.
   - **Round-Robin**: Distributes load evenly across healthy providers.
4. **Health Check & Metrics**: Tracks latency, error rates, and active provider status.

## How to Run
