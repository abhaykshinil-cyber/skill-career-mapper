"""
main.py — Entry point for the Skill Career Mapper agent.

Usage
-----
    # Interactive mode (default)
    python main.py

    # Single query via CLI flag
    python main.py --query "What is the demand for Python developers in Bangalore?"

    # Enable MCP mode (requires MCP_TAVILY_URL in .env)
    python main.py --mcp --query "Tell me about ML engineer roles in India"

Environment
-----------
    Copy .env.example → .env and set:
        GEMINI_API_KEY
        RAPIDAPI_KEY
        TAVILY_API_KEY      (required when MCP_TAVILY_URL is not set)
        MCP_TAVILY_URL      (optional — Composio-hosted Tavily MCP endpoint)
"""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "src"))

from skill_career_mapper.config import Config
from skill_career_mapper.tools import make_search_jobs_tool, get_tavily_tool
from skill_career_mapper.agent import build_agent, build_agent_with_mcp, run_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Skill Career Mapper — industry demand + job listings"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Run a single query and exit (omit for interactive mode).",
    )
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Use MCP mode (requires MCP_TAVILY_URL in environment).",
    )
    return parser.parse_args()


async def _async_main(cfg: Config, args: argparse.Namespace) -> None:
    """Async entry point used only when --mcp flag is active."""
    local_tools = [make_search_jobs_tool(cfg)]
    executor = await build_agent_with_mcp(cfg, local_tools)
    query = args.query or f"What is the demand for {cfg.default_skill} in the industry?"
    answer = run_query(executor, query)
    print("\n" + "=" * 60)
    print(answer)


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = Config()
    cfg.validate()

    if args.mcp:
        if not cfg.mcp_tavily_url:
            print("ERROR: --mcp requires MCP_TAVILY_URL to be set in .env")
            sys.exit(1)
        asyncio.run(_async_main(cfg, args))
        return

    # ── Standard (non-MCP) mode ───────────────────────────────────────────────
    search_jobs_tool = make_search_jobs_tool(cfg)
    tavily_tool = get_tavily_tool(cfg)
    executor = build_agent(cfg, tools=[tavily_tool, search_jobs_tool])

    if args.query:
        answer = run_query(executor, args.query)
        print("\n" + "=" * 60)
        print(answer)
    else:
        print("\nSkill Career Mapper — type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if user_input.lower() in {"exit", "quit", "q"}:
                print("Goodbye!")
                break
            if not user_input:
                continue
            answer = run_query(executor, user_input)
            print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()
