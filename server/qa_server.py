from http.client import HTTPException
import os
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import requests
from logging import getLogger

logger = getLogger(__name__)
# Initialize FastMCP server
mcp = FastMCP("QA MCP Server")

load_dotenv()

rag_service_url = os.getenv("RAG_SERVICE_URL", "https://0.0.0.0:8080")

@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Welcome to the STDIO server."

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


if __name__ == "__main__":
    # Initialize and run the server
    logger.info("Starting the STDIO server...")
    logger.info(f"rag_service_url: {rag_service_url}")
    mcp.run(transport='stdio')