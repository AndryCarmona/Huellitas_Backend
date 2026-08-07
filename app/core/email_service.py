import os
import random
import requests

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_REMITENTE_CORREO = os.getenv("BREVO_REMITENTE_CORREO")
BREVO_REMITENTE_NOMBRE = "Huellitas"

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def generar_codigo_verificacion() -> str:
    """Genera un código numérico de 6 dígitos como string, ej. '045213'."""
    return f"{random.randint(0, 999999):06d}"


async def enviar_correo_verificacion(destinatario: str, codigo: str, nombre_usuario: str = ""):
    """Envía el correo con el código de verificación vía la API HTTPS de Brevo."""
    saludo = f"Hola {nombre_usuario}," if nombre_usuario else "Hola,"

    payload = {
        "sender": {"name": BREVO_REMITENTE_NOMBRE, "email": BREVO_REMITENTE_CORREO},
        "to": [{"email": destinatario}],
        "subject": "Tu código de verificación - Huellitas",
        "textContent": f"""{saludo}

Tu código de verificación para Huellitas es:

{codigo}

Este código expira en 15 minutos. Si no solicitaste este correo, puedes ignorarlo.

- Equipo Huellitas
""",
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    response = requests.post(BREVO_URL, json=payload, headers=headers, timeout=10)

    if response.status_code >= 400:
        raise RuntimeError(f"Error al enviar correo con Brevo: {response.status_code} - {response.text}")