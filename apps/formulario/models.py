from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.security.models import User

# Clase base de auditoría
class AuditoriaModel(models.Model):
    #Modelo abstracto para auditoría que incluye campos de tracking
    activo = models.BooleanField('Activo', default=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(class)s_creados',
        verbose_name='Creado por',
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de Actualización', auto_now=True)
    
    class Meta:
        abstract = True

class TipoAutorizacion(AuditoriaModel):
    #Catálogo de tipos de autorización
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=50)
    descripcion = models.TextField('Descripción', blank=True)
    
    class Meta:
        db_table = 'formulario_tipo_autorizacion'
        verbose_name = 'Tipo de Autorización'
        verbose_name_plural = 'Tipos de Autorización'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class UsuarioAutorizacion(AuditoriaModel):
    #Usuario que tiene autorizaciones (separado del User de seguridad)
    # Información personal
    nombres = models.CharField('Nombres Completos', max_length=100)
    
    # Identificación
    cedula = models.CharField(
        'Cédula',
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^09\d{8}$',  # CORREGIDO: 09 + 8 dígitos = 10 total
                message='La cédula debe comenzar con 09 y tener 10 dígitos'
            )
        ]
    )
    ruc = models.CharField(
        'RUC',
        max_length=13,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{13}$',
                message='El RUC debe tener 13 dígitos'
            )
        ]
    )
    
    # Contacto
    correo = models.EmailField('Correo Electrónico', unique=True, blank=True, null=True)
    telefono = models.CharField(
        'Teléfono',
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^09\d{8}$',  # CORREGIDO: 09 + 8 dígitos = 10 total
                message='El teléfono debe comenzar con 09 y tener 10 dígitos'
            )
        ]
    )
    
    class Meta:
        db_table = 'formulario_usuario_autorizacion'
        verbose_name = 'Usuario con Autorización'
        verbose_name_plural = 'Usuarios con Autorización'
        ordering = ['nombres']
        indexes = [
            models.Index(fields=['cedula']),
            models.Index(fields=['ruc']),
            models.Index(fields=['correo']),
            models.Index(fields=['nombres']),
        ]
    
    def __str__(self):
        return f"{self.nombres} ({self.cedula})"
    
    def get_identificacion_completa(self):
        """Retorna la identificación completa formateada"""
        if self.cedula and self.ruc:
            return f"Cédula: {self.cedula} / RUC: {self.ruc}"
        elif self.cedula:
            return f"Cédula: {self.cedula}"
        elif self.ruc:
            return f"RUC: {self.ruc}"
        return "No disponible"

class Autorizacion(AuditoriaModel):
    #Autorizaciones asociadas a los usuarios
    # Relaciones
    usuario = models.ForeignKey(
        UsuarioAutorizacion,
        on_delete=models.CASCADE,
        related_name='autorizaciones',
        verbose_name='Usuario'
    )
    tipo_autorizacion = models.ForeignKey(
        TipoAutorizacion,
        on_delete=models.PROTECT,
        related_name='autorizaciones',
        verbose_name='Tipo de Autorización'
    )
    
    # Información del vehículo
    placa = models.CharField(
        'Placa del Vehículo',
        max_length=20,
        help_text='Ej: OBM0979-ABC1234'
    )
    
    # Información de la autorización
    numero_autorizacion = models.CharField(
        'Número de Autorización',
        max_length=30,
        unique=True,
        help_text='Ej: ACT-EP-DPOTTTM-016-2025-ACVIL'
    )
    vigencia = models.DateField('Vigencia de Autorización')
    
    # QR
    codigo_qr = models.TextField(
        'Código QR',
        blank=True,
        null=True,
        help_text='URL del código QR generado'
    )
    qr_generado = models.BooleanField('QR Generado', default=False)
    
    # Auditoría específica de autorización
    fecha_descarga_qr = models.DateTimeField(
        'Fecha de Descarga QR',
        blank=True,
        null=True
    )
    fecha_descarga_pdf = models.DateTimeField(
        'Fecha de Descarga PDF',
        blank=True,
        null=True
    )
    
    class Meta:
        db_table = 'formulario_autorizacion'
        verbose_name = 'Autorización'
        verbose_name_plural = 'Autorizaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['placa']),
            models.Index(fields=['numero_autorizacion']),
            models.Index(fields=['vigencia']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['activo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'placa', 'tipo_autorizacion'],
                name='unique_usuario_placa_tipo'
            )
        ]
    
    def __str__(self):
        return f"{self.placa} - {self.numero_autorizacion} - {self.usuario.nombres}"

    def get_tipo_autorizacion_display(self):
        """Retorna el nombre del tipo de autorización"""
        return self.tipo_autorizacion.nombre if self.tipo_autorizacion else "No especificado"
    
    @property
    def esta_caducada(self):
        """Verifica si la autorización está caducada"""
        from django.utils import timezone
        return self.vigencia < timezone.now().date()
    
    @property
    def dias_restantes(self):
        """Calcula los días restantes para la caducidad"""
        from django.utils import timezone
        from datetime import date
        hoy = timezone.now().date()
        if self.vigencia > hoy:
            return (self.vigencia - hoy).days
        return 0

class HistorialAutorizacion(AuditoriaModel):
    #Historial de cambios en las autorizaciones
    autorizacion = models.ForeignKey(
        Autorizacion,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    accion = models.CharField('Acción', max_length=50)
    descripcion = models.TextField('Descripción')
    fecha_accion = models.DateTimeField('Fecha de Acción', auto_now_add=True)
    
    # Sobrescribir el related_name para el creado_por en historial
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='historial_autorizaciones_creados',
        verbose_name='Usuario que realizó la acción'
    )
    
    class Meta:
        db_table = 'formulario_historial_autorizacion'
        verbose_name = 'Historial de Autorización'
        verbose_name_plural = 'Historial de Autorizaciones'
        ordering = ['-fecha_accion']
    
    def __str__(self):
        return f"{self.autorizacion.placa} - {self.accion} - {self.fecha_accion}"