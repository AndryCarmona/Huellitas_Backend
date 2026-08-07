import os
import random
import aiosmtplib
from email.message import EmailMessage

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def generar_codigo_verificacion() -> str:
    """Genera un código numérico de 6 dígitos como string, ej. '045213'."""
    return f"{random.randint(0, 999999):06d}"


async def enviar_correo_verificacion(destinatario: str, codigo: str, nombre_usuario: str = ""):
    """Envía el correo con el código de verificación vía Gmail SMTP."""
    mensaje = EmailMessage()
    mensaje["From"] = f"Huellitas <{GMAIL_USER}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Tu código de verificación - Huellitas"

    saludo = f"Hola {nombre_usuario}," if nombre_usuario else "Hola,"

    mensaje.set_content(f"""
{saludo}

Tu código de verificación para Huellitas es:

{codigo}

Este código expira en 15 minutos. Si no solicitaste este correo, puedes ignorarlo.

- Equipo Huellitas
""")

    await aiosmtplib.send(
        mensaje,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=GMAIL_USER,
        password=GMAIL_APP_PASSWORD,
    )