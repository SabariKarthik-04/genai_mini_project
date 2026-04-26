import pandas as pd
from .chroma_initializer import ChromaInitializer
import chromadb,uuid

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
# LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'


class Data_Ingestion_Pipeline:
    client: chromadb.PersistentClient
    colection: chromadb.api.models.Collection.Collection
    def __init__(self):
        chroma_initializer = ChromaInitializer(embedding_model=EMBEDDING_MODEL)
        self.client, self.collection = chroma_initializer.initialize_local_embedding(path=r"D:\Sabari\Learning\projects\GENAI_MINI_PROJECT\genai_mini_project\food_recomendations\chroma_db",collection_name="recipes_data")


    def _batch_data_ingestor(self,collection, data, batch_size=400):
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            ids = [str(uuid.uuid4()) for _ in range(len(batch))]
            documents = batch['ingredients'].tolist()
            metadatas = batch.drop(columns=['id','contributor_id','submitted']).to_dict(orient='records')
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
            print(f"Batch {i//batch_size + 1} ingested successfully.")

    def drop_collection(self, collection_name):
        self.client.delete_collection(name=collection_name)

    def data_ingestion_handler(self):
        recepies_1 = pd.read_csv(r"C:\Users\SabariKarthikS\Desktop\Gen_AI\Mini_Project\food_recomendations\data\recipes_1.csv")[:2000]
        recepies_1.dropna(inplace=True)
        if(self.collection.count() > 0):
            self.drop_collection(collection_name="recipes_data")
        self._batch_data_ingestor(self.collection, recepies_1)

    def similarity_search_handler(self, query: str, top_k: int):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=['metadatas']
        )
        return results