from .service import SuggestionsService


class SuggestionsController:
    def __init__(self):
        self.service = SuggestionsService()

    def generate(self, user_id: str) -> dict:
        return self.service.generate(user_id)

    def get_latest(self, user_id: str) -> dict:
        return self.service.get_latest(user_id)
