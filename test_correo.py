import asyncio
from app.core.email_service import enviar_correo_verificacion

async def main():
    await enviar_correo_verificacion(
        destinatario="tu_correo_real@gmail.com",  # pon aquí un correo tuyo real
        codigo="123456",
        nombre_usuario="Andry",
    )
    print("Correo enviado, revisa tu bandeja")

asyncio.run(main())