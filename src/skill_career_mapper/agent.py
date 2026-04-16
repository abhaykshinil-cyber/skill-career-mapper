"""
agent.py — Skill Career Mapper agent construction and invocation.

The agent uses Gemini 2.5 Flash and is given two tools:
  - search_jobs    →  live job listings from JSearch / RapidAPI
  - TavilySearch   →  industry demand, salary, and trend research

MCP mode (optional)
-------------------
When MCP_TAVILY_URL is set in the environment, the agent additionally
connects to a Composio-hosted Tavily MCP server and merges those tools
with the local ones.  This requires `langchain-mcp-adapters` to be
installed and the event loop to be running (async path).
"""

import asyncio
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

from .config import Config

SYSTEM_PROMPT = """You are a Skill-to-Career Mapping assistant that helps students
understand skill demand and find matching job opportunities.

You have access to these tools:
- TavilySearch: Search for industry demand, salary insights, and career trends.
- search_jobs: Find actual job listings requiring specific skills.

{tools}

Help the student by researching the skill they ask about and finding relevant
opportunities. Present results in a clean, readable format with clear sections
and proper spacing. Include all job details with apply links.
Do not use markdown formatting — plain text only.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


def build_agent(cfg: Config, tools: list) -> AgentExecutor:
    """
    Construct and return a LangChain AgentExecutor.

    Args:
        cfg:   Populated Config dataclass.
        tools: List of LangChain tool callables.

    Returns:
        Runnable AgentExecutor that accepts {"input": str}.
    """
    llm = init_chat_model(cfg.llm_model, api_key=cfg.gemini_api_key)
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=12,
    )


async def build_agent_with_mcp(cfg: Config, local_tools: list) -> AgentExecutor:
    """
    Build an AgentExecutor that merges local tools with MCP-sourced tools.

    This is the async variant used when MCP_TAVILY_URL is configured.

    Args:
        cfg:         Populated Config dataclass.
        local_tools: Locally defined tools to merge with MCP tools.

    Returns:
        Runnable AgentExecutor.
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError as exc:
        raise ImportError(
            "Install langchain-mcp-adapters to use MCP mode: "
            "pip install langchain-mcp-adapters"
        ) from exc

    client = MultiServerMCPClient(
        {
            "mcp_tavily": {
                "transport": "http",
                "url": cfg.mcp_tavily_url,
            }
        }
    )
    mcp_tools = await client.get_tools()
    all_tools = mcp_tools + local_tools
    return build_agent(cfg, all_tools)


def run_query(executor: AgentExecutor, query: str) -> str:
    """
    Synchronously invoke the agent and return the final answer.

    Args:
        executor: Constructed AgentExecutor.
        query:    User's natural-language question.

    Returns:
        Final answer string.
    """
    response = executor.invoke({"input": query})
    output = response.get("output", "")
    # Handle cases where the LLM returns a list of content blocks
    if isinstance(output, list):
        texts = [block.get("text", "") for block in output if isinstance(block, dict)]
        return "\n".join(texts)
    return output
