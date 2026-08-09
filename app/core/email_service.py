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

    texto_plano = f"""{saludo}

Tu código de verificación para Huellitas es:

{codigo}

Este código expira en 15 minutos. Si no solicitaste este correo, puedes ignorarlo.

- Equipo Huellitas
"""

    html = f"""\
<!DOCTYPE html>
<html lang="es">
<body style="margin:0; padding:0; background-color:#f2f4f3; font-family:Arial, Helvetica, sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f2f4f3; padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:420px; background-color:#ffffff; border-radius:16px; overflow:hidden;">
          <tr>
            <td style="background-color:#2e7d32; padding:28px 24px; text-align:center;">
              <span style="font-size:28px;">🐾</span>
              <div style="color:#ffffff; font-size:20px; font-weight:bold; margin-top:6px;">Huellitas</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px 28px;">
              <p style="font-size:15px; color:#222222; margin:0 0 4px 0;">{saludo}</p>
              <p style="font-size:15px; color:#222222; margin:0 0 20px 0;">
                Este es tu código de verificación para confirmar tu correo en Huellitas:
              </p>
              <div style="background-color:#eaf5eb; border-radius:12px; padding:18px; text-align:center; margin-bottom:20px;">
                <span style="font-size:32px; font-weight:bold; letter-spacing:8px; color:#2e7d32;">{codigo}</span>
              </div>
              <p style="font-size:13px; color:#666666; margin:0 0 4px 0;">
                Este código expira en <strong>15 minutos</strong>.
              </p>
              <p style="font-size:13px; color:#666666; margin:0;">
                Si tú no solicitaste este código, puedes ignorar este correo.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color:#f7f7f7; padding:16px 28px; text-align:center;">
              <span style="font-size:12px; color:#999999;">Equipo Huellitas · Cuidando juntos a nuestras mascotas</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    payload = {
        "sender": {"name": BREVO_REMITENTE_NOMBRE, "email": BREVO_REMITENTE_CORREO},
        "to": [{"email": destinatario}],
        "subject": "Tu código de verificación - Huellitas",
        "textContent": texto_plano,
        "htmlContent": html,
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    response = requests.post(BREVO_URL, json=payload, headers=headers, timeout=10)

    if response.status_code >= 400:
        raise RuntimeError(f"Error al enviar correo con Brevo: {response.status_code} - {response.text}")