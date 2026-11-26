import urllib.parse
import requests

def generate_c4_puml(description: str) -> str:
    """
    Turns a short text description into a C4-PlantUML diagram source string.
    """
    lines = [
        "@startuml",
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
        "LAYOUT_TOP_DOWN()",
        "",
        f"title C4 Diagram generated from: {description}",
        "",
        "Person(user, \"User\", \"A user of the system\")",
        "System_Boundary(c1, \"Software System\") {",
        "    Container(web_app, \"Web Application\", \"React, TypeScript\", \"Delivers the static content and web UI\")",
        "    Container(api_app, \"API Application\", \"Python, FastAPI\", \"Provides core business logic via API\")",
        "    ContainerDb(database, \"Database\", \"PostgreSQL\", \"Stores user data and application state\")",
        "}",
        "",
        "Rel(user, web_app, \"Visits\", \"HTTPS\")",
        "Rel(web_app, api_app, \"Makes API calls\", \"JSON/HTTPS\")",
        "Rel(api_app, database, \"Reads from and writes to\", \"SQL\")",
        "@enduml"
    ]
    return "\n".join(lines)

def render_via_kroki(puml_code: str, format_type: str = "svg") -> str:
    """
    Sends PlantUML source code to the public Kroki API and returns the rendered output url or response.
    """
    url = f"https://kroki.io/plantuml/{format_type}"
    response = requests.post(url, json={"diagram_source": puml_code}, timeout=10)
    response.raise_for_status()
    return response.text
