"""
tools.py — Custom LangChain tools for the Skill Career Mapper.

Tools
-----
search_jobs      — Query the JSearch API (RapidAPI) for live job listings.
get_tavily_tool  — Factory returning a Tavily web-search tool (fallback when
                   MCP is not configured).
"""

import requests
from langchain.tools import tool
from langchain_tavily import TavilySearch

from .config import Config


def make_search_jobs_tool(cfg: Config):
    """
    Create and return the `search_jobs` LangChain tool.

    The tool is a closure over *cfg* so environment-sourced credentials
    are injected at build time rather than call time.

    Args:
        cfg: Populated Config dataclass.

    Returns:
        A LangChain tool callable with signature (skill, location) -> list.
    """

    @tool
    def search_jobs(skill: str, location: str) -> list:
        """
        Search for job listings requiring a specific skill via JSearch (RapidAPI).

        Use this tool to surface actual, current job openings — including
        title, company, city, and direct apply links.

        Args:
            skill:    Technology or skill name (e.g. "generative ai", "Python").
            location: City or region to search in (e.g. "Bangalore", "India").

        Returns:
            List of dicts with keys: title, company, location, apply_link.
        """
        print(f"\n[search_jobs] Searching: '{skill}' in '{location}'")

        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "x-rapidapi-key": cfg.rapidapi_key,
            "x-rapidapi-host": "jsearch.p.rapidapi.com",
        }
        params = {
            "query": f"{skill} in {location}",
            "page": "1",
            "country": cfg.jsearch_country,
            "employment_types": cfg.jsearch_employment_types,
            "job_requirements": cfg.jsearch_job_requirements,
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            return [{"error": f"JSearch API request failed: {exc}"}]

        jobs = response.json().get("data", [])
        print(f"[search_jobs] Found {len(jobs)} jobs.")

        return [
            {
                "title": job.get("job_title"),
                "company": job.get("employer_name"),
                "location": job.get("job_city"),
                "apply_link": job.get("job_apply_link"),
            }
            for job in jobs
        ]

    return search_jobs


def get_tavily_tool(cfg: Config) -> TavilySearch:
    """
    Build a TavilySearch tool for industry-demand / salary research.

    Args:
        cfg: Populated Config dataclass.

    Returns:
        TavilySearch instance.
    """
    return TavilySearch(
        max_results=cfg.tavily_max_results,
        search_depth=cfg.tavily_search_depth,
        tavily_api_key=cfg.tavily_api_key,
    )
