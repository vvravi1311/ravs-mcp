from langchain_pinecone import PineconeVectorStore
from typing import Tuple, List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from app.constants import GPT_EMBEDDING_MODEL,INDEX_NAME,PINECONE_API_KEY,OPENAI_API_KEY,K
from pprint import pprint


# Initialize embeddings (same as ingestion.py)
embeddings = OpenAIEmbeddings(
    model=GPT_EMBEDDING_MODEL,api_key=OPENAI_API_KEY
)

#Initialize vector store
vectorstore = PineconeVectorStore(
    index_name=INDEX_NAME, embedding=embeddings,pinecone_api_key=PINECONE_API_KEY
)

def retrieve_context(query: str) -> Tuple[str, List[Document]]:
    """Retrieve relevant documentation to help answer answers Insurance agents' queries about Real-Time clause and Benefit lookup."""
    retrieved_docs = vectorstore.as_retriever().invoke(query, k=K)

    # Serialize documents for the model
    serialized = "\n\n".join(
        (f"Source: {doc.metadata.get('source', 'Unknown')}\n\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

if __name__ == "__main__":
    context = retrieve_context("plan N")
    pprint(context)