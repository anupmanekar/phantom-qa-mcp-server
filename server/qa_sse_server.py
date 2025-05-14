# sse_server.py
from browser_use import Agent as BrowserUseAgent
from browser_use.browser.context import BrowserContextConfig
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
rag_service_url = os.getenv("RAG_SERVICE_URL", "https://0.0.0.0:8080")

# Create the MCP server
mcp = FastMCP("QA MCP SSE Server")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=SecretStr(api_key))

@mcp.tool()
async def run_browser_use_tool(bdd_steps:str):
    """ This tool is used to run the browser use tool."""
    logger.info(f"Received BDD steps: {bdd_steps}")
    agent = BrowserUseAgent(
        task=bdd_steps,
        llm=llm,
        max_actions_per_step=1,
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

@mcp.tool()
def generate_bdd_for_features(description: str) -> str:
    """Generate BDD for features."""
    # Placeholder for actual BDD generation logic
    logger.info(f"rag_service_url: {rag_service_url}")
    url = f"{rag_service_url}/generate-bdd-for-features?description={description}"
    payload = {}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        logger.info(f"Response: {response}")
        logger.info(f"Response JSON: {response.json()}")
        response.raise_for_status()
        return {"results": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(f"Error calling API: {e}")

@mcp.tool()
def generate_bdd_for_ticket_id(ticket_id: str) -> str:
    """Generate BDD for ticket."""
    # Placeholder for actual BDD generation logic
    url = f"{rag_service_url}/generate-bdd-for-ticket?ticket_id={ticket_id}"
    payload = {}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {"results": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(f"Error calling API: {e}")


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

if __name__ == "__main__":
    # Get the underlying MCP server
    mcp_server = mcp._mcp_server
    
    # Create Starlette app with SSE support
    starlette_app = create_starlette_app(mcp_server, debug=True)
    
    port = 8080
    logger.info(f"Starting MCP server with SSE transport on port {port}...")
    logger.info(f"SSE endpoint available at: http://localhost:{port}/sse")
    
    # Run the server using uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)