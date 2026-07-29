from fastapi import FastAPI
from app.modules.catalogos.router import router as catalogos_router
from app.modules.reportes.router import router as reportes_router
from app.modules.usuarios.router import router as usuarios_router
from app.modules.insignias.router import router as insignias_router
from app.modules.donaciones.router import router as donaciones_router

app = FastAPI(title="Huellitas API")

app.include_router(catalogos_router)
app.include_router(reportes_router)
app.include_router(usuarios_router)
app.include_router(insignias_router)
app.include_router(donaciones_router)

@app.get("/diagnostico-embeddings")
def diagnostico():
    import faiss
    import numpy as np
    import requests
    return {
        "faiss_version": faiss.__version__,
        "numpy_version": np.__version__,
        "requests_version": requests.__version__,
    }