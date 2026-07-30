import math
import faiss
import numpy as np

from app.core.database import supabase

DIMENSION = 384
SCORE_MINIMO = 0.85
DISTANCIA_MAXIMA_KM = 0.75  # ~750 metros
FASE_CONCLUIDO = 3


class FaissIndexService:
    def __init__(self):
        self.index = faiss.IndexFlatIP(DIMENSION)
        self.reporte_ids: list[int] = []  # posición en el índice -> reporte_id
        self.metadata: dict[int, dict] = {}  # reporte_id -> {latitud, longitud, fecha_reporte}

    def _normalizar(self, vector: list[float]) -> np.ndarray:
        arr = np.array([vector], dtype="float32")
        faiss.normalize_L2(arr)
        return arr

    def construir_indice(self):
        """Se llama al arrancar el servidor. Lee todos los reportes ACTIVOS
        (no concluidos) que ya tienen embedding guardado, y arma el índice
        desde cero en memoria."""
        self.index = faiss.IndexFlatIP(DIMENSION)
        self.reporte_ids = []
        self.metadata = {}

        response = (
            supabase.table("reporte")
            .select("reporte_id, embedding_texto, latitud, longitud, fecha_reporte")
            .not_.is_("embedding_texto", "null")
            .execute()
        )
        reportes = response.data

        historial_response = (
            supabase.table("historial_fases_reporte")
            .select("reporte_id, fase_id, fecha_cambio")
            .order("fecha_cambio", desc=True)
            .execute()
        )
        ultima_fase_por_reporte = {}
        for h in historial_response.data:
            rid = h["reporte_id"]
            if rid not in ultima_fase_por_reporte:
                ultima_fase_por_reporte[rid] = h["fase_id"]

        vectores = []
        for r in reportes:
            rid = r["reporte_id"]
            fase_actual = ultima_fase_por_reporte.get(rid, 1)
            if fase_actual == FASE_CONCLUIDO:
                continue  # no comparamos contra reportes ya concluidos

            embedding = r.get("embedding_texto")
            if not embedding:
                continue

            vectores.append(embedding)
            self.reporte_ids.append(rid)
            self.metadata[rid] = {
                "latitud": r["latitud"],
                "longitud": r["longitud"],
                "fecha_reporte": r["fecha_reporte"],
            }

        if vectores:
            arr = np.array(vectores, dtype="float32")
            faiss.normalize_L2(arr)
            self.index.add(arr)

        print(f"[FAISS] Índice construido con {len(self.reporte_ids)} reportes activos")

    def agregar(self, reporte_id: int, embedding: list[float], latitud: float, longitud: float, fecha_reporte: str):
        """Agrega un reporte recién publicado al índice sin reconstruir todo."""
        arr = self._normalizar(embedding)
        self.index.add(arr)
        self.reporte_ids.append(reporte_id)
        self.metadata[reporte_id] = {
            "latitud": latitud,
            "longitud": longitud,
            "fecha_reporte": fecha_reporte,
        }

    def buscar_similares(self, embedding: list[float], latitud: float, longitud: float, top_k: int = 5) -> list[dict]:
        """Busca los reportes más parecidos por texto Y cercanos en ubicación."""
        if self.index.ntotal == 0:
            return []

        arr = self._normalizar(embedding)
        scores, posiciones = self.index.search(arr, min(top_k, self.index.ntotal))

        resultados = []
        for score, pos in zip(scores[0], posiciones[0]):
            if pos == -1 or score < SCORE_MINIMO:
                continue

            rid = self.reporte_ids[pos]
            meta = self.metadata.get(rid)
            if not meta:
                continue

            distancia_km = self._distancia_haversine(
                latitud, longitud, meta["latitud"], meta["longitud"]
            )
            if distancia_km > DISTANCIA_MAXIMA_KM:
                continue

            resultados.append({
                "reporte_id": rid,
                "score": round(float(score), 4),
                "distancia_km": round(distancia_km, 2),
            })

        # Ordena del más parecido al menos parecido
        resultados.sort(key=lambda r: r["score"], reverse=True)
        return resultados

    @staticmethod
    def _distancia_haversine(lat1, lon1, lat2, lon2) -> float:
        """Distancia en kilómetros entre dos coordenadas GPS."""
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c


# Instancia única que vive en memoria mientras el servidor esté corriendo
faiss_service = FaissIndexService()