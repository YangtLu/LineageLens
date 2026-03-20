from __future__ import annotations

from collections.abc import Iterable

from lineagelens.models.schema import LineageEdge, MetadataEntity


class MetadataGraph:
    def __init__(self) -> None:
        self.entities: dict[str, MetadataEntity] = {}
        self.edges: list[LineageEdge] = []

    def add_entity(self, entity: MetadataEntity) -> None:
        self.entities[entity.id] = entity

    def add_edge(self, edge: LineageEdge) -> None:
        self.edges.append(edge)


class GraphBuilder:
    def build(self, entities: Iterable[MetadataEntity], edges: Iterable[LineageEdge]) -> MetadataGraph:
        graph = MetadataGraph()
        for entity in entities:
            graph.add_entity(entity)
        for edge in edges:
            graph.add_edge(edge)
        return graph
