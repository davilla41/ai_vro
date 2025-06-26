from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings
import os
from typing import List, Dict, Optional

class LLMService:
    def __init__(self):
        if not settings.GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
            raise ValueError(
                "La variable de entorno GOOGLE_APPLICATION_CREDENTIALS no está configurada "
                "o el archivo JSON de credenciales no existe en la ruta especificada."
                "Asegúrate de que 'GOOGLE_APPLICATION_CREDENTIALS=./credentials.json' "
                "esté en tu archivo .env y el archivo credentials.json exista."
            )        
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)

    def classify_query(self, query: str) -> str:
        """Clasifica si la pregunta necesita búsqueda en la base de conocimiento o es simple."""
        prompt = PromptTemplate(
            input_variables=["query"],            
            template="""Tu tarea es clasificar preguntas personales en una de dos categorías semánticas: **Estado** o **Identidad**. 
            Responde únicamente con una de estas dos palabras: `"Estado"` o `"Identidad"`. No incluyas explicaciones, ejemplos, ni puntuación adicional.
            ### Criterios de clasificación:
            - Usa **"Estado"** si la pregunta:
            - Se refiere a cómo está alguien en el presente o pasado inmediato (física, emocional o contextualmente)
            - Indaga sobre acciones recientes o condiciones ambientales
            - Puede responderse con "sí/no" o con respuestas cortas y subjetivas
            - Ejemplos:  
                - "¿Cómo te sientes?" → Estado  
                - "¿Ya comiste?" → Estado  
                - "¿Está lloviendo?" → Estado  
                - "¿Te hiciste daño?" → Estado  
                - "¿Fuiste a la iglesia ayer?" → Estado

            - Usa **"Identidad"** si la pregunta:
            - Busca información estable, biográfica o histórica del interlocutor
            - Requiere respuestas que no se pueden deducir del contexto inmediato
            - Involucra hechos sobre la familia, nombre, estudios, ocupación, relaciones o historia personal
            - Ejemplos:  
                - "¿Cómo te llamas?" → Identidad  
                - "¿Cuál es tu profesión?" → Identidad  
                - "¿En qué universidad estudiaste?" → Identidad  
                - "¿Cuántos hermanos tienes?" → Identidad  
                - "¿Cómo se llaman tus hijos?" → Identidad

            ### Formato de salida:
            Responde exclusivamente con una de estas dos palabras:
            - `Estado`
            - `Identidad`

            No devuelvas ningún otro texto, explicación o símbolo.

            ### Ejemplos adicionales:
            - "¿Estás cansado?" → Estado  
            - "¿Dónde naciste?" → Identidad  
            - "¿Tienes hambre?" → Estado  
            - "¿Cuál es tu nacionalidad?" → Identidad

            ### Instrucción:
            Clasifica la siguiente pregunta:

            Pregunta: "{query}"

            Clasificación:
            """
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        classification = chain.invoke({"query": query})
        return classification['text'].strip().lower()
    
    def generate_cypher_query(self, natural_language_query: str, graph_schema: str) -> str:
        """
        Genera una consulta Cypher basada en una pregunta en lenguaje natural y el esquema del grafo.
        """
        prompt_template = PromptTemplate(
            input_variables=["natural_language_query", "graph_schema"],
            template="""Dado el siguiente esquema de base de datos de grafos de Neo4j:

            {graph_schema}

            Genera una consulta Cypher que responda a la siguiente pregunta en lenguaje natural.
            Siempre que analices la pregunta, considera el esquema del grafo proporcionado.
            La consulta debe ser lo más precisa posible para extraer la información relevante.
            Las propiedades de tipo string en Neo4j (como nombres, apellidos, etc) son sensibles a mayúsculas y minúsculas. Usa la capitalización correcta que es minúsculas.
            Siempre ten en cuenta que Hernando Villanueva Valdes (cuyo nickname es Junior, no confundir con Hernando Villanueva Alvear) es el usuario principal del sistema y es a quien van dirigidas todas las preguntas.
            Si la pregunta no se puede responder directamente con los datos del grafo, genera una consulta que devuelva información general relevante o una cadena vacía.
            Responde ÚNICAMENTE con la consulta Cypher, sin explicaciones ni texto adicional.

            Pregunta en lenguaje natural: "{natural_language_query}"

            Consulta Cypher:"""
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        cypher_query_response = chain.invoke({
            "natural_language_query": natural_language_query,
            "graph_schema": graph_schema
        })
        return cypher_query_response['text'].strip()
    
    def generate_multi_tone_answers(self, original_query: str, graph_data: Optional[List[Dict]] = None, vector_data: Optional[List[Dict]] = None) -> List[Dict[str, str]]:
        """
        Genera opciones de respuesta en diferentes tonos (informal, formal, neutra)
        basadas en la pregunta original y el contexto recuperado.
        """
        graph_context = "\n".join([str(item) for item in graph_data]) if graph_data else "No hay información de relaciones relevante."
        vector_context = "\n".join([doc['page_content'] for doc in vector_data]) if vector_data else "No hay información de hechos relevante."

        # Prompt para generar respuestas en diferentes tonos
        prompt_template = PromptTemplate(
            input_variables=["original_query", "graph_context", "vector_context"],
            template="""Eres un asistente diseñado para ayudar a Hernando Villanueva Valdes (cuyo nickname es Junior)
            a comunicarse verbalmente.
            Hernando es el usuario principal de todo el sistema, es una persona con afasia por lo que no puede hablar ni escribir pero si puede leer.
            Tu objetivo es, dada una pregunta que le hagan a él, proporcionarle opciones de respuesta claras, concisas y relevantes a una pregunta,
            utilizando la información de contexto proporcionada. Las respuestas siempre deben ser en español.
            Si la pregunta es simple y se puede responder con opciones predefinidas, genera esas opciones.
            Las respuestas siempre deben ser redactadas como si fuera él quien contestara, no como si fuera un asistente, de esa manera su interlocutor encontrará la respuesta más natural a la conversación.

            **Información de Relaciones (Grafo):**
            {graph_context}

            **Información de Hechos (Documentos):**
            {vector_context}

            **Pregunta original:** "{original_query}"

            Genera TRES opciones de respuesta, cada una con un tono distinto:
            1.  **Informal:** Conversacional, amigable, sencillo.
            2.  **Formal:** Respetuoso, directo, profesional si aplica.
            3.  **Neutro:** Objetivo, claro, sin emociones.

            Si la información de contexto es insuficiente para una respuesta detallada,
            genera opciones generales o que expresen incertidumbre, manteniendo los tonos.

            Formato de salida:
            Informal: [Respuesta informal]
            Formal: [Respuesta formal]
            Neutro: [Respuesta neutra]
            """
        )

        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response_dict = chain.invoke({
            "original_query": original_query,
            "graph_context": graph_context,
            "vector_context": vector_context
        })

        generated_text = response_dict['text']
        
        # Parsear las respuestas generadas en los diferentes tonos
        possible_answers = []
        lines = generated_text.strip().split("\n")
        
        current_tone = None
        for line in lines:
            line = line.strip()
            if line.lower().startswith("informal:"):
                current_tone = "Informal"
                possible_answers.append({"text": line[len("informal:"):].strip(), "source": "KnowledgeBase_LLM", "tone": current_tone})
            elif line.lower().startswith("formal:"):
                current_tone = "Formal"
                possible_answers.append({"text": line[len("formal:"):].strip(), "source": "KnowledgeBase_LLM", "tone": current_tone})
            elif line.lower().startswith("neutro:"):
                current_tone = "Neutro"
                possible_answers.append({"text": line[len("neutro:"):].strip(), "source": "KnowledgeBase_LLM", "tone": current_tone})
            elif current_tone:
                # Si una línea no es un nuevo encabezado de tono pero estamos dentro de uno, añádela
                # Esto es útil si las respuestas son multilínea.
                if possible_answers and possible_answers[-1]['tone'] == current_tone:
                    possible_answers[-1]['text'] += " " + line.strip() # Concatena a la última respuesta del mismo tono

        return possible_answers
    