import sys
import zlib
import base64
import requests

def description_to_mermaid(description: str) -> str:
    """
    Turns a short text description into a Mermaid diagram source representing
    the taste skill workflow (anti-slop frontend generation & verification).
    """
    text = description.strip() or "Default Taste Skill Workflow"
    
    mermaid_code = f"""flowchart TD
    subgraph Input ["Client Brief"]
        A["{text}"]
    end

    subgraph TasteSkill ["Taste Skill (Anti-Slop Pipeline)"]
        B["Art Direction & References"] --> C["One Design System Setup"]
        C --> D["Layout & Section Engineering"]
        D --> E["Real Assets & Brand Integration"]
    end

    subgraph Verification ["Browser Check & Finish Gate"]
        E --> F["Real Browser Checker"]
        F --> G{{"Passes Anti-Slop Check?"}}
    end

    A --> B
    G -- Yes --> H["Professional Production Output"]
    G -- No --> D

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#ff9,stroke:#333,stroke-width:2px
    """
    return mermaid_code.strip()

def render_via_kroki(mermaid_code: str, format: str = "svg") -> str:
    """
    Encodes Mermaid diagram source using deflate + base64url and requests
    the rendered diagram from the public Kroki API.
    """
    data = mermaid_code.encode("utf-8")
    compressed = zlib.compress(data, level=9)
    # Kroki uses URL-safe base64 without padding
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    
    url = f"https://kroki.io/mermaid/{format}/{encoded}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text
