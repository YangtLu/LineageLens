from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from lineagelens.lineage.graph_builder import GraphBuilder, MetadataGraph
from lineagelens.models.schema import EntityType, LineageEdge, LineageEdgeType, MetadataEntity
from lineagelens.query.service import QueryService

STATIC_DIR = Path(__file__).resolve().parent / "static"
READ_TABLE_PATTERN = re.compile(r"\b(?:from|join)\s+([\w.]+)", re.IGNORECASE)
WRITE_TABLE_PATTERN = re.compile(r"\b(?:insert\s+into|update|create\s+table|merge\s+into)\s+([\w.]+)", re.IGNORECASE)
PYTHON_SQL_PATTERN = re.compile(r"([\"\']{3}.*?[\"\']{3}|[\"\'].*?[\"\'])", re.DOTALL)
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][\w.]*$")


class UploadProcessor:
    def build_graph(self, files: list[dict[str, str]]) -> MetadataGraph:
        entities: dict[str, MetadataEntity] = {}
        edges: list[LineageEdge] = []

        def add_entity(entity: MetadataEntity) -> None:
            entities.setdefault(entity.id, entity)

        for file_index, file_info in enumerate(files):
            filename = file_info["name"]
            content = file_info["content"]
            artifact_id = f"artifact:{filename}"
            add_entity(
                MetadataEntity(
                    id=artifact_id,
                    entity_type=EntityType.CODE_ARTIFACT,
                    qualified_name=filename,
                    display_name=filename,
                    description=f"Uploaded {file_info['type'].upper()} script",
                    properties={"language": file_info["type"]},
                )
            )

            jobs = self._extract_jobs(filename, content, file_info["type"], file_index)
            for job in jobs:
                add_entity(job["job_entity"])
                edges.append(
                    LineageEdge(
                        source_id=artifact_id,
                        target_id=job["job_entity"].id,
                        edge_type=LineageEdgeType.ARTIFACT_DEFINES_JOB,
                        confidence=1.0,
                        extraction_method="file_upload",
                    )
                )
                for entity in job["entities"]:
                    add_entity(entity)
                edges.extend(job["edges"])

        return GraphBuilder().build(entities.values(), edges)

    def _extract_jobs(self, filename: str, content: str, file_type: str, file_index: int) -> list[dict[str, Any]]:
        statements: list[str]
        extraction_method = "sql_parser" if file_type == "sql" else "python_sql_heuristic"
        if file_type == "sql":
            statements = [statement.strip() for statement in content.split(";") if statement.strip()]
        else:
            statements = [self._strip_quotes(match) for match in PYTHON_SQL_PATTERN.findall(content)]
            statements = [statement for statement in statements if self._looks_like_sql(statement)]
            if not statements:
                statements = [content]

        jobs: list[dict[str, Any]] = []
        for statement_index, statement in enumerate(statements):
            read_tables = self._extract_identifiers(READ_TABLE_PATTERN.findall(statement))
            write_tables = self._extract_identifiers(WRITE_TABLE_PATTERN.findall(statement))
            if not read_tables and not write_tables:
                continue

            job_name = f"{Path(filename).stem}:{statement_index + 1}"
            job_id = f"job:{file_index}:{statement_index}"
            job_entity = MetadataEntity(
                id=job_id,
                entity_type=EntityType.ETL_JOB,
                qualified_name=job_name,
                display_name=job_name,
                description=f"Derived from {filename}",
                properties={"statement": statement.strip()},
            )
            entities: list[MetadataEntity] = []
            edges: list[LineageEdge] = []
            for table_name in sorted(read_tables | write_tables):
                table_id = f"table:{table_name.lower()}"
                entities.append(
                    MetadataEntity(
                        id=table_id,
                        entity_type=EntityType.TABLE,
                        qualified_name=table_name.lower(),
                        display_name=table_name.split(".")[-1],
                        description=f"Discovered from {filename}",
                    )
                )
            for table_name in sorted(read_tables):
                edges.append(
                    LineageEdge(
                        source_id=job_id,
                        target_id=f"table:{table_name.lower()}",
                        edge_type=LineageEdgeType.JOB_READS_TABLE,
                        confidence=0.9,
                        extraction_method=extraction_method,
                    )
                )
            for table_name in sorted(write_tables):
                table_id = f"table:{table_name.lower()}"
                edges.append(
                    LineageEdge(
                        source_id=job_id,
                        target_id=table_id,
                        edge_type=LineageEdgeType.JOB_WRITES_TABLE,
                        confidence=0.95,
                        extraction_method=extraction_method,
                    )
                )
                for upstream_table in sorted(read_tables):
                    if upstream_table.lower() == table_name.lower():
                        continue
                    edges.append(
                        LineageEdge(
                            source_id=f"table:{upstream_table.lower()}",
                            target_id=table_id,
                            edge_type=LineageEdgeType.TABLE_DERIVES_FROM_TABLE,
                            confidence=0.85,
                            extraction_method=extraction_method,
                        )
                    )
            jobs.append({"job_entity": job_entity, "entities": entities, "edges": edges})
        return jobs

    @staticmethod
    def _strip_quotes(value: str) -> str:
        if value.startswith(("\"\"\"", "'''") ) and value.endswith(("\"\"\"", "'''")):
            return value[3:-3]
        if value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
            return value[1:-1]
        return value

    @staticmethod
    def _looks_like_sql(value: str) -> bool:
        normalized = value.lower()
        return any(keyword in normalized for keyword in ("select ", "insert ", "update ", "merge ", "create table"))

    @staticmethod
    def _extract_identifiers(items: list[str]) -> set[str]:
        identifiers = set()
        for item in items:
            cleaned = item.strip().strip(",")
            if IDENTIFIER_PATTERN.match(cleaned):
                identifiers.add(cleaned)
        return identifiers


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


class LineageLensServer:
    def __init__(self) -> None:
        self.processor = UploadProcessor()
        self.graph = MetadataGraph()
        self.query_service = QueryService(self.graph)

    def ingest_files(self, files: list[dict[str, str]]) -> dict[str, Any]:
        self.graph = self.processor.build_graph(files)
        self.query_service = QueryService(self.graph)
        return self.serialize_graph()

    def serialize_graph(self) -> dict[str, Any]:
        nodes = [_to_jsonable(asdict(entity)) for entity in self.graph.entities.values()]
        edges = [_to_jsonable(asdict(edge)) for edge in self.graph.edges]
        stats = {
            "entities": len(nodes),
            "jobs": sum(1 for entity in self.graph.entities.values() if entity.entity_type == EntityType.ETL_JOB),
            "tables": sum(1 for entity in self.graph.entities.values() if entity.entity_type == EntityType.TABLE),
            "edges": len(edges),
        }
        return {"nodes": nodes, "edges": edges, "stats": stats}

    def query_lineage(self, query: str) -> dict[str, Any]:
        matches = self.query_service.search_entities(query)
        matched_ids = {entity.id for entity in matches}
        relevant_edges = [edge for edge in self.graph.edges if edge.source_id in matched_ids or edge.target_id in matched_ids]
        neighbor_ids = matched_ids | {edge.source_id for edge in relevant_edges} | {edge.target_id for edge in relevant_edges}
        relevant_nodes = [asdict(entity) for entity_id, entity in self.graph.entities.items() if entity_id in neighbor_ids]
        return {
            "matches": [_to_jsonable(asdict(entity)) for entity in matches],
            "subgraph": {"nodes": [_to_jsonable(node) for node in relevant_nodes], "edges": [_to_jsonable(asdict(edge)) for edge in relevant_edges]},
        }


def make_handler(server_state: LineageLensServer) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/graph":
                self._send_json(server_state.serialize_graph())
                return
            if parsed.path == "/api/query":
                params = parse_qs(parsed.query)
                query = params.get("q", [""])[0]
                self._send_json(server_state.query_lineage(query))
                return
            self._serve_static(parsed.path)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/api/upload":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            files = payload.get("files", [])
            self._send_json(server_state.ingest_files(files))

        def _serve_static(self, path: str) -> None:
            target = "index.html" if path in {"/", ""} else path.lstrip("/")
            file_path = STATIC_DIR / target
            if not file_path.exists() or not file_path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            content_type = "text/plain"
            if file_path.suffix == ".html":
                content_type = "text/html; charset=utf-8"
            elif file_path.suffix == ".css":
                content_type = "text/css; charset=utf-8"
            elif file_path.suffix == ".js":
                content_type = "application/javascript; charset=utf-8"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(file_path.read_bytes())

        def _send_json(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LineageLens browser UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(LineageLensServer()))
    print(f"LineageLens UI running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
