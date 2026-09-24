from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from common.config import settings


def build_llm(max_tokens: int = 500) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.model,
        temperature=0,
        max_tokens=max_tokens,
    )


def run_specialist(
    question: str,
    llm: ChatOpenAI,
    tools: list[BaseTool],
    system_prompt: str,
) -> str:
    bound = llm.bind_tools(tools)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
    response = bound.invoke(messages)
    tool_calls = getattr(response, "tool_calls", None)
    if tool_calls:
        tool_out = ToolNode(tools).invoke({"messages": [response]})
        final = llm.invoke(messages + [response] + tool_out["messages"])
        return str(final.content)
    return str(response.content)
