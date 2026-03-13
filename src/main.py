# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import rooms_router, ws_router
import uvicorn

from db import init_engine, close_engine

app = FastAPI(title="Кино вместе API", version="1.0.0")

# Настройка CORS
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
app.include_router(rooms_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"message": "Кино вместе API", "status": "running"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    await init_engine()
    print("\n" + "=" * 60)
    print("🚀 Сервер запущен!")
    print("=" * 60)
    print("\n📋 Доступные эндпоинты:")
    print("-" * 40)

    http_routes = []
    ws_routes = []

    for route in app.routes:
        if hasattr(route, 'methods'):
            methods = ",".join(route.methods)
            http_routes.append(f"  🔷 {route.path:35} [{methods}]")
        else:
            ws_routes.append(f"  🔶 {route.path} [WEBSOCKET]")

    # Сортируем и выводим HTTP маршруты
    for route in sorted(http_routes):
        print(route)

    # Выводим WebSocket маршруты
    if ws_routes:
        print("\n  WebSocket маршруты:")
        for route in ws_routes:
            print(route)

    print("-" * 40)
    print(f"\n🌐 HTTP:  http://localhost:8000")
    print(f"🔌 WebSocket: ws://localhost:8000")
    print(f"📚 Документация: http://localhost:8000/docs")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    await close_engine()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )