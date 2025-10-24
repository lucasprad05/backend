from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from datetime import datetime
import uuid

from app.core.security import get_current_active_user
from app.models.assessment import AssessmentIn, AssessmentOut, compute_assessment
from app.db.memory import DB_ASSESSMENTS

from app.core.gemini import generate_recommendations

# Define o router principal responsável pelas rotas de avaliações (assessments).
# Prefixo comum: /assessments
router = APIRouter(prefix="/assessments", tags=["assessments"])

# Cria uma nova avaliação (teste de estresse) para o usuário autenticado.
# - Recebe as respostas (AssessmentIn)
# - Calcula o resultado via compute_assessment
# - Armazena o registro em memória
# - Retorna o objeto formatado conforme AssessmentOut, incluindo recomendações geradas pelo Gemini.
@router.post("", response_model=AssessmentOut)
def create_assessment(
    payload: AssessmentIn,
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    user_id = current_user["id"]
    percent, level, dims = compute_assessment(payload.answers)

    rec = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow(),
        "percent": percent,
        "level": level,
        "dims": [d.model_dump() for d in dims],
    }

    # Gera recomendações usando o Gemini AI
    rec["recommendations"] = generate_recommendations(percent, level, rec["dims"])
  
    DB_ASSESSMENTS.setdefault(user_id, []).append(rec)
    return AssessmentOut(**rec)

# Retorna todas as avaliações realizadas pelo usuário autenticado.
# Os registros são retornados em ordem decrescente de data (mais recentes primeiro).
@router.get("/me", response_model=list[AssessmentOut])
def list_my_assessments(current_user: Annotated[dict, Depends(get_current_active_user)]):
    user_id = current_user["id"]
    items = DB_ASSESSMENTS.get(user_id, [])
    items_sorted = sorted(items, key=lambda x: x["created_at"], reverse=True)
    return [AssessmentOut(**it) for it in items_sorted]
