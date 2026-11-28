"""Offline simulation of the browser-use core technique: an agent loop with a REPL,
browser actions (CDP-like step simulation), and LLM tool/code generation.
"""

import json
import re
from typing import Callable, Any, Dict, List, Optional


class BrowserREPL:
    """Simulated persistent browser REPL environment."""
    def __init__(self):
        self.history: List[str] = []
        self.current_url: str = "about:blank"
        self.state: Dict[str, Any] = {"elements": {}, "cookies": {}}

    def execute(self, code: str) -> str:
        """Execute a Python-like browser action snippet safely."""
        self.history.append(code)
        output = []
        
        # Simple pattern matching for simulated browser actions
        if "new_tab" in code or "goto" in code:
            match = re.search(r"['\"](https?://[^'\"]+)['\"]", code)
            if match:
                self.current_url = match.group(1)
                output.append(f"Navigated to {self.current_url}")
            else:
                output.append("Navigated to new tab")
        elif "click" in code:
            match = re.search(r"click\(([^)]+)\)", code)
            target = match.group(1) if match else "unknown"
            output.append(f"Clicked element {target}")
        elif "js" in code or "evaluate" in code:
            output.append("Executed JS script successfully")
        elif "finish" in code:
            match = re.search(r"finish\(([^)]+)\)", code)
            res = match.group(1) if match else "done"
            output.append(f"FINISHED: {res}")
        else:
            output.append(f"Ran REPL statement: {code.strip()}")

        return "\n".join(output)


class SimulatedBrowserAgent:
    """Agent that generates Python snippets to interact with the browser-use REPL."""
    def __init__(self, llm_generator: Callable[[str, List[Dict[str, Any]]], str]):
        self.llm_generator = llm_generator
        self.repl = BrowserREPL()
        self.messages: List[Dict[str, Any]] = []

    def run(self, task: str, max_steps: int = 5) -> str:
        """Run the agent loop until finish() is called or max_steps reached."""
        self.messages.append({"role": "user", "content": task})
        
        for step in range(max_steps):
            prompt = f"Task: {task}\nCurrent URL: {self.repl.current_url}\nHistory: {self.repl.history}"
            code_snippet = self.llm_generator(prompt, self.messages)
            
            self.messages.append({"role": "assistant", "content": code_snippet})
            execution_result = self.repl.execute(code_snippet)
            
            self.messages.append({"role": "system", "content": f"Output: {execution_result}"})
            
            if "finish(" in code_snippet:
                return execution_result
                
        return "Max steps reached without finish()"
