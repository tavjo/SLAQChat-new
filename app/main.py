# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from API import sample_retriever_graph

app = FastAPI(title="NExtSEEK Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sample_retriever_graph.router, prefix="/sampleretriever")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)