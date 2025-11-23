from django.contrib import admin
from apps.formulario.models import TipoAutorizacion, UsuarioAutorizacion, Autorizacion, HistorialAcciones, HistorialAutorizacion

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

@admin.register(HistorialAutorizacion)
class HistorialAutorizacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_placa',
        'get_tipo_autorizacion',
        'get_usuario',
        'get_vigencia',
        'creado_por',
        'fecha_creacion'
    )
    list_filter = (
        'fecha_creacion',
        'autorizacion__tipo_autorizacion',
        'autorizacion__vigencia',
    )
    search_fields = (
        'autorizacion__placa',
        'autorizacion__usuario__nombres',
        'autorizacion__numero_autorizacion',
    )
    readonly_fields = (
        'autorizacion',
        'creado_por',
        'fecha_creacion',
        'fecha_actualizacion'
    )
    date_hierarchy = 'fecha_creacion'
    
    def get_placa(self, obj):
        return obj.autorizacion.placa
    get_placa.short_description = 'Placa'
    get_placa.admin_order_field = 'autorizacion__placa'
    
    def get_tipo_autorizacion(self, obj):
        return obj.autorizacion.tipo_autorizacion.nombre
    get_tipo_autorizacion.short_description = 'Tipo Autorización'
    get_tipo_autorizacion.admin_order_field = 'autorizacion__tipo_autorizacion__nombre'
    
    def get_usuario(self, obj):
        return obj.autorizacion.usuario.nombres
    get_usuario.short_description = 'Usuario'
    get_usuario.admin_order_field = 'autorizacion__usuario__nombres'
    
    def get_vigencia(self, obj):
        return obj.autorizacion.vigencia
    get_vigencia.short_description = 'Vigencia'
    get_vigencia.admin_order_field = 'autorizacion__vigencia'
    
    def has_add_permission(self, request):
        # No permitir agregar manualmente desde el admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # No permitir editar desde el admin
        return False