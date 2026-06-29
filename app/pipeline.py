from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

from app.nodes.understand import understand_node
from app.nodes.query import query_node
from app.nodes.execute import execute_node
from app.nodes.visualize import visualize_node
from app.nodes.format import format_node


class NL2VizState(TypedDict):
    # Input
    question: str
    provider: str
    model: str
    api_key: str

    # Node 1 output
    understanding: Optional[dict]
    schema: Optional[str]

    # Node 2 output
    sql: Optional[str]

    # Node 3 output
    data: Optional[dict]
    error: Optional[str]

    # Node 4 output — list of chart configs (supports multiple charts)
    viz_configs: Optional[list]

    # Node 5 output — list of ECharts options
    echarts_options: Optional[list]


def should_continue(state: NL2VizState) -> str:
    if state.get("error"):
        return "error"
    if not state.get("data") or state["data"].get("row_count", 0) == 0:
        return "no_data"
    return "continue"


def build_pipeline():
    workflow = StateGraph(NL2VizState)

    workflow.add_node("understand", understand_node)
    workflow.add_node("write_query", query_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("visualize", visualize_node)
    workflow.add_node("format", format_node)

    workflow.set_entry_point("understand")
    workflow.add_edge("understand", "write_query")
    workflow.add_edge("write_query", "execute")

    workflow.add_conditional_edges(
        "execute",
        should_continue,
        {"continue": "visualize", "error": END, "no_data": END},
    )

    workflow.add_edge("visualize", "format")
    workflow.add_edge("format", END)

    return workflow.compile()


pipeline = build_pipeline()
