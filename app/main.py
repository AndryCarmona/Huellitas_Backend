from fastapi import FastAPI
from app.modules.catalogos.router import router as catalogos_router
from app.modules.reportes.router import router as reportes_router
from app.modules.usuarios.router import router as usuarios_router
from app.modules.insignias.router import router as insignias_router
from app.modules.donaciones.router import router as donaciones_router
from app.modules.foro.router import router as foro_router
from app.modules.tarjetas.router import router as tarjetas_router

app = FastAPI(title="Huellitas API")

app.include_router(catalogos_router)
app.include_router(reportes_router)
app.include_router(usuarios_router)
app.include_router(insignias_router)
app.include_router(donaciones_router)
app.include_router(foro_router)
app.include_router(tarjetas_router)
