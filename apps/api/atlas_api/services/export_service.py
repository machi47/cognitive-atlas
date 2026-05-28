from __future__ import annotations

import json

from atlas_api.db.repositories import Repository


class ExportService:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def session_markdown(self, session_id: str) -> str:
        session = await self.repo.get_session(session_id)
        if not session:
            return "# Missing session\n"
        turns = await self.repo.list_turns(session_id)
        lines = [
            f"# {session.title}",
            "",
            f"- Created: {session.created_at}",
            f"- Updated: {session.updated_at}",
            f"- Status: {session.status}",
            "",
            "## Turns",
            "",
        ]
        for turn in turns:
            speaker = "User" if turn.role == "user" else "Assistant"
            lines.extend([f"### {speaker} - {turn.created_at}", "", turn.content, ""])
            artifacts = await self.repo.list_artifacts_for_turn(turn.id)
            if artifacts:
                lines.append("Artifacts:")
                for artifact in artifacts:
                    lines.append(f"- {artifact['artifact_type']}: {artifact['title']} ({artifact['status']})")
                lines.append("")
        return "\n".join(lines)

    async def map_markdown(self, map_id: str) -> str:
        graph = await self.repo.map_graph(map_id)
        if not graph:
            return "# Missing map\n"
        lines = [f"# {graph.map.title}", "", graph.map.summary or "", "", "## Core Concepts"]
        for node in graph.nodes:
            lines.append(f"- **{node.label}**: {node.description or node.node_type} ({node.epistemic_status}, confidence {node.confidence:.2f})")
        lines.extend(["", "## Relations"])
        node_by_id = {node.id: node.label for node in graph.nodes}
        for edge in graph.edges:
            lines.append(f"- {node_by_id.get(edge.from_node_id, edge.from_node_id)} {edge.relation_type} {node_by_id.get(edge.to_node_id, edge.to_node_id)}")
        lines.extend(["", "## Open Questions"])
        for question in graph.questions:
            lines.append(f"- {question.question}")
        if graph.latent_bridges:
            lines.extend(["", "## Latent Bridges"])
            for bridge in graph.latent_bridges:
                lines.append(f"- {bridge.get('from_label')} -> {bridge.get('to_label')}: {bridge.get('reason')}")
        return "\n".join(lines)

    async def atlas_json(self, workspace_id: str) -> str:
        tree = await self.repo.atlas_tree(workspace_id)
        maps = [item.model_dump() for item in await self.repo.list_maps(workspace_id)]
        sources = [item.model_dump() for item in await self.repo.list_sources(workspace_id, limit=500)]
        return json.dumps({"version": 1, "workspace_id": workspace_id, "tree": tree.model_dump(), "maps": maps, "sources": sources}, indent=2)

