from http.client import HTTPException
import os
from pydantic import BaseModel
from typing import List
import uvicorn
from connectors.jira_connector import JiraConnector
from connectors.azure_devops_connector import AzureDevOpsConnector
from vectordb.mongo_storage import EmbeddingStorage
from genai.llm_handler import LLMHandler
from genai.rag_handler import RAGHandler
from dotenv import load_dotenv
from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("QA MCP Server")

load_dotenv()

azure_connector = AzureDevOpsConnector.get_instance(
            azure_devops_url=os.environ.get("AZURE_DEVOPS_URL"),
            pat=os.environ.get("AZURE_DEVOPS_PAT"),
            project=os.environ.get("AZURE_DEVOPS_PROJECT"),
            username=os.environ.get("AZURE_DEVOPS_USERNAME")
        )

jira_connector = JiraConnector.get_instance(
            jira_url=os.getenv("JIRA_URL"),
            username=os.getenv("JIRA_USERNAME"),
            api_token=os.getenv("JIRA_API_TOKEN")
        )

embedding_storage = EmbeddingStorage.get_instance(
            mongo_uri=os.environ.get("MONGO_URI"),
            db_name=os.environ.get("DB_NAME"),
            collection_name=os.environ.get("COLLECTION_NAME")
        )

llm_handler = LLMHandler()
rag_handler = RAGHandler(llm_handler, embedding_storage)


@mcp.tool(name="Generate BDD", description="Generate BDD scenarios for given features")
async def generate_bdd(description: str) -> dict[str, Any]:
    try:
        results = rag_handler.generate_bdd_for_features(features=description)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mcp.tool(name="Ingest Tickets into Azure", description="Ingest tickets from Azure DevOps into VectorDB")
async def ingest_azure():
    try:
        print("Ingesting Azure DevOps")
        project = os.environ.get("AZURE_DEVOPS_PROJECT")
        # query = f"Select [System.Id], [System.Title], [System.Description] From WorkItems Where [System.TeamProject] = '{request.ProjectKey}'"
        query = f"Select [System.Id], [System.Title], [System.Description] From WorkItems Where [System.WorkItemType] = 'Task' and [System.TeamProject] = '{project}'"
        #tickets = azure_connector.fetch_tickets(query)[:request.MaxTickets]
        tickets = azure_connector.fetch_tickets(query)[:100]
        embeddings = azure_connector.convert_to_embeddings(tickets)
        #embedding_storage.store_embeddings(embeddings)
        
        return {"message": "Ingestion successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')