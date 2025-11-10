from django.urls import path
from apps.formulario.views import historial, home, usuario_autorizacion, autorizacion, qr_code

app_name = 'formulario'

urlpatterns = [
    # Generación de QR
    path('generar-qr/', qr_code.GenerarQRView.as_view(), name='generar_qr'),
    path('descargar-qr/<int:autorizacion_id>/', qr_code.DescargarQRView.as_view(), name='descargar_qr'),
    path('generar-pdf/<int:autorizacion_id>/', qr_code.GenerarPDFView.as_view(), name='generar_pdf'),
    path('verificar-qr/', qr_code.VerificarQRView.as_view(), name='verificar_qr'),
    
    # CRUD de Usuarios
    path('usuarios/', usuario_autorizacion.UsuarioAutorizacionListView.as_view(), name='usuario_list'),
    path('usuarios/<int:pk>/', usuario_autorizacion.UsuarioAutorizacionDetailView.as_view(), name='usuario_detail'),
    path('usuarios/crear/', usuario_autorizacion.UsuarioAutorizacionCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', usuario_autorizacion.UsuarioAutorizacionUpdateView.as_view(), name='usuario_update'),
    path('usuarios/<int:pk>/eliminar/', usuario_autorizacion.UsuarioAutorizacionDeleteView.as_view(), name='usuario_delete'),
    
    # CRUD de Autorizaciones
    path('autorizaciones/', autorizacion.AutorizacionListView.as_view(), name='autorizacion_list'),
    path('autorizaciones/<int:pk>/', autorizacion.AutorizacionDetailView.as_view(), name='autorizacion_detail'),
    path('autorizaciones/<int:pk>/editar/', autorizacion.AutorizacionUpdateView.as_view(), name='autorizacion_update'),
    path('autorizaciones/<int:pk>/eliminar/', autorizacion.AutorizacionDeleteView.as_view(), name='autorizacion_delete'),
    
    # Rutas para mostrar QR y descargar PDF
    path('autorizaciones/<int:autorizacion_id>/mostrar-qr/', qr_code.MostrarQRView.as_view(), name='mostrar_qr'),
    path('autorizaciones/<int:autorizacion_id>/descargar-qr/', qr_code.DescargarQRAutorizacionView.as_view(), name='descargar_qr_autorizacion'),
    path('autorizaciones/<int:autorizacion_id>/descargar-pdf/', qr_code.DescargarPDFAutorizacionView.as_view(), name='descargar_pdf_autorizacion'),
    
    # Historial
    path('historial/', historial.HistorialListView.as_view(), name='historial_list'),
    
    # API y utilidades
    path('api/tipos-autorizacion/', home.GetTiposAutorizacionAPIView.as_view(), name='get_tipos_autorizacion'),
    
    # Dashboard
    path('dashboard/', home.DashboardView.as_view(), name='dashboard'),
    
    # Página principal
    path('', home.DashboardView.as_view(), name='inicio'),
]