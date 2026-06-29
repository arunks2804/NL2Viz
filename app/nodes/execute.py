from langsmith import traceable
from app.database import execute_query


@traceable(name="execute_query")
async def execute_node(state: dict) -> dict:
    result = execute_query(state["sql"])

    if result["error"]:
        return {**state, "error": result["error"], "data": None}

    return {**state, "data": result, "error": None}
