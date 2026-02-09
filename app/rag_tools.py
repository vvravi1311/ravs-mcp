from langchain_pinecone import PineconeVectorStore
from typing import Tuple, List
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from app.constants import GPT_EMBEDDING_MODEL,INDEX_NAME,PINECONE_API_KEY,OPENAI_API_KEY,K
from pprint import pprint
from functools import lru_cache

_embeddings = None
_vectorstore = None

def get_vectorstore():
    global _embeddings, _vectorstore
    if _vectorstore is None:
        _embeddings = OpenAIEmbeddings(model=GPT_EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
        _vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=_embeddings, pinecone_api_key=PINECONE_API_KEY)
    return _vectorstore

@lru_cache(maxsize=100)
def retrieve_context(query: str) -> Tuple[str, List[Document]]:
    """Retrieve relevant documentation to help answer answers Insurance agents' queries about Real-Time clause and Benefit lookup."""
    print("***********************************************************   in retrieve_context function   **********")
    vectorstore = get_vectorstore()
    retrieved_docs = vectorstore.as_retriever(search_kwargs={"k": K}).invoke(query)
    print("***********************************************************   in retreived docs successfully   **********")
    # Serialize documents for the model
    serialized = "\n\n".join(
        (f"Source: {doc.metadata.get('source', 'Unknown')}\n\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, tuple(retrieved_docs)

if __name__ == "__main__":
    context = retrieve_context("plan N")
    pprint(context)