import json
from urllib.parse import urlencode
from django.utils import timezone
from django.urls import reverse
from .models import UsuarioAutorizacion, Autorizacion

def generar_url_qr(autorizacion, request):
    """Genera la URL para el código QR optimizada"""
    base_url = request.build_absolute_uri(reverse('formulario:verificar_qr'))
    
    # Datos comprimidos
    datos_comprimidos = {
        'p': autorizacion.placa,  # placa
        'n': autorizacion.usuario.nombres[:15],  # nombre (limitado)
        'a': autorizacion.numero_autorizacion[:20],  # autorización (limitado)
        'c': autorizacion.vigencia.isoformat(),  # caducidad
        'ta': autorizacion.tipo_autorizacion.codigo[:3],  # tipo autorización (código corto)
        'ci': autorizacion.usuario.cedula,  # cédula
        'r': autorizacion.usuario.ruc or '',  # ruc
    }
    
    # Filtrar campos vacíos y crear URL
    datos_filtrados = {k: v for k, v in datos_comprimidos.items() if v}
    url_qr = f"{base_url}?{urlencode(datos_filtrados)}"
    
    return url_qr

def validar_autorizacion_caducada(vigencia):
    """Verifica si una autorización está caducada"""
    hoy = timezone.now().date()
    # La autorización caduca al día siguiente de la fecha de vigencia
    fecha_caducidad = vigencia + timezone.timedelta(days=1)
    return hoy >= fecha_caducidad

def crear_autorizacion_desde_form(form_data, usuario_creador):
    """Crea una nueva autorización a partir de los datos del formulario"""
    try:
        # Preparar datos del usuario
        cedula = form_data.get('cedula', '').strip()
        ruc = form_data.get('ruc', '').strip()
        
        # Convertir cadenas vacías a None para campos únicos
        ruc = ruc if ruc else None
        correo = form_data.get('correo', '').strip() or None
        telefono = form_data.get('telefono', '').strip() or None
        
        # Buscar usuario existente por cédula
        usuario = None
        if cedula:
            usuario = UsuarioAutorizacion.objects.filter(cedula=cedula).first()
        
        # Si no se encontró por cédula y hay RUC, buscar por RUC
        if not usuario and ruc:
            usuario = UsuarioAutorizacion.objects.filter(ruc=ruc).first()
        
        # Si se encontró el usuario, actualizarlo
        if usuario:
            # Actualizar campos si vienen en el formulario
            usuario.nombres = form_data['nombres']
            if ruc:
                usuario.ruc = ruc
            if correo:
                usuario.correo = correo
            if telefono:
                usuario.telefono = telefono
            usuario.save()
            usuario_creado = False
        else:
            # Crear nuevo usuario
            usuario = UsuarioAutorizacion.objects.create(
                nombres=form_data['nombres'],
                cedula=cedula if cedula else None,
                ruc=ruc,
                correo=correo,
                telefono=telefono,
                creado_por=usuario_creador
            )
            usuario_creado = True
        
        # Crear autorización
        autorizacion = Autorizacion.objects.create(
            usuario=usuario,
            tipo_autorizacion=form_data['tipo_autorizacion'],
            placa=form_data['placa'],
            numero_autorizacion=form_data['numero_autorizacion'],
            vigencia=form_data['vigencia'],
            creado_por=usuario_creador
        )
        
        return autorizacion, usuario_creado
        
    except Exception as e:
        raise Exception(f"Error al crear autorización: {str(e)}")