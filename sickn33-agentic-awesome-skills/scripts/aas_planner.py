"""AAS Planner & Skill Selector.

Inspired by sickn33/agentic-awesome-skills (AAS Core), this module provides local
catalog discovery, agent-owned skill selection, and plan preview without any network access.
"""

from typing import Dict, List, Any


class AASPlanner:
    def __init__(self, catalog: List[Dict[str, Any]]) -> None:
        """Initialize the planner with a local catalog of skill dictionaries.

        Each skill dict should have keys like 'name', 'description', and 'topics'.
        """
        self.catalog = catalog
        self.selected_skills: List[Dict[str, Any]] = []

    def search_catalog(self, query: str) -> List[Dict[str, Any]]:
        """Search local catalog for skills matching query in name, description, or topics."""
        q = query.lower()
        results = []
        for skill in self.catalog:
            name = skill.get("name", "").lower()
            desc = skill.get("description", "").lower()
            topics = [t.lower() for t in skill.get("topics", [])]

            if q in name or q in desc or any(q in t for t in topics):
                results.append(skill)
        return results

    def select_skill(self, skill_name: str) -> bool:
        """Agent-owned selection of a skill by name from the catalog."""
        for skill in self.catalog:
            if skill.get("name") == skill_name:
                if skill not in self.selected_skills:
                    self.selected_skills.append(skill)
                return True
        return False

    def preview_plan(self, task_description: str) -> Dict[str, Any]:
        """Preview an execution plan combining selected skills and a toy task."""
        steps = []
        for i, skill in enumerate(self.selected_skills, start=1):
            steps.append({
                "step": i,
                "skill": skill.get("name"),
                "action": f"Apply playbook for {skill.get('name')} to target task"
            })

        return {
            "task": task_description,
            "selected_skill_count": len(self.selected_skills),
            "steps": steps,
            "status": "ready_for_execution"
        }

    def execute_with_llm(self, llm_func, task_description: str) -> str:
        """Execute plan using a fake LLM function (no network)."""
        plan = self.preview_plan(task_description)
        prompt = f"Task: {task_description}\nPlan Steps: {len(plan['steps'])}\nExecute successfully."
        return llm_func(prompt)
