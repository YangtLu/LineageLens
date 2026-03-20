# LineageLens Architecture

## 1. Problem framing
You have a traditional SQL ecosystem with:
- tens of thousands of tables,
- columns and comments,
- ETL scripts that read, transform, and write data,
- a need for fast metadata lookup and reliable lineage analysis.

This is best designed as a **metadata + lineage platform first**, and an **LLM/GraphRAG application second**.

If you start with the LLM before building a precise metadata backbone, the answers will be hard to trust. For lineage and root-cause analysis, deterministic graph traversal should be the primary engine, while the LLM should help with interpretation, summarization, and flexible querying.

## 2. Core design principles
1. **Metadata is the source of truth**  
   Store canonical representations of systems, databases, schemas, tables, columns, ETL jobs, and lineage edges.
2. **Graph for relationships, vector index for search**  
   Use a graph model for lineage/path traversal and embeddings for fuzzy discovery.
3. **Deterministic first, LLM second**  
   Exact lookup, lineage tracing, and impact analysis should work without an LLM.
4. **Incremental ingestion**  
   Re-ingest only changed schemas and scripts.
5. **Confidence-aware lineage**  
   Every lineage edge should include extraction method and confidence.
6. **Python-first implementation**  
   Build ingestion, parsing, indexing, orchestration, and APIs primarily in Python.

## 3. Recommended logical architecture

```text
                +---------------------------+
                |   Source SQL metadata     |
                | tables / columns/comments |
                +-------------+-------------+
                              |
                              v
                +---------------------------+
                | Metadata ingestion layer  |
                | connectors + normalization|
                +-------------+-------------+
                              |
                              v
                +---------------------------+
                | ETL parsing layer         |
                | Python AST / SQL parser   |
                +-------------+-------------+
                              |
                              v
                +---------------------------+
                | Canonical metadata graph  |
                | tables columns jobs edges |
                +------+------+-------------+
                       |      |
                       |      +----------------------+
                       |                             |
                       v                             v
        +---------------------------+   +---------------------------+
        | Graph / lineage store     |   | Embedding / vector index  |
        | Neo4j / Memgraph / PG     |   | pgvector / Qdrant / FAISS |
        +-------------+-------------+   +-------------+-------------+
                      \                           /
                       \                         /
                        v                       v
                     +--------------------------------+
                     | Query service / GraphRAG layer |
                     | lookup lineage RCA explanation |
                     +--------------------------------+
```

## 4. Canonical data model

### 4.1 Node types
You should define these core node types:
- `System`: source platform or warehouse.
- `Database`
- `Schema`
- `Table`
- `Column`
- `ETLJob`: Python script, Airflow task, Spark job, dbt model, stored procedure, etc.
- `CodeArtifact`: script/module/file.
- `Transformation`: optional intermediate logical step.
- `Owner`: team or person.
- `Tag`: domain, PII, criticality, quality label.
- `RunEvent`: optional runtime execution instance for observability.

### 4.2 Edge types
Recommended lineage/metadata edges:
- `DATABASE_CONTAINS_SCHEMA`
- `SCHEMA_CONTAINS_TABLE`
- `TABLE_CONTAINS_COLUMN`
- `JOB_READS_TABLE`
- `JOB_READS_COLUMN`
- `JOB_WRITES_TABLE`
- `JOB_WRITES_COLUMN`
- `COLUMN_DERIVES_FROM_COLUMN`
- `TABLE_DERIVES_FROM_TABLE`
- `JOB_CALLS_JOB`
- `ARTIFACT_DEFINES_JOB`
- `TABLE_HAS_TAG`
- `COLUMN_HAS_TAG`
- `TABLE_OWNED_BY`
- `COLUMN_OWNED_BY`

### 4.3 Required properties
Each node/edge should include:
- stable ID,
- source system,
- display name,
- description/comment,
- timestamps,
- ingestion version,
- extraction method,
- confidence score,
- optional code location (`file`, `line_start`, `line_end`).

## 5. Storage recommendation
For your scale and use case, a practical stack is:

### Option A: PostgreSQL + pgvector + NetworkX/SQL tables
Best when you want operational simplicity.
- PostgreSQL stores metadata tables and lineage edges.
- `pgvector` stores embeddings.
- Python handles traversal queries or recursive SQL.

### Option B: Neo4j + PostgreSQL + pgvector
Best when lineage traversal is central and paths are complex.
- Neo4j stores graph relationships.
- PostgreSQL stores ingestion state and structured metadata.
- `pgvector` or Qdrant stores embeddings.

### Recommendation
If this is your first version, start with **PostgreSQL + pgvector**, and keep the graph schema compatible with Neo4j later. This reduces operational complexity while you prove the metadata extraction quality.

## 6. Ingestion pipeline design

### 6.1 Metadata ingestion
Inputs:
- table names,
- column names,
- comments,
- database/schema hierarchy,
- optional stats such as row counts, refresh frequency, owners.

Output:
- normalized table and column entities.

Implementation suggestion:
- Use `pandas` or direct SQLAlchemy queries for extraction.
- Normalize names into a canonical format:
  - `system.database.schema.table`
  - `system.database.schema.table.column`
- Preserve original casing as display metadata.

### 6.2 ETL ingestion
Inputs:
- Python ETL scripts,
- embedded SQL strings,
- Airflow DAGs or orchestration metadata if available.

Extraction approach:
1. Parse Python with `ast`.
2. Extract SQL strings and execution calls.
3. Parse SQL using `sqlglot`.
4. Detect read/write tables and column mappings.
5. Attach confidence levels:
   - high: explicit SQL `INSERT INTO ... SELECT ...`
   - medium: inferred from variable flow
   - low: heuristic string matching

### 6.3 Incremental update strategy
Maintain ingestion fingerprints for:
- schema snapshots,
- file hashes for ETL scripts,
- parser version,
- extraction timestamp.

This lets you rebuild only changed graph segments.

## 7. Lineage extraction strategy
Use a layered approach.

### Layer 1: Table-level lineage
Fastest and easiest to stabilize.
- Which upstream tables feed this table?
- Which downstream tables depend on this table?

### Layer 2: Column-level lineage
More valuable for root-cause analysis.
- Which source columns contribute to a target column?
- Which transformations exist between them?

### Layer 3: Runtime lineage and quality signals
Later enhancement.
- Which specific run introduced a problem?
- Which job version changed lineage?
- Which alerts or test failures relate to the field?

## 8. GraphRAG design
GraphRAG should not replace exact graph traversal. It should orchestrate retrieval from multiple evidence sources.

### 8.1 Retrieval layers
For a user query, retrieve from:
1. exact metadata lookup,
2. graph neighborhood expansion,
3. vector similarity over table/column/job descriptions,
4. optional keyword/BM25 search.

### 8.2 Embedding units
Generate embeddings for:
- table documents,
- column documents,
- job documents,
- lineage path summaries.

Example table document:
```text
Table: finance.daily_revenue
Description: Daily aggregated revenue by region.
Columns: revenue_date, region_id, gross_revenue, net_revenue.
Upstream: raw.orders, raw.refunds.
Downstream: finance.monthly_revenue.
Owner: finance-analytics.
```

### 8.3 Query flow
1. Parse question intent: lookup, lineage, impact, root-cause, discovery.
2. Run deterministic retrieval first.
3. Expand relevant subgraph around matched entities.
4. Use vector retrieval for semantically similar entities.
5. Ask LLM to summarize only the retrieved evidence.
6. Return answer with lineage path and confidence.

## 9. Example product capabilities

### 9.1 Data discovery
Questions:
- "Find tables related to customer churn."
- "What fields contain refund amount?"

Implementation:
- lexical search + embeddings + comments.

### 9.2 Lineage
Questions:
- "What upstream fields feed `mart_sales.net_amount`?"
- "Show downstream impact of changing `raw_orders.discount`"

Implementation:
- graph traversal over `COLUMN_DERIVES_FROM_COLUMN` and `TABLE_DERIVES_FROM_TABLE`.

### 9.3 Root-cause analysis
Questions:
- "Why is `finance.daily_revenue.net_revenue` wrong?"
- "Which source columns and jobs influence this field?"

Implementation:
- trace upstream columns,
- include jobs and code references,
- rank paths by confidence and recency.

## 10. Suggested Python technology stack

### Core libraries
- `pydantic`: typed config and models.
- `sqlalchemy`: database access.
- `pandas`: metadata ingestion convenience.
- `sqlglot`: SQL parsing and lineage extraction.
- `networkx`: local graph algorithms and prototyping.
- `sentence-transformers` or provider embeddings: semantic search.
- `fastapi`: API layer.
- `typer`: CLI tooling.
- `pytest`: tests.

### Optional libraries
- `neo4j` Python driver if you adopt Neo4j.
- `qdrant-client` if using Qdrant.
- `duckdb` for local prototyping.
- `tree-sitter` if Python AST is insufficient for SQL extraction patterns.

## 11. Recommended implementation roadmap

### Phase 1: Metadata backbone
Build:
- schema ingestion,
- canonical IDs,
- table/column search,
- basic API.

Deliverable:
- exact lookup by table/column/comment.

### Phase 2: Table-level lineage
Build:
- ETL script registry,
- read/write extraction,
- job-to-table lineage.

Deliverable:
- upstream/downstream table traversal.

### Phase 3: Column-level lineage
Build:
- SQL select expression parsing,
- column mapping edges,
- confidence scoring.

Deliverable:
- source-field to target-field tracing.

### Phase 4: GraphRAG
Build:
- embedding pipeline,
- hybrid retrieval,
- LLM summarization with citations.

Deliverable:
- natural-language query answering grounded in metadata graph.

### Phase 5: Quality and observability
Build:
- data quality annotations,
- run failures,
- freshness info,
- lineage change detection.

Deliverable:
- faster issue diagnosis and impact analysis.

## 12. API design recommendation
Create a small set of stable service interfaces:
- `search_entities(query, entity_type=None)`
- `get_table(table_id)`
- `get_column(column_id)`
- `get_upstream(entity_id, depth=3)`
- `get_downstream(entity_id, depth=3)`
- `explain_column_lineage(column_id)`
- `root_cause_analysis(column_id)`
- `semantic_search(question)`
- `answer_question(question)`

## 13. Important design warnings
1. **Do not rely on comments alone**  
   Comments help discovery but are not lineage truth.
2. **Do not make LLM extraction the only extraction method**  
   Use parsers first; use LLMs only as fallback or summarizer.
3. **Do not skip canonical IDs**  
   Name ambiguity will become painful at your scale.
4. **Do not mix raw and curated lineage edges without confidence labels**  
   Keep provenance and confidence explicit.
5. **Do not start with full automation for all ETL styles**  
   Start with the ETL patterns that produce most of your business-critical tables.

## 14. Best first milestone
Your fastest path to value is:
1. ingest all tables, columns, and comments,
2. support exact and semantic search,
3. parse one major ETL pattern,
4. build table-level lineage,
5. expose a Python API and FastAPI endpoint.

Once that works, expand to column-level lineage and then GraphRAG summaries.
