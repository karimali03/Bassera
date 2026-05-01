from fastapi import FastAPI
from api.users.router import router as users_router
from api.bank.router import router as bank_router
from api.suggestions.router import router as suggestions_router

app = FastAPI()

app.include_router(users_router)
app.include_router(bank_router)
app.include_router(suggestions_router)