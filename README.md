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

### 1. Generate sample data
```bash
python scripts/generate_data.py
```

### 2. Copy env file
```bash
cp .env.example .env
# Add your LANGCHAIN_API_KEY from smith.langchain.com
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start app
```bash
uvicorn app.main:app --reload --port 8003
```

### 5. Open UI
```bash
open frontend/index.html
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
