from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.movies_router import router
import uvicorn

from db import init_engine, close_engine

app = FastAPI(title="API movies", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "API movies", "status": "running"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    await init_engine()
    print("=== ЗАРЕГИСТРИРОВАННЫЕ МАРШРУТЫ ===")
    for route in app.routes:
        print(f"Путь: {route.path}, Методы: {getattr(route, 'methods', 'N/A')}")


@app.on_event("shutdown")
async def shutdown_event():
    await close_engine()
