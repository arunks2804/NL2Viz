import pandas as pd
import numpy as np
import json
from faker import Faker
from pathlib import Path
from datetime import date, timedelta
import random

fake = Faker()
random.seed(42)
np.random.seed(42)

BASE = Path(__file__).parent.parent

# ── Sales data ────────────────────────────────────────────────────────────────

PRODUCTS = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse", "Headphones", "Webcam"]
CATEGORIES = {
    "Laptop": "Electronics", "Phone": "Electronics", "Tablet": "Electronics", "Monitor": "Electronics",
    "Keyboard": "Accessories", "Mouse": "Accessories", "Headphones": "Accessories", "Webcam": "Accessories",
}
UNIT_PRICES = {
    "Laptop": (800, 1500), "Phone": (400, 900), "Tablet": (300, 700), "Monitor": (200, 500),
    "Keyboard": (50, 150), "Mouse": (20, 80), "Headphones": (80, 300), "Webcam": (60, 200),
}
REGIONS = ["North", "South", "East", "West"]
REPS = [fake.name() for _ in range(10)]

start = date(2023, 1, 1)
days = (date(2024, 12, 31) - start).days + 1

rows = []
for _ in range(500):
    d = start + timedelta(days=random.randint(0, days - 1))
    product = random.choice(PRODUCTS)
    lo, hi = UNIT_PRICES[product]
    unit_price = round(random.uniform(lo, hi), 2)
    units_sold = random.randint(1, 50)
    revenue = round(unit_price * units_sold, 2)
    cost = round(revenue * random.uniform(0.4, 0.6), 2)
    rows.append({
        "date": d,
        "product": product,
        "category": CATEGORIES[product],
        "region": random.choice(REGIONS),
        "sales_rep": random.choice(REPS),
        "units_sold": units_sold,
        "unit_price": unit_price,
        "revenue": revenue,
        "cost": cost,
        "profit": round(revenue - cost, 2),
    })

sales_df = pd.DataFrame(rows)
sales_path = BASE / "data" / "excel" / "sales.xlsx"
sales_df.to_excel(sales_path, index=False)
print(f"sales.xlsx written — {len(sales_df)} rows")

# ── Employees data ────────────────────────────────────────────────────────────

DEPARTMENTS = ["Sales", "Engineering", "Marketing", "Finance", "HR", "Operations"]
SALARY_RANGES = {
    "Engineering": (80000, 150000),
    "Sales": (50000, 90000),
    "Finance": (70000, 120000),
    "Marketing": (55000, 95000),
    "HR": (45000, 80000),
    "Operations": (40000, 75000),
}
STATUSES = ["Active"] * 8 + ["On Leave"] + ["Resigned"]
hire_start = date(2018, 1, 1)
hire_days = (date(2024, 12, 31) - hire_start).days

emp_rows = []
for i in range(1, 151):
    dept = random.choice(DEPARTMENTS)
    lo, hi = SALARY_RANGES[dept]
    status = random.choice(STATUSES)
    emp_rows.append({
        "employee_id": f"EMP{i:03d}",
        "name": fake.name(),
        "department": dept,
        "region": random.choice(REGIONS),
        "salary": round(random.uniform(lo, hi), 2),
        "hire_date": hire_start + timedelta(days=random.randint(0, hire_days)),
        "status": status,
        "performance_rating": random.randint(1, 5),
    })

emp_df = pd.DataFrame(emp_rows)
emp_path = BASE / "data" / "excel" / "employees.xlsx"
emp_df.to_excel(emp_path, index=False)
print(f"employees.xlsx written — {len(emp_df)} rows")

# ── Knowledge graph ───────────────────────────────────────────────────────────

kg = {
    "tables": {
        "sales": {
            "description": "Daily sales transactions for all products across regions",
            "columns": {
                "date": {"type": "DATE", "description": "Transaction date"},
                "product": {"type": "VARCHAR", "description": "Product name", "values": PRODUCTS},
                "category": {"type": "VARCHAR", "description": "Product category"},
                "region": {"type": "VARCHAR", "description": "Sales region", "values": REGIONS},
                "sales_rep": {"type": "VARCHAR", "description": "Sales representative name"},
                "units_sold": {"type": "INTEGER", "description": "Number of units sold"},
                "unit_price": {"type": "DECIMAL", "description": "Price per unit in USD"},
                "revenue": {"type": "DECIMAL", "description": "Total revenue in USD"},
                "cost": {"type": "DECIMAL", "description": "Total cost in USD"},
                "profit": {"type": "DECIMAL", "description": "Profit in USD"},
            },
            "time_column": "date",
            "useful_for": ["sales analysis", "revenue trends", "product performance", "regional comparison", "profit analysis"],
        },
        "employees": {
            "description": "Employee records including salary, department, and performance",
            "columns": {
                "employee_id": {"type": "VARCHAR", "description": "Unique employee identifier"},
                "name": {"type": "VARCHAR", "description": "Employee full name"},
                "department": {"type": "VARCHAR", "description": "Department name", "values": DEPARTMENTS},
                "region": {"type": "VARCHAR", "description": "Employee region"},
                "salary": {"type": "DECIMAL", "description": "Annual salary in USD"},
                "hire_date": {"type": "DATE", "description": "Date employee was hired"},
                "status": {"type": "VARCHAR", "description": "Employment status", "values": ["Active", "On Leave", "Resigned"]},
                "performance_rating": {"type": "INTEGER", "description": "Performance rating 1-5"},
            },
            "time_column": "hire_date",
            "useful_for": ["headcount analysis", "salary comparison", "department breakdown", "hiring trends", "performance analysis"],
        },
    },
    "relationships": [
        {
            "from": "sales.region",
            "to": "employees.region",
            "type": "same_region",
            "description": "Sales and employees share the same region values — useful for cross-table regional analysis",
        }
    ],
    "common_queries": [
        "total revenue by product last year",
        "monthly sales trend 2024 vs 2023",
        "top performing regions by profit",
        "salary distribution by department",
        "headcount by department",
        "revenue contribution by product category",
        "employee hiring trend over years",
        "profit margin by product",
    ],
}

kg_path = BASE / "data" / "schema" / "knowledge_graph.json"
with open(kg_path, "w") as f:
    json.dump(kg, f, indent=2)
print(f"knowledge_graph.json written")
