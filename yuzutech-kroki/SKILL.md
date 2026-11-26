---
name: yuzutech-kroki
description: Creates diagrams from textual descriptions!
source: https://github.com/yuzutech/kroki
license: MIT
stars: 4415
language: JavaScript
topics: api, blockdiag, bpmn, bytefield, c4, diagrams, ditaa, erd, excalidraw, graphviz, hacktoberfest, images, mermaid, pikchr, plantuml, svgbob, text, uml, umlet, wavedrom
saved: 2026-11-26
---

# Kroki

Kroki provides a unified REST API to render diagrams from textual descriptions. It supports 20+ diagramming engines including PlantUML, Mermaid, GraphViz/DOT, D2, Excalidraw, C4, BPMN, DBML, Ditaa, Erd, WaveDrom, Pikchr, and BlockDiag without requiring individual CLI tooling per engine.

---

## When to use

- **Multi-engine diagram rendering**: You need to generate diagrams (SVG, PNG, PDF) from text formats like Mermaid, PlantUML, Graphviz, D2, or Excalidraw without installing and managing individual rendering dependencies.
- **Automated documentation pipelines**: Generating diagrams dynamically inside CI/CD, documentation builders (Antora, MkDocs, Sphinx, VitePress), or static site generators.
- **Microservices & Web Apps**: Providing dynamic diagram generation as a service via a standard HTTP API.
- **Markdown embedding**: Embedding dynamically rendered diagram images directly in README files or web pages using Deflate + URL-safe Base64 encoded GET requests.

---

## How to use

### 1. HTTP POST Request (Quickest for scripts & CI/CD)

Send raw diagram text via `curl` to the public instance (`https://kroki.io`) or a self-hosted instance:

#### Mermaid to SVG
```bash
curl -X POST https://kroki.io/mermaid/svg \
  -H "Content-Type: text/plain" \
  --data-binary @- <<'EOF' > diagram.svg
graph TD
    A[Client] -->|HTTP POST| B(Kroki Gateway)
    B --> C{Engine}
    C -->|Mermaid| D[SVG Result]
EOF
```

#### PlantUML to PNG
```bash
curl -X POST https://kroki.io/plantuml/png \
  -H "Content-Type: text/plain" \
  --data-binary @- <<'EOF' > diagram.png
@startuml
actor User
participant "API Gateway" as Gateway
database Database

User -> Gateway: Request data
Gateway -> Database: Query
Database --> Gateway: Response
Gateway --> User: 200 OK
@enduml
EOF
```

#### JSON Payload (with options)
```bash
curl -X POST https://kroki.io \
  -H "Content-Type: application/json" \
  -d '{
    "diagram_source": "digraph G { Hello -> World }",
    "diagram_type": "graphviz",
    "output_format": "svg"
  }' > graph.svg
```

---

### 2. HTTP GET Request (URL-Safe Base64 Encoding)

To embed diagrams directly in Markdown or HTML image tags (`<img src="...">`), compress diagram text using zlib deflate, then encode using URL-safe Base64.

#### Python helper script to generate Kroki URLs:
```python
import base64
import zlib

def kroki_url(diagram_source: str, diagram_type: str = "mermaid", output_format: str = "svg") -> str:
    compressed = zlib.compress(diagram_source.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return f"https://kroki.io/{diagram_type}/{output_format}/{encoded}"

diagram = """
graph LR
    A --> B
    B --> C
"""

print(kroki_url(diagram, "mermaid", "svg"))
```

---

### 3. Self-Hosting with Docker

To avoid sending diagram text to public servers and eliminate network latency:

```bash
# Run core Kroki instance (supports PlantUML, Ditaa, C4, Erd, Graphviz, SvgBob)
docker run -d --name kroki -p 8000:8000 yuzutech/kroki

# Test local endpoint
curl http://localhost:8000/graphviz/svg -d 'digraph { A -> B }'
```

#### Full Stack (Docker Compose)
For engines written in Node/Python/Go (Mermaid, D2, BPMN, Excalidraw, WireViz), run Kroki alongside companion containers:

```yaml
version: '3.8'
services:
  kroki:
    image: yuzutech/kroki
    environment:
      - KROKI_BLOCKDIAG_HOST=kroki-blockdiag
      - KROKI_MERMAID_HOST=kroki-mermaid
      - KROKI_BPMN_HOST=kroki-bpmn
      - KROKI_EXCALIDRAW_HOST=kroki-excalidraw
    ports:
      - "8000:8000"
  kroki-mermaid:
    image: yuzutech/kroki-mermaid
  kroki-blockdiag:
    image: yuzutech/kroki-blockdiag
  kroki-bpmn:
    image: yuzutech/kroki-bpmn
  kroki-excalidraw:
    image: yuzutech/kroki-excalidraw
```

---

## Limitations

- **Privacy & Security**: The public service (`https://kroki.io`) transmits diagram source text over the Internet; proprietary architecture specifications should use a self-hosted instance.
- **Companion Containers Required**: The base Docker image (`yuzutech/kroki`) only bundles Java and C-based engines (PlantUML, Graphviz). Engines like Mermaid, Excalidraw, BPMN, and BlockDiag require companion sidecar containers.
- **Engine-Dependent Output Formats**: Not every diagram type supports all output formats (e.g., some engines only support `svg`, while others support `png`, `pdf`, `jpeg`, or `txt`).
- **Debugging Feedback**: Syntax errors in diagram source return HTTP error codes (typically 400 with a text message); Kroki does not provide visual syntax error highlighting or interactive debugging.
- **URL Length Limits**: GET requests with large or complex diagrams (e.g., detailed C4 models or large Excalidraw JSON) may exceed HTTP URL/header size limits; use POST requests for non-trivial diagrams.
