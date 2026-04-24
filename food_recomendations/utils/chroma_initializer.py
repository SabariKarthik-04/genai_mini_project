import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction



class ChromaInitializer:
    EMBEDDING_MODEL: str
    def __init__(self,embedding_model:str):
        self.EMBEDDING_MODEL = embedding_model

    def initialize_local_embedding(self,path:str,collection_name:str):
        client = chromadb.PersistentClient(path=path)
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=OllamaEmbeddingFunction(
                model_name=self.EMBEDDING_MODEL,
                url="http://localhost:11434/api/embeddings"
                ),
                metadata={"hnsw:space": "cosine"}
                )
        return client, collection
