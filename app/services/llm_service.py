from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings
import os

class LLMService:
    def __init__(self):
        # Asegurarse de que la variable GOOGLE_APPLICATION_CREDENTIALS esté configurada
        if not settings.GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
            raise ValueError(
                "La variable de entorno GOOGLE_APPLICATION_CREDENTIALS no está configurada "
                "o el archivo JSON de credenciales no existe en la ruta especificada."
                "Asegúrate de que 'GOOGLE_APPLICATION_CREDENTIALS=./credentials.json' "
                "esté en tu archivo .env y el archivo credentials.json exista."
            )
        
        # Para ChatGoogleGenerativeAI, la autenticación se maneja automáticamente
        # si GOOGLE_APPLICATION_CREDENTIALS está configurado.
        # No necesitas pasar google_api_key directamente aquí si estás usando la cuenta de servicio.
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.5)

    def generate_answers_from_context(self, question: str, graph_context: str = "", vector_context: str = "") -> list[str]:
        """
        Genera una respuesta utilizando el LLM, con el contexto de la base de datos de grafos y vectorial.
        """
        prompt_template = PromptTemplate(
            input_variables=["question", "graph_context", "vector_context"],
            template="""Eres un asistente diseñado para ayudar a una persona con afasia a comunicarse verbalmente.
            Tu objetivo es proporcionar opciones de respuesta claras, concisas y relevantes a una pregunta,
            teniendo en cuenta su dificultad para expresarse. La persona puede leer en inglés y español.
            Si la pregunta es simple y se puede responder con opciones predefinidas, genera esas opciones.
            Si requiere información de contexto, utiliza la información proporcionada.

            **Información de Contexto de Relaciones (GraphDB):**
            {graph_context}

            **Información de Hechos (Knowledge Base):**
            {vector_context}

            **Pregunta recibida:** "{question}"

            **Instrucciones para generar opciones de respuesta:**
            1.  Genera de 2 a 4 opciones de respuesta distintas y significativas.
            2.  Las opciones deben ser frases completas y fáciles de leer.
            3.  Si la pregunta es una simple pregunta de estado ("cómo te sientes?"), ofrece opciones generales y directas como "Me siento bien.", "No muy bien.", "Más o menos.".
            4.  Si la pregunta busca información (fechas, nombres, hechos), utiliza el contexto provisto para formular las opciones.
            5.  Si no hay contexto relevante, genera opciones generales o una opción que indique que no se sabe la respuesta.
            6.  Prioriza la claridad y la brevedad.
            7.  Siempre responde en español.

            **Ejemplos de Formato (solo texto plano, no markdown para las opciones finales):**
            Opcion 1: [Respuesta clara 1]
            Opcion 2: [Respuesta clara 2]
            Opcion 3: [Respuesta clara 3]
            """
        )

        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response = chain.run(question=question, graph_context=graph_context, vector_context=vector_context)

        # El resultado de .invoke() en LLMChain es un diccionario, la salida está en 'text' por defecto.
        generated_text = response['text'] 

        # Parsear las opciones del texto plano generado por el LLM
        possible_answers_raw = generated_text.strip().split("\n")
        parsed_answers = []
        for ans in possible_answers_raw:
            if ans.strip().lower().startswith("opcion"):
                text_content = ": ".join(ans.split(": ")[1:]).strip()
                if text_content:
                    parsed_answers.append(text_content)
        return parsed_answers

    def classify_query(self, query: str) -> str:
        """Clasifica si la pregunta necesita búsqueda en la base de conocimiento o es simple."""
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""Clasifica la siguiente pregunta como 'simple' o 'conocimiento'.
            'Simple' significa que la respuesta no requiere buscar información en bases de datos (ej. cómo te sientes, estás bien).
            'Conocimiento' significa que la respuesta probablemente requiere buscar información en bases de datos (ej. cuándo naciste, quién es David, tienes hermanos).
            Responde con solo una palabra: 'simple' o 'conocimiento'.

            Pregunta: "{query}"

            Clasificación:"""
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        classification = chain.invoke({"query": query}) # Usando .invoke()
        
        # El resultado de .invoke() en LLMChain es un diccionario, la salida está en 'text' por defecto.
        return classification['text'].strip().lower()