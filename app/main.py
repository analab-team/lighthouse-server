from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.admin import admin_router
from routers.monitoring import monitoring_router
from routers.vault import vault_router

app = FastAPI(title="LightHouse Server")
app.include_router(admin_router)
app.include_router(monitoring_router)
app.include_router(vault_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["api_key"],
)
