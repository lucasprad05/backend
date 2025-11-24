from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from datetime import datetime
import json

from app.core.security import get_current_active_user
from app.models.assessment import AssessmentIn, AssessmentOut, compute_assessment
from app.db.session import get_session
from app.db.models import AssessmentModel
from app.core.gemini import generate_recommendations

router = APIRouter(prefix="/assessments", tags=["assessments"])


# CRIA AVALIAÇÃO
@router.post("", response_model=AssessmentOut)
def create_assessment(
    payload: AssessmentIn,
    current_user=Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    percent, level, dims = compute_assessment(payload.answers)

    recs = generate_recommendations(
        percent,
        level,
        [d.model_dump() for d in dims],
    )

    row = AssessmentModel(
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        percent=percent,
        level=level,
        dims=json.dumps([d.model_dump() for d in dims]),
        recommendations=json.dumps(recs),
    )

    session.add(row)
    session.commit()
    session.refresh(row)

    return AssessmentOut.from_sql(row)


# LISTA AS MINHAS AVALIAÇÕES
@router.get("/me", response_model=list[AssessmentOut])
def list_my_assessments(
    current_user=Depends(get_current_active_user),
    session: Session = Depends(get_session),
):
    stmt = (
        select(AssessmentModel)
        .where(AssessmentModel.user_id == current_user.id)
        .order_by(AssessmentModel.created_at.desc())
    )
    results = session.exec(stmt).all()

    return [AssessmentOut.from_sql(r) for r in results]
