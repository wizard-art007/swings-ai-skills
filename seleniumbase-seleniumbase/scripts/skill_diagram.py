import zlib
import base64
import requests

def text_to_diagram(description: str) -> str:
    """
    Converts a short text description into a Mermaid diagram source string
    tailored to SeleniumBase automation and stealth concepts.
    """
    desc_lower = description.lower()
    
    if "cdp" in desc_lower or "stealth" in desc_lower or "cloudflare" in desc_lower:
        diagram = """graph TD
    A[Start: User Script] --> B[Initialize sb_cdp.Chrome]
    B --> C[Bypass Bot Detection / Cloudflare]
    C --> D[Navigate to Target URL]
    D --> E[Interact with Elements]
    E --> F[End: Scraping / Testing Complete]"""
    elif "pytest" in desc_lower or "test" in desc_lower:
        diagram = """graph TD
    A[Start: Pytest Suite] --> B[Setup SeleniumBase Fixture]
    B --> C[Execute Test Steps]
    C --> D{Assertions Pass?}
    D -- Yes --> E[Test Passed]
    D -- No --> F[Capture Failure / Screenshot]
    E --> G[Teardown]
    F --> G"""
    else:
        diagram = f"""graph TD
    A[Input Description] --> B[{description}]
    B --> C[SeleniumBase Automation]
    C --> D[Execution Result]"""
        
    return diagram.strip()

def render_via_kroki(diagram_source: str, diagram_type: str = "mermaid", format_type: str = "svg", timeout: int = 5) -> str:
    """
    Renders a diagram source string via the public Kroki API using zlib and base64 encoding.
    Returns the URL to the rendered diagram or raises an exception on failure.
    """
    compressed = zlib.compress(diagram_source.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    
    url = f"https://kroki.io/{diagram_type}/{format_type}/{encoded}"
    
    # Verify connectivity / validity via a lightweight HEAD or GET request
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    
    return url
