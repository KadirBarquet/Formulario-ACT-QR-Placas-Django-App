from django.contrib import admin
from apps.formulario.models import TipoAutorizacion, UsuarioAutorizacion, Autorizacion, HistorialAcciones

@admin.register(TipoAutorizacion)
class TipoAutorizacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    def save_model(self, request, obj, form, change):
        obj.creado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(UsuarioAutorizacion)
class UsuarioAutorizacionAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'cedula', 'ruc', 'correo', 'telefono', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombres', 'cedula', 'ruc', 'correo', 'telefono')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'cedula', 'ruc')
        }),
        ('Contacto', {
            'fields': ('correo', 'telefono')
        }),
        ('Auditoría', {
            'fields': ('activo', 'creado_por', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Autorizacion)
class AutorizacionAdmin(admin.ModelAdmin):
    list_display = (
        'placa', 
        'usuario', 
        'tipo_autorizacion', 
        'numero_autorizacion',
        'vigencia',
        'qr_generado',
        'activo',
        'fecha_creacion'
    )
    list_filter = (
        'tipo_autorizacion',
        'qr_generado',
        'activo',
        'vigencia',
        'fecha_creacion'
    )
    search_fields = (
        'placa',
        'usuario__nombres',
        'usuario__cedula',
        'usuario__ruc',
        'usuario__correo',
        'usuario__telefono',
        'numero_autorizacion'
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
        'fecha_descarga_qr',
        'fecha_descarga_pdf'
    )
    raw_id_fields = ('usuario', 'creado_por')
    
    fieldsets = (
        ('Información del Vehículo', {
            'fields': ('placa',)
        }),
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Autorización', {
            'fields': ('tipo_autorizacion', 'numero_autorizacion', 'vigencia')
        }),
        ('QR', {
            'fields': ('codigo_qr', 'qr_generado')
        }),
        ('Auditoría', {
            'fields': (
                'activo',
                'creado_por',
                'fecha_creacion',
                'fecha_actualizacion',
                'fecha_descarga_qr',
                'fecha_descarga_pdf'
            ),
            'classes': ('collapse',)
        }),
    )

@admin.register(HistorialAcciones)
class HistorialAccionesAdmin(admin.ModelAdmin):
    list_display = ('autorizacion', 'creado_por', 'accion', 'fecha_accion')
    list_filter = ('accion', 'fecha_accion')
    search_fields = ('autorizacion__placa', 'creado_por__email', 'accion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'fecha_accion')