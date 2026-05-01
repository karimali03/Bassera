from fastapi import APIRouter
from .controller import SuggestionsController
from .schemas import SuggestionsRecord

router = APIRouter(prefix="/api/suggestions", tags=["Suggestions"])
controller = SuggestionsController()

@router.post("/{user_id}/generate", response_model=SuggestionsRecord, status_code=201)
def generate_suggestions(user_id: str):
    return controller.generate(user_id)

@router.get("/{user_id}", response_model=SuggestionsRecord)
def get_latest_suggestions(user_id: str):
    return controller.get_latest(user_id)
