from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class AnswerOption(BaseModel):
    text: str
    source: Optional[str] = None # Origen de la respuesta
    tone: Optional[str] = None # Tono de la respuesta, si aplica

class InteractionResponse(BaseModel):
    original_query: str
    possible_answers: List[AnswerOption]
    suggested_action: Optional[str] = None