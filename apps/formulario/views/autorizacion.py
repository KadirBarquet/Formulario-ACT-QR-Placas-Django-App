from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from apps.formulario.models import Autorizacion, HistorialAutorizacion
from apps.formulario.form import BusquedaAutorizacionForm, FiltroAutorizacionForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
import threading

# Thread-local guard para evitar recursión en eliminaciones cruzadas entre vistas
_deleting = threading.local()

def _get_delete_set():
    if not hasattr(_deleting, "set"):
        _deleting.set = set()
    return _deleting.set

def _in_delete(key):
    return key in _get_delete_set()

def _add_delete(key):
    _get_delete_set().add(key)

def _remove_delete(key):
    _get_delete_set().discard(key)

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
        auth_key = ("autorizacion", autorizacion.pk)

        # Si ya estamos borrando esta autorización desde otra operación, seguir con delete normal
        if _in_delete(auth_key):
            messages.success(
                request, 
                f'Autorización para la placa "{autorizacion.placa}" eliminada exitosamente'
            )
            return super().delete(request, *args, **kwargs)

        _add_delete(auth_key)
        try:
            # Registrar eliminación en historial antes de eliminar
            HistorialAutorizacion.objects.create(
                autorizacion=autorizacion,
                creado_por=request.user,
                accion='ELIMINAR_AUTORIZACION',
                descripcion=f'Autorización eliminada: Placa {autorizacion.placa}, Número {autorizacion.numero_autorizacion}'
            )
            
            # Guardar referencia al usuario antes de eliminar la autorización
            usuario = autorizacion.usuario if hasattr(autorizacion, 'usuario') else None

            # Eliminar la autorización (modelo)
            result = super().delete(request, *args, **kwargs)

            # Si existe un usuario relacionado y no tiene otras autorizaciones, eliminar al usuario también
            if usuario:
                otras = usuario.autorizaciones.exclude(pk=autorizacion.pk).exists()
                if not otras:
                    usuario_key = ("usuario", usuario.pk)
                    if not _in_delete(usuario_key):
                        _add_delete(usuario_key)
                        try:
                            # Registrar en historial que se elimina usuario por eliminación de autorización
                            HistorialAutorizacion.objects.create(
                                autorizacion=None,
                                creado_por=request.user,
                                accion='ELIMINAR_USUARIO_POR_ELIMINAR_AUTORIZACION',
                                descripcion=f'Usuario {usuario.nombres} eliminado al borrar su última autorización'
                            )
                            usuario.delete()
                        finally:
                            _remove_delete(usuario_key)

            messages.success(
                request, 
                f'Autorización para la placa "{autorizacion.placa}" eliminada exitosamente'
            )
            return result
        finally:
            _remove_delete(auth_key)