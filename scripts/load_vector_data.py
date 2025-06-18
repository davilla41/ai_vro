import os
import sys
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from app.utils.pdf_processor import extract_text_from_pdf

load_dotenv() # Carga las variables de entorno

# Verifica la variable de entorno para Google Cloud credentials
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    print("Error: La variable de entorno GOOGLE_APPLICATION_CREDENTIALS no está definida. No se podrá autenticar con Google Generative AI.\n" \
          "Por favor, define GOOGLE_APPLICATION_CREDENTIALS en tu entorno o en el archivo .env con la ruta al archivo de credenciales JSON de Google Cloud.")
    sys.exit(1)

# Configuración
PDF_DOCUMENTS_PATH = "./data/raw/documents/"
CHROMA_PERSIST_DIRECTORY = "./data/chroma_db"
COLLECTION_NAME = "knowledge_base"

def load_documents_and_create_embeddings():
    """
    Carga documentos PDF, crea embeddings y los almacena en ChromaDB.
    """
    if not os.path.exists(PDF_DOCUMENTS_PATH):
        print(f"Error: La ruta de documentos '{PDF_DOCUMENTS_PATH}' no existe.")
        return

    documents = []
    for filename in os.listdir(PDF_DOCUMENTS_PATH):
        if filename.endswith(".pdf"):
            filepath = os.path.join(PDF_DOCUMENTS_PATH, filename)
            print(f"Procesando: {filepath}")
            try:
                content = extract_text_from_pdf(filepath)
                # Aquí puedes dividir el texto en chunks si es muy largo
                # Para esta PoC, asumimos que el PDF no es excesivamente largo
                documents.append(Document(page_content=content, metadata={"source": filename}))
            except Exception as e:
                print(f"Error al procesar {filename}: {e}")

    if not documents:
        print("No se encontraron documentos PDF para procesar.")
        return

    print(f"Cargando {len(documents)} documentos en ChromaDB...")

    # Inicializa el modelo de embeddings usando SentenceTransformers
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Crea o carga la base de datos vectorial
    # persist_directory hará que los datos se guarden en disco
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME
    )
    print(f"Documentos cargados y embeddings creados en {CHROMA_PERSIST_DIRECTORY}")

if __name__ == "__main__":
    load_documents_and_create_embeddings()

