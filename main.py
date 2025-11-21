# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import research, analyze

app = FastAPI(
    title="AI Research Assistant",
    version="1.0.0",
    description="LangChain + LangGraph powered micro-orchestrator for research & analysis"
)

# --------------------------
# CORS (optional but recommended)
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Routers
# --------------------------
app.include_router(research.router, prefix="/chain", tags=["Research"])
app.include_router(analyze.router, prefix="/graph", tags=["Analyze"])


# --------------------------
# Health check (optional)
# --------------------------
@app.get("/")
def root():
    return {"message": "AI Research Assistant is running!"}

def main():
    print("Hello from ai-research-assistant-micro-orchestrator!")


if __name__ == "__main__":
    main()
