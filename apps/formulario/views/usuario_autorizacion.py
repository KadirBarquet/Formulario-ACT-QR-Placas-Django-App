from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.formulario.models import UsuarioAutorizacion, HistorialAutorizacion
from apps.formulario.form import UsuarioAutorizacionForm
from django.urls import reverse_lazy
from django.db.models import Q
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
        
        # Registrar en historial
        HistorialAutorizacion.objects.create(
            autorizacion=None,
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
        usuario_key = ("usuario", usuario.pk)

        # Si ya estamos borrando este usuario desde otra operación, seguir con el delete normal
        if _in_delete(usuario_key):
            messages.success(
                request,
                f'Usuario "{usuario.nombres}" eliminado exitosamente'
            )
            return super().delete(request, *args, **kwargs)

        _add_delete(usuario_key)
        try:
            # Borrar todas las autorizaciones relacionadas y registrar en historial
            autorizaciones = list(usuario.autorizaciones.all())
            for auth in autorizaciones:
                auth_key = ("autorizacion", auth.pk)
                if _in_delete(auth_key):
                    continue
                _add_delete(auth_key)
                try:
                    # Registrar en historial antes de eliminar la autorización
                    HistorialAutorizacion.objects.create(
                        autorizacion=auth,
                        creado_por=request.user,
                        accion='ELIMINAR_AUTORIZACION_POR_ELIMINAR_USUARIO',
                        descripcion=f'Autorización eliminada al borrar usuario {usuario.nombres}'
                    )
                    # Eliminación directa del modelo
                    auth.delete()
                finally:
                    _remove_delete(auth_key)

            # Finalmente eliminar el usuario
            messages.success(
                request, 
                f'Usuario "{usuario.nombres}" eliminado exitosamente'
            )
            return super().delete(request, *args, **kwargs)
        finally:
            _remove_delete(usuario_key)