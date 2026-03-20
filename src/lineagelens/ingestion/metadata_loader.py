from __future__ import annotations

from collections.abc import Iterable

from lineagelens.models.schema import MetadataEntity


class MetadataLoader:
    """Interface for loading table and column metadata from source systems."""

    def load_entities(self) -> Iterable[MetadataEntity]:
        raise NotImplementedError
