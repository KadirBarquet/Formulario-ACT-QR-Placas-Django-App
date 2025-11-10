from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from apps.formulario.models import UsuarioAutorizacion, Autorizacion, TipoAutorizacion, HistorialAutorizacion
from django.utils import timezone
from django.db.models import Count
from django.http import JsonResponse

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