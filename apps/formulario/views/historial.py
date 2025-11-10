from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.formulario.models import HistorialAutorizacion
from django.utils import timezone

# ============================================================================
# HISTORIAL DE ACCIONES
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