# sse_server.py
from browser_use import Agent as BrowserUseAgent
from browser_use import BrowserProfile, BrowserSession
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
import uvicorn
import requests
from dotenv import load_dotenv
from starlette.exceptions import HTTPException
import asyncio
import os
from logging import getLogger

logger = getLogger(__name__)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Create the MCP server
mcp = FastMCP("QA MCP SSE Server")
    
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@mcp.tool()
async def run_browser_use_tool(instructions:str):
    """ This tool is used to run the browser use tool."""
    logger.info(f"Received BDD steps: {instructions}")
    base_config = BrowserProfile(
        wait_between_actions= 1,
        highlight_elements=False,
        wait_for_network_idle_page_load_time =2,
        save_recording_path= "./recordings",
    )
    
    agent = BrowserUseAgent(
            task=instructions,
            llm=llm,
            max_failures=2,
            browser_session=BrowserSession(browser_profile=base_config),
            generate_gif=True,
        )
    history = await agent.run()
    #logger.info(f"Input Token Count: {history.input_token_usage}")
    #logger.info(f"Total Input Tokens: {history.total_input_tokens}")
    logger.info(f"Result from BrowserUseAgent: {history.final_result()}")
    return history.final_result()

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name"""
    logger.info(f"Received greeting request for name: {name}")
    return f"Hello, {name}! Welcome to the SSE server."

@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers and return the result"""
    return f"The sum of {a} and {b} is {a + b}."

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the MCP server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


mcp_server = mcp._mcp_server
starlette_app = create_starlette_app(mcp_server, debug=True)

if __name__ == "__main__":
    port = 8080
    logger.info(f"Starting MCP server with SSE transport on port {port}...")
    logger.info(f"SSE endpoint available at: http://localhost:{port}/sse")
    
    # # Run the server using uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    #asyncio.run(run_browser_use_tool("Open Google and search for 'Python programming'"))