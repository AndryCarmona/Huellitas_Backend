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