from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from datetime import datetime
import uuid

from app.core.security import get_current_active_user
from app.models.assessment import AssessmentIn, AssessmentOut, compute_assessment
from app.db.memory import DB_ASSESSMENTS

router = APIRouter(prefix="/assessments", tags=["assessments"])

@router.post("", response_model=AssessmentOut)
def create_assessment(
    payload: AssessmentIn,
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Salva um assessment para o usuário autenticado.
    - Não exige escopo 'write' para não bloquear usuários novos (apenas estar logado).
    - created_at vem do servidor.
    """
    user_id = current_user["id"]
    percent, level, dims = compute_assessment(payload.answers)

    rec = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow(),
        "percent": percent,
        "level": level,
        "dims": [d.model_dump() for d in dims],
    }
    DB_ASSESSMENTS.setdefault(user_id, []).append(rec)
    return AssessmentOut(**rec)

@router.get("/me", response_model=list[AssessmentOut])
def list_my_assessments(current_user: Annotated[dict, Depends(get_current_active_user)]):
    user_id = current_user["id"]
    items = DB_ASSESSMENTS.get(user_id, [])
    # mais recente primeiro
    items_sorted = sorted(items, key=lambda x: x["created_at"], reverse=True)
    return [AssessmentOut(**it) for it in items_sorted]
