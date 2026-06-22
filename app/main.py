from fastapi import FastAPI
from app.modules.catalogos.router import router as catalogos_router
from app.modules.reportes.router import router as reportes_router
from app.modules.usuarios.router import router as usuarios_router

app = FastAPI(title="Huellitas API")

app.include_router(catalogos_router)
app.include_router(reportes_router)
app.include_router(usuarios_router)
