import os
from typing import Any

from dotenv import load_dotenv
from fastmcp import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from mcp.types import TextContent, Tool as MCPTool

# Load environment variables from .env
load_dotenv()

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash", 
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def _to_langchain_tool(client: Client, tool: MCPTool) -> StructuredTool:
    async def call_tool(**arguments: Any) -> Any:
        result = await client.call_tool(tool.name, arguments)
        if result.structured_content is not None:
            return result.structured_content
        if all(isinstance(content, TextContent) for content in result.content):
            return "\n".join(content.text for content in result.content)
        return [
            content.model_dump(mode="json", by_alias=True, exclude_none=True)
            for content in result.content
        ]

    return StructuredTool.from_function(
        coroutine=call_tool,
        name=tool.name,
        description=tool.description or tool.name,
        args_schema=tool.input_schema,
    )


async def ask_gemini(prompt: str) -> str:
    messages = [
        SystemMessage(content="Você é um assistente útil. Quando o usuário perguntar o endereço referente a um CEP, use a ferramenta disponível para consultar os dados do CEP."),
        HumanMessage(content=prompt)
    ]
    async with Client(
        os.getenv("CEP_MCP_URL")
    ) as client:
        tools = [
            _to_langchain_tool(client, tool)
            for tool in await client.list_tools()
        ]
        tools_by_name = {tool.name: tool for tool in tools}
        llm_with_tools = llm.bind_tools(tools)
        response = await llm_with_tools.ainvoke(messages)

        if response.tool_calls:
            messages.append(response)
            for tool_call in response.tool_calls:
                selected_tool = tools_by_name[tool_call["name"]]
                messages.append(await selected_tool.ainvoke(tool_call))
            response = await llm_with_tools.ainvoke(messages)

        return response.text