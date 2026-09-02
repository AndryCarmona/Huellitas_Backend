# Huellitas Backend

API REST de **Huellitas**, una plataforma orientada al cuidado y bienestar animal. El backend permite administrar usuarios y organizaciones, publicar reportes de animales, gestionar adopciones, realizar donaciones y participar en una comunidad mediante publicaciones, comentarios y grupos.

## Tecnologías

- Python 3.10 o superior
- FastAPI y Uvicorn
- Supabase (base de datos, autenticación y almacenamiento)
- JWT para autenticación
- FAISS para búsquedas por similitud
- Hugging Face para embeddings de texto y asistencia en adopciones
- Roboflow CLIP para embeddings de imágenes
- Brevo para correos de verificación

## Funcionalidades principales

- Registro, inicio de sesión y administración de perfiles.
- Perfiles y estadísticas de organizaciones.
- Reportes de animales con evidencia, ubicación, estado y asignación.
- Publicaciones, comentarios, reacciones y grupos comunitarios.
- Publicación de animales en adopción, postulaciones y ranking de candidatos.
- Donaciones y administración segura de tarjetas.
- Insignias y notificaciones para usuarios.
- Búsqueda semántica mediante índices FAISS de texto e imagen.

## Requisitos previos

- Python 3.10+
- Una instancia de Supabase con el esquema y los buckets requeridos por la aplicación.
- Credenciales de los servicios externos que se deseen utilizar.

## Instalación

1. Clona el repositorio y entra en su directorio:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Huellitas_Backend
   ```

2. Crea y activa un entorno virtual:

   **Windows (PowerShell)**

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   **Linux/macOS**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto. No publiques este archivo ni incluyas credenciales reales en el repositorio.

```env
# Supabase (obligatorias)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_de_supabase
SUPABASE_JWT=tu_secreto_jwt

# Cifrado de tarjetas (obligatoria al iniciar la aplicación)
TARJETAS_KEY=tu_clave_fernet

# Correo de verificación
BREVO_API_KEY=tu_api_key
BREVO_REMITENTE_CORREO=no-reply@tu-dominio.com

# Servicios de IA
HUGGINGFACE_API_TOKEN=tu_token
ROBOFLOW_API_KEY=tu_api_key

# Opcional; su valor predeterminado es true
EXIGIR_CORREO_CONFIRMADO=true
```

`TARJETAS_KEY` debe ser una clave Fernet válida. Puedes generar una para desarrollo con:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Ejecución local

Inicia el servidor de desarrollo desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

- Documentación Swagger UI: `http://127.0.0.1:8000/docs`

Durante el arranque, la aplicación construye los índices FAISS de texto e imagen a partir de los datos disponibles. Esto puede aumentar el tiempo de inicio y requiere una conexión válida con Supabase.

## Módulos de la API

| Módulo         | Ruta base                                   | Descripción                                         |
| -------------- | ------------------------------------------- | --------------------------------------------------- |
| Usuarios       | `/usuarios`                                 | Registro, autenticación, perfil y organización      |
| Catálogos      | `/catalogos`                                | Tipos de animal, reporte y urgencia                 |
| Reportes       | `/reportes`                                 | Creación, evidencia, estados y atención de reportes |
| Adopciones     | `/adopciones`                               | Publicaciones, postulaciones, preguntas y ranking   |
| Donaciones     | `/donaciones`                               | Donaciones, organizaciones, metas y estadísticas    |
| Tarjetas       | `/tarjetas`                                 | Métodos de pago cifrados y tarjeta predeterminada   |
| Insignias      | `/insignias`                                | Insignias obtenidas por los usuarios                |
| Notificaciones | `/notificaciones`                           | Consulta y marcado de notificaciones                |
| Foro           | `/publicaciones`, `/comentarios`, `/grupos` | Comunidad, publicaciones, comentarios y grupos      |

Los endpoints protegidos esperan un token JWT en el encabezado HTTP:

```http
Authorization: Bearer <token>
```

## Estructura del proyecto

```text
Huellitas_Backend/
├── app/
│   ├── core/                  # Base de datos, seguridad, geolocalización y correo
│   ├── modules/
│   │   ├── adopciones/
│   │   ├── catalogos/
│   │   ├── donaciones/
│   │   ├── embeddings/
│   │   ├── foro/
│   │   ├── insignias/
│   │   ├── notificaciones/
│   │   ├── reportes/
│   │   ├── tarjetas/
│   │   └── usuarios/
│   └── main.py               # Creación y configuración de FastAPI
├── scripts/                   # Tareas de mantenimiento y migración de datos
├── .env                      # Variables locales (no versionadas)
├── requirements.txt
└── README.md
```

Cada módulo sigue, en general, una separación por responsabilidades:

- `router.py`: endpoints HTTP y dependencias de FastAPI.
- `schemas.py`: modelos de entrada y salida con Pydantic.
- `service.py`: reglas de negocio.
- `repository.py`: acceso a datos en Supabase.

## Desarrollo

Para agregar una funcionalidad, crea o actualiza el módulo correspondiente y registra su `router` en `app/main.py`. Antes de compartir cambios, verifica que:

- La aplicación inicia sin errores.
- Los secretos permanecen únicamente en `.env`.
- Los endpoints nuevos aparecen en `/docs`.
- Las rutas protegidas validan el usuario autenticado.
