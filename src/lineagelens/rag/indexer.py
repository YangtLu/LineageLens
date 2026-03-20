from __future__ import annotations

from collections.abc import Iterable

from lineagelens.models.schema import MetadataEntity


class GraphRAGIndexer:
    """Interface for creating searchable documents from metadata entities."""

    def build_documents(self, entities: Iterable[MetadataEntity]) -> list[str]:
        documents: list[str] = []
        for entity in entities:
            documents.append(
                f"{entity.entity_type.value}: {entity.qualified_name}\n"
                f"description: {entity.description or ''}"
            )
        return documents
