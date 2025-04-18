from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_fireworks import FireworksEmbeddings
import os
from logging import getLogger

logger = getLogger(__name__)

class EmbeddingStorage:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EmbeddingStorage, cls).__new__(cls)
        return cls._instance

    def __init__(self, mongo_uri, db_name, collection_name):
        if not hasattr(self, 'initialized'):
            logger.info(f"Connecting to MongoDB at {mongo_uri}")
            self.client = MongoClient(mongo_uri, tlsAllowInvalidCertificates=True)
            self.db = self.client.get_database(db_name)
            self.collection = self.db.get_collection(collection_name)
            self.embeddings = FireworksEmbeddings(model='nomic-ai/nomic-embed-text-v1.5')
            self.vector_store = MongoDBAtlasVectorSearch.from_connection_string(
                connection_string=mongo_uri,
                namespace=db_name + "." + collection_name,
                embedding=self.embeddings,
                index_name="vector_index",
                text_key="ticket_title",
            )
            self.initialized = True

    @classmethod
    def get_instance(cls, mongo_uri=None, db_name=None, collection_name=None):
        if not cls._instance:
            cls._instance = cls(mongo_uri, db_name, collection_name)
        return cls._instance

    def store_embeddings(self, embeddings):
        self.collection.delete_many({})
        self.collection.insert_many(embeddings)

    def search_embeddings(self, query_embedding, threshold=0.8):
        return []
    
    def get_document(self, criteria):
        logger.info(f"Getting document with criteria: {criteria}")
        doc = self.collection.find_one(criteria)
        logger.info(f"Document retrieved: {doc}")
        return doc
