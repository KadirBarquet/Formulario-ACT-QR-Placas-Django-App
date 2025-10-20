from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count
from django.db import models

from apps.formulario.models import UsuarioAutorizacion, Autorizacion, TipoAutorizacion, HistorialAutorizacion
from apps.formulario.form import (
    FormularioCompletoQRForm, 
    BusquedaAutorizacionForm, 
    FiltroAutorizacionForm,
    UsuarioAutorizacionForm
)
from .utils import generar_url_qr, validar_autorizacion_caducada, crear_autorizacion_desde_form

# ============================================================================
# VISTAS PARA GENERACIÓN DE QR
# ============================================================================

class GenerarQRView(LoginRequiredMixin, View):
    """Vista para generar código QR - Réplica del formulario web"""
    template_name = 'formulario/generar_qr.html'
    
    def get(self, request):
        form = FormularioCompletoQRForm()
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = FormularioCompletoQRForm(request.POST)
        context = self.get_context_data(form=form)
        
        if form.is_valid():
            try:
                # Crear la autorización
                autorizacion, usuario_creado = crear_autorizacion_desde_form(
                    form.cleaned_data, 
                    request.user
                )
                
                # Generar URL para QR
                qr_url = generar_url_qr(autorizacion, request)
                
                # Actualizar autorización con QR
                autorizacion.codigo_qr = qr_url
                autorizacion.qr_generado = True
                autorizacion.save()
                
                # Crear registro en historial
                HistorialAutorizacion.objects.create(
                    autorizacion=autorizacion,
                    creado_por=request.user,
                    accion='GENERAR_QR',
                    descripcion=f'QR generado para placa {autorizacion.placa}'
                )
                
                context.update({
                    'qr_generado': True,
                    'qr_url': qr_url,
                    'autorizacion_data': {
                        'placa': autorizacion.placa,
                        'nombres': autorizacion.usuario.nombres,
                        'numero_autorizacion': autorizacion.numero_autorizacion,
                        'tipo_autorizacion': autorizacion.get_tipo_autorizacion_display(),
                        'vigencia': autorizacion.vigencia,
                        'esta_caducada': autorizacion.esta_caducada,
                        'id': autorizacion.id,
                    }
                })
                
                messages.success(request, '✅ QR generado exitosamente')
                
            except Exception as e:
                messages.error(request, f'Error al generar QR: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = {
            'current_date': timezone.now().strftime('%d/%m/%Y, %H:%M'),
        }
        context.update(kwargs)
        return context

class DescargarQRView(LoginRequiredMixin, View):
    """Vista para descargar QR como PNG"""
    
    def get(self, request, autorizacion_id):
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id, creado_por=request.user)
        
        if validar_autorizacion_caducada(autorizacion.vigencia):
            messages.error(request, 'No se puede descargar QR: autorización caducada')
            return redirect('formulario:generar_qr')
        
        # Registrar descarga en historial
        HistorialAutorizacion.objects.create(
            autorizacion=autorizacion,
            creado_por=request.user,
            accion='DESCARGAR_QR',
            descripcion=f'QR descargado para placa {autorizacion.placa}'
        )
        
        # Actualizar fecha de descarga
        autorizacion.fecha_descarga_qr = timezone.now()
        autorizacion.save()
        
        messages.success(request, 'QR listo para descargar')
        return redirect('formulario:generar_qr')

class GenerarPDFView(LoginRequiredMixin, View):
    """Vista para generar PDF de autorización"""
    
    def get(self, request, autorizacion_id):
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id, creado_por=request.user)
        
        if validar_autorizacion_caducada(autorizacion.vigencia):
            messages.error(request, 'No se puede generar PDF: autorización caducada')
            return redirect('formulario:generar_qr')
        
        # Registrar generación de PDF en historial
        HistorialAutorizacion.objects.create(
            autorizacion=autorizacion,
            creado_por=request.user,
            accion='GENERAR_PDF',
            descripcion=f'PDF generado para placa {autorizacion.placa}'
        )
        
        # Actualizar fecha de descarga PDF
        autorizacion.fecha_descarga_pdf = timezone.now()
        autorizacion.save()
        
        messages.success(request, 'PDF generado exitosamente')
        return redirect('formulario:generar_qr')

class VerificarQRView(View):
    """Vista para verificar QR cuando se escanea"""
    template_name = 'formulario/verificar_qr.html'
    
    def get(self, request):
        # Parámetros de la URL (optimizados)
        placa = request.GET.get('p') or request.GET.get('placa')
        nombres = request.GET.get('n') or request.GET.get('nombre')
        cedula = request.GET.get('ci') or request.GET.get('cedula')
        ruc = request.GET.get('r') or request.GET.get('ruc')
        numero_autorizacion = request.GET.get('a') or request.GET.get('autorizacion')
        vigencia_str = request.GET.get('c') or request.GET.get('caducidad')
        tipo_autorizacion_codigo = request.GET.get('ta') or request.GET.get('tipoAutorizacion')
        
        autorizacion_data = None
        esta_caducada = False
        mensaje = ''
        
        if all([placa, nombres, numero_autorizacion, vigencia_str]):
            try:
                # Buscar autorización
                autorizacion = Autorizacion.objects.filter(
                    placa=placa,
                    numero_autorizacion=numero_autorizacion,
                    activo=True
                ).first()
                
                if autorizacion:
                    # Verificar si está caducada
                    esta_caducada = autorizacion.esta_caducada
                    
                    autorizacion_data = {
                        'placa': autorizacion.placa,
                        'nombres': autorizacion.usuario.nombres,
                        'cedula': autorizacion.usuario.cedula,
                        'ruc': autorizacion.usuario.ruc,
                        'numero_autorizacion': autorizacion.numero_autorizacion,
                        'tipo_autorizacion': autorizacion.get_tipo_autorizacion_display(),
                        'vigencia': autorizacion.vigencia,
                        'esta_caducada': esta_caducada,
                    }
                    
                    if esta_caducada:
                        mensaje = '⚠️ AUTORIZACIÓN CADUCADA - Esta autorización ya no es válida'
                    else:
                        mensaje = f'✅ Autorización válida para placa: {placa}'
                else:
                    # Si no encuentra en BD, mostrar datos del QR
                    from datetime import datetime
                    try:
                        vigencia = datetime.strptime(vigencia_str, '%Y-%m-%d').date()
                        esta_caducada = validar_autorizacion_caducada(vigencia)
                        
                        autorizacion_data = {
                            'placa': placa,
                            'nombres': nombres,
                            'cedula': cedula or 'No disponible',
                            'ruc': ruc or 'No disponible',
                            'numero_autorizacion': numero_autorizacion,
                            'tipo_autorizacion': 'No disponible',
                            'vigencia': vigencia,
                            'esta_caducada': esta_caducada,
                        }
                        
                        if esta_caducada:
                            mensaje = '⚠️ AUTORIZACIÓN CADUCADA - Esta autorización ya no es válida'
                        else:
                            mensaje = f'✅ Autorización válida para placa: {placa}'
                            
                    except ValueError:
                        mensaje = '❌ Error: Formato de fecha inválido'
            except Exception as e:
                mensaje = f'❌ Error al verificar autorización: {str(e)}'
        else:
            mensaje = '❌ Datos de autorización incompletos'
        
        context = {
            'autorizacion_data': autorizacion_data,
            'mensaje': mensaje,
            'esta_caducada': esta_caducada,
            'current_date': timezone.now().strftime('%d/%m/%Y, %H:%M'),
        }
        
        return render(request, self.template_name, context)

# ============================================================================
# CRUD DE USUARIOS AUTORIZACION
# ============================================================================

class UsuarioAutorizacionListView(LoginRequiredMixin, ListView):
    """Lista de usuarios con autorizaciones"""
    model = UsuarioAutorizacion
    template_name = 'formulario/usuarioautorizacion_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('creado_por')
        
        # Búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(cedula__icontains=search) |
                Q(ruc__icontains=search) |
                Q(correo__icontains=search) |
                Q(telefono__icontains=search)
            )
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado == 'activos':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivos':
            queryset = queryset.filter(activo=False)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        context['search_term'] = self.request.GET.get('search', '')
        context['estado_filter'] = self.request.GET.get('estado', '')
        return context

class UsuarioAutorizacionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de usuario con sus autorizaciones"""
    model = UsuarioAutorizacion
    template_name = 'formulario/usuarioautorizacion_detail.html'
    context_object_name = 'usuario'
    
    def get_queryset(self):
        return super().get_queryset().select_related('creado_por')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['autorizaciones'] = self.object.autorizaciones.select_related(
            'tipo_autorizacion', 'creado_por'
        ).order_by('-fecha_creacion')
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context

class UsuarioAutorizacionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Crear nuevo usuario"""
    model = UsuarioAutorizacion
    form_class = UsuarioAutorizacionForm
    template_name = 'formulario/usuarioautorizacion_form.html'
    permission_required = 'formulario.add_usuarioautorizacion'
    success_url = reverse_lazy('formulario:usuario_list')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Usuario creado exitosamente')
        return super().form_valid(form)

class UsuarioAutorizacionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar usuario existente"""
    model = UsuarioAutorizacion
    form_class = UsuarioAutorizacionForm
    template_name = 'formulario/usuarioautorizacion_form.html'
    permission_required = 'formulario.change_usuarioautorizacion'
    
    def get_success_url(self):
        return reverse_lazy('formulario:usuario_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente')
        
        # Registrar en historial (podrías crear un historial específico para usuarios)
        HistorialAutorizacion.objects.create(
            autorizacion=None,  # O crear un modelo de historial para usuarios
            creado_por=self.request.user,
            accion='ACTUALIZAR_USUARIO',
            descripcion=f'Usuario {self.object.nombres} actualizado'
        )
        
        return super().form_valid(form)

class UsuarioAutorizacionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Eliminar usuario"""
    model = UsuarioAutorizacion
    template_name = 'formulario/usuarioautorizacion_confirm_delete.html'
    permission_required = 'formulario.delete_usuarioautorizacion'
    success_url = reverse_lazy('formulario:usuario_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        # Contar autorizaciones relacionadas
        context['autorizaciones_count'] = self.object.autorizaciones.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()
        messages.success(
            request, 
            f'Usuario "{usuario.nombres}" eliminado exitosamente'
        )
        return super().delete(request, *args, **kwargs)

# ============================================================================
# CRUD DE AUTORIZACIONES
# ============================================================================

class AutorizacionListView(LoginRequiredMixin, ListView):
    """Lista de autorizaciones con búsqueda y filtros"""
    model = Autorizacion
    template_name = 'formulario/autorizacion_list.html'
    context_object_name = 'autorizaciones'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Autorizacion.objects.select_related(
            'usuario', 'tipo_autorizacion', 'creado_por'
        )
        
        # Aplicar búsqueda
        busqueda_form = BusquedaAutorizacionForm(self.request.GET or None)
        if busqueda_form.is_valid():
            tipo_busqueda = busqueda_form.cleaned_data['tipo_busqueda']
            termino = busqueda_form.cleaned_data['termino_busqueda']
            solo_activas = busqueda_form.cleaned_data['solo_activas']
            
            if termino:
                if tipo_busqueda == 'placa':
                    queryset = queryset.filter(placa__icontains=termino)
                elif tipo_busqueda == 'nombres':
                    queryset = queryset.filter(usuario__nombres__icontains=termino)
                elif tipo_busqueda == 'cedula':
                    queryset = queryset.filter(usuario__cedula__icontains=termino)
                elif tipo_busqueda == 'ruc':
                    queryset = queryset.filter(usuario__ruc__icontains=termino)
                elif tipo_busqueda == 'correo':
                    queryset = queryset.filter(usuario__correo__icontains=termino)
                elif tipo_busqueda == 'telefono':
                    queryset = queryset.filter(usuario__telefono__icontains=termino)
                elif tipo_busqueda == 'numero_autorizacion':
                    queryset = queryset.filter(numero_autorizacion__icontains=termino)
                elif tipo_busqueda == 'tipo_autorizacion':
                    queryset = queryset.filter(tipo_autorizacion__nombre__icontains=termino)
            
            if solo_activas:
                queryset = queryset.filter(activo=True)
        
        # Aplicar filtros
        filtro_form = FiltroAutorizacionForm(self.request.GET or None)
        if filtro_form.is_valid():
            tipo_autorizacion = filtro_form.cleaned_data['tipo_autorizacion']
            estado = filtro_form.cleaned_data['estado']
            fecha_desde = filtro_form.cleaned_data['fecha_desde']
            fecha_hasta = filtro_form.cleaned_data['fecha_hasta']
            
            if tipo_autorizacion:
                queryset = queryset.filter(tipo_autorizacion=tipo_autorizacion)
            
            if estado == 'activas':
                queryset = queryset.filter(activo=True)
            elif estado == 'caducadas':
                queryset = queryset.filter(vigencia__lt=timezone.now().date())
            elif estado == 'inactivas':
                queryset = queryset.filter(activo=False)
            
            if fecha_desde:
                queryset = queryset.filter(fecha_creacion__date__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fecha_creacion__date__lte=fecha_hasta)
        
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busqueda_form'] = BusquedaAutorizacionForm(self.request.GET or None)
        context['filtro_form'] = FiltroAutorizacionForm(self.request.GET or None)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context

class AutorizacionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de autorización con historial"""
    model = Autorizacion
    template_name = 'formulario/autorizacion_detail.html'
    context_object_name = 'autorizacion'
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'usuario', 'tipo_autorizacion', 'creado_por'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historial'] = self.object.historial.select_related(
            'creado_por'
        ).order_by('-fecha_accion')
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context

class AutorizacionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar autorización"""
    model = Autorizacion
    template_name = 'formulario/autorizacion_form.html'
    permission_required = 'formulario.change_autorizacion'
    fields = ['vigencia', 'activo']
    
    def get_success_url(self):
        return reverse_lazy('formulario:autorizacion_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Registrar cambio en historial
        cambios = []
        if 'vigencia' in form.changed_data:
            cambios.append(f'Vigencia cambiada a {form.cleaned_data["vigencia"]}')
        if 'activo' in form.changed_data:
            estado = "Activo" if form.cleaned_data["activo"] else "Inactivo"
            cambios.append(f'Estado cambiado a {estado}')
        
        if cambios:
            HistorialAutorizacion.objects.create(
                autorizacion=self.object,
                creado_por=self.request.user,
                accion='ACTUALIZAR_AUTORIZACION',
                descripcion='; '.join(cambios)
            )
        
        messages.success(self.request, 'Autorización actualizada exitosamente')
        return super().form_valid(form)

class AutorizacionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Eliminar autorización"""
    model = Autorizacion
    template_name = 'formulario/autorizacion_confirm_delete.html'
    permission_required = 'formulario.delete_autorizacion'
    success_url = reverse_lazy('formulario:autorizacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context
    
    def delete(self, request, *args, **kwargs):
        autorizacion = self.get_object()

        # Registrar eliminación en historial antes de eliminar
        HistorialAutorizacion.objects.create(
            autorizacion=autorizacion,
            creado_por=request.user,
            accion='ELIMINAR_AUTORIZACION',
            descripcion=f'Autorización eliminada: Placa {autorizacion.placa}, Número {autorizacion.numero_autorizacion}'
        )
        
        messages.success(
            request, 
            f'Autorización para la placa "{autorizacion.placa}" eliminada exitosamente'
        )
        return super().delete(request, *args, **kwargs)

# ============================================================================
# HISTORIAL
# ============================================================================

class HistorialListView(LoginRequiredMixin, ListView):
    """Lista de todo el historial del sistema"""
    model = HistorialAutorizacion
    template_name = 'formulario/historial_list.html'
    context_object_name = 'historial'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'autorizacion', 'creado_por', 'autorizacion__usuario'
        )
        
        # Filtrar por tipo de acción
        accion = self.request.GET.get('accion')
        if accion:
            queryset = queryset.filter(accion=accion)
        
        # Filtrar por fecha
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        
        if fecha_desde:
            queryset = queryset.filter(fecha_accion__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_accion__date__lte=fecha_hasta)
        
        return queryset.order_by('-fecha_accion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acciones'] = HistorialAutorizacion.objects.values_list(
            'accion', flat=True
        ).distinct()
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context

# ============================================================================
# DASHBOARD Y APIS
# ============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard con estadísticas"""
    template_name = 'formulario/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas
        context['total_autorizaciones'] = Autorizacion.objects.count()
        context['autorizaciones_activas'] = Autorizacion.objects.filter(activo=True).count()
        context['autorizaciones_caducadas'] = Autorizacion.objects.filter(
            vigencia__lt=timezone.now().date()
        ).count()
        context['total_usuarios'] = UsuarioAutorizacion.objects.count()
        
        # Autorizaciones por tipo
        context['autorizaciones_por_tipo'] = Autorizacion.objects.filter(
            activo=True
        ).values(
            'tipo_autorizacion__nombre'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Últimas autorizaciones
        context['ultimas_autorizaciones'] = Autorizacion.objects.select_related(
            'usuario', 'tipo_autorizacion'
        ).order_by('-fecha_creacion')[:5]
        
        # Actividad reciente
        context['actividad_reciente'] = HistorialAutorizacion.objects.select_related(
            'creado_por', 'autorizacion'
        ).order_by('-fecha_accion')[:10]
        
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context

class GetTiposAutorizacionAPIView(LoginRequiredMixin, View):
    """API para obtener tipos de autorización (AJAX)"""
    
    def get(self, request):
        tipos = TipoAutorizacion.objects.filter(activo=True).values('id', 'codigo', 'nombre')
        return JsonResponse(list(tipos), safe=False)