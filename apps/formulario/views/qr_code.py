from django.contrib.auth.mixins import LoginRequiredMixin
from apps.formulario.utils import generar_url_qr, validar_autorizacion_caducada, crear_autorizacion_desde_form
from django.views import View
from apps.formulario.form import FormularioCompletoQRForm
from django.shortcuts import render, redirect, get_object_or_404
from apps.formulario.models import Autorizacion, HistorialAcciones
from django.contrib import messages
from django.utils import timezone

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

                # Asegurar que creado_por esté asignado
                if not getattr(autorizacion, 'creado_por', None):
                    autorizacion.creado_por = request.user
                autorizacion.save()
                autorizacion.refresh_from_db()

                # Generar URL para QR
                qr_url = generar_url_qr(autorizacion, request)

                # Actualizar autorización con QR
                autorizacion.codigo_qr = qr_url
                autorizacion.qr_generado = True
                autorizacion.save()

                # Crear registros en historial (QR y PDF)
                try:
                    # Registrar generación de QR
                    HistorialAcciones.objects.create(
                        autorizacion=autorizacion,
                        creado_por=request.user,
                        accion='GENERAR_QR',
                        descripcion=f'QR generado para placa {autorizacion.placa}'
                    )
                    
                    # Registrar generación de PDF
                    HistorialAcciones.objects.create(
                        autorizacion=autorizacion,
                        creado_por=request.user,
                        accion='GENERAR_PDF',
                        descripcion=f'PDF de autorización preparado para placa {autorizacion.placa}'
                    )
                except Exception as e:
                    print(f'Error al registrar en historial: {e}')
                    pass
                
                # Pasar datos a la plantilla
                context.update({
                    'qr_generado': True,
                    'qr_url': qr_url,
                    'autorizacion_id': autorizacion.id,
                    'autorizacion_data': {
                        'placa': autorizacion.placa,
                        'nombres': autorizacion.usuario.nombres if autorizacion.usuario else '',
                        'numero_autorizacion': autorizacion.numero_autorizacion,
                        'tipo_autorizacion': autorizacion.get_tipo_autorizacion_display() if hasattr(autorizacion, 'get_tipo_autorizacion_display') else '',
                        'vigencia': autorizacion.vigencia.strftime('%Y-%m-%d'),
                        'esta_caducada': getattr(autorizacion, 'esta_caducada', False),
                        'id': autorizacion.id,
                    }
                })
                
                messages.success(request, 'QR generado exitosamente')
                
            except Exception as e:
                messages.error(request, f'Error al generar QR: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')
        
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = {
            'current_date': timezone.now().strftime('%d/%m/%Y, %H:%M'),
            'qr_generado': False,  # Por defecto False
        }
        context.update(kwargs)
        return context

class DescargarQRView(LoginRequiredMixin, View):
    """Vista para preparar la descarga del QR (no genera archivo aquí, sólo registra y redirige)"""
    
    def get(self, request, autorizacion_id):
        # Quitar la restricción creado_por=request.user para evitar que falle si no coincide
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id)
        
        if validar_autorizacion_caducada(autorizacion.vigencia):
            messages.error(request, 'No se puede descargar QR: autorización caducada')
            return redirect('formulario:generar_qr')
        
        # Registrar descarga en historial (no bloquear si falla)
        try:
            HistorialAcciones.objects.create(
                autorizacion=autorizacion,
                creado_por=request.user,
                accion='DESCARGAR_QR',
                descripcion=f'QR descargado para placa {autorizacion.placa}'
            )
        except Exception:
            pass
        
        # Actualizar fecha de descarga
        autorizacion.fecha_descarga_qr = timezone.now()
        autorizacion.save()
        
        messages.success(request, 'QR listo para descargar')
        # Ideal: redirigir al detalle de autorización o a la misma página mostrando el QR
        return redirect(request.GET.get('next', 'formulario:generar_qr'))

class GenerarPDFView(LoginRequiredMixin, View):
    """Vista para preparar la generación de PDF de autorización (no crea archivo aquí)"""
    
    def get(self, request, autorizacion_id):
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id)
        
        if validar_autorizacion_caducada(autorizacion.vigencia):
            messages.error(request, 'No se puede generar PDF: autorización caducada')
            return redirect('formulario:generar_qr')
        
        # Registrar descarga de PDF en historial
        try:
            HistorialAcciones.objects.create(
                autorizacion=autorizacion,
                creado_por=request.user,
                accion='DESCARGAR_PDF',
                descripcion=f'PDF descargado para placa {autorizacion.placa}'
            )
        except Exception:
            pass
        
        # Actualizar fecha de descarga PDF
        autorizacion.fecha_descarga_pdf = timezone.now()
        autorizacion.save()
        
        messages.success(request, 'PDF generado exitosamente')
        return redirect(request.GET.get('next', 'formulario:generar_qr')) 

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
                        'nombres': autorizacion.usuario.nombres if autorizacion.usuario else nombres,
                        'cedula': autorizacion.usuario.cedula if autorizacion.usuario else cedula or 'No disponible',
                        'ruc': autorizacion.usuario.ruc if autorizacion.usuario else ruc or 'No disponible',
                        'numero_autorizacion': autorizacion.numero_autorizacion,
                        'tipo_autorizacion': autorizacion.get_tipo_autorizacion_display() if hasattr(autorizacion, 'get_tipo_autorizacion_display') else 'No disponible',
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

# Vista para boton para visualizar y descargar como png el QR de autorizacion generado
class MostrarQRView(LoginRequiredMixin, View):
    """Vista para mostrar el QR de una autorización existente"""
    template_name = 'formulario/mostrar_qr.html'

    def get(self, request, autorizacion_id):
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id)
        
        # Generar URL del QR si no existe
        if not autorizacion.codigo_qr:
            qr_url = generar_url_qr(autorizacion, request)
            autorizacion.codigo_qr = qr_url
            autorizacion.qr_generado = True
            autorizacion.save()
        
        context = {
            'autorizacion': autorizacion,
            'qr_url': autorizacion.codigo_qr,
            'autorizacion_data': {
                'placa': autorizacion.placa,
                'nombres': autorizacion.usuario.nombres if autorizacion.usuario else '',
                'numero_autorizacion': autorizacion.numero_autorizacion,
                'tipo_autorizacion': autorizacion.get_tipo_autorizacion_display(),
                'vigencia': autorizacion.vigencia.strftime('%Y-%m-%d'),
                'esta_caducada': autorizacion.esta_caducada,
            },
            'current_date': timezone.now().strftime('%d/%m/%Y, %H:%M'),
        }

        return render(request, self.template_name, context)

class DescargarQRAutorizacionView(LoginRequiredMixin, View):
    """Vista para registrar la descarga del QR"""
    
    def get(self, request, autorizacion_id):
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id)

        # Registrar descarga en historial
        try:
            HistorialAcciones.objects.create(
                autorizacion=autorizacion,
                creado_por=request.user,
                accion='DESCARGAR_QR',
                descripcion=f'QR descargado para placa {autorizacion.placa}'
            )
        except Exception as e:
            print(f'Error: {e}') # 
        
        # Actualizar fecha de descarga
        autorizacion.fecha_descarga_qr = timezone.now()
        autorizacion.save()
        
        messages.success(request, 'QR descargado exitosamente')
        return redirect('formulario:mostrar_qr', autorizacion_id=autorizacion_id)

class DescargarPDFAutorizacionView(LoginRequiredMixin, View):
    """Vista para preparar la descarga del PDF de autorización"""
    
    def get(self, request, autorizacion_id):
        autorizacion = get_object_or_404(Autorizacion, id=autorizacion_id)
        
        # Registrar descarga de PDF en historial
        try:
            HistorialAcciones.objects.create(
                autorizacion=autorizacion,
                creado_por=request.user,
                accion='DESCARGAR_PDF',
                descripcion=f'PDF descargado para placa {autorizacion.placa}'
            )
        except Exception as e:
            print(f'Error: {e}')
        
        # Actualizar fecha de descarga PDF
        autorizacion.fecha_descarga_pdf = timezone.now()
        autorizacion.save()
        
        # Preparar datos para la plantilla
        context = {
            'autorizacion': autorizacion,
            'autorizacion_data': {
                'placa': autorizacion.placa,
                'nombres': autorizacion.usuario.nombres if autorizacion.usuario else '',
                'numero_autorizacion': autorizacion.numero_autorizacion,
                'tipo_autorizacion': autorizacion.get_tipo_autorizacion_display(),
                'vigencia': autorizacion.vigencia.strftime('%Y-%m-%d'),
                'cedula': autorizacion.usuario.cedula if autorizacion.usuario else '',
                'ruc': autorizacion.usuario.ruc if autorizacion.usuario else '',
                'correo': autorizacion.usuario.correo if autorizacion.usuario else '',
                'telefono': autorizacion.usuario.telefono if autorizacion.usuario else '',
            },
            'current_date': timezone.now().strftime('%d/%m/%Y, %H:%M'),
        }
        
        return render(request, 'formulario/descargar_pdf.html', context)