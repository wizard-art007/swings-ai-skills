"""
OpenHeart Diagram Helper

Turns a short text description into diagram source compatible with OpenHeart/Kroki,
and provides a client to render it via the public Kroki API.
"""

import requests


class OpenHeartDiagramHelper:
    """Helper class to generate and render diagram descriptions."""

    def __init__(self, kroki_url: str = "https://kroki.io"):
        self.kroki_url = kroki_url.rstrip("/")

    def generate_diagram_source(self, description: str, diagram_type: str = "plantuml") -> str:
        """
        Transforms a short text description into a diagram source string.
        
        Args:
            description: A short natural language description of the architecture/flow.
            diagram_type: The diagram type (e.g., 'plantuml', 'mermaid', 'dot').
            
        Returns:
            A string containing the valid diagram source code.
        """
        clean_desc = description.strip()
        if not clean_desc:
            clean_desc = "Empty Description"

        if diagram_type.lower() == "mermaid":
            lines = ["graph TD;", f"    subgraph OpenHeartAnalysis", f"        A[Input Source] --> B[{clean_desc}]", f"        B --> C[UML / SCPG Output]", f"    end"]
            return "\n".join(lines)
        
        elif diagram_type.lower() == "dot":
            lines = [
                "digraph OpenHeartCFG {",
                "    node [shape=box, fontname=\"Helvetica\"];",
                f"    \"Start\" -> \"Process: {clean_desc}\";",
                "    \"Process: " + clean_desc + "\" -> \"End\";",
                "}"
            ]
            return "\n".join(lines)

        else:  # Default to PlantUML
            lines = [
                "@startuml",
                "skinparam monochrome true",
                f"title OpenHeart Analysis: {clean_desc}",
                "participant \"Tree-Sitter\" as TS",
                "participant \"OpenHeart Pipeline\" as OH",
                "participant \"UML Generator\" as UML",
                "",
                "[-> TS: Source Code (.java)",
                "activate TS",
                "TS -> OH: Concrete Syntax Tree",
                "deactivate TS",
                "activate OH",
                f"note right of OH: Analyzing: {clean_desc}",
                "OH -> UML: SSA, CFG, Call Graph",
                "deactivate OH",
                "activate UML",
                "[<- UML: Export Diagrams (SVG/DOT)",
                "deactivate UML",
                "@enduml"
            ]
            return "\n".join(lines)

    def render_via_kroki(self, diagram_source: str, diagram_type: str = "plantuml", output_format: str = "svg") -> str:
        """
        Sends the diagram source to Kroki and returns the rendered output (e.g., SVG).
        
        Args:
            diagram_source: The source code of the diagram.
            diagram_type: The diagram engine (plantuml, mermaid, dot, etc.).
            output_format: The target format (svg, png, pdf, etc.).
            
        Returns:
            The raw response content (string for SVG/text, bytes otherwise).
        """
        url = f"{self.kroki_url}/{diagram_type.lower()}/{output_format.lower()}"
        response = requests.post(url, data=diagram_source.encode("utf-8"), timeout=15)
        response.raise_for_status()
        return response.text
