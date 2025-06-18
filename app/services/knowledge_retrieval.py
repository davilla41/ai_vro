from app.db.graph_db import GraphDB
from app.db.vector_db import VectorDB
from app.services.llm_service import LLMService

class KnowledgeRetrievalService:
    def __init__(self):
        self.graph_db = GraphDB()
        self.vector_db = VectorDB()
        self.llm_service = LLMService() # Para clasificar la query inicialmente

    def get_relevant_knowledge(self, query: str):
        graph_context = ""
        vector_context = ""

        # Clasificar la pregunta para decidir si necesitamos buscar en bases de datos
        # Esto ya lo hace el endpoint de FastAPI, pero lo mantenemos aquí si se quisiera usar este servicio de forma independiente.
        # En el contexto del endpoint, `classification` ya vendría del endpoint.
        # Para evitar doble clasificación o re-clasificar, podríamos refactorizar slightly
        # Pero por ahora, la dejamos para ilustrar el punto de que este servicio recupera conocimiento.
        
        # --- Heurística para extraer nombres (se podría mejorar con LLM o NER) ---
        # Una forma más robusta sería pedir al LLM que extraiga entidades relevantes de la query.
        # Por ahora, mantendremos la lista de nombres conocidos.
        potential_names = self._extract_names_from_query(query)

        for name in potential_names:
            # Buscar en GraphDB
            relationships = self.graph_db.get_person_relationships(name)
            details = self.graph_db.get_person_details(name)

            if relationships:
                graph_context += f"Relaciones de {name}: "
                for r in relationships:
                    rel_type = r['relationship_type'].replace('_', ' ').replace('DE', 'de').lower()
                    graph_context += f"{name} {rel_type} {r['related_name']} {r['related_apellido']}. "
                graph_context += "\n"
            if details:
                graph_context += f"Detalles de {name}: Nombre: {details.get('nombre', 'N/A')}, Apellido: {details.get('apellido', 'N/A')}, Apodo: {details.get('apodo', 'N/A')}, Fecha de Nacimiento: {details.get('fecha_nacimiento', 'N/A')}, Profesión: {details.get('profesion', 'N/A')}. "
                graph_context += "\n"
        
        # Buscar en VectorDB (conocimiento general y de documentos)
        vector_docs = self.vector_db.search_documents(query)
        if vector_docs:
            vector_context += "Contexto de documentos: "
            for doc in vector_docs:
                vector_context += doc.page_content + "\n"

        return graph_context, vector_context

    def _extract_names_from_query(self, query: str) -> list[str]:
        """
        Heurística simple para extraer nombres de la query.
        Para un sistema robusto, usar un modelo de NER o un LLM.
        """
        # Cargar la lista de nombres conocidos desde una fuente externa o el CSV si es dinámico.
        # Por ahora, mantenemos la lista hardcodeada como ejemplo.
        known_names = [
            "hernando", "deyanira", "david", "karina", "jimmy", "mary", "claudia",
            "lina", "pascasio", "valentina", "santiago", "sara", "isaac", "candelaria", "david felipe"
        ]
        
        extracted_names = []
        for name in known_names:
            # Buscar el nombre completo o solo el primer nombre
            if name.lower() in query.lower():
                extracted_names.append(name)
        
        return list(set(extracted_names)) # Eliminar duplicados