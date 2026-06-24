# SENA CBA - Sistema de Reservas de Espacios

Aplicación web Django para la gestión de reservas de espacios y recursos del **Centro de Biotecnología Agropecuario (CBA)** del SENA.

## Tecnologías

- **Backend:** Django 6.0, Python 3.14
- **Base de datos:** PostgreSQL (Supabase)
- **Frontend:** Bootstrap 5.3 (modo oscuro), Bootstrap Icons
- **Despliegue:** Vercel (serverless) + Whitenoise (estáticos)

## Modelo de datos

```
CBAUsuario (AbstractUser)
├── username, email, password, telefono
├── rol (admin | regular)
└── relación 1:N con CBAReserva

CBAEspacio
├── nombre, descripcion, tipo (laboratorio/sala_estudio/equipo/aula/taller)
├── capacidad, ubicacion, disponible
└── relación 1:N con CBAReserva y CBAHorario

CBAHorario
├── FK → CBAEspacio
├── dia_semana, hora_inicio, hora_fin, activo

CBAReserva
├── FK → CBAEspacio
├── FK → CBAUsuario
├── fecha_inicio, fecha_fin, estado (pendiente/confirmada/cancelada/completada)
├── proposito
└── Validación de conflictos de horario
```

## Funcionalidades

- Autenticación (registro/login/logout) con roles admin/regular
- CRUD completo de Espacios, Reservas y Horarios
- Validación de conflictos de horario en reservas
- Filtro de reservas por espacio y estado
- Dashboard con conteo de reservas por estado y espacios disponibles
- Cancelación de reservas
- Interfaz responsive con Bootstrap 5 dark mode

## Requisitos

- Python 3.12+
- pip

## Instalación local

```bash
# Clonar repositorio
git clone <repo-url>
cd tarea_proyecto

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

## Conexión a Neon (PostgreSQL)

El proyecto usa `dj-database-url` para conectar a PostgreSQL en Neon.

### Obtener cadena de conexión

1. Regístrate en [neon.tech](https://neon.tech)
2. Crea un proyecto y obtén la cadena de conexión tipo:
   ```
   postgresql://usuario:password@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Colócala en tu `.env` como `DATABASE_URL`

### Migraciones

```bash
# Reemplaza con tu cadena de Neon
DATABASE_URL="postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require" python manage.py migrate
```

## Despliegue en Vercel

1. Conecta el repositorio a Vercel.
2. Configura las variables de entorno en Vercel:
   - `DATABASE_URL`: cadena de conexión de Neon
   - `SECRET_KEY`: clave secreta de Django
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.vercel.app`
3. Vercel ejecuta automáticamente `vercel.json` (build + collectstatic).
4. Antes del deploy, corre las migraciones apuntando a Neon:
   ```bash
   DATABASE_URL="<tu-cadena-neon>" python manage.py migrate
   ```

> Las migraciones no se ejecutan automáticamente en Vercel. Debes correrlas manualmente antes de cada deploy.

## Estructura del proyecto

```
tarea_proyecto/
├── api/index.py          # Handler serverless para Vercel
├── core/                 # App principal
│   ├── models.py         # CBAUsuario, CBAEspacio, CBAHorario, CBAReserva
│   ├── views.py          # CBVs (List, Create, Update, Delete)
│   ├── forms.py          # Formularios con validaciones
│   └── urls.py           # URLs del core
├── templates/            # Templates Bootstrap 5
├── static/               # Archivos estáticos
├── tarea_proyecto/       # Configuración del proyecto
│   ├── settings.py
│   └── wsgi.py
├── vercel.json           # Configuración de Vercel
└── requirements.txt      # Dependencias Python
```

## Licencia

MIT
