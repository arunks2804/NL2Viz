# NL2Viz — Product Specification

> **One-line pitch:** Ask a question about your data in plain English. Get an interactive chart in seconds — no SQL, no BI tool, no waiting for a data analyst.

> **Status:** This is a working prototype. Data comes from Excel files loaded into DuckDB. Direct connections to Snowflake, Redshift, BigQuery and other warehouses are on the roadmap — the pipeline and the interface are already built for it.

---

## The Problem

Data is only useful when people can see it.

Every business runs on data — sales numbers, headcount, revenue trends, profit margins. But the people who need that data the most (managers, ops leads, finance teams) cannot access it without help. They depend on data analysts who are already overloaded, BI tools that require training, or SQL they don't know how to write.

The result is a chronic bottleneck between the question and the answer:

- A sales manager wants to know which region had the best Q4 — she files a data request and waits three days.
- A finance lead needs revenue vs. profit by product for a board meeting — he exports to Excel and builds a chart manually.
- An ops team wants to track hiring trends by department — they don't know which table to query or what the columns mean.
- Every insight requires an intermediary. Every intermediary is a delay. Every delay is a decision made without data.

**The cost:** slow decisions, overloaded analysts, and entire teams flying blind on data that already exists in their warehouse.

---

## Who This Is For

### Persona 1 — The Business Manager
*"I know what I want to see. I just can't get to it without asking someone."*

**Profile:** Sales lead, ops manager, or finance director. Comfortable with Excel. Has never written SQL. Knows the data exists somewhere — Snowflake, Redshift, a warehouse she has no access to. Currently sends requests to the data team and waits days for a chart she needed yesterday.

**Challenges:**
- Every data question requires a ticket, a meeting, or a Slack message to a data analyst.
- By the time the chart arrives, the decision has already been made — or made badly.
- Cannot explore data freely — each follow-up question is another request.
- No visibility into what data is even available to ask about.

---

### Persona 2 — The Data Analyst
*"I spend 60% of my time answering the same five questions in different formats."*

**Profile:** Owns the data warehouse. Writes SQL daily. Builds dashboards in Looker or Tableau. Constantly fielding ad hoc requests from managers and execs that are each five minutes of work but collectively consume the entire week.

**Challenges:**
- Repetitive ad hoc requests crowd out deep analytical work.
- Every stakeholder wants a slightly different slice of the same data — region filter here, date range there.
- Building and maintaining dashboards for every team is unsustainable.
- No self-serve option means all requests funnel through one person.

---

### Persona 3 — The Product / Operations Lead
*"I want to make data-driven decisions but I don't have time to learn SQL or wait for a dashboard."*

**Profile:** Runs a product team or operations function. Makes fast decisions. Needs numbers to back them up. Has tried BI tools and found them too slow to set up for a question that only needs answering once.

**Challenges:**
- BI tools require schema knowledge, training, and significant setup time.
- One-off questions don't justify building a permanent dashboard.
- Cannot iterate quickly — each new angle on the data requires another request or another chart build.
- Doesn't know what questions are even answerable without asking the data team first.

---

### Persona 4 — The Executive
*"I need three numbers before this meeting starts. Someone get me the data."*

**Profile:** C-suite or VP. Needs specific numbers fast and in a form they can put in a slide. Has no patience for tooling. Delegates data requests but is often blocked when the analyst is unavailable.

**Challenges:**
- No way to self-serve even the simplest question without involving someone else.
- Data requests at short notice rarely arrive in time.
- Charts from analysts are formatted for analysts — not for boardroom slides.
- Follow-up questions ("now show me just the West region") require another round-trip.

---

## The Proposition

### General
NL2Viz is the **plain-English interface to your data**. It uses a LangGraph pipeline — understand, query, execute, visualise — to convert a natural language question into an interactive ECharts chart, with every step traced in LangSmith.

In this prototype, data comes from Excel files you upload — loaded instantly into DuckDB and queryable in plain English. The architecture is designed to evolve: the same pipeline will connect directly to Snowflake, Redshift, BigQuery, and Postgres without changing how the user experience works.

No SQL. No BI tool. No data analyst required for every question.

---

### For the Business Manager
Type the question you would normally send in a Slack message. NL2Viz writes the query, fetches the data, picks the right chart type, and renders it interactively — in the time it takes to refresh a page. Ask follow-ups immediately. No waiting, no tickets, no dependencies.

### For the Data Analyst
Stop being the middleman for every "quick question." Point NL2Viz at the data warehouse and let stakeholders self-serve the 80% of questions that don't need your expertise. Free your time for the analysis that actually requires it.

### For the Product / Operations Lead
Get answers to one-off questions without building a dashboard. NL2Viz is designed for exactly the questions that don't justify a Looker report — fast, disposable, accurate. Ask three follow-up questions in a row. Each one is a new chart in seconds.

### For the Executive
One text box. One button. One chart. No tooling to learn, no one to call. Ask the question before the meeting. Get the number. Move on.

---

## Features

### 1. Natural Language → Interactive Chart (Core)
Type any question about your data in plain English. NL2Viz runs a five-node LangGraph pipeline and returns an interactive ECharts chart:

1. **Understand** — LLM identifies intent, tables, time period, aggregation, group-by, and filters
2. **Write Query** — deterministic query builder reads the Knowledge Graph and constructs precise DuckDB SQL — no hallucinated column names
3. **Execute** — DuckDB runs the query and returns structured results
4. **Decide Visualization** — LLM picks the best chart type for the data and the question
5. **Format** — deterministic ECharts formatter builds the complete chart config

Every step is traced in LangSmith.

---

### 2. Multiple Charts Per Question
Questions that ask for multiple things get multiple charts. Ask *"Show me revenue and profit by product"* — NL2Viz generates two charts side by side, one per metric. The SQL fetches all relevant columns in a single query; the visualisation layer splits them into separate, clearly labelled charts.

---

### 3. Smart Chart Selection
The LLM decides the chart type based on the data and the question:

| Question type | Chart |
|---|---|
| Trend over time | Line chart (smooth) |
| Category comparison | Bar chart |
| Ranking | Horizontal bar |
| Part to whole | Pie / donut (≤8 categories) |
| Two metrics compared | Grouped bar |
| Correlation | Scatter |
| Multi-series over time | Multi-line |

---

### 4. Knowledge Graph — Schema Without SQL
NL2Viz maintains a JSON Knowledge Graph describing every table, column, data type, and possible values. The query builder reads this graph directly — so column names in the SQL are always correct, even for complex questions.

Ships with two pre-built datasets:
- **Sales** — 500 rows, 2 years, 8 products, 4 regions, 10 reps
- **Employees** — 150 records, 6 departments, salary, performance, hire date, status

Upload your own Excel file and NL2Viz extends the Knowledge Graph automatically.

---

### 5. Upload Your Own Data
Drop any `.xlsx` or `.xls` file into the upload panel. NL2Viz loads it into DuckDB instantly and makes it queryable in plain English. No schema setup, no mapping, no configuration.

---

### 6. Full Pipeline Observability via LangSmith
Every query is traced end-to-end in LangSmith:
- Which node ran, how long it took, what it received and returned
- The exact SQL written by the query builder
- The chart type the LLM chose and why
- Any errors at any node — visible immediately without digging through logs

Connect once with an API key. Every subsequent query appears automatically in your LangSmith project.

---

### 7. Multi-LLM, Zero Lock-in
Works with any of six LLM providers — selected in the UI, never in a config file:

| Provider | Best For | Cost |
|---|---|---|
| **Ollama** (local) | Development, privacy-sensitive environments | Free |
| **Claude Sonnet** | Highest quality intent understanding | Paid |
| **OpenAI GPT-4o** | General use, broad accuracy | Paid |
| **Gemini** | Long context, large schemas | Free tier / Paid |
| **Mistral** | Fast, EU-hosted option | Paid |
| **Groq** | Lowest latency responses | Paid |

API keys stored only in browser `localStorage` — never sent to the NL2Viz server.

---

### 8. SQL and Raw Data Inspector
Every result includes a collapsible details panel:
- **SQL Query** — the exact query that ran, syntax highlighted, with a copy button
- **Raw Data** — the first 20 rows of query results in a table, with row count

Analysts can verify what ran. Non-technical users can ignore it.

---

## User Workflows

> **For engineers setting up the app:** see [README.md](README.md) for installation and startup instructions.

---

### Workflow 1 — Getting a quick answer from the built-in data
*Primary persona: Business Manager / Executive*

1. Open NL2Viz at `http://localhost:8003`.
2. In the **LLM Provider** panel, select your provider and enter credentials. For Ollama, type the model name you have running locally.
3. Type your question in the input box. Be specific about what you want to compare and over what time period. Example: *"Which region had the highest profit in 2024?"*
4. Click **Visualize**.
5. Watch the five pipeline steps complete — each shows a checkmark as it finishes.
6. The chart appears. Hover over bars or points for exact values.
7. Below the chart, read the reasoning — one sentence explaining why this chart type was chosen.
8. Click **Query Details** to see the SQL and raw data if you want to verify the numbers.
9. Ask a follow-up immediately — type the next question and click Visualize again.

---

### Workflow 2 — Asking a multi-metric question
*Primary persona: Finance Lead / Product Manager*

1. Type a question that references two metrics. Example: *"Show me both revenue and profit by product."*
2. NL2Viz detects both metrics, writes SQL that fetches both columns in one query, and generates two charts — one for revenue, one for profit — displayed side by side.
3. Compare the two charts visually. A product with high revenue but low profit is immediately visible.
4. Ask a follow-up: *"Now show just 2024."* The filter is applied and the charts update.

---

### Workflow 3 — Uploading your own Excel data
*Primary persona: Data Analyst / Ops Lead*

1. Scroll to the **Upload Your Own Data** panel at the bottom of the page.
2. Drop your `.xlsx` file onto the panel or click to browse.
3. NL2Viz loads the file into DuckDB, detects columns and types, and confirms the table is ready.
4. Ask questions about your uploaded data immediately — NL2Viz knows the column names from the file.
5. Use the SQL inspector to verify the query is referencing the right columns.

---

### Workflow 4 — Monitoring a query pipeline in LangSmith
*Primary persona: Data Analyst / Engineer*

1. Ensure `LANGCHAIN_API_KEY` is set in `.env`.
2. Ask any question in NL2Viz.
3. Open `smith.langchain.com` → project `nl2viz`.
4. The trace appears: five nodes, each with timing, inputs, and outputs.
5. Click the `write_query` node to see the exact SQL generated.
6. Click the `decide_visualization` node to see which chart type the LLM chose and the reasoning.
7. If a query returned no data, the trace shows exactly which node stopped and why.

---

## What's Not in v1

| Feature | Status |
|---|---|
| Direct database connections (Snowflake, Redshift, BigQuery, Postgres) | **Next up** |
| Dashboard mode — save and arrange multiple charts | Roadmap |
| Chart export to PNG / PDF | Roadmap |
| Query history — recall previous questions and results | Roadmap |
| Scheduled reports — run a question on a cron and email the chart | Roadmap |
| Natural language filter refinement ("now show just North region") | Roadmap |
| Multi-table joins via Knowledge Graph relationships | Roadmap |
| Role-based access — restrict which tables each user can query | Roadmap |
| Embedded widget — drop a NL2Viz chart into any web app | Roadmap |
