COLORS = [
    "#4f9cf9", "#7c3aed", "#10b981",
    "#f59e0b", "#ef4444", "#06b6d4",
    "#8b5cf6", "#84cc16",
]


def build_echarts_option(viz_config: dict, data: dict) -> dict:
    chart_type = viz_config.get("chart_type", "bar")
    title = viz_config.get("title", "Chart")
    x_col = viz_config.get("x_axis")
    y_col = viz_config.get("y_axis")
    series_col = viz_config.get("series_column")

    columns = data["columns"]
    rows = data["rows"]

    if not x_col and columns:
        x_col = columns[0]
    if not y_col and len(columns) > 1:
        y_col = columns[-1]

    records = [dict(zip(columns, row)) for row in rows]

    option = {
        "title": {"text": title, "textStyle": {"color": "#e2e8f0", "fontSize": 14}},
        "backgroundColor": "transparent",
        "color": COLORS,
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"containLabel": True, "left": "8%", "right": "5%", "bottom": "20%", "top": "18%"},
        "legend": {"textStyle": {"color": "#94a3b8"}, "top": "8%"},
    }

    if chart_type == "line":
        x_values = list(dict.fromkeys([str(r.get(x_col, "")) for r in records]))
        if series_col:
            series_values = list(dict.fromkeys([str(r.get(series_col, "")) for r in records]))
            series = [
                {
                    "name": sv, "type": "line", "smooth": True,
                    "data": [r.get(y_col, 0) for r in records if str(r.get(series_col, "")) == sv],
                }
                for sv in series_values
            ]
        else:
            series = [{"type": "line", "smooth": True, "data": [r.get(y_col, 0) for r in records]}]
        option["xAxis"] = {"type": "category", "data": x_values, "axisLabel": {"color": "#94a3b8", "rotate": 30, "interval": 0}}
        option["yAxis"] = {"type": "value", "axisLabel": {"color": "#94a3b8"}}
        option["series"] = series

    elif chart_type == "bar":
        x_values = list(dict.fromkeys([str(r.get(x_col, "")) for r in records]))
        if series_col:
            series_values = list(dict.fromkeys([str(r.get(series_col, "")) for r in records]))
            series = []
            for sv in series_values:
                lookup = {str(r.get(x_col, "")): r.get(y_col, 0) for r in records if str(r.get(series_col, "")) == sv}
                series.append({
                    "name": sv, "type": "bar", "barCategoryGap": "30%",
                    "data": [lookup.get(x, 0) for x in x_values],
                })
        else:
            series = [{"type": "bar", "barCategoryGap": "40%", "data": [r.get(y_col, 0) for r in records]}]
        option["xAxis"] = {"type": "category", "data": x_values, "axisLabel": {"color": "#94a3b8", "rotate": 30, "interval": 0}}
        option["yAxis"] = {"type": "value", "axisLabel": {"color": "#94a3b8"}}
        option["series"] = series

    elif chart_type == "pie":
        option["series"] = [{
            "type": "pie", "radius": ["40%", "70%"],
            "data": [{"name": str(r.get(x_col, "")), "value": r.get(y_col, 0)} for r in records],
            "label": {"color": "#e2e8f0"},
        }]
        option.pop("xAxis", None)
        option.pop("yAxis", None)
        option.pop("grid", None)

    elif chart_type == "bar_horizontal":
        option["xAxis"] = {"type": "value", "axisLabel": {"color": "#94a3b8"}}
        option["yAxis"] = {
            "type": "category",
            "data": [str(r.get(x_col, "")) for r in records],
            "axisLabel": {"color": "#94a3b8", "interval": 0},
        }
        option["series"] = [{"type": "bar", "barCategoryGap": "40%", "data": [r.get(y_col, 0) for r in records]}]

    elif chart_type == "scatter":
        option["xAxis"] = {"type": "value", "axisLabel": {"color": "#94a3b8"}}
        option["yAxis"] = {"type": "value", "axisLabel": {"color": "#94a3b8"}}
        option["series"] = [{"type": "scatter", "data": [[r.get(x_col, 0), r.get(y_col, 0)] for r in records]}]

    else:
        x_values = [str(r.get(x_col, "")) for r in records]
        option["xAxis"] = {"type": "category", "data": x_values, "axisLabel": {"color": "#94a3b8", "interval": 0}}
        option["yAxis"] = {"type": "value", "axisLabel": {"color": "#94a3b8"}}
        option["series"] = [{"type": "bar", "barCategoryGap": "40%", "data": [r.get(y_col, 0) for r in records]}]

    return option
