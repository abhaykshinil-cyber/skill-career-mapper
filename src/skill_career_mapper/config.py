"""
config.py — Centralised configuration for the Skill Career Mapper agent.
"""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # ── LLM ──────────────────────────────────────────────────────────────────
    gemini_api_key: str = field(
        default_factory=lambda: os.environ.get("GEMINI_API_KEY", "")
    )
    llm_model: str = field(
        default_factory=lambda: os.environ.get("LLM_MODEL", "google_genai:gemini-2.5-flash")
    )

    # ── Tavily (web search) ───────────────────────────────────────────────────
    tavily_api_key: str = field(
        default_factory=lambda: os.environ.get("TAVILY_API_KEY", "")
    )
    tavily_max_results: int = 5
    tavily_search_depth: str = "advanced"

    # ── JSearch via RapidAPI ──────────────────────────────────────────────────
    rapidapi_key: str = field(
        default_factory=lambda: os.environ.get("RAPIDAPI_KEY", "")
    )
    jsearch_country: str = "in"
    jsearch_employment_types: str = "INTERN,FULLTIME"
    jsearch_job_requirements: str = "no_experience,under_3_years_experience"

    # ── MCP (optional) ────────────────────────────────────────────────────────
    # When set, the agent also connects to this Composio-hosted Tavily MCP.
    # Leave blank to use TavilySearch directly instead.
    mcp_tavily_url: str = field(
        default_factory=lambda: os.environ.get("MCP_TAVILY_URL", "")
    )

    # ── Default query ─────────────────────────────────────────────────────────
    default_skill: str = "generative ai"
    default_location: str = "India"

    def validate(self) -> None:
        """Raise ValueError for any required-but-missing keys."""
        missing = []
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.rapidapi_key:
            missing.append("RAPIDAPI_KEY")
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example → .env and fill in the values."
            )
