from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings
import os

class VectorDB:
    def __init__(self):
        
        if not settings.GOOGLE_APPLICATION_CREDENTIALS:
           raise ValueError("GOOGLE_APPLICATION_CREDENTIALS no está configurada en las variables de entorno para Gemini Embeddings.")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


        # Inicializa ChromaDB
        self.db = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
            embedding_function=self.embeddings,
            collection_name=settings.CHROMA_COLLECTION_NAME
        )
        print(f"ChromaDB inicializado con persistencia en: {settings.CHROMA_PERSIST_DIRECTORY}")


    def search_documents(self, query: str, k: int = 3):
        """Busca documentos similares a la query en la base de datos vectorial."""
        if not os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
            print(f"Advertencia: El directorio de persistencia de ChromaDB no existe: {settings.CHROMA_PERSIST_DIRECTORY}. Asegúrate de haber ejecutado 'python -m scripts.load_vector_data'.")
            return []
        return self.db.similarity_search(query, k=k)