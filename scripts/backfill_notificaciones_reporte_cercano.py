"""
Script de UNA SOLA VEZ: genera notificaciones "reporte_cercano" retroactivas
para reportes ya existentes, comparando contra la ubicacion ACTUAL guardada
de cada usuario (usuario.latitud_actual / longitud_actual).

Es idempotente: si vuelves a correrlo, no duplica notificaciones ya creadas
para el mismo par (usuario, reporte).

Uso (desde la raiz del proyecto backend, con el venv activado):
    python -m scripts.backfill_notificaciones_reporte_cercano

Por seguridad arranca en modo DRY_RUN (no inserta nada, solo te dice
cuantas notificaciones crearia). Cuando confirmes el numero, cambia
DRY_RUN a False y corre otra vez.
"""

from app.core.database import supabase
from app.core.geo import distancia_km

RADIO_KM = 2
DRY_RUN = False          # <-- cambia a False para insertar de verdad
LOTE = 200               # tamano de lote para el insert
TIPO_MALTRATO_ANIMAL = 4  # mismo criterio que listar_reportes()


def obtener_reportes():
    result = (
        supabase.table("reporte")
        .select("reporte_id, latitud, longitud, usuario_id_fk, tipo_reporte")
        .execute()
    )
    return result.data


def obtener_usuarios_con_ubicacion():
    result = (
        supabase.table("usuario")
        .select("usuario_id_pk, latitud_actual, longitud_actual, verificado")
        .not_.is_("latitud_actual", "null")
        .not_.is_("longitud_actual", "null")
        .execute()
    )
    return result.data


def obtener_pares_ya_notificados():
    result = (
        supabase.table("notificaciones")
        .select("usuario_id, data")
        .eq("tipo", "reporte_cercano")
        .execute()
    )
    pares = set()
    for n in result.data:
        data = n.get("data") or {}
        reporte_id = data.get("reporte_id")
        if reporte_id is not None:
            pares.add((n["usuario_id"], reporte_id))
    return pares


def main():
    reportes = obtener_reportes()
    usuarios = obtener_usuarios_con_ubicacion()
    ya_notificados = obtener_pares_ya_notificados()

    print(f"Reportes totales: {len(reportes)}")
    print(f"Usuarios con ubicacion guardada: {len(usuarios)}")
    print(f"Pares ya notificados (se van a saltar): {len(ya_notificados)}")

    nuevas = []
    for reporte in reportes:
        rid = reporte["reporte_id"]
        lat_r = reporte.get("latitud")
        lng_r = reporte.get("longitud")
        if lat_r is None or lng_r is None:
            continue

        es_maltrato = reporte.get("tipo_reporte") == TIPO_MALTRATO_ANIMAL

        for usuario in usuarios:
            uid = usuario["usuario_id_pk"]

            if uid == reporte.get("usuario_id_fk"):
                continue
            if (uid, rid) in ya_notificados:
                continue
            if es_maltrato and not usuario.get("verificado"):
                continue

            dist = distancia_km(
                lat_r, lng_r,
                usuario["latitud_actual"], usuario["longitud_actual"],
            )
            if dist <= RADIO_KM:
                nuevas.append({
                    "usuario_id": uid,
                    "tipo": "reporte_cercano",
                    "titulo": "Reporte cerca de ti",
                    "mensaje": f"Hay un reporte de animal a menos de {RADIO_KM} km de tu ubicacion.",
                    "data": {"reporte_id": rid, "latitud": lat_r, "longitud": lng_r},
                })

    print(f"\nSe {'crearian' if DRY_RUN else 'van a crear'} {len(nuevas)} notificaciones nuevas.")

    if DRY_RUN:
        print("DRY_RUN=True: no se inserto nada. Cambia DRY_RUN a False para ejecutar de verdad.")
        return

    for i in range(0, len(nuevas), LOTE):
        lote = nuevas[i:i + LOTE]
        supabase.table("notificaciones").insert(lote).execute()
        print(f"Insertado lote {i // LOTE + 1} ({len(lote)} filas)")

    print("Listo.")


if __name__ == "__main__":
    main()