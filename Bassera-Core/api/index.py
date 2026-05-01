from fastapi import FastAPI
from api.users.router import router as users_router
from api.bank.router import router as bank_router
from api.suggestions.router import router as suggestions_router

app = FastAPI()


@app.get("/")
def root():
	return {
		"message": "Bassera Core API is running",
		"frontend": "http://localhost:3000",
		"api_docs": "/docs",
		"health": "/health",
	}


@app.get("/health")
def health():
	return {"status": "ok"}

app.include_router(users_router)
app.include_router(bank_router)
app.include_router(suggestions_router)