import json
from pathlib import Path

KG_PATH = "./data/schema/knowledge_graph.json"


def load_kg() -> dict:
    with open(KG_PATH) as f:
        return json.load(f)


def save_kg(kg: dict):
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2)


def add_table_to_kg(table_name: str, columns: list, description: str = ""):
    kg = load_kg()
    col_dict = {col: {"type": "VARCHAR", "description": col.replace("_", " ").title()} for col in columns}
    kg["tables"][table_name] = {
        "description": description or f"Uploaded table: {table_name}",
        "columns": col_dict,
        "time_column": next((c for c in columns if "date" in c.lower() or "time" in c.lower()), None),
        "useful_for": [f"{table_name} analysis"],
    }
    save_kg(kg)
