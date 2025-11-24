from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import json

# IDs fixos das perguntas do questionário
QuestionId = Literal[
    "sono",
    "carga",
    "prazo",
    "preocupacao",
    "pausas",
    "sintomas",
    "apoio",
]

# ENTRADA: o que o front manda para POST /assessments
class AssessmentIn(BaseModel):
    answers: Dict[QuestionId, int] = Field(..., description="Mapa de respostas 1..5")


# Dimensão individual do teste
class DimScore(BaseModel):
    id: QuestionId
    score: int  # 0..100
    raw: int    # 1..5


# Recomendação individual
class Recommendation(BaseModel):
    tag: str
    text: str


# SAÍDA: o que o back devolve para o front
class AssessmentOut(BaseModel):
    id: int
    created_at: datetime
    percent: int
    level: Literal["baixo", "moderado", "alto"]
    dims: List[DimScore]
    recommendations: List[Recommendation] | None = None

    @classmethod
    def from_sql(cls, row):
        # row.dims e row.recommendations são strings JSON no banco
        dims_data = json.loads(row.dims) if isinstance(row.dims, str) else row.dims
        recs_data = (
            json.loads(row.recommendations)
            if isinstance(row.recommendations, str) and row.recommendations is not None
            else None
        )

        dims = [DimScore(**d) for d in dims_data]
        recs = [Recommendation(**r) for r in recs_data] if recs_data is not None else None

        return cls(
            id=row.id,
            created_at=row.created_at,
            percent=int(row.percent),
            level=row.level,
            dims=dims,
            recommendations=recs,
        )


# Lógica do cálculo do teste
def compute_assessment(answers: Dict[QuestionId, int]):
    dims: List[DimScore] = []
    for q, v in answers.items():
        v_int = int(v)
        # 1 -> 0%, 5 -> 100%
        score = round((v_int - 1) * 25)
        dims.append(DimScore(id=q, score=score, raw=v_int))

    if not dims:
        return 0, "baixo", []

    percent = round(sum(d.score for d in dims) / len(dims))

    level: Literal["baixo", "moderado", "alto"] = "baixo"
    if 35 <= percent < 65:
        level = "moderado"
    elif percent >= 65:
        level = "alto"

    return percent, level, dims
