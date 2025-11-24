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
        # CORRECCIÓN: Manejo seguro de None antes de hacer strip()
        # Usamos (form_data.get('campo') or '') para asegurar que sea string antes del strip
        
        cedula_val = form_data.get('cedula')
        cedula = cedula_val.strip() if cedula_val else None
        
        ruc_val = form_data.get('ruc')
        ruc = ruc_val.strip() if ruc_val else None
        
        correo_val = form_data.get('correo')
        correo = correo_val.strip() if correo_val else None
        
        telefono_val = form_data.get('telefono')
        telefono = telefono_val.strip() if telefono_val else None
        
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
            
            # Solo actualizamos si vienen datos nuevos
            if ruc:
                usuario.ruc = ruc
            if correo:
                usuario.correo = correo
            if telefono:
                usuario.telefono = telefono
                
            # Si el usuario existente no tenía cédula y ahora sí viene, la guardamos
            if not usuario.cedula and cedula:
                usuario.cedula = cedula
                
            usuario.save()
            usuario_creado = False
        else:
            # Validar que exista al menos un documento para crear nuevo usuario
            if not cedula and not ruc:
                raise ValueError("Debe existir al menos Cédula o RUC para registrar al usuario")

            # Crear nuevo usuario
            usuario = UsuarioAutorizacion.objects.create(
                nombres=form_data['nombres'],
                cedula=cedula,
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
        # Imprimir error en consola para depuración
        print(f"Error en crear_autorizacion_desde_form: {str(e)}")
        raise Exception(f"Error al crear autorización: {str(e)}")