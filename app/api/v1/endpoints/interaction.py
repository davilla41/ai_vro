from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, InteractionResponse, AnswerOption
from app.services.knowledge_retrieval import KnowledgeRetrievalService
from app.services.llm_service import LLMService

router = APIRouter()

knowledge_service = KnowledgeRetrievalService()
llm_service = LLMService()

@router.post("/ask", response_model=InteractionResponse)
async def ask_question(request: QueryRequest):
    """
    Recibe una pregunta, busca en la base de conocimiento y genera posibles respuestas.
    """
    query_text = request.query.strip()
    
    # Clasificar la pregunta para determinar el flujo
    classification = llm_service.classify_query(query_text)

    if "simple" in classification:
        print(f"Pregunta clasificada como SIMPLE: '{query_text}'")
        possible_answers_raw = llm_service.generate_answers_from_context(
            question=query_text,
            graph_context="",
            vector_context=""
        )
        possible_answers = [AnswerOption(text=ans, source="LLM_Simple") for ans in possible_answers_raw]
        return InteractionResponse(
            original_query=query_text,
            possible_answers=possible_answers,
            suggested_action="Selecciona la opción que mejor te exprese."
        )
    elif "conocimiento" in classification:
        print(f"Pregunta clasificada como CONOCIMIENTO: '{query_text}'")
        graph_context, vector_context = knowledge_service.get_relevant_knowledge(query_text) # Ya no devuelve la clasificación
        
        print(f"Contexto del grafo: {graph_context}")
        print(f"Contexto vectorial: {vector_context}")

        if not graph_context and not vector_context:
            possible_answers_raw = llm_service.generate_answers_from_context(
                question=query_text,
                graph_context="No se encontró información relevante en la base de grafos.",
                vector_context="No se encontró información relevante en la base de documentos."
            )
            possible_answers = [AnswerOption(text=ans, source="LLM_NoContext") for ans in possible_answers_raw]
            return InteractionResponse(
                original_query=query_text,
                possible_answers=possible_answers,
                suggested_action="No se encontró información específica, selecciona la opción que más se acerque."
            )
        else:
            possible_answers_raw = llm_service.generate_answers_from_context(
                question=query_text,
                graph_context=graph_context,
                vector_context=vector_context
            )
            possible_answers = [AnswerOption(text=ans, source="KnowledgeBase_LLM") for ans in possible_answers_raw]
            return InteractionResponse(
                original_query=query_text,
                possible_answers=possible_answers,
                suggested_action="Selecciona la opción que mejor te exprese."
            )
    else:
        raise HTTPException(status_code=400, detail="No se pudo clasificar el tipo de pregunta.")