# NL2Viz

Ask questions about your data in plain English.
Get interactive charts instantly.
Powered by LangGraph + LangSmith + DuckDB + ECharts.

## How it works

1. You ask: "Compare revenue by product 2024 vs 2023"
2. LangGraph pipeline runs 5 nodes:
   - Understand your question
   - Write DuckDB SQL
   - Execute and fetch data
   - Decide best chart type
   - Format for ECharts
3. Interactive chart appears in seconds
4. Every step traced in LangSmith

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate sample data
This creates `data/excel/sales.xlsx`, `data/excel/employees.xlsx`, and `data/schema/knowledge_graph.json`.
The `data/` folder does not exist in the repo — this step creates it.
```bash
python scripts/generate_data.py
```

### 3. Configure environment
```bash
cp .env.example .env
```
Open `.env` and add your `LANGCHAIN_API_KEY` from [smith.langchain.com](https://smith.langchain.com).
LangSmith is optional — the app works without it, tracing just won't be active.

### 4. Start the server
DuckDB loads the Excel files automatically on first startup.
```bash
uvicorn app.main:app --reload --port 8003
```

### 5. Open the app
```
http://localhost:8003
```

## Supported LLM Providers
Ollama (local, free) | Claude | OpenAI | Gemini | Mistral | Groq

Configure in the UI — no config file needed.

## Upload your own data
Drop any Excel file in the UI.
NL2Viz loads it into DuckDB and you can query it immediately.

## Monitor in LangSmith
Every query is traced automatically.
See which node took longest, what SQL was generated,
which chart type was chosen and why.
Open smith.langchain.com to see live traces.

## Stack
- LangGraph — agent orchestration
- LangSmith — monitoring and tracing
- DuckDB — analytics database
- ECharts — interactive visualizations
- FastAPI — backend API
- Vanilla JS — frontend
