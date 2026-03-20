from __future__ import annotations

from lineagelens.lineage.graph_builder import MetadataGraph
from lineagelens.models.schema import EntityType, MetadataEntity


class QueryService:
    def __init__(self, graph: MetadataGraph) -> None:
        self.graph = graph

    def search_entities(self, query: str, entity_type: EntityType | None = None) -> list[MetadataEntity]:
        normalized = query.lower()
        results = []
        for entity in self.graph.entities.values():
            if entity_type is not None and entity.entity_type != entity_type:
                continue
            haystack = " ".join(filter(None, [entity.qualified_name, entity.display_name, entity.description]))
            if normalized in haystack.lower():
                results.append(entity)
        return results
