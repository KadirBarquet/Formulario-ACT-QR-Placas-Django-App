from django.urls import path
from apps.formulario import views

app_name = 'formulario'

urlpatterns = [
    # Generación de QR
    path('generar-qr/', views.GenerarQRView.as_view(), name='generar_qr'),
    path('descargar-qr/<int:autorizacion_id>/', views.DescargarQRView.as_view(), name='descargar_qr'),
    path('generar-pdf/<int:autorizacion_id>/', views.GenerarPDFView.as_view(), name='generar_pdf'),
    path('verificar-qr/', views.VerificarQRView.as_view(), name='verificar_qr'),
    
    # CRUD de Usuarios
    path('usuarios/', views.UsuarioAutorizacionListView.as_view(), name='usuario_list'),
    path('usuarios/<int:pk>/', views.UsuarioAutorizacionDetailView.as_view(), name='usuario_detail'),
    path('usuarios/crear/', views.UsuarioAutorizacionCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.UsuarioAutorizacionUpdateView.as_view(), name='usuario_update'),
    
    # CRUD de Autorizaciones
    path('autorizaciones/', views.AutorizacionListView.as_view(), name='autorizacion_list'),
    path('autorizaciones/<int:pk>/', views.AutorizacionDetailView.as_view(), name='autorizacion_detail'),
    path('autorizaciones/<int:pk>/editar/', views.AutorizacionUpdateView.as_view(), name='autorizacion_update'),
    
    # Historial
    path('historial/', views.HistorialListView.as_view(), name='historial_list'),
    
    # API y utilidades
    path('api/tipos-autorizacion/', views.GetTiposAutorizacionAPIView.as_view(), name='get_tipos_autorizacion'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Página principal
    path('', views.DashboardView.as_view(), name='inicio'),
]