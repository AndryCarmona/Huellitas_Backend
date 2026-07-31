import math
from datetime import datetime, timezone
import faiss
import numpy as np

from app.core.database import supabase

DIMENSION = 512
SCORE_MINIMO = 0.85
DISTANCIA_MAXIMA_KM = 0.75
DIAS_MAX_ANTIGUEDAD = 30
FASE_CONCLUIDO = 3


class FaissIndexImagenService:
    def __init__(self):
        self.index = faiss.IndexFlatIP(DIMENSION)
        self.reporte_ids: list[int] = []
        self.metadata: dict[int, dict] = {}

    def _normalizar(self, vector: list[float]) -> np.ndarray:
        arr = np.array([vector], dtype="float32")
        faiss.normalize_L2(arr)
        return arr

    def construir_indice(self):
        self.index = faiss.IndexFlatIP(DIMENSION)
        self.reporte_ids = []
        self.metadata = {}

        response = (
            supabase.table("reporte")
            .select("reporte_id, embedding_imagen, latitud, longitud, fecha_reporte, tipo_animal")
            .not_.is_("embedding_imagen", "null")
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
                continue

            embedding = r.get("embedding_imagen")
            if not embedding:
                continue

            vectores.append(embedding)
            self.reporte_ids.append(rid)
            self.metadata[rid] = {
                "latitud": r["latitud"],
                "longitud": r["longitud"],
                "fecha_reporte": r["fecha_reporte"],
                "tipo_animal": r["tipo_animal"],
            }

        if vectores:
            arr = np.array(vectores, dtype="float32")
            faiss.normalize_L2(arr)
            self.index.add(arr)

        print(f"[FAISS-Imagen] Índice construido con {len(self.reporte_ids)} reportes activos")

    def agregar(
        self,
        reporte_id: int,
        embedding: list[float],
        latitud: float,
        longitud: float,
        fecha_reporte: str,
        tipo_animal: int,
    ):
        arr = self._normalizar(embedding)
        self.index.add(arr)
        self.reporte_ids.append(reporte_id)
        self.metadata[reporte_id] = {
            "latitud": latitud,
            "longitud": longitud,
            "fecha_reporte": fecha_reporte,
            "tipo_animal": tipo_animal,
        }

    def buscar_similares(
        self,
        embedding: list[float],
        latitud: float,
        longitud: float,
        tipo_animal: int,
        top_k: int = 5,
    ) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        arr = self._normalizar(embedding)
        k_busqueda = min(top_k * 4, self.index.ntotal)
        scores, posiciones = self.index.search(arr, k_busqueda)

        ahora = datetime.now(timezone.utc)
        resultados = []

        for score, pos in zip(scores[0], posiciones[0]):
            if pos == -1 or score < SCORE_MINIMO:
                continue

            rid = self.reporte_ids[pos]
            meta = self.metadata.get(rid)
            if not meta:
                continue

            if meta["tipo_animal"] != tipo_animal:
                continue

            fecha_reporte = meta["fecha_reporte"]
            if isinstance(fecha_reporte, str):
                fecha_reporte = datetime.fromisoformat(fecha_reporte.replace("Z", "+00:00"))
            antiguedad_dias = (ahora - fecha_reporte).days
            if antiguedad_dias > DIAS_MAX_ANTIGUEDAD:
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

            if len(resultados) >= top_k:
                break

        resultados.sort(key=lambda r: r["score"], reverse=True)
        return resultados

    @staticmethod
    def _distancia_haversine(lat1, lon1, lat2, lon2) -> float:
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c


faiss_imagen_service = FaissIndexImagenService()