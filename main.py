from fastapi import FastAPI
from routers import summarizer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Summary API",
    description="An API to fetch URLs and summarize them using AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include router
app.include_router(summarizer.router, prefix="/api/v1", tags=["Summarizer"])
