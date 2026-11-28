"""
Helper for ahmedkhaleel2004-gitdiagram skill.
Turns a short text description into Mermaid diagram source and renders it via Kroki.
"""

import zlib
import base64
import json
import requests

def text_to_mermaid(description: str) -> str:
    """
    Converts a short text description into a Mermaid diagram source string.
    """
    if not description or not description.strip():
        raise ValueError("Description cannot be empty")
    
    desc = description.strip()
    
    # Simple deterministic heuristic mapping based on keywords
    if any(kw in desc.lower() for kw in ["sequence", "flow", "interaction", "call"]):
        lines = [
            "sequenceDiagram",
            "    autonumber",
            "    participant Client",
            "    participant API as GitDiagram API",
            "    participant AI as AI Engine / LLM",
            "    Client->>API: Request diagram for repo",
            "    API->>AI: Analyze codebase structure",
            "    AI-->>API: Return architecture components",
            "    API-->>Client: Render interactive Mermaid diagram"
        ]
    elif any(kw in desc.lower() for kw in ["class", "object", "structure", "model"]):
        lines = [
            "classDiagram",
            "    class Repository {",
            "        +string owner",
            "        +string name",
            "        +getFiles()",
            "    }",
            "    class ArchitectureDiagram {",
            "        +string markdownContent",
            "        +string mermaidSource",
            "        +render()",
            "    }",
            "    class VideoExplainer {",
            "        +string resolution",
            "        +generateVideo()",
            "    }",
            "    Repository --> ArchitectureDiagram : generates",
            "    ArchitectureDiagram --> VideoExplainer : feeds into"
        ]
    else:
        lines = [
            "graph TD",
            "    Client[Client / GitHub URL] -->|Replace hub with diagram| Gateway[GitDiagram Gateway]",
            "    Gateway --> Parser[Codebase Parser]",
            "    Parser --> LLM[AI Agent / LLM]",
            "    LLM --> Mermaid[Mermaid Diagram Generator]",
            "    LLM --> Video[Narrated Video Generator]",
            "    Mermaid --> UI[Interactive UI / Markdown]"
        ]
    return "\n".join(lines)

def render_mermaid_kroki(mermaid_code: str, output_format: str = "svg") -> bytes:
    """
    Renders Mermaid code via the public Kroki API.
    """
    if not mermaid_code or not mermaid_code.strip():
        raise ValueError("Mermaid code cannot be empty")
    
    # Compress using zlib (deflate without header usually used by Kroki: zlib.compress with wbits)
    compressed = zlib.compress(mermaid_code.encode("utf-8"), level=9)
    # URL-safe base64 encoding
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    
    url = f"https://kroki.io/mermaid/{output_format}/{encoded}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content
