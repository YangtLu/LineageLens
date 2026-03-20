from lineagelens.lineage.graph_builder import MetadataGraph
from lineagelens.models.schema import EntityType, MetadataEntity
from lineagelens.query.service import QueryService


def test_search_entities_matches_description() -> None:
    graph = MetadataGraph()
    graph.add_entity(
        MetadataEntity(
            id="table:finance.daily_revenue",
            entity_type=EntityType.TABLE,
            qualified_name="warehouse.finance.daily_revenue",
            display_name="daily_revenue",
            description="Daily aggregated revenue by region.",
        )
    )

    service = QueryService(graph)

    results = service.search_entities("aggregated revenue")

    assert len(results) == 1
    assert results[0].display_name == "daily_revenue"
