from langsmith import traceable
from app.tools.query_builder import build_query, load_kg


@traceable(name="build_query_from_kg")
async def query_node(state: dict) -> dict:
    """
    Node 2: Deterministic query builder.
    Uses Knowledge Graph to construct SQL — no LLM, always correct column names.
    """
    kg = load_kg()
    sql = build_query(state["understanding"], kg)

    return {**state, "sql": sql}
