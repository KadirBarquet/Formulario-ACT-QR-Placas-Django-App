# Sistema de Gestión de Autorizaciones ACT Milagro

## Tabla de Contenidos

- [Descripción del Sistema](#descripción-del-sistema)
- [Requisitos Previos](#requisitos-previos)
- [Proceso de Instalación](#proceso-de-instalación)
- [Configuración del Sistema](#configuración-del-sistema)
- [Gestión de la Base de Datos](#gestión-de-la-base-de-datos)
- [Datos Iniciales](#datos-iniciales)
- [Ejecución del Sistema](#ejecución-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías Implementadas](#tecnologías-implementadas)
- [Solución de Problemas Comunes](#solución-de-problemas-comunes)
- [Consideraciones para Producción](#consideraciones-para-producción)
- [Contacto y Soporte](#contacto-y-soporte)

---

## Descripción del Sistema

Sistema web desarrollado en Django para la gestión y generación de códigos QR destinados a las autorizaciones emitidas por la Autoridad de Control de Tránsito de Milagro, Ecuador.

### Funcionalidades Principales

**Módulo de Autorizaciones**
- Registro y validación de autorizaciones vehiculares
- Generación automática de códigos QR
- Exportación en formato PNG y PDF
- Sistema de verificación mediante escaneo
- Control de vigencias y alertas de caducidad

**Módulo Administrativo**
- Gestión integral de usuarios autorizados
- Panel de control con indicadores estadísticos
- Registro histórico de operaciones
- Sistema de búsqueda y filtros avanzados
- Interfaz adaptativa para múltiples dispositivos

**Seguridad del Sistema**
- Autenticación de administradores
- Control de acceso basado en permisos
- Registro de auditoría completo
- Validaciones exhaustivas de datos

---

## Requisitos Previos

Antes de iniciar la instalación, verifique que su sistema cuenta con los siguientes componentes:

- Python 3.10 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)
- git
- virtualenv (recomendado para ambientes aislados)

### Verificación de Componentes

Ejecute los siguientes comandos para verificar las versiones instaladas:
```bash
python --version
psql --version
git --version
```

---

## Proceso de Instalación

### 1. Obtención del Código Fuente

Clone el repositorio del proyecto en su equipo local:
```bash
git clone https://github.com/KadirBarquet/Formulario-ACT-QR-Placas-Django-App.git
cd Formulario-ACT-QR-Placas-Django-App
```

### 2. Configuración del Entorno Virtual

Es altamente recomendable utilizar un entorno virtual para aislar las dependencias del proyecto.

**En sistemas Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En sistemas Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Una vez activado, el indicador `(venv)` aparecerá al inicio de la línea de comandos.

### 3. Instalación de Dependencias

Actualice pip e instale las dependencias del proyecto:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependencias principales del proyecto:**
- Django 5.2.7 (Framework web)
- psycopg2-binary 2.9.11 (Adaptador PostgreSQL)
- Pillow 11.3.0 (Procesamiento de imágenes)
- python-dotenv 1.1.1 (Variables de entorno)
- django-widget-tweaks 1.5.0
- django-crispy-forms 2.4
- crispy-bootstrap5 2025.6
- openpyxl 3.1.5 (Exportación Excel)

---

## Configuración del Sistema

### 1. Configuración de la Base de Datos PostgreSQL

#### Opción A: Mediante línea de comandos (psql)
```bash
psql -U postgres
```

Una vez dentro de PostgreSQL, ejecute:
```sql
CREATE DATABASE act_milagro_db;
CREATE USER act_admin WITH PASSWORD 'su_contraseña_segura';
ALTER ROLE act_admin SET client_encoding TO 'utf8';
ALTER ROLE act_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE act_admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE act_milagro_db TO act_admin;
\q
```

#### Opción B: Mediante pgAdmin (interfaz gráfica)

1. Abra pgAdmin
2. Clic derecho en "Databases" → Create → Database
3. Nombre: `act_milagro_db`
4. Owner: cree el usuario `act_admin` con una contraseña segura
5. Guarde la configuración

### 2. Configuración de Variables de Entorno

Cree el archivo `.env` en el directorio raíz del proyecto:

**Windows:**
```bash
type nul > .env
```

**Linux/Mac:**
```bash
touch .env
```

**Contenido del archivo `.env`:**
```env
# Configuración de Base de Datos
DB_ENGINE=django.db.backends.postgresql
DB_DATABASE=act_milagro_db
DB_USERNAME=act_admin
DB_PASSWORD=su_contraseña_segura
DB_HOST=localhost
DB_PORT=5432

# Configuración de Django
SECRET_KEY=genere_una_clave_secreta_unica_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de Correo Electrónico (Opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=correo@ejemplo.com
EMAIL_HOST_PASSWORD=contraseña_aplicacion

# Configuración de Archivos Estáticos (Producción)
# STATIC_ROOT=/ruta/absoluta/static/
# MEDIA_ROOT=/ruta/absoluta/media/
```

**Nota importante:** El archivo `.env` contiene información sensible y no debe ser compartido ni subido a repositorios públicos. Este archivo ya está incluido en `.gitignore`.

**Generación de SECRET_KEY:**

Ejecute el siguiente comando en la terminal de Python:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie el resultado y reemplace el valor de `SECRET_KEY` en el archivo `.env`.

---

## Gestión de la Base de Datos

### 1. Aplicación de Migraciones

Las migraciones crean las estructuras de tablas necesarias en la base de datos:
```bash
python manage.py migrate
```

Si necesita regenerar las migraciones (solo en caso de problemas):
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Creación de Usuario Administrador

Ejecute el siguiente comando y proporcione la información solicitada:
```bash
python manage.py createsuperuser
```

Ingrese:
- Username: nombre de usuario para acceder al sistema
- Email: correo electrónico del administrador
- Password: contraseña segura (no se mostrará al escribir)
- Password (again): confirme la contraseña

---

## Datos Iniciales

### Carga de Tipos de Autorización

El sistema requiere la carga inicial de los tipos de autorización. Puede realizarla mediante dos métodos:

#### Método 1: Comando Personalizado
```bash
python manage.py tipo_autorizacion_command
```

Este comando cargará automáticamente los tipos predefinidos:
- Estacionamiento Liviano
- Estacionamiento Pesado
- Carga y Descarga Liviana
- Carga y Descarga Pesada
- Circulación Pesada
- Circulación Liviana
- Circulación Escolar Pesado
- Circulación Escolar Liviano

#### Método 2: Shell de Django
```bash
python manage.py shell
```

Dentro del shell, ejecute:
```python
from apps.formulario.models import TipoAutorizacion
from apps.security.models import User

admin = User.objects.first()

tipos = [
    {'codigo': 'AUT-001', 'nombre': 'Estacionamiento Liviano', 'descripcion': 'Autorización de Estacionamiento Liviano'},
    {'codigo': 'AUT-002', 'nombre': 'Estacionamiento Pesado', 'descripcion': 'Autorización de Estacionamiento Pesado'},
    {'codigo': 'AUT-003', 'nombre': 'Carga y Descarga Liviana', 'descripcion': 'Autorización de Carga y Descarga Liviana'},
    {'codigo': 'AUT-004', 'nombre': 'Carga y Descarga Pesada', 'descripcion': 'Autorización de Carga y Descarga Pesada'},
    {'codigo': 'AUT-005', 'nombre': 'Circulación Pesada', 'descripcion': 'Autorización de Circulación Pesada'},
    {'codigo': 'AUT-006', 'nombre': 'Circulación Liviana', 'descripcion': 'Autorización de Circulación Liviana'},
    {'codigo': 'AUT-007', 'nombre': 'Circulación Escolar Pesado', 'descripcion': 'Autorización de Circulación Escolar Pesado'},
    {'codigo': 'AUT-008', 'nombre': 'Circulación Escolar Liviano', 'descripcion': 'Autorización de Circulación Escolar Liviano'},
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

print("Tipos de autorización cargados exitosamente")
exit()
```

### Recolección de Archivos Estáticos

Recopile todos los archivos estáticos del proyecto:
```bash
python manage.py collectstatic --noinput
```

---

## Ejecución del Sistema

### Servidor de Desarrollo

Para iniciar el servidor de desarrollo local:
```bash
python manage.py runserver
```

El sistema estará disponible en: **http://127.0.0.1:8000**

### Acceso al Sistema

**Panel Administrativo:**
- URL: `http://127.0.0.1:8000/security/login/`
- Credenciales: las configuradas al crear el superusuario
- Nota: Solo usuarios con privilegios de superusuario pueden acceder

**Dashboard Principal:**
- URL: `http://127.0.0.1:8000/`
- Acceso mediante autenticación previa

---

## Estructura del Proyecto
```
Formulario-ACT-QR-Placas-Django-App/
├── apps/
│   ├── formulario/              # Aplicación principal
│   │   ├── migrations/          # Migraciones de base de datos
│   │   ├── templates/           # Plantillas HTML
│   │   ├── views/               # Vistas del sistema
│   │   ├── admin.py             # Configuración administrativa
│   │   ├── models.py            # Modelos de datos
│   │   ├── urls.py              # Rutas URL
│   │   ├── forms.py             # Formularios
│   │   └── utils.py             # Funciones auxiliares
│   └── security/                # Aplicación de seguridad
│       ├── models.py            # Modelo de usuario personalizado
│       └── views/               # Vistas de autenticación
├── config/                      # Configuración de Django
│   ├── settings.py              # Configuración principal
│   ├── urls.py                  # URLs raíz
│   └── wsgi.py                  # Configuración WSGI
├── static/                      # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── img/
├── templates/                   # Plantillas base
├── media/                       # Archivos de usuario
├── venv/                        # Entorno virtual
├── .env                         # Variables de entorno
├── .gitignore                   # Archivos ignorados por Git
├── requirements.txt             # Dependencias del proyecto
├── manage.py                    # Herramienta de gestión Django
└── README.md                    # Documentación
```

---

## Tecnologías Implementadas

### Backend
- Django 5.2.7 - Framework web de Python
- PostgreSQL 12+ - Sistema de gestión de base de datos
- Python 3.10+ - Lenguaje de programación

### Frontend
- HTML5, CSS3, JavaScript - Tecnologías web estándar
- Bootstrap 5 - Framework CSS
- QRCode.js - Generación de códigos QR
- jsPDF - Generación de documentos PDF

### Librerías Principales
- psycopg2 - Adaptador de PostgreSQL para Python
- Pillow - Biblioteca de procesamiento de imágenes
- django-widget-tweaks - Mejoras en renderizado de formularios
- django-crispy-forms - Formularios con estilos Bootstrap
- openpyxl - Manipulación de archivos Excel

---

## Solución de Problemas Comunes

### Error: "No module named 'psycopg2'"

**Solución:**
```bash
pip install psycopg2-binary
```

### Error: "FATAL: password authentication failed"

**Solución:**
Verifique las credenciales en el archivo `.env`:
- DB_USERNAME
- DB_PASSWORD
- DB_DATABASE

Asegúrese de que coincidan con las configuradas en PostgreSQL.

### Error: "Port 8000 is already in use"

**Solución en Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID [número_proceso] /F
```

**Solución en Linux/Mac:**
```bash
lsof -i :8000
kill -9 [número_proceso]
```

**Alternativa:** Utilice un puerto diferente:
```bash
python manage.py runserver 8001
```

### Error: "Static files not found"

**Solución:**
```bash
python manage.py collectstatic --clear
python manage.py collectstatic --noinput
```

### Problemas con la Generación de QR

**Verificaciones:**
1. Confirme que el archivo `qrcode.min.js` se carga correctamente en `base.html`
2. Abra la consola del navegador (F12) para identificar errores JavaScript
3. Verifique la URL del CDN en `base.html`:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
```

### Problemas con la Generación de PDF

**Verificación:**
Confirme que la librería jsPDF se carga correctamente:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

---

## Consideraciones para Producción

### Lista de Verificación Previa al Despliegue

Antes de implementar el sistema en un entorno de producción, complete los siguientes pasos:

- Cambiar `DEBUG = False` en `settings.py`
- Configurar `ALLOWED_HOSTS` con los dominios de producción
- Generar y configurar una `SECRET_KEY` única para producción
- Implementar certificado SSL/TLS (HTTPS)
- Configurar servidor web (Nginx + Gunicorn recomendado)
- Configurar firewall y restricción de puertos
- Establecer rutina de respaldos de base de datos
- Configurar sistema de logging apropiado
- Revisar y ajustar permisos de archivos y directorios
- Utilizar variables de entorno para todas las credenciales
- Configurar servidor de correo electrónico de producción

### Comando para SECRET_KEY de Producción
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Contacto y Soporte

### Información Institucional

**Entidad:** EMOVIM-EP - Autoridad de Control de Tránsito de Milagro

**Dirección:** Av. Simón Bolívar y Juan Montalvo, Milagro, Ecuador

**Correo Electrónico:** genercia@emovim-ep.gob.ec

### Recursos Adicionales

- Documentación de Django: https://docs.djangoproject.com/
- Documentación de PostgreSQL: https://www.postgresql.org/docs/
- Documentación de Python: https://docs.python.org/3/

---

## Licencia y Derechos

Este sistema es de uso exclusivo de la Autoridad de Control de Tránsito de Milagro (ACT).

Todos los derechos reservados © 2025 EMOVIM-EP

---

**Versión del Documento:** 1.0

**Última Actualización:** Noviembre 2025