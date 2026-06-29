import os
import json
import shutil
from pathlib import Path

import httpx
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "nl2viz")

from app.pipeline import pipeline
from app.database import init_database, get_schema_summary, load_excel_table
from app.knowledge_graph import add_table_to_kg

app = FastAPI(title="NL2Viz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


@app.on_event("startup")
async def startup():
    init_database()


# ─── Models ───────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    provider: str = "ollama"
    model: str = "mistral"
    api_key: Optional[str] = ""


class QueryResponse(BaseModel):
    echarts_options: Optional[list] = None   # list of ECharts option objects
    sql: Optional[str] = None
    viz_configs: Optional[list] = None
    row_count: Optional[int] = None
    error: Optional[str] = None
    no_data: Optional[bool] = None
    reasoning: Optional[str] = None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    result = await pipeline.ainvoke({
        "question": req.question,
        "provider": req.provider,
        "model": req.model,
        "api_key": req.api_key or "",
        "understanding": None,
        "schema": None,
        "sql": None,
        "data": None,
        "error": None,
        "viz_configs": None,
        "echarts_options": None,
    })

    if result.get("error"):
        return QueryResponse(error=result["error"], sql=result.get("sql"))

    row_count = (result.get("data") or {}).get("row_count", 0)
    if row_count == 0:
        return QueryResponse(
            no_data=True,
            sql=result.get("sql"),
            row_count=0,
            error="No data found for your question. Try a different time period or rephrasing.",
        )

    viz_configs = result.get("viz_configs") or []
    reasoning = " | ".join(c.get("reasoning", "") for c in viz_configs if c.get("reasoning"))

    return QueryResponse(
        echarts_options=result.get("echarts_options"),
        sql=result.get("sql"),
        viz_configs=viz_configs,
        row_count=row_count,
        error=None,
        no_data=False,
        reasoning=reasoning,
    )


@app.get("/health")
async def health():
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:11434/api/tags")
            ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "status": "ok",
        "langsmith": bool(os.getenv("LANGCHAIN_API_KEY")),
        "duckdb": "connected",
        "ollama": ollama_ok,
    }


@app.get("/schema")
async def schema():
    return {"schema": get_schema_summary()}


@app.get("/sample-questions")
async def sample_questions():
    return {
        "questions": [
            "Compare total revenue by product in 2024 vs 2023",
            "Show monthly sales trend for last year",
            "Which region has the highest profit margin?",
            "What is the salary distribution across departments?",
            "Show headcount by department",
            "Top 5 products by revenue in 2024",
            "How has hiring changed year over year?",
            "Compare profit by region for 2024",
        ]
    }


@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    excel_dir = Path("./data/excel")
    excel_dir.mkdir(parents=True, exist_ok=True)

    safe_name = Path(file.filename).stem.lower().replace(" ", "_").replace("-", "_")
    dest = excel_dir / file.filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    result = load_excel_table(str(dest), safe_name)
    if result["error"]:
        return {"error": result["error"]}

    add_table_to_kg(safe_name, result["columns"])

    return {
        "table": safe_name,
        "columns": result["columns"],
        "row_count": result["row_count"],
        "message": f"Table '{safe_name}' loaded — {result['row_count']} rows. You can now query it.",
    }
