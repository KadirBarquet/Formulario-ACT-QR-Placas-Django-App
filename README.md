# 🚗 Sistema de Gestión de Autorizaciones ACT Milagro

Sistema web desarrollado en Django para la gestión y generación de códigos QR para autorizaciones de la Autoridad de Control de Tránsito de Milagro, Ecuador.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías](#tecnologías)
- [Contribuir](#contribuir)

## ✨ Características

### Gestión de Autorizaciones
- ✅ Creación de autorizaciones con validación de datos
- ✅ Generación automática de códigos QR
- ✅ Descarga de QR en formato PNG
- ✅ Generación de PDF de autorización
- ✅ Verificación de autorizaciones mediante escaneo de QR
- ✅ Gestión de vigencias y alertas de caducidad

### Administración
- 👥 Gestión completa de usuarios autorizados
- 📊 Dashboard con estadísticas en tiempo real
- 📜 Historial completo de todas las acciones
- 🔍 Búsqueda y filtros avanzados
- 📱 Interfaz responsive (móvil, tablet, desktop)

### Seguridad
- 🔐 Sistema de autenticación de administradores
- 🛡️ Control de acceso basado en permisos
- 📝 Auditoría completa de todas las operaciones
- ⚠️ Validaciones exhaustivas de datos

## 🔧 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10+** - [Descargar Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Descargar PostgreSQL](https://www.postgresql.org/download/)
- **pip** (viene con Python)
- **git** - [Descargar Git](https://git-scm.com/downloads)
- **virtualenv** (opcional pero recomendado)

### Verificar instalaciones

```bash
python --version
# Salida esperada: Python 3.10.x o superior

psql --version
# Salida esperada: psql (PostgreSQL) 12.x o superior

git --version
# Salida esperada: git version 2.x.x
```

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/act-milagro-autorizaciones.git
cd act-milagro-autorizaciones
```

### 2. Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comandos.

### 3. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencias principales:**
- Django 5.2.7
- psycopg2-binary 2.9.11 (PostgreSQL adapter)
- Pillow 11.3.0 (manejo de imágenes)
- python-dotenv 1.1.1 (variables de entorno)
- django-widget-tweaks 1.5.0
- django-crispy-forms 2.4
- crispy-bootstrap5 2025.6

### 4. Configurar Base de Datos PostgreSQL

#### Crear Base de Datos

**Opción 1: Usando psql (terminal)**

```bash
# Conectarse a PostgreSQL
psql -U postgres

# Dentro de psql, ejecutar:
CREATE DATABASE act_milagro_db;
CREATE USER act_admin WITH PASSWORD 'tu_password_seguro';
ALTER ROLE act_admin SET client_encoding TO 'utf8';
ALTER ROLE act_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE act_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE act_milagro_db TO act_admin;
\q
```

**Opción 2: Usando pgAdmin (interfaz gráfica)**

1. Abrir pgAdmin
2. Click derecho en "Databases" → Create → Database
3. Nombre: `act_milagro_db`
4. Owner: crear usuario `act_admin` con contraseña segura
5. Save

### 5. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Windows
type nul > .env

# Linux/Mac
touch .env
```

**Contenido del archivo `.env`:**

```env
# ==============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==============================================
DB_ENGINE=django.db.backends.postgresql
DB_DATABASE=nombre_de_la_bd
DB_USERNAME=postgres
DB_PASSWORD=tu_password_seguro_aqui
DB_HOST=localhost
DB_PORT=5432

# ==============================================
# CONFIGURACIÓN DE DJANGO
# ==============================================
SECRET_KEY=django-insecure-CAMBIA_ESTO_POR_UNA_CLAVE_SEGURA_RANDOM
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ==============================================
# CONFIGURACIÓN DE EMAIL (Opcional)
# ==============================================
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_de_aplicacion

# ==============================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS (Producción)
# ==============================================
# STATIC_ROOT=/var/www/act-milagro/static/
# MEDIA_ROOT=/var/www/act-milagro/media/
```

**⚠️ IMPORTANTE:** 
- Nunca subas el archivo `.env` a GitHub
- Ya está incluido en `.gitignore`
- Genera una SECRET_KEY única y segura

**Generar SECRET_KEY segura:**

```python
# Ejecutar en terminal Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Aplicar Migraciones

```bash
# Crear las tablas en la base de datos
python manage.py migrate
```

Deberías ver algo como:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, formulario, security, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

Ingresar:
- **Username:** admin (o el que prefieras)
- **Email:** admin@actmilagro.gob.ec
- **Password:** (contraseña segura)
- **Password (again):** (repetir contraseña)

### 8. Cargar Datos Iniciales (Opcional)

Crear tipos de autorización iniciales:

```bash
python manage.py shell
```

Dentro del shell de Django:

```python
from apps.formulario.models import TipoAutorizacion
from apps.security.models import User

# Obtener el superusuario
admin = User.objects.first()

# Crear tipos de autorización
tipos = [
    {'codigo': 'TRANS', 'nombre': 'Transporte', 'descripcion': 'Autorización de transporte'},
    {'codigo': 'CARGA', 'nombre': 'Carga', 'descripcion': 'Autorización de carga'},
    {'codigo': 'PASAJ', 'nombre': 'Pasajeros', 'descripcion': 'Autorización de pasajeros'},
    {'codigo': 'ESPECIAL', 'nombre': 'Especial', 'descripcion': 'Autorización especial'},
    {'codigo': 'OTRO', 'nombre': 'Otro', 'descripcion': 'Otro tipo de autorización'},
]

for tipo in tipos:
    TipoAutorizacion.objects.get_or_create(
        codigo=tipo['codigo'],
        defaults={
            'nombre': tipo['nombre'],
            'descripcion': tipo['descripcion'],
            'creado_por': admin,
            'activo': True
        }
    )

print("Tipos de autorización creados exitosamente")
exit()
```

### 9. Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 10. Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Abrir navegador en: **http://127.0.0.1:8000**

## 🎯 Uso

### Acceso al Sistema

1. **Login Administrativo:**
   - URL: `http://127.0.0.1:8000/security/login/`
   - Usuario: El superusuario que creaste
   - Solo usuarios con `is_superuser=True` pueden acceder

2. **Dashboard:**
   - URL principal: `http://127.0.0.1:8000/`
   - Vista general con estadísticas

### Flujo de Trabajo Principal

#### 1. Generar Autorización con QR

1. Ir a **"Generar QR"** en el menú
2. Completar formulario:
   - Placa del vehículo
   - Datos del propietario (nombres, cédula/RUC, contacto)
   - Tipo de autorización
   - Número de autorización
   - Fecha de vigencia
3. Click en **"Validar y Generar QR"**
4. Descargar QR (PNG) o PDF

#### 2. Gestionar Autorizaciones

- **Listar:** Ver todas las autorizaciones
- **Buscar:** Por placa, nombres, cédula, número de autorización
- **Filtrar:** Por tipo, estado, fechas
- **Ver QR:** Mostrar y descargar QR de autorización existente
- **Descargar PDF:** Generar PDF de la autorización
- **Editar:** Modificar vigencia o estado
- **Eliminar:** Borrar autorización (con confirmación)

#### 3. Verificar Autorizaciones

1. Escanear código QR con cualquier lector
2. Se abrirá la página de verificación
3. Mostrará:
   - ✅ Estado de la autorización (VÁLIDA/CADUCADA)
   - 📋 Datos del vehículo y propietario
   - 📅 Vigencia y días restantes

## 📁 Estructura del Proyecto

```
Formulario-ACT-QR-Placas-Django-App/
│
├── apps/
│   ├── formulario/              # App principal
│   │   ├── migrations/          # Migraciones de BD
│   │   ├── templates/           # Templates HTML
│   │   │   └── formulario/
│   │   │       ├── generar_qr.html
│   │   │       ├── mostrar_qr.html
│   │   │       ├── descargar_pdf.html
│   │   │       ├── autorizacion_list.html
│   │   │       ├── autorizacion_detail.html
│   │   │       └── ...
│   │   ├── admin.py             # Configuración admin
│   │   ├── models.py            # Modelos de datos
│   │   ├── views.py             # Vistas
│   │   ├── urls.py              # URLs
│   │   ├── form.py              # Formularios
│   │   └── utils.py             # Utilidades
│   │
│   └── security/                # App de seguridad
│       ├── models.py            # User personalizado
│       ├── views/
│       │   └── auth.py          # Login/Logout
│       └── ...
│
├── config/                     # Configuración Django
    ├── asgi.py
│   ├── settings.py              # Settings principal
│   ├── urls.py                  # URLs raíz
│   └── wsgi.py                  # WSGI config
│
├── static/                      # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
│       └── Logo_ACT.png         # Logo oficial
        ├── favicon.ico          # Ícono Principal
│
├── templates/                   # Templates base
│   └── base.html                # Template principal
│
├── media/                       # Archivos subidos (creado automáticamente)
│
├── venv/                        # Entorno virtual (no subir a Git)
├── .env                         # Variables de entorno (no subir a Git)
├── .gitignore                   # Archivos ignorados por Git
├── requirements.txt             # Dependencias Python
├── manage.py                    # CLI de Django
└── README.md                    # Este archivo
```

## 🛠️ Tecnologías

### Backend
- **Django 5.2.7** - Framework web Python
- **PostgreSQL 12+** - Base de datos relacional
- **Python 3.10+** - Lenguaje de programación

### Frontend
- **HTML5, CSS3, JavaScript** - Tecnologías web estándar
- **Bootstrap 5** - Framework CSS (via crispy-forms)
- **QRCode.js** - Generación de códigos QR
- **jsPDF** - Generación de PDFs en el cliente

### Librerías Principales
- **psycopg2** - Adaptador PostgreSQL
- **Pillow** - Procesamiento de imágenes
- **django-widget-tweaks** - Mejoras en formularios
- **django-crispy-forms** - Formularios con Bootstrap

## 🔒 Seguridad

### Producción (Checklist)

Antes de desplegar en producción:

- [ ] Cambiar `DEBUG = False` en settings.py
- [ ] Configurar `ALLOWED_HOSTS` con dominios reales
- [ ] Usar SECRET_KEY única y segura (nunca la misma de desarrollo)
- [ ] Configurar HTTPS/SSL
- [ ] Usar servidor web (Nginx + Gunicorn)
- [ ] Configurar firewall y limitar puertos
- [ ] Hacer backup regular de la base de datos
- [ ] Configurar logging apropiado
- [ ] Revisar permisos de archivos y directorios
- [ ] Usar variables de entorno para credenciales

### Comando para generar SECRET_KEY de producción:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🧪 Testing

Ejecutar tests:

```bash
# Todos los tests
python manage.py test

# Tests de una app específica
python manage.py test apps.formulario

# Tests con verbosidad
python manage.py test --verbosity=2

# Tests con cobertura (instalar coverage primero)
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🐛 Solución de Problemas

### Error: "No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### Error: "FATAL: password authentication failed"

Verificar credenciales en `.env`:
- DB_USERNAME
- DB_PASSWORD
- DB_DATABASE

### Error: "Port 8000 is already in use"

```bash
# Encontrar proceso usando el puerto
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Usar otro puerto
python manage.py runserver 8001
```

### Error: "Static files not found"

```bash
python manage.py collectstatic --clear
python manage.py collectstatic --noinput
```

### QR no se genera

1. Verificar que `qrcode.min.js` esté cargado en base.html
2. Abrir consola del navegador (F12) para ver errores
3. Verificar URL de CDN en base.html:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
```

### PDF no se descarga

Verificar que `jspdf` esté cargado:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

## 📞 Soporte

### Contacto

- **Institución:** EMOVIM-EP - ACT Milagro
- **Email:** genercia@emovim-ep.gob.ec
- **Dirección:** Av. Simón Bolívar y Juan Montalvo, Milagro, Ecuador

### Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Documentation](https://docs.python.org/3/)

## 📝 Licencia

Este proyecto es de uso exclusivo de la Autoridad de Control de Tránsito de Milagro (ACT).

Todos los derechos reservados © 2025 EMOVIM-EP

## 👥 Contribuir

### Para Colaboradores

1. **Fork del proyecto**
2. **Crear rama para tu feature:**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Commit de cambios:**
   ```bash
   git commit -m "Add: nueva funcionalidad increíble"
   ```
4. **Push a la rama:**
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
5. **Abrir Pull Request**

### Convenciones de Código

- Seguir [PEP 8](https://pep8.org/) para código Python
- Usar nombres descriptivos en español para variables de negocio
- Comentar código complejo
- Escribir docstrings para funciones y clases
- Mantener líneas de menos de 100 caracteres

### Commits Semánticos

```
Add: nueva funcionalidad
Fix: corrección de bug
Update: actualización de código existente
Remove: eliminación de código
Docs: cambios en documentación
Style: cambios de formato
Refactor: refactorización de código
Test: agregar o modificar tests
```

## 🗺️ Roadmap

### Versión Actual: 1.0.0

- [x] Sistema de autenticación
- [x] Generación de QR
- [x] Gestión de autorizaciones
- [x] Gestión de usuarios
- [x] Historial de acciones
- [x] Dashboard con estadísticas
- [x] Verificación de QR
- [x] Descarga de PDF

### Próximas Versiones

**v1.1.0**
- [ ] Notificaciones por email
- [ ] Reportes en Excel
- [ ] Búsqueda avanzada con operadores
- [ ] Filtros guardados

**v1.2.0**
- [ ] API REST para integraciones
- [ ] App móvil para verificación
- [ ] Firma digital en PDF
- [ ] Multi-idioma (ES/EN)

**v2.0.0**
- [ ] Renovación automática de autorizaciones
- [ ] Portal para ciudadanos
- [ ] Integración con sistemas externos
- [ ] Analítica avanzada

---

**¿Listo para comenzar? 🚀**

```bash
git clone https://github.com/KadirBarquet/Formulario-ACT-QR-Placas-Django-App.git
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
cd Formulario-ACT-QR-Placas-Django-App
# Configurar .env
python manage.py makemigrations #Recomendado eliminar primero las migraciones y generarlas de nuevo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

¡Disfruta usando el sistema! 🎉