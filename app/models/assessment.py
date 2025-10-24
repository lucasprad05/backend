from typing import Dict, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

# Define os identificadores fixos das perguntas do questionário.
# O uso de Literal garante que só esses valores são aceitos.
QuestionId = Literal["sono", "carga", "prazo", "preocupacao", "pausas", "sintomas", "apoio"]

# Modelo de entrada recebido pela API.
# Contém um dicionário com as respostas do usuário (valores de 1 a 5).
class AssessmentIn(BaseModel):
    answers: Dict[QuestionId, int] = Field(..., description="Mapa de respostas 1..5")

# Representa uma dimensão avaliada individualmente.
# Cada dimensão tem:
# - id: qual pergunta ela representa
# - score: pontuação normalizada (0 a 100)
# - raw: valor original respondido (1 a 5)
class DimScore(BaseModel):
    id: QuestionId
    score: int  # 0..100
    raw: int    # 1..5

# Representa uma recomendação gerada para o usuário.
# Cada recomendação tem uma tag e um texto descritivo.
class Recommendation(BaseModel):
    tag: str
    text: str

# Modelo de saída retornado pela API.
# Inclui dados agregados do teste e suas dimensões calculadas.
class AssessmentOut(BaseModel):
    id: str
    created_at: datetime
    percent: int
    level: Literal["baixo", "moderado", "alto"]
    dims: List[DimScore]
    recommendations: list[Recommendation] | None = None

# Função que processa as respostas e calcula os resultados do teste.
# Converte cada resposta (1..5) em um score percentual (0..100),
# calcula a média geral e classifica o nível de estresse.
def compute_assessment(answers: Dict[QuestionId, int]):
    dims: List[DimScore] = []
    for q, v in answers.items():
        v_int = int(v)
        score = round((v_int - 1) * 25)  # 1 -> 0%, 5 -> 100%
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
