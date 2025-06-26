from app.db.graph_db import GraphDB
from app.db.vector_db import VectorDB
from app.services.llm_service import LLMService
from typing import List, Dict, Tuple
class KnowledgeRetrievalService:
    def __init__(self):
        self.graph_db = GraphDB()
        self.vector_db = VectorDB()
        self.llm_service = LLMService() # uso variado en el flujo
    
    def get_relevant_knowledge_and_answers(self, query: str) -> List[Dict[str, str]]:
        """
        Orquesta la recuperación de conocimiento del grafo y vectorial,
        y genera respuestas en diferentes tonos para preguntas específicas.
        """
        
        # 1. Obtener el esquema del grafo para que el LLM lo entienda
        graph_schema = self.graph_db.get_graph_schema()
        print(f"Esquema del grafo recuperado para LLM:\n{graph_schema}")

        # 2. Pedir al LLM que genere una consulta Cypher
        cypher_query = self.llm_service.generate_cypher_query(query, graph_schema)
        print(f"Consulta Cypher generada por LLM:\n{cypher_query}")

        graph_data = []
        if cypher_query: # Solo ejecutar si el LLM generó una consulta
            graph_data = self.graph_db.execute_cypher_query(cypher_query)
            print(f"Resultados de la consulta Cypher:\n{graph_data}")
        else:
            print("El LLM no generó una consulta Cypher válida.")

        # 3. Realizar búsqueda en la base de datos vectorial
        vector_docs = self.vector_db.search_documents(query)
        # Convertir documentos a un formato más simple para el LLM si es necesario
        vector_data = [{"page_content": doc.page_content, "source": doc.metadata.get("source", "unknown")} for doc in vector_docs]
        print(f"Documentos vectoriales recuperados:\n{vector_data}")

        # 4. Generar respuestas multi-tono con el contexto combinado
        possible_answers = self.llm_service.generate_multi_tone_answers(
            original_query=query,
            graph_data=graph_data,
            vector_data=vector_data
        )

        return possible_answers
