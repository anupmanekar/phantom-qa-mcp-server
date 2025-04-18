import requests
from langchain_fireworks import FireworksEmbeddings
import os
import base64
from requests.auth import HTTPBasicAuth

class JiraConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(JiraConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self, jira_url, username, api_token):
        if not hasattr(self, 'initialized'):
            self.jira_url = jira_url
            self.auth = HTTPBasicAuth(username, api_token)
            self.initialized = True

    @classmethod
    def get_instance(cls, jira_url=None, username=None, api_token=None):
        if not cls._instance:
            cls._instance = cls(jira_url, username, api_token)
        return cls._instance

    def fetch_tickets(self, jql):
        url = f"{self.jira_url}/rest/api/2/search"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {
            "jql": jql
        }
        response = requests.get(url, headers=headers, params=params, auth=self.auth)
        response.raise_for_status()
        return response.json()["issues"]

    def convert_to_embeddings(self, tickets):
        embeddings = FireworksEmbeddings()
        ticket_embeddings = []
        for ticket in tickets:
            ticket_data = f"{ticket['key']} {ticket['fields']['summary']} {ticket['fields']['description']}"
            embedding = embeddings.encode(ticket_data)
            ticket_embeddings.append({
                "ticket_id": ticket["id"],
                "embedding": embedding
            })
        return ticket_embeddings
