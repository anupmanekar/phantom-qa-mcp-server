from genai.llm_handler import LLMHandler
from vectordb.mongo_storage import EmbeddingStorage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from logging import getLogger


logger = getLogger(__name__)

class RAGHandler:
    def __init__(self, llm_handler: LLMHandler, embedding_storage: EmbeddingStorage):
        self.llm_handler = llm_handler
        self.embedding_storage = embedding_storage

    def answer_query(self, query: str) -> str:
        logger.info(f"Answering query: {query}")
        retriever = self.embedding_storage.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        logger.info("Retriever created")
        docs = retriever.invoke(query)
        logger.info(f"Retrieved documents: {docs}")
        logger.info("Template creation in process")
        messages = [
            (
                "system",
                "You are a software QA tester who uses following pieces of context {context} to answer the question",
            ),
            ("human", "{question}"),
        ]
        prompt = ChatPromptTemplate.from_messages(messages=messages)
        logger.info("Prompt created")
        parse_output = StrOutputParser()
        naive_rag_chain = prompt | self.llm_handler.model | parse_output
        logger.info("Chain created")
        result = naive_rag_chain.invoke({"question": query, "context": docs})

        return result
    
    def generate_bdd_for_features(self, features: str) -> str:
        logger.info(f"Generating BDD for Features: {features}")
        retriever = self.embedding_storage.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 1})
        logger.info("Retriever created")
        query = f"Get documents for functionality: {features}"
        docs = retriever.invoke(query)
        logger.info(f"Retrieved documents: {docs}")
        logger.info("Template creation in process")
        messages = [
            (
                "system",
                "You are a software QA tester who uses following pieces of context {context} to answer the question",
            ),
            ("human", "{question}"),
        ]
        prompt = ChatPromptTemplate.from_messages(messages=messages)
        logger.info("Prompt created")
        parse_output = StrOutputParser()
        naive_rag_chain = prompt | self.llm_handler.model | parse_output
        logger.info("Chain created")
        result = naive_rag_chain.invoke({"question": "Generate the BDD for the requirement", "context": docs})

        return result
    
    def generate_bdd_for_ticket(self, ticket_id: int) -> str:
        logger.info(f"Generating BDD for Features: {ticket_id}")
        task_record = self.embedding_storage.get_document({"ticket_id": ticket_id})
        retriever = self.embedding_storage.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 1})
        logger.info("Retriever created")
        query = f"Get documents for functionality: {task_record['description']}"
        docs = retriever.invoke(query)
        logger.info(f"Retrieved documents: {docs}")
        logger.info("Template creation in process")
        messages = [
            (
                "system",
                "You are a software QA tester who uses following pieces of context {context} to answer the question",
            ),
            ("human", "{question}"),
        ]
        prompt = ChatPromptTemplate.from_messages(messages=messages)
        logger.info("Prompt created")
        parse_output = StrOutputParser()
        naive_rag_chain = prompt | self.llm_handler.model | parse_output
        logger.info("Chain created")
        result = naive_rag_chain.invoke({"question": "Generate the BDD for the requirement", "context": docs})

        return result

