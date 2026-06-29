from langsmith import traceable
from app.tools.echarts_formatter import build_echarts_option


@traceable(name="format_echarts")
async def format_node(state: dict) -> dict:
    """
    Node 5: Deterministic ECharts formatter.
    Builds one ECharts option per viz_config — supports multiple charts.
    """
    echarts_options = [
        build_echarts_option(cfg, state["data"])
        for cfg in state["viz_configs"]
    ]

    return {**state, "echarts_options": echarts_options}
