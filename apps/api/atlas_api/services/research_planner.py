from __future__ import annotations


class ResearchPlanner:
    def plan(self, research_need: dict, topics: list[str]) -> dict:
        if not research_need.get("needs_research"):
            return {"queries": [], "source_types": [], "priority": 0}
        intents = research_need.get("query_intents") or topics
        queries = []
        for intent in intents[:3]:
            queries.append({"query": f"{intent} recent survey technical limitations", "search_type": "openalex"})
            queries.append({"query": f"{intent} ADC DAC overhead compute-in-memory", "search_type": "arxiv"})
        return {
            "queries": queries[:5],
            "source_types": research_need.get("source_types") or ["openalex", "crossref", "arxiv"],
            "priority": research_need.get("priority", 0.5),
        }

