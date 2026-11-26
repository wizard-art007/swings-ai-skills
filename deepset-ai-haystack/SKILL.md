---
name: deepset-ai-haystack
description: Open-source AI orchestration framework for building context-engineered, production-ready LLM applications. Design modular pipelines and agent workflows with explicit control over retrieval, routing, m
source: https://github.com/deepset-ai/haystack
license: Apache-2.0
stars: 27118
language: Python
topics: agent-framework, agentic-ai, agentic-rag, agents, ai, ai-agents, context-engineering, framework, genai, generative-ai, information-retrieval, large-language-models, llm, mcp, multi-agent, orchestration, python, rag, retrieval-augmented-generation, semantic-search
saved: 2026-11-26
---

# deepset-ai/haystack

## Summary from README
| | | | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | | CI/CD | [](https://github.com/deepset-ai/haystack/actions/workflows/tests.yml) [](https://github.com/python/mypy) [](https://htmlpreview.github.io/?https://github.com/deepset-ai/haystack/blob/python-coverage-comment-action-data/htmlcov/index.html) [](https://github.com/astral-sh/ruff) | | Docs | [](https://docs.haystack.deepset.ai) | | Package | [](https://pypi.org/project/haystack-ai/) [](https://anaconda.org/conda-forge/haystack-ai) [](https://github.com/deepset-ai/haystack/blob/main/LICENSE) [](https://github.com/deepset-ai/haystack/actions/workflows/license_compliance.yml) | | Meta | [](https://discord.com/invite/qZxjM4bAHU) |

## When to use
Use this skill when you need to:
- Build modular Retrieval-Augmented Generation (RAG) pipelines using Haystack components.
- Implement agent workflows, prompt routing, and tool-use orchestration using Python.
- Integrate large language models (LLMs), document stores, and embedding retrievers into production-ready AI applications.
- Inspect, test, or extend existing Haystack scripts such as `agent_prompt_router.py`.

## How to use
Haystack applications are built by connecting components (such as retrievers, generators, and routers) into directed acyclic pipelines.

1. **Install dependencies:**
   ```bash
   pip install haystack-ai
   ```

2. **Run existing helper scripts:**
   To execute prompt routing and agent workflow demonstrations:
   ```bash
   python agent_prompt_router.py
   ```

3. **Define a basic pipeline in Python:**
   ```python
   from haystack import Pipeline
   from haystack.components.builders import PromptBuilder
   from haystack.components.generators import OpenAIGenerator

   # Define prompt template and pipeline
   prompt_template = "Answer the following query based on the context: {{query}}"
   pipeline = Pipeline()
   pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
   pipeline.add_component("generator", OpenAIGenerator(model="gpt-4o-mini"))
   
   pipeline.connect("prompt_builder.prompt", "generator.prompt")
   
   result = pipeline.run({"prompt_builder": {"query": "What is Haystack?"}})
   print(result)
   ```

## Limitations
- Haystack requires explicit wiring of pipeline inputs and outputs, which adds boilerplate compared to lower-code frameworks for trivial use cases.
- External API dependencies (e.g., OpenAI, Anthropic, or vector database providers) require proper environment variables and API keys to execute successfully.