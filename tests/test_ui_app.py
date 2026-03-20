from lineagelens.models.schema import LineageEdgeType
from lineagelens.ui.app import LineageLensServer


def test_ingest_files_extracts_tables_jobs_and_lineage() -> None:
    server = LineageLensServer()

    graph = server.ingest_files(
        [
            {
                "name": "daily_revenue.sql",
                "type": "sql",
                "content": "insert into finance.daily_revenue select * from raw.orders join raw.refunds on raw.orders.id = raw.refunds.order_id;",
            },
            {
                "name": "backfill.py",
                "type": "python",
                "content": 'query = """create table mart.customer_health as select * from finance.daily_revenue join crm.accounts on finance.daily_revenue.account_id = crm.accounts.id"""',
            },
        ]
    )

    assert graph["stats"]["jobs"] == 2
    assert graph["stats"]["tables"] >= 4
    assert any(edge["edge_type"] == LineageEdgeType.TABLE_DERIVES_FROM_TABLE for edge in graph["edges"])


def test_query_lineage_returns_matching_subgraph() -> None:
    server = LineageLensServer()
    server.ingest_files(
        [
            {
                "name": "daily_revenue.sql",
                "type": "sql",
                "content": "insert into finance.daily_revenue select * from raw.orders;",
            }
        ]
    )

    result = server.query_lineage("daily_revenue")

    assert any(match["display_name"] == "daily_revenue" for match in result["matches"])
    assert result["subgraph"]["edges"]
