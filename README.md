# LineageLens

LineageLens is a Python-first blueprint for turning large-scale SQL metadata and ETL code into a lineage-aware GraphRAG system.

## Goals
- Ingest tens of thousands of SQL tables, columns, comments, and ETL relationships.
- Build a normalized metadata graph that supports lineage traversal.
- Generate embeddings and graph-aware retrieval for fast data discovery.
- Answer questions such as:
  - "Which downstream tables depend on `orders.amount`?"
  - "What ETL jobs write into `finance.daily_revenue`?"
  - "Which source fields may explain a bad processed field?"

## Proposed architecture
See [docs/architecture.md](docs/architecture.md).

## Repository layout
- `docs/architecture.md`: system design and implementation phases.
- `src/lineagelens/models/schema.py`: core metadata and lineage models.
- `src/lineagelens/config/settings.py`: typed application settings.
- `src/lineagelens/ingestion/metadata_loader.py`: metadata ingestion interfaces.
- `src/lineagelens/lineage/graph_builder.py`: graph construction service.
- `src/lineagelens/rag/indexer.py`: GraphRAG indexing interfaces.
- `src/lineagelens/query/service.py`: high-level query APIs.

## Recommended implementation phases
1. Build metadata ingestion for schemas, columns, comments, and ETL scripts.
2. Normalize everything into one canonical graph model.
3. Add lineage extraction rules for SQL and Python ETL.
4. Add graph storage and vector indexing.
5. Expose query APIs for lookup, lineage, and root-cause analysis.
6. Add LLM-powered GraphRAG only after deterministic retrieval works well.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```
