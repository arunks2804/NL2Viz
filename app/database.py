import duckdb
import json
from pathlib import Path

DB_PATH = "./data/nl2viz.duckdb"
EXCEL_DIR = "./data/excel"
KG_PATH = "./data/schema/knowledge_graph.json"


def get_connection():
    return duckdb.connect(DB_PATH)


def init_database():
    conn = duckdb.connect(DB_PATH)

    existing = {r[0] for r in conn.execute("SHOW TABLES").fetchall()}

    if "sales" not in existing:
        sales_path = Path(EXCEL_DIR) / "sales.xlsx"
        if sales_path.exists():
            conn.execute(f"CREATE TABLE sales AS SELECT * FROM read_xlsx('{sales_path}')")
            print(f"Sales rows: {conn.execute('SELECT COUNT(*) FROM sales').fetchone()[0]}")
        else:
            print("WARNING: sales.xlsx not found — run scripts/generate_data.py first")

    if "employees" not in existing:
        emp_path = Path(EXCEL_DIR) / "employees.xlsx"
        if emp_path.exists():
            conn.execute(f"CREATE TABLE employees AS SELECT * FROM read_xlsx('{emp_path}')")
            print(f"Employee rows: {conn.execute('SELECT COUNT(*) FROM employees').fetchone()[0]}")
        else:
            print("WARNING: employees.xlsx not found — run scripts/generate_data.py first")

    print("DuckDB initialized")
    return conn


def get_schema_summary() -> str:
    with open(KG_PATH) as f:
        kg = json.load(f)

    lines = ["Available tables and columns:\n"]
    for table_name, table_info in kg["tables"].items():
        lines.append(f"Table: {table_name}")
        lines.append(f"Description: {table_info['description']}")
        lines.append("Columns:")
        for col_name, col_info in table_info["columns"].items():
            line = f"  - {col_name} ({col_info['type']}): {col_info['description']}"
            if "values" in col_info:
                line += f" — possible values: {col_info['values']}"
            lines.append(line)
        lines.append(f"Time column: {table_info['time_column']}")
        lines.append("")

    if kg.get("relationships"):
        lines.append("Relationships between tables:")
        for rel in kg["relationships"]:
            lines.append(f"  - {rel['from']} → {rel['to']}: {rel['description']}")

    return "\n".join(lines)


def execute_query(sql: str) -> dict:
    try:
        conn = get_connection()
        result = conn.execute(sql).fetchdf()
        # Convert non-serialisable types (dates, numpy) to plain Python
        rows = []
        for row in result.values.tolist():
            rows.append([str(v) if hasattr(v, 'isoformat') else (None if str(v) == 'nan' else v) for v in row])
        return {
            "columns": list(result.columns),
            "rows": rows,
            "row_count": len(result),
            "error": None,
        }
    except Exception as e:
        return {"columns": [], "rows": [], "row_count": 0, "error": str(e)}


def load_excel_table(file_path: str, table_name: str) -> dict:
    try:
        conn = get_connection()
        existing = {r[0] for r in conn.execute("SHOW TABLES").fetchall()}
        if table_name in existing:
            conn.execute(f"DROP TABLE {table_name}")
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_xlsx('{file_path}')")
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        cols = [r[0] for r in conn.execute(f"DESCRIBE {table_name}").fetchall()]
        return {"table": table_name, "columns": cols, "row_count": row_count, "error": None}
    except Exception as e:
        return {"table": table_name, "columns": [], "row_count": 0, "error": str(e)}
