"""
BPMN Process Generator tool for agents365-ai-drawio-skill.
Converts textual workflow descriptions (e.g., "Start -> Task -> End") into valid BPMN XML definitions.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

def generate_bpmn(process_description: str) -> str:
    """
    Generates a valid BPMN 2.0 XML string from a simple step-by-step process description.
    Example: "Start -> Task -> End"
    """
    # Parse steps from description
    if "->" in process_description:
        steps = [s.strip() for s in process_description.split("->")]
    else:
        steps = [s.strip() for s in process_description.split(",") if s.strip()]
        if not steps:
            steps = [process_description.strip()]

    # Root definitions element
    definitions = ET.Element("definitions", {
        "xmlns": "http://www.omg.org/spec/BPMN/20100524/MODEL",
        "xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
        "xmlns:omgdc": "http://www.omg.org/spec/DD/20100524/DC",
        "xmlns:omgdi": "http://www.omg.org/spec/DD/20100524/DI",
        "targetNamespace": "http://www.omg.org/spec/BPMN/20100524/MODEL"
    })

    process = ET.SubElement(definitions, "process", {
        "id": "Process_1",
        "isExecutable": "false"
    })

    node_ids = []
    for idx, step_name in enumerate(steps):
        lower_name = step_name.lower()
        if "start" in lower_name and idx == 0:
            elem_id = f"StartEvent_{idx+1}"
            node = ET.SubElement(process, "startEvent", {"id": elem_id, "name": step_name})
        elif "end" in lower_name and idx == len(steps) - 1:
            elem_id = f"EndEvent_{idx+1}"
            node = ET.SubElement(process, "endEvent", {"id": elem_id, "name": step_name})
        else:
            elem_id = f"Task_{idx+1}"
            node = ET.SubElement(process, "task", {"id": elem_id, "name": step_name})
        node_ids.append((elem_id, step_name))

    # Add sequence flows
    for i in range(len(node_ids) - 1):
        source_id, _ = node_ids[i]
        target_id, _ = node_ids[i+1]
        flow_id = f"Flow_{i+1}"
        ET.SubElement(process, "sequenceFlow", {
            "id": flow_id,
            "sourceRef": source_id,
            "targetRef": target_id
        })

    # Convert to formatted XML string
    rough_string = ET.tostring(definitions, encoding="utf-8")
    parsed = minidom.parseString(rough_string)
    return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
