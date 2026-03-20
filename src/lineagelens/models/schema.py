from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntityType(str, Enum):
    SYSTEM = "system"
    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    ETL_JOB = "etl_job"
    CODE_ARTIFACT = "code_artifact"
    TRANSFORMATION = "transformation"


class LineageEdgeType(str, Enum):
    SCHEMA_CONTAINS_TABLE = "schema_contains_table"
    TABLE_CONTAINS_COLUMN = "table_contains_column"
    JOB_READS_TABLE = "job_reads_table"
    JOB_WRITES_TABLE = "job_writes_table"
    JOB_READS_COLUMN = "job_reads_column"
    JOB_WRITES_COLUMN = "job_writes_column"
    TABLE_DERIVES_FROM_TABLE = "table_derives_from_table"
    COLUMN_DERIVES_FROM_COLUMN = "column_derives_from_column"
    ARTIFACT_DEFINES_JOB = "artifact_defines_job"


@dataclass(slots=True)
class MetadataEntity:
    id: str
    entity_type: EntityType
    qualified_name: str
    display_name: str
    description: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LineageEdge:
    source_id: str
    target_id: str
    edge_type: LineageEdgeType
    confidence: float = 1.0
    extraction_method: str = "deterministic"
    properties: dict[str, Any] = field(default_factory=dict)
