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

Open `.env` and fill in the values:

```
# LangSmith (optional but recommended)
# Get your key from smith.langchain.com → Settings → API Keys → Create API Key
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=nl2viz        # name of the project in LangSmith
LANGCHAIN_TRACING_V2=true       # enables tracing — set to false to disable

# LLM provider keys (optional — you can enter these in the UI instead)
# Only needed if you want server-side fallback defaults
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
MISTRAL_API_KEY=
```

> **Note:** Never commit your `.env` file. It is already in `.gitignore`.
> LLM provider keys are safer entered in the browser UI — they are stored in
> `localStorage` only and never sent to the server.
> LangSmith is optional — the app works fully without it, tracing just won't be active.

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
