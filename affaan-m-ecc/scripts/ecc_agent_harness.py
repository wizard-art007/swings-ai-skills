"""
ECC Agent Harness Optimization System (Offline Python Helper)

Demonstrates core techniques of Everything Claude Code (ECC):
1. Instinct & Memory System: Persistent context and prompt instincts.
2. AgentShield Security: Tool call permission checking and sandboxing.
3. Harness Execution Loop: Plan, security-check tool calls, execute, update memory.
"""

from typing import List, Dict, Any, Callable, Optional


class AgentShield:
    """Security shield for checking tool calls before execution."""

    def __init__(
        self,
        allowed_tools: Optional[List[str]] = None,
        blocked_patterns: Optional[List[str]] = None,
    ):
        self.allowed_tools = (
            set(allowed_tools)
            if allowed_tools is not None
            else {"read_file", "search_code", "calculator"}
        )
        self.blocked_patterns = blocked_patterns or [
            "rm ",
            "drop table",
            "sudo",
            "exec",
        ]

    def is_tool_allowed(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    def inspect_tool_call(self, tool_name: str, args: Dict[str, Any]) -> tuple:
        """Inspects tool call name and arguments against security rules.
        Returns (is_safe: bool, reason: str).
        """
        if not self.is_tool_allowed(tool_name):
            return False, f"Tool '{tool_name}' is not in allowed tools list."

        args_str = str(args).lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in args_str:
                return False, f"Argument contains blocked pattern: '{pattern}'"

        return True, "Approved"


class InstinctStore:
    """Stores prompt instincts and performance optimization rules for the agent."""

    def __init__(self):
        self.instincts: List[Dict[str, str]] = []

    def add_instinct(self, name: str, pattern: str, guidance: str) -> None:
        self.instincts.append(
            {"name": name, "pattern": pattern, "guidance": guidance}
        )

    def get_relevant_instincts(self, prompt: str) -> List[str]:
        prompt_lower = prompt.lower()
        active_guidance = []
        for inst in self.instincts:
            if inst["pattern"].lower() in prompt_lower:
                active_guidance.append(f"[{inst['name']}] {inst['guidance']}")
        return active_guidance


class MemoryManager:
    """Persistent context memory management for harness execution."""

    def __init__(self):
        self.memories: List[Dict[str, Any]] = []

    def remember(self, key: str, value: Any) -> None:
        self.memories.append({"key": key, "value": value})

    def recall_all(self) -> Dict[str, Any]:
        result = {}
        for mem in self.memories:
            result[mem["key"]] = mem["value"]
        return result


class ECCAgentHarness:
    """ECC Harness coordinating memory, instincts, security shield, and execution."""

    def __init__(
        self,
        llm_fn: Callable[[str, List[Dict[str, Any]]], Dict[str, Any]],
        shield: Optional[AgentShield] = None,
    ):
        self.llm_fn = llm_fn
        self.shield = shield or AgentShield()
        self.instincts = InstinctStore()
        self.memory = MemoryManager()
        self.tools: Dict[str, Callable] = {}

        # Register default safe built-in tools
        self.register_tool("calculator", self._tool_calculator)
        self.register_tool("search_code", self._tool_search_code)

    def register_tool(self, name: str, func: Callable) -> None:
        self.tools[name] = func

    def _tool_calculator(self, expression: str) -> str:
        if "+" in expression:
            parts = expression.split("+")
            return str(float(parts[0].strip()) + float(parts[1].strip()))
        return "Calculation complete"

    def _tool_search_code(self, query: str) -> str:
        return f"Results for code search '{query}'"

    def execute(self, prompt: str) -> Dict[str, Any]:
        """Runs an agent step with ECC optimizations."""
        active_instincts = self.instincts.get_relevant_instincts(prompt)

        context = {
            "prompt": prompt,
            "instincts": active_instincts,
            "memory": self.memory.recall_all(),
        }

        llm_response = self.llm_fn(prompt, [context])

        tool_name = llm_response.get("tool_name")
        tool_args = llm_response.get("tool_args", {})
        final_answer = llm_response.get("answer", "")

        execution_log = {
            "prompt": prompt,
            "instincts_applied": len(active_instincts),
            "tool_called": tool_name,
            "status": "success",
            "result": None,
            "answer": final_answer,
        }

        if tool_name:
            is_safe, reason = self.shield.inspect_tool_call(tool_name, tool_args)
            if not is_safe:
                execution_log["status"] = "shield_blocked"
                execution_log["error"] = reason
                return execution_log

            tool_func = self.tools.get(tool_name)
            if tool_func:
                try:
                    tool_result = tool_func(**tool_args)
                    execution_log["result"] = tool_result
                    self.memory.remember(f"tool_output_{tool_name}", tool_result)
                except Exception as err:
                    execution_log["status"] = "tool_error"
                    execution_log["error"] = str(err)
            else:
                execution_log["status"] = "tool_not_found"

        return execution_log
