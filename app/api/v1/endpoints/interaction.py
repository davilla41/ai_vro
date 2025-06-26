from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, InteractionResponse, AnswerOption
from app.services.knowledge_retrieval import KnowledgeRetrievalService
from app.services.llm_service import LLMService
from typing import List, Dict

router = APIRouter()

knowledge_service = KnowledgeRetrievalService()
llm_service = LLMService()

@router.post("/ask", response_model=InteractionResponse)
async def ask_question(request: QueryRequest):
    """
    Recibe una pregunta, la clasifica y determina si se busca en la base de conocimiento
    y genera posibles respuestas o se responde con una respuesta simple.
    """
    query_text = request.query.strip()
    
    # Clasificar la pregunta para determinar el flujo
    classification = llm_service.classify_query(query_text)

    if "estado" in classification:
        print(f"Pregunta clasificada como ESTADO: '{query_text}'")
        # sin DBs
        possible_answers_raw = llm_service.generate_multi_tone_answers(
            original_query=query_text, 
            graph_data=None, 
            vector_data=None 
        )
        
        formatted_answers = [
            AnswerOption(text=ans['text'], source=ans.get('source', 'LLM_Simple')) 
            for ans in possible_answers_raw
        ]        
        
        return InteractionResponse(
            original_query=query_text,
            possible_answers=formatted_answers,
            suggested_action="Selecciona la opción que mejor te exprese."
        )
    elif "identidad" in classification:
        print(f"Pregunta clasificada como IDENTIDAD: '{query_text}'")        
        
        possible_answers_raw_with_tones = knowledge_service.get_relevant_knowledge_and_answers(query_text)        
        
        formatted_answers = []
        for ans in possible_answers_raw_with_tones:            
            formatted_answers.append(AnswerOption(
                text=ans['text'],
                source=ans.get('source', 'KnowledgeBase_LLM'),
                tone=ans.get('tone', None) 
            ))

        return InteractionResponse(
            original_query=query_text,
            possible_answers=formatted_answers,
            suggested_action="Selecciona la opción que mejor te exprese."
        )
    else:
        raise HTTPException(status_code=400, detail=f"No se pudo clasificar el tipo de pregunta: {classification}. Se esperaba 'simple' o 'específica'.")