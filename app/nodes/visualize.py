import json
from langsmith import traceable
from app.llm_provider import call_llm
from app.prompts import VISUALIZE_PROMPT


@traceable(name="decide_visualization")
async def visualize_node(state: dict) -> dict:
    data = state["data"]
    u = state["understanding"]

    has_time = any(
        col.lower() in ["date", "month", "year", "hire_date"]
        for col in data["columns"]
    )
    sample = data["rows"][:3] if data["rows"] else []

    response = await call_llm(
        provider=state["provider"],
        model=state["model"],
        api_key=state["api_key"],
        system_prompt=VISUALIZE_PROMPT.format(
            question=state["question"],
            columns=data["columns"],
            sample_data=sample,
            row_count=data["row_count"],
            has_time=has_time,
            is_comparison=u.get("comparison", False),
        ),
        user_prompt="Decide the best visualization(s).",
    )

    parsed = json.loads(response)

    # Normalise — always a list
    if isinstance(parsed, dict):
        viz_configs = [parsed]
    else:
        viz_configs = parsed

    # Auto-expand: if only one chart config but data has multiple numeric columns,
    # generate one chart per numeric column so all metrics are shown
    columns = data["columns"]
    numeric_cols = [c for c in columns[1:] if c not in ("year", "month", "date")]
    if len(viz_configs) == 1 and len(numeric_cols) > 1:
        base = viz_configs[0]
        x_col = base.get("x_axis") or columns[0]
        viz_configs = [
            {
                **base,
                "y_axis": col,
                "title": col.replace("total_", "").replace("avg_", "").replace("_", " ").title() + " by " + x_col.replace("_", " ").title(),
                "reasoning": base.get("reasoning", ""),
            }
            for col in numeric_cols
        ]

    return {**state, "viz_configs": viz_configs}
