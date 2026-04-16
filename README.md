# Skill Career Mapper

A LangChain-based agent that helps students and early-career professionals understand the **industry demand** for any technology skill and surfaces **real, matching job listings** from live job boards.

---

## Architecture

```
User Query (skill name)
        │
   ReAct Agent (Gemini 2.5 Flash)
        ├── TavilySearch ──► demand trends, salary ranges, career outlook
        └── search_jobs  ──► JSearch API (RapidAPI) ──► live job listings
                │
    Formatted plain-text report
    (demand overview + job titles, companies, locations, apply links)
```

**Optional MCP mode:** connects to a Composio-hosted Tavily MCP server for richer tool coverage (`--mcp` flag).

---

## Project Structure

```
skill_career_mapper/
├── main.py                           # Entry point — interactive, single-query, or MCP mode
├── requirements.txt
├── .env.example
└── src/skill_career_mapper/
    ├── config.py                     # All settings via environment variables
    ├── tools.py                      # search_jobs tool (JSearch/RapidAPI) + TavilySearch factory
    └── agent.py                      # Agent construction (standard + async MCP variant)
```

---

## Modules

| File | Responsibility |
|---|---|
| `config.py` | Dataclass for all env-var-sourced settings; validates required keys at startup |
| `tools.py` | `search_jobs` tool calls JSearch (RapidAPI) and returns title/company/location/apply_link per job; `get_tavily_tool` builds the web-search tool |
| `agent.py` | Builds `create_react_agent + AgentExecutor`; `build_agent_with_mcp()` async variant merges MCP tools when configured |
| `main.py` | CLI entry point with `--query`, `--mcp` flags and interactive fallback |

---

## Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/abhaykshinil-cyber/skill-career-mapper.git
cd skill-career-mapper

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and fill in your API keys
```

---

## Required API Keys

| Variable | Description | Get it from |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini LLM | https://aistudio.google.com/app/apikey |
| `RAPIDAPI_KEY` | JSearch job listings | https://rapidapi.com → subscribe to JSearch |
| `TAVILY_API_KEY` | Web search (standard mode) | https://tavily.com |
| `MCP_TAVILY_URL` *(optional)* | Composio Tavily MCP endpoint | https://composio.dev |

---

## Usage

```bash
# Interactive mode
python main.py

# Single query
python main.py --query "What is the demand for generative AI engineers in India?"

# MCP mode (requires MCP_TAVILY_URL in .env)
python main.py --mcp --query "Machine learning jobs in Bangalore"
```

### Sample Output

```
GENERATIVE AI — SKILL DEMAND REPORT

Industry Demand
---------------
Generative AI is one of the fastest-growing skill areas in 2025.
Salary range: ₹12–40 LPA for 0–3 years experience in India.
Top hiring sectors: FinTech, EdTech, Enterprise SaaS.

Job Listings
------------
1. AI Engineer — Infosys, Bengaluru
   Apply: https://infosys.com/careers/...

2. ML Engineer (GenAI) — Flipkart, Bengaluru
   Apply: https://flipkart.com/careers/...
```

---

## Tool Details

### `search_jobs`
- **API:** JSearch via RapidAPI (`jsearch.p.rapidapi.com`)
- **Input:** skill name + location string
- **Filters:** country=`in`, employment types=`INTERN,FULLTIME`, experience=`no_experience,under_3_years_experience`
- **Output:** list of `{title, company, location, apply_link}`

### `TavilySearch`
- **Purpose:** research industry demand, salary benchmarks, growth trends
- **Config:** `max_results=5`, `search_depth=advanced`

---

## Limitations

- JSearch free tier has rate limits (~10 requests/month on free plan).
- MCP mode requires a live Composio-hosted endpoint URL.
- Job data reflects real-time listings and may vary by day.
