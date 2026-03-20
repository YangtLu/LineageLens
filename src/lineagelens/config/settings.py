from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StorageSettings:
    metadata_backend: str = "postgres"
    graph_backend: str = "postgres"
    vector_backend: str = "pgvector"


@dataclass(slots=True)
class ParsingSettings:
    sql_parser: str = "sqlglot"
    python_parser: str = "ast"
    enable_column_lineage: bool = False


@dataclass(slots=True)
class AppSettings:
    environment: str = "dev"
    storage: StorageSettings = field(default_factory=StorageSettings)
    parsing: ParsingSettings = field(default_factory=ParsingSettings)
