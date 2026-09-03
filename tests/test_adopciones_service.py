import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.modules.adopciones.schemas import PostulacionCreate, RespuestaCreate
from app.modules.adopciones import service


class FakeQuery:
    def __init__(self, db, table):
        self.db = db
        self.table_name = table
        self.filters = []
        self.single_result = False
        self.inserted = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters.append((key, value))
        return self

    def order(self, *_args, **_kwargs):
        return self

    def single(self):
        self.single_result = True
        return self

    def insert(self, row):
        self.inserted = dict(row)
        self.db.setdefault("inserted", {}).setdefault(self.table_name, []).append(self.inserted)
        return self

    def execute(self):
        if self.inserted is not None:
            row = dict(self.inserted)
            if self.table_name == "adopcion_postulacion":
                row.setdefault("postulacion_id", 90)
                row.setdefault("fecha_registro", "2026-09-02T00:00:00Z")
            else:
                row.setdefault("respuesta_id", 100)
            return SimpleNamespace(data=[row])
        rows = [
            dict(row)
            for row in self.db.get(self.table_name, [])
            if all(row.get(key) == value for key, value in self.filters)
        ]
        return SimpleNamespace(data=(rows[0] if self.single_result and rows else rows))


class FakeSupabase:
    def __init__(self, data):
        self.data = data

    def table(self, name):
        return FakeQuery(self.data, name)


class AdopcionesServiceTests(unittest.TestCase):
    def test_postulacion_ignora_usuario_del_body_y_separa_contacto(self):
        db = {
            "adopcion": [{"adopcion_id": 7, "usuario_id_fk": 1, "estado": "activa"}],
            "adopcion_pregunta": [
                {"pregunta_id": 10, "texto": "¿Cuál es tu medio de contacto?", "adopcion_id_fk": 7},
                {"pregunta_id": 11, "texto": "¿Tienes patio?", "adopcion_id_fk": 7},
            ],
        }
        solicitud = PostulacionCreate(
            usuario_id_fk=999,
            respuestas=[
                RespuestaCreate(pregunta_id=10, respuesta_texto=" 555-0100 "),
                RespuestaCreate(pregunta_id=11, respuesta_texto="Sí"),
            ],
        )

        with patch.object(service, "supabase", FakeSupabase(db)):
            resultado = service.crear_postulacion(7, solicitud, usuario_id=2)

        insertada = db["inserted"]["adopcion_postulacion"][0]
        self.assertEqual(insertada["usuario_id_fk"], 2)
        self.assertEqual(insertada["contacto"], "555-0100")
        self.assertNotIn("contacto", resultado)
        self.assertEqual(len(db["inserted"]["adopcion_respuesta"]), 1)
        self.assertEqual(db["inserted"]["adopcion_respuesta"][0]["pregunta_id_fk"], 11)

    def test_aprobacion_valida_contacto_y_delega_operacion_atomica(self):
        with patch.object(service, "_verificar_dueno") as verificar, patch.object(
            service, "aprobar_postulacion_atomica", return_value={"estado": "completada"}
        ) as atomica:
            resultado = service.aprobar_postulacion(3, 4, 5, " correo@ejemplo.test ")

        verificar.assert_called_once_with(3, 5)
        atomica.assert_called_once_with(3, 4, 5, "correo@ejemplo.test")
        self.assertEqual(resultado["estado"], "completada")

    def test_mi_postulacion_no_filtra_contacto_a_rechazado(self):
        db = {
            "adopcion_postulacion": [{
                "postulacion_id": 4,
                "adopcion_id_fk": 3,
                "usuario_id_fk": 8,
                "fecha_registro": "2026-09-02T00:00:00Z",
                "estado": "rechazada",
            }],
            "adopcion": [{
                "adopcion_id": 3,
                "estado": "completada",
                "adoptante_id": 9,
                "contacto_responsable": "secreto",
            }],
        }
        with patch.object(service, "supabase", FakeSupabase(db)):
            resultado = service.obtener_mi_postulacion(3, 8)

        self.assertFalse(resultado["postulacion"]["fue_aceptada"])
        self.assertIsNone(resultado["postulacion"]["contacto_responsable"])

    def test_responsable_solo_ve_contacto_de_postulacion_aceptada(self):
        db = {
            "adopcion": [{
                "adopcion_id": 3,
                "usuario_id_fk": 5,
                "estado": "completada",
                "adoptante_id": 8,
            }],
            "adopcion_postulacion": [
                {"postulacion_id": 4, "adopcion_id_fk": 3, "usuario_id_fk": 8,
                 "estado": "aceptada", "contacto": "aceptado@test"},
                {"postulacion_id": 5, "adopcion_id_fk": 3, "usuario_id_fk": 9,
                 "estado": "rechazada", "contacto": "rechazado@test"},
            ],
            "adopcion_respuesta": [],
            "usuario": [
                {"usuario_id_pk": 8, "nombre_usuario": "ocho"},
                {"usuario_id_pk": 9, "nombre_usuario": "nueve"},
            ],
        }
        with patch.object(service, "supabase", FakeSupabase(db)), patch.object(
            service,
            "_conteo_insignias_por_categoria",
            return_value={"rescate": 0, "reporte": 0, "donacion": 0},
        ):
            filas = service.listar_postulaciones(3, 5)

        self.assertEqual(filas[0]["contacto"], "aceptado@test")
        self.assertIsNone(filas[1]["contacto"])


if __name__ == "__main__":
    unittest.main()
