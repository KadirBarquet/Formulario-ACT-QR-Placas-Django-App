from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from apps.formulario.models import HistorialAcciones
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse

# ============================================================================
# HISTORIAL DE ACCIONES
# ============================================================================

class HistorialAccionesListView(LoginRequiredMixin, ListView):
    """Lista de todo el historial del sistema"""
    model = HistorialAcciones
    template_name = 'formulario/historial_acciones_list.html'
    context_object_name = 'historial_acciones'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'autorizacion', 'creado_por', 'autorizacion__usuario'
        )
        
        # Filtrar por tipo de acción
        accion = self.request.GET.get('accion')
        if accion:
            queryset = queryset.filter(accion=accion)
        
        # Filtrar por fecha específica
        fecha = self.request.GET.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha_accion__date=fecha)
        
        return queryset.order_by('-fecha_accion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lista de acciones disponibles
        context['acciones'] = HistorialAcciones.objects.values_list(
            'accion', flat=True
        ).distinct()
        
        # Total de registros (todas las acciones en el historial)
        context['total_acciones'] = HistorialAcciones.objects.count()
        
        # QRs - Contar todas las acciones relacionadas con QR en el historial
        context['total_qrs_generados'] = HistorialAcciones.objects.filter(
            accion__in=['GENERAR_QR', 'DESCARGAR_QR']
        ).count()
        
        # PDFs - Contar todas las acciones relacionadas con PDF en el historial
        context['total_pdfs_generados'] = HistorialAcciones.objects.filter(
            accion__in=['GENERAR_PDF', 'DESCARGAR_PDF']
        ).count()
        
        # Actualizaciones - Contar todas las acciones de actualización en el historial
        context['total_actualizaciones'] = HistorialAcciones.objects.filter(
            accion__in=['ACTUALIZAR_AUTORIZACION', 'ACTUALIZAR_USUARIO']
        ).count()
        
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context


class VaciarHistorialAccionesView(LoginRequiredMixin, View):
    """Vista para vaciar todo el historial"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Eliminar todos los registros del historial
            cantidad = HistorialAcciones.objects.count()
            HistorialAcciones.objects.all().delete()
            
            messages.success(
                request, 
                f'Se eliminaron {cantidad} registro(s) del historial exitosamente.'
            )
        except Exception as e:
            messages.error(
                request, 
                f'Error al vaciar el historial: {str(e)}'
            )
        
        return redirect('formulario:historial_acciones_list')


class EliminarHistorialAccionesSeleccionadoView(LoginRequiredMixin, View):
    """Vista para eliminar registros seleccionados del historial"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Obtener los IDs seleccionados del POST
            ids_seleccionados = request.POST.getlist('historial_ids[]')
            
            if not ids_seleccionados:
                return JsonResponse({
                    'success': False,
                    'message': 'No se seleccionaron registros para eliminar.'
                })
            
            # Eliminar los registros seleccionados
            cantidad = HistorialAcciones.objects.filter(
                id__in=ids_seleccionados
            ).delete()[0]
            
            return JsonResponse({
                'success': True,
                'message': f'Se eliminaron {cantidad} registro(s) del historial exitosamente.',
                'cantidad': cantidad
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar registros: {str(e)}'
            })