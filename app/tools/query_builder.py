import json
import re

KG_PATH = "./data/schema/knowledge_graph.json"


def load_kg() -> dict:
    with open(KG_PATH) as f:
        return json.load(f)


def extract_years(time_period: str) -> list:
    years = re.findall(r'\d{4}', str(time_period))
    return [int(y) for y in years]


def find_metric_columns(table_info: dict, intent: str) -> list:
    """Return all numeric columns mentioned in the intent. Falls back to first numeric column."""
    intent_lower = intent.lower()
    matched = []
    for col_name, col_info in table_info["columns"].items():
        if col_info["type"] in ["DECIMAL", "INTEGER"]:
            if col_name.lower() in intent_lower or col_name.replace("_", " ").lower() in intent_lower:
                matched.append(col_name)
    if not matched:
        for col_name, col_info in table_info["columns"].items():
            if col_info["type"] in ["DECIMAL", "INTEGER"]:
                return [col_name]
    return matched


def build_query(understanding: dict, kg: dict) -> str:
    tables = understanding.get("tables_needed", ["sales"])
    table = tables[0] if tables else "sales"
    table_info = kg["tables"].get(table, {})
    time_col = table_info.get("time_column", "date")
    intent = understanding.get("intent", "")

    select_cols = []
    where_clauses = []
    group_by_cols = []
    order_by = ""

    # Group by column
    group_by = understanding.get("group_by")
    if group_by and group_by in table_info.get("columns", {}):
        select_cols.append(group_by)
        group_by_cols.append(group_by)

    # Time period
    time_period = str(understanding.get("time_period", "") or "")

    if "vs" in time_period or "versus" in time_period:
        years = extract_years(time_period)
        if years:
            where_clauses.append(f"YEAR({time_col}) IN ({','.join(map(str, years))})")
        select_cols.append(f"YEAR({time_col}) as year")
        group_by_cols.append(f"YEAR({time_col})")

    elif "last year" in time_period.lower():
        where_clauses.append(f"{time_col} >= CURRENT_DATE - INTERVAL 1 YEAR")
        select_cols.append(f"strftime({time_col}, '%Y-%m') as month")
        group_by_cols.append(f"strftime({time_col}, '%Y-%m')")

    elif "last month" in time_period.lower():
        where_clauses.append(f"{time_col} >= CURRENT_DATE - INTERVAL 1 MONTH")

    elif re.match(r'^\d{4}$', time_period.strip()):
        where_clauses.append(f"YEAR({time_col}) = {time_period.strip()}")

    # Metric columns and aggregation — supports multiple metrics
    metric_cols = find_metric_columns(table_info, intent)
    aggregation = understanding.get("aggregation", "sum")
    first_alias = None

    for metric_col in metric_cols:
        if aggregation == "count":
            alias = "count"
            select_cols.append("COUNT(*) as count")
        elif aggregation == "average":
            alias = f"avg_{metric_col}"
            select_cols.append(f"ROUND(AVG({metric_col}), 2) as {alias}")
        elif aggregation == "percentage":
            alias = f"pct_{metric_col}"
            select_cols.append(
                f"ROUND(SUM({metric_col}) * 100.0 / SUM(SUM({metric_col})) OVER(), 2) as {alias}"
            )
        else:  # sum (default)
            alias = f"total_{metric_col}"
            select_cols.append(f"ROUND(SUM({metric_col}), 2) as {alias}")
        if first_alias is None:
            first_alias = alias

    order_by = f"{first_alias} DESC" if first_alias else ""

    # Filters — skip date/time columns (already handled by time_period logic above)
    TIME_COLS = {"date", "hire_date", "month", "year"}
    filters = understanding.get("filters", {}) or {}
    for col, val in filters.items():
        if col in table_info.get("columns", {}) and col.lower() not in TIME_COLS:
            where_clauses.append(f"{col} = '{val}'")

    # Build SQL
    sql = f"SELECT {', '.join(select_cols) or '*'}"
    sql += f"\nFROM {table}"
    if where_clauses:
        sql += f"\nWHERE {' AND '.join(where_clauses)}"
    if group_by_cols:
        sql += f"\nGROUP BY {', '.join(group_by_cols)}"
    if order_by:
        sql += f"\nORDER BY {order_by}"
    sql += "\nLIMIT 50"

    return sql
