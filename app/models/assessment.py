from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

QuestionId = Literal["sono", "carga", "prazo", "preocupacao", "pausas", "sintomas", "apoio"]

class AssessmentIn(BaseModel):
    answers: Dict[QuestionId, int] = Field(..., description="Mapa de respostas 1..5")

class DimScore(BaseModel):
    id: QuestionId
    score: int  # 0..100
    raw: int    # 1..5

class AssessmentOut(BaseModel):
    id: str
    created_at: datetime
    percent: int
    level: Literal["baixo", "moderado", "alto"]
    dims: List[DimScore]

def compute_assessment(answers: Dict[QuestionId, int]):
    dims: List[DimScore] = []
    for q, v in answers.items():
        v_int = int(v)
        score = round((v_int - 1) * 25)  # 1->0%, 5->100%
        dims.append(DimScore(id=q, score=score, raw=v_int))
    if not dims:
        return 0, "baixo", []

    percent = round(sum(d.score for d in dims) / len(dims))
    level = "baixo"
    if 35 <= percent < 65:
        level = "moderado"
    elif percent >= 65:
        level = "alto"
    return percent, level, dims
