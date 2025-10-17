"""
Tests para la aplicación de formulario
Incluye tests para models, forms, views y utils
"""
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal

from apps.formulario.models import (
    TipoAutorizacion, 
    UsuarioAutorizacion, 
    Autorizacion, 
    HistorialAutorizacion
)
from apps.formulario.form import (
    FormularioCompletoQRForm,
    BusquedaAutorizacionForm,
    FiltroAutorizacionForm,
    UsuarioAutorizacionForm
)
from apps.formulario.utils import (
    generar_url_qr,
    validar_autorizacion_caducada,
    crear_autorizacion_desde_form
)

User = get_user_model()


# ============================================================================
# TESTS DE MODELOS
# ============================================================================

class TipoAutorizacionModelTest(TestCase):
    """Tests para el modelo TipoAutorizacion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_crear_tipo_autorizacion(self):
        """Test crear tipo de autorización"""
        tipo = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            descripcion='Autorización de transporte',
            creado_por=self.user
        )
        
        self.assertEqual(tipo.codigo, 'TRAN')
        self.assertEqual(tipo.nombre, 'Transporte')
        self.assertTrue(tipo.activo)
        self.assertEqual(str(tipo), 'Transporte')
    
    def test_codigo_unico(self):
        """Test que el código sea único"""
        TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        with self.assertRaises(Exception):
            TipoAutorizacion.objects.create(
                codigo='TRAN',
                nombre='Transporte Otro',
                creado_por=self.user
            )


class UsuarioAutorizacionModelTest(TestCase):
    """Tests para el modelo UsuarioAutorizacion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_crear_usuario_autorizacion_con_cedula(self):
        """Test crear usuario solo con cédula"""
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        self.assertEqual(usuario.nombres, 'Juan Pérez')
        self.assertEqual(usuario.cedula, '0912345678')
        self.assertIsNone(usuario.ruc)
        self.assertEqual(str(usuario), 'Juan Pérez (0912345678)')
    
    def test_crear_usuario_con_cedula_y_ruc(self):
        """Test crear usuario con cédula y RUC"""
        usuario = UsuarioAutorizacion.objects.create(
            nombres='María López',
            cedula='0923456789',
            ruc='0923456789001',
            correo='maria@example.com',
            telefono='0998765432',
            creado_por=self.user
        )
        
        self.assertEqual(usuario.ruc, '0923456789001')
        self.assertIsNotNone(usuario.ruc)
    
    def test_cedula_invalida_formato(self):
        """Test validación de formato de cédula"""
        with self.assertRaises(Exception):
            usuario = UsuarioAutorizacion(
                nombres='Test User',
                cedula='1234567890',  # No empieza con 09
                correo='test@example.com',
                telefono='0987654321',
                creado_por=self.user
            )
            usuario.full_clean()
    
    def test_ruc_invalido_longitud(self):
        """Test validación de longitud de RUC"""
        with self.assertRaises(Exception):
            usuario = UsuarioAutorizacion(
                nombres='Test User',
                cedula='0912345678',
                ruc='12345',  # Muy corto
                correo='test@example.com',
                telefono='0987654321',
                creado_por=self.user
            )
            usuario.full_clean()
    
    def test_correo_unico(self):
        """Test que el correo sea único"""
        UsuarioAutorizacion.objects.create(
            nombres='Usuario 1',
            cedula='0912345678',
            correo='correo@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        with self.assertRaises(Exception):
            UsuarioAutorizacion.objects.create(
                nombres='Usuario 2',
                cedula='0923456789',
                correo='correo@example.com',  # Correo duplicado
                telefono='0998765432',
                creado_por=self.user
            )
    
    def test_get_identificacion_completa(self):
        """Test método get_identificacion_completa"""
        # Solo cédula
        usuario1 = UsuarioAutorizacion.objects.create(
            nombres='Usuario 1',
            cedula='0912345678',
            correo='user1@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        self.assertEqual(
            usuario1.get_identificacion_completa(),
            'Cédula: 0912345678'
        )
        
        # Cédula y RUC
        usuario2 = UsuarioAutorizacion.objects.create(
            nombres='Usuario 2',
            cedula='0923456789',
            ruc='0923456789001',
            correo='user2@example.com',
            telefono='0998765432',
            creado_por=self.user
        )
        self.assertEqual(
            usuario2.get_identificacion_completa(),
            'Cédula: 0923456789 / RUC: 0923456789001'
        )


class AutorizacionModelTest(TestCase):
    """Tests para el modelo Autorizacion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        self.usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
    
    def test_crear_autorizacion(self):
        """Test crear autorización"""
        vigencia = timezone.now().date() + timedelta(days=365)
        autorizacion = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=vigencia,
            creado_por=self.user
        )
        
        self.assertEqual(autorizacion.placa, 'ABC1234')
        self.assertEqual(autorizacion.numero_autorizacion, 'ACT-EP-001-2025')
        self.assertTrue(autorizacion.activo)
        self.assertFalse(autorizacion.qr_generado)
        self.assertIn('ABC1234', str(autorizacion))
    
    def test_numero_autorizacion_unico(self):
        """Test que el número de autorización sea único"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=vigencia,
            creado_por=self.user
        )
        
        with self.assertRaises(Exception):
            Autorizacion.objects.create(
                usuario=self.usuario,
                tipo_autorizacion=self.tipo_autorizacion,
                placa='XYZ5678',
                numero_autorizacion='ACT-EP-001-2025',  # Duplicado
                vigencia=vigencia,
                creado_por=self.user
            )
    
    def test_esta_caducada_property(self):
        """Test propiedad esta_caducada"""
        # Autorización vigente
        autorizacion_vigente = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=timezone.now().date() + timedelta(days=30),
            creado_por=self.user
        )
        self.assertFalse(autorizacion_vigente.esta_caducada)
        
        # Autorización caducada
        autorizacion_caducada = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='XYZ5678',
            numero_autorizacion='ACT-EP-002-2025',
            vigencia=timezone.now().date() - timedelta(days=1),
            creado_por=self.user
        )
        self.assertTrue(autorizacion_caducada.esta_caducada)
    
    def test_dias_restantes_property(self):
        """Test propiedad dias_restantes"""
        # Autorización con 30 días restantes
        autorizacion = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=timezone.now().date() + timedelta(days=30),
            creado_por=self.user
        )
        self.assertEqual(autorizacion.dias_restantes, 30)
        
        # Autorización caducada
        autorizacion_caducada = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='XYZ5678',
            numero_autorizacion='ACT-EP-002-2025',
            vigencia=timezone.now().date() - timedelta(days=10),
            creado_por=self.user
        )
        self.assertEqual(autorizacion_caducada.dias_restantes, 0)
    
    def test_get_tipo_autorizacion_display(self):
        """Test método get_tipo_autorizacion_display"""
        autorizacion = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=timezone.now().date() + timedelta(days=365),
            creado_por=self.user
        )
        
        self.assertEqual(
            autorizacion.get_tipo_autorizacion_display(),
            'Transporte'
        )
    
    def test_constraint_unique_usuario_placa_tipo(self):
        """Test constraint de unicidad usuario-placa-tipo"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        # Primera autorización
        Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=vigencia,
            creado_por=self.user
        )
        
        # Intentar crear autorización duplicada
        with self.assertRaises(Exception):
            Autorizacion.objects.create(
                usuario=self.usuario,
                tipo_autorizacion=self.tipo_autorizacion,
                placa='ABC1234',  # Misma placa y tipo
                numero_autorizacion='ACT-EP-002-2025',
                vigencia=vigencia,
                creado_por=self.user
            )


class HistorialAutorizacionModelTest(TestCase):
    """Tests para el modelo HistorialAutorizacion"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        self.autorizacion = Autorizacion.objects.create(
            usuario=usuario,
            tipo_autorizacion=tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=timezone.now().date() + timedelta(days=365),
            creado_por=self.user
        )
    
    def test_crear_historial(self):
        """Test crear registro de historial"""
        historial = HistorialAutorizacion.objects.create(
            autorizacion=self.autorizacion,
            accion='GENERAR_QR',
            descripcion='QR generado para placa ABC1234',
            creado_por=self.user
        )
        
        self.assertEqual(historial.accion, 'GENERAR_QR')
        self.assertEqual(historial.autorizacion, self.autorizacion)
        self.assertIn('ABC1234', str(historial))
    
    def test_multiples_registros_historial(self):
        """Test crear múltiples registros de historial"""
        HistorialAutorizacion.objects.create(
            autorizacion=self.autorizacion,
            accion='GENERAR_QR',
            descripcion='QR generado',
            creado_por=self.user
        )
        
        HistorialAutorizacion.objects.create(
            autorizacion=self.autorizacion,
            accion='DESCARGAR_QR',
            descripcion='QR descargado',
            creado_por=self.user
        )
        
        HistorialAutorizacion.objects.create(
            autorizacion=self.autorizacion,
            accion='GENERAR_PDF',
            descripcion='PDF generado',
            creado_por=self.user
        )
        
        self.assertEqual(
            self.autorizacion.historial.count(),
            3
        )


# ============================================================================
# TESTS DE FORMULARIOS
# ============================================================================

class FormularioCompletoQRFormTest(TestCase):
    """Tests para FormularioCompletoQRForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
    
    def test_form_valido_con_cedula(self):
        """Test formulario válido con cédula"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'placa': 'ABC1234',
            'nombres': 'Juan Pérez',
            'tipo_identificacion': 'cedula',
            'cedula': '0912345678',
            'correo': 'juan@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EP-001-2025',
            'vigencia': vigencia
        }
        
        form = FormularioCompletoQRForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valido_con_ruc(self):
        """Test formulario válido con RUC"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'placa': 'ABC1234',
            'nombres': 'María López',
            'tipo_identificacion': 'ruc',
            'ruc': '0923456789001',
            'correo': 'maria@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EP-002-2025',
            'vigencia': vigencia
        }
        
        form = FormularioCompletoQRForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_valido_con_ambos(self):
        """Test formulario válido con cédula y RUC"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'placa': 'ABC1234',
            'nombres': 'Pedro Gómez',
            'tipo_identificacion': 'ambos',
            'cedula': '0934567890',
            'ruc': '0934567890001',
            'correo': 'pedro@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EP-003-2025',
            'vigencia': vigencia
        }
        
        form = FormularioCompletoQRForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_cedula_faltante(self):
        """Test formulario inválido - falta cédula cuando es requerida"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'placa': 'ABC1234',
            'nombres': 'Juan Pérez',
            'tipo_identificacion': 'cedula',
            # cedula faltante
            'correo': 'juan@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EP-001-2025',
            'vigencia': vigencia
        }
        
        form = FormularioCompletoQRForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)
    
    def test_form_invalido_cedula_formato(self):
        """Test formulario inválido - formato de cédula incorrecto"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'placa': 'ABC1234',
            'nombres': 'Juan Pérez',
            'tipo_identificacion': 'cedula',
            'cedula': '1234567890',  # No empieza con 09
            'correo': 'juan@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EP-001-2025',
            'vigencia': vigencia
        }
        
        form = FormularioCompletoQRForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cedula', form.errors)
    
    def test_form_invalido_vigencia_pasada(self):
        """Test formulario inválido - fecha de vigencia pasada"""
        vigencia = timezone.now().date() - timedelta(days=30)
        
        form_data = {
            'placa': 'ABC1234',
            'nombres': 'Juan Pérez',
            'tipo_identificacion': 'cedula',
            'cedula': '0912345678',
            'correo': 'juan@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EP-001-2025',
            'vigencia': vigencia
        }
        
        form = FormularioCompletoQRForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('vigencia', form.errors)


class BusquedaAutorizacionFormTest(TestCase):
    """Tests para BusquedaAutorizacionForm"""
    
    def test_form_valido(self):
        """Test formulario de búsqueda válido"""
        form_data = {
            'tipo_busqueda': 'placa',
            'termino_busqueda': 'ABC1234',
            'solo_activas': True
        }
        
        form = BusquedaAutorizacionForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_todos_los_tipos_busqueda(self):
        """Test todos los tipos de búsqueda"""
        tipos = ['placa', 'nombres', 'cedula', 'ruc', 'correo', 
                'telefono', 'numero_autorizacion', 'tipo_autorizacion']
        
        for tipo in tipos:
            form_data = {
                'tipo_busqueda': tipo,
                'termino_busqueda': 'test',
                'solo_activas': False
            }
            
            form = BusquedaAutorizacionForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Falló para tipo: {tipo}")


# ============================================================================
# TESTS DE UTILS
# ============================================================================

class UtilsTest(TestCase):
    """Tests para funciones de utils"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        self.usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez González',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        self.autorizacion = Autorizacion.objects.create(
            usuario=self.usuario,
            tipo_autorizacion=self.tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-DPOTTTM-016-2025-ACVIL',
            vigencia=timezone.now().date() + timedelta(days=365),
            creado_por=self.user
        )
    
    def test_generar_url_qr(self):
        """Test generación de URL para QR"""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'testserver'
        
        url_qr = generar_url_qr(self.autorizacion, request)
        
        self.assertIsNotNone(url_qr)
        self.assertIn('verificar-qr', url_qr)
        self.assertIn('p=ABC1234', url_qr)  # placa
        self.assertIn('n=Juan', url_qr)  # nombre (limitado)
        self.assertIn('ci=0912345678', url_qr)  # cédula
    
    def test_validar_autorizacion_caducada_vigente(self):
        """Test validación de autorización vigente"""
        vigencia = timezone.now().date() + timedelta(days=30)
        
        esta_caducada = validar_autorizacion_caducada(vigencia)
        
        self.assertFalse(esta_caducada)
    
    def test_validar_autorizacion_caducada_vencida(self):
        """Test validación de autorización caducada"""
        vigencia = timezone.now().date() - timedelta(days=10)
        
        esta_caducada = validar_autorizacion_caducada(vigencia)
        
        self.assertTrue(esta_caducada)
    
    def test_validar_autorizacion_caducada_hoy(self):
        """Test validación de autorización que caduca hoy"""
        vigencia = timezone.now().date()
        
        esta_caducada = validar_autorizacion_caducada(vigencia)
        
        # Caduca al día siguiente, por lo tanto HOY aún es válida
        self.assertFalse(esta_caducada)
    
    def test_crear_autorizacion_desde_form_usuario_nuevo(self):
        """Test crear autorización con usuario nuevo"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'nombres': 'María López',
            'cedula': '0923456789',
            'ruc': '0923456789001',
            'correo': 'maria@example.com',
            'telefono': '0998765432',
            'tipo_autorizacion': self.tipo_autorizacion,
            'placa': 'XYZ5678',
            'numero_autorizacion': 'ACT-EP-002-2025',
            'vigencia': vigencia
        }
        
        autorizacion, usuario_creado = crear_autorizacion_desde_form(
            form_data, 
            self.user
        )
        
        self.assertTrue(usuario_creado)
        self.assertEqual(autorizacion.placa, 'XYZ5678')
        self.assertEqual(autorizacion.usuario.nombres, 'María López')
        self.assertEqual(autorizacion.creado_por, self.user)
    
    def test_crear_autorizacion_desde_form_usuario_existente(self):
        """Test crear autorización con usuario existente"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        form_data = {
            'nombres': 'Juan Pérez',
            'cedula': '0912345678',  # Usuario existente
            'correo': 'juan@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion,
            'placa': 'DEF9012',
            'numero_autorizacion': 'ACT-EP-003-2025',
            'vigencia': vigencia
        }
        
        autorizacion, usuario_creado = crear_autorizacion_desde_form(
            form_data, 
            self.user
        )
        
        self.assertFalse(usuario_creado)
        self.assertEqual(autorizacion.usuario, self.usuario)
        self.assertEqual(autorizacion.placa, 'DEF9012')


# ============================================================================
# TESTS DE VISTAS
# ============================================================================

class GenerarQRViewTest(TestCase):
    """Tests para la vista de generación de QR"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_get_generar_qr_view(self):
        """Test GET a la vista de generar QR"""
        response = self.client.get(reverse('formulario:generar_qr'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/generar_qr.html')
        self.assertIn('form', response.context)
    
    def test_post_generar_qr_valido(self):
        """Test POST válido para generar QR"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        post_data = {
            'placa': 'TEST123',
            'nombres': 'Usuario Test',
            'tipo_identificacion': 'cedula',
            'cedula': '0945678901',
            'correo': 'test@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-TEST-001-2025',
            'vigencia': vigencia
        }
        
        response = self.client.post(
            reverse('formulario:generar_qr'),
            data=post_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó la autorización
        autorizacion = Autorizacion.objects.filter(
            placa='TEST123'
        ).first()
        
        self.assertIsNotNone(autorizacion)
        self.assertTrue(autorizacion.qr_generado)
        self.assertIsNotNone(autorizacion.codigo_qr)
    
    def test_post_generar_qr_sin_login(self):
        """Test POST sin estar autenticado"""
        self.client.logout()
        
        vigencia = timezone.now().date() + timedelta(days=365)
        
        post_data = {
            'placa': 'TEST123',
            'nombres': 'Usuario Test',
            'tipo_identificacion': 'cedula',
            'cedula': '0945678901',
            'correo': 'test@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-TEST-001-2025',
            'vigencia': vigencia
        }
        
        response = self.client.post(
            reverse('formulario:generar_qr'),
            data=post_data
        )
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class VerificarQRViewTest(TestCase):
    """Tests para la vista de verificación de QR"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        self.autorizacion = Autorizacion.objects.create(
            usuario=usuario,
            tipo_autorizacion=tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=timezone.now().date() + timedelta(days=365),
            creado_por=self.user
        )
    
    def test_verificar_qr_autorizacion_valida(self):
        """Test verificar QR con autorización válida"""
        url = reverse('formulario:verificar_qr')
        params = {
            'p': self.autorizacion.placa,
            'n': self.autorizacion.usuario.nombres,
            'a': self.autorizacion.numero_autorizacion,
            'c': self.autorizacion.vigencia.isoformat(),
            'ci': self.autorizacion.usuario.cedula,
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/verificar_qr.html')
        self.assertIn('autorizacion_data', response.context)
        self.assertIn('✅', response.context['mensaje'])
    
    def test_verificar_qr_autorizacion_caducada(self):
        """Test verificar QR con autorización caducada"""
        # Crear autorización caducada
        autorizacion_caducada = Autorizacion.objects.create(
            usuario=self.autorizacion.usuario,
            tipo_autorizacion=self.autorizacion.tipo_autorizacion,
            placa='XYZ5678',
            numero_autorizacion='ACT-EP-002-2025',
            vigencia=timezone.now().date() - timedelta(days=30),
            creado_por=self.user
        )
        
        url = reverse('formulario:verificar_qr')
        params = {
            'p': autorizacion_caducada.placa,
            'n': autorizacion_caducada.usuario.nombres,
            'a': autorizacion_caducada.numero_autorizacion,
            'c': autorizacion_caducada.vigencia.isoformat(),
            'ci': autorizacion_caducada.usuario.cedula,
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('⚠️', response.context['mensaje'])
        self.assertTrue(response.context['esta_caducada'])
    
    def test_verificar_qr_datos_incompletos(self):
        """Test verificar QR con datos incompletos"""
        url = reverse('formulario:verificar_qr')
        params = {
            'p': 'ABC1234',
            # Faltan otros parámetros
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('❌', response.context['mensaje'])


class AutorizacionListViewTest(TestCase):
    """Tests para la vista de lista de autorizaciones"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        # Crear varias autorizaciones
        for i in range(5):
            Autorizacion.objects.create(
                usuario=usuario,
                tipo_autorizacion=tipo_autorizacion,
                placa=f'ABC{i}234',
                numero_autorizacion=f'ACT-EP-00{i}-2025',
                vigencia=timezone.now().date() + timedelta(days=365),
                creado_por=self.user
            )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_get_lista_autorizaciones(self):
        """Test GET a lista de autorizaciones"""
        response = self.client.get(reverse('formulario:autorizacion_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/autorizacion_list.html')
        self.assertIn('autorizaciones', response.context)
        self.assertEqual(len(response.context['autorizaciones']), 5)
    
    def test_busqueda_por_placa(self):
        """Test búsqueda de autorizaciones por placa"""
        response = self.client.get(
            reverse('formulario:autorizacion_list'),
            {
                'tipo_busqueda': 'placa',
                'termino_busqueda': 'ABC1234',
                'solo_activas': 'on'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        autorizaciones = response.context['autorizaciones']
        self.assertEqual(len(autorizaciones), 1)
        self.assertEqual(autorizaciones[0].placa, 'ABC1234')
    
    def test_busqueda_por_numero_autorizacion(self):
        """Test búsqueda por número de autorización"""
        response = self.client.get(
            reverse('formulario:autorizacion_list'),
            {
                'tipo_busqueda': 'numero_autorizacion',
                'termino_busqueda': 'ACT-EP-002-2025',
                'solo_activas': 'on'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        autorizaciones = response.context['autorizaciones']
        self.assertEqual(len(autorizaciones), 1)
        self.assertEqual(
            autorizaciones[0].numero_autorizacion,
            'ACT-EP-002-2025'
        )
    
    def test_lista_sin_login(self):
        """Test acceso a lista sin login"""
        self.client.logout()
        
        response = self.client.get(reverse('formulario:autorizacion_list'))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class AutorizacionDetailViewTest(TestCase):
    """Tests para la vista de detalle de autorización"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        self.autorizacion = Autorizacion.objects.create(
            usuario=usuario,
            tipo_autorizacion=tipo_autorizacion,
            placa='ABC1234',
            numero_autorizacion='ACT-EP-001-2025',
            vigencia=timezone.now().date() + timedelta(days=365),
            creado_por=self.user
        )
        
        # Crear historial
        HistorialAutorizacion.objects.create(
            autorizacion=self.autorizacion,
            accion='GENERAR_QR',
            descripcion='QR generado',
            creado_por=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_get_detalle_autorizacion(self):
        """Test GET a detalle de autorización"""
        response = self.client.get(
            reverse(
                'formulario:autorizacion_detail',
                kwargs={'pk': self.autorizacion.pk}
            )
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/autorizacion_detail.html')
        self.assertEqual(
            response.context['autorizacion'],
            self.autorizacion
        )
        self.assertIn('historial', response.context)
        self.assertEqual(len(response.context['historial']), 1)


class UsuarioAutorizacionListViewTest(TestCase):
    """Tests para la vista de lista de usuarios"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear varios usuarios
        for i in range(3):
            UsuarioAutorizacion.objects.create(
                nombres=f'Usuario {i}',
                cedula=f'091234567{i}',
                correo=f'usuario{i}@example.com',
                telefono=f'098765432{i}',
                creado_por=self.user
            )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_get_lista_usuarios(self):
        """Test GET a lista de usuarios"""
        response = self.client.get(reverse('formulario:usuario_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/usuarioautorizacion_list.html')
        self.assertEqual(len(response.context['usuarios']), 3)
    
    def test_busqueda_usuario_por_nombres(self):
        """Test búsqueda de usuario por nombres"""
        response = self.client.get(
            reverse('formulario:usuario_list'),
            {'search': 'Usuario 1'}
        )
        
        self.assertEqual(response.status_code, 200)
        usuarios = response.context['usuarios']
        self.assertEqual(len(usuarios), 1)
        self.assertIn('Usuario 1', usuarios[0].nombres)
    
    def test_busqueda_usuario_por_cedula(self):
        """Test búsqueda de usuario por cédula"""
        response = self.client.get(
            reverse('formulario:usuario_list'),
            {'search': '0912345671'}
        )
        
        self.assertEqual(response.status_code, 200)
        usuarios = response.context['usuarios']
        self.assertEqual(len(usuarios), 1)


class DashboardViewTest(TestCase):
    """Tests para la vista del dashboard"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        # Crear autorizaciones activas
        for i in range(3):
            Autorizacion.objects.create(
                usuario=usuario,
                tipo_autorizacion=tipo_autorizacion,
                placa=f'ABC{i}234',
                numero_autorizacion=f'ACT-EP-00{i}-2025',
                vigencia=timezone.now().date() + timedelta(days=365),
                creado_por=self.user
            )
        
        # Crear autorizaciones caducadas
        for i in range(2):
            Autorizacion.objects.create(
                usuario=usuario,
                tipo_autorizacion=tipo_autorizacion,
                placa=f'XYZ{i}567',
                numero_autorizacion=f'ACT-EP-10{i}-2024',
                vigencia=timezone.now().date() - timedelta(days=30),
                creado_por=self.user
            )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_get_dashboard(self):
        """Test GET al dashboard"""
        response = self.client.get(reverse('formulario:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/dashboard.html')
        
        # Verificar estadísticas
        self.assertEqual(response.context['total_autorizaciones'], 5)
        self.assertEqual(response.context['autorizaciones_activas'], 5)
        self.assertEqual(response.context['autorizaciones_caducadas'], 2)
        self.assertEqual(response.context['total_usuarios'], 1)


# ============================================================================
# TESTS DE INTEGRACIÓN
# ============================================================================

class IntegracionGenerarQRTest(TestCase):
    """Tests de integración para el flujo completo de generación de QR"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tipo_autorizacion = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_flujo_completo_generacion_qr(self):
        """Test del flujo completo: crear usuario, autorización y generar QR"""
        vigencia = timezone.now().date() + timedelta(days=365)
        
        # Paso 1: Generar QR (crea usuario y autorización)
        post_data = {
            'placa': 'INTEG01',
            'nombres': 'Usuario Integración',
            'tipo_identificacion': 'cedula',
            'cedula': '0956789012',
            'correo': 'integracion@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-INTEG-001-2025',
            'vigencia': vigencia
        }
        
        response = self.client.post(
            reverse('formulario:generar_qr'),
            data=post_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se creó el usuario
        usuario = UsuarioAutorizacion.objects.filter(
            cedula='0956789012'
        ).first()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.nombres, 'Usuario Integración')
        
        # Verificar que se creó la autorización
        autorizacion = Autorizacion.objects.filter(
            placa='INTEG01'
        ).first()
        self.assertIsNotNone(autorizacion)
        self.assertTrue(autorizacion.qr_generado)
        self.assertIsNotNone(autorizacion.codigo_qr)
        
        # Verificar que se creó el historial
        historial = HistorialAutorizacion.objects.filter(
            autorizacion=autorizacion,
            accion='GENERAR_QR'
        ).first()
        self.assertIsNotNone(historial)
        
        # Paso 2: Verificar el QR
        url_verificar = reverse('formulario:verificar_qr')
        params = {
            'p': autorizacion.placa,
            'n': autorizacion.usuario.nombres,
            'a': autorizacion.numero_autorizacion,
            'c': autorizacion.vigencia.isoformat(),
            'ci': autorizacion.usuario.cedula,
        }
        
        response_verificar = self.client.get(url_verificar, params)
        
        self.assertEqual(response_verificar.status_code, 200)
        self.assertIn('autorizacion_data', response_verificar.context)
        self.assertFalse(response_verificar.context['esta_caducada'])
    
    def test_flujo_usuario_existente_nueva_autorizacion(self):
        """Test crear nueva autorización para usuario existente"""
        # Crear usuario
        usuario = UsuarioAutorizacion.objects.create(
            nombres='Usuario Existente',
            cedula='0967890123',
            correo='existente@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        vigencia = timezone.now().date() + timedelta(days=365)
        
        # Crear primera autorización
        post_data_1 = {
            'placa': 'EXIST01',
            'nombres': 'Usuario Existente',
            'tipo_identificacion': 'cedula',
            'cedula': '0967890123',
            'correo': 'existente@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EXIST-001-2025',
            'vigencia': vigencia
        }
        
        response_1 = self.client.post(
            reverse('formulario:generar_qr'),
            data=post_data_1
        )
        
        # Crear segunda autorización para el mismo usuario
        post_data_2 = {
            'placa': 'EXIST02',
            'nombres': 'Usuario Existente',
            'tipo_identificacion': 'cedula',
            'cedula': '0967890123',  # Misma cédula
            'correo': 'existente@example.com',
            'telefono': '0987654321',
            'tipo_autorizacion': self.tipo_autorizacion.id,
            'numero_autorizacion': 'ACT-EXIST-002-2025',
            'vigencia': vigencia
        }
        
        response_2 = self.client.post(
            reverse('formulario:generar_qr'),
            data=post_data_2
        )
        
        # Verificar que solo hay un usuario
        usuarios = UsuarioAutorizacion.objects.filter(
            cedula='0967890123'
        )
        self.assertEqual(usuarios.count(), 1)
        
        # Verificar que hay dos autorizaciones
        autorizaciones = Autorizacion.objects.filter(
            usuario=usuario
        )
        self.assertEqual(autorizaciones.count(), 2)


class IntegracionBusquedaFiltroTest(TestCase):
    """Tests de integración para búsqueda y filtros"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.tipo_autorizacion_1 = TipoAutorizacion.objects.create(
            codigo='TRAN',
            nombre='Transporte',
            creado_por=self.user
        )
        
        self.tipo_autorizacion_2 = TipoAutorizacion.objects.create(
            codigo='CARG',
            nombre='Carga',
            creado_por=self.user
        )
        
        # Crear usuarios y autorizaciones de prueba
        usuario_1 = UsuarioAutorizacion.objects.create(
            nombres='Juan Pérez',
            cedula='0912345678',
            correo='juan@example.com',
            telefono='0987654321',
            creado_por=self.user
        )
        
        usuario_2 = UsuarioAutorizacion.objects.create(
            nombres='María López',
            cedula='0923456789',
            correo='maria@example.com',
            telefono='0998765432',
            creado_por=self.user
        )
        
        # Autorizaciones de transporte
        Autorizacion.objects.create(
            usuario=usuario_1,
            tipo_autorizacion=self.tipo_autorizacion_1,
            placa='ABC1234',
            numero_autorizacion='ACT-TRAN-001-2025',
            vigencia=timezone.now().date() + timedelta(days=365),
            creado_por=self.user
        )
        
        # Autorizaciones de carga
        Autorizacion.objects.create(
            usuario=usuario_2,
            tipo_autorizacion=self.tipo_autorizacion_2,
            placa='XYZ5678',
            numero_autorizacion='ACT-CARG-001-2025',
            vigencia=timezone.now().date() + timedelta(days=180),
            creado_por=self.user
        )
        
        # Autorización caducada
        Autorizacion.objects.create(
            usuario=usuario_1,
            tipo_autorizacion=self.tipo_autorizacion_1,
            placa='OLD9012',
            numero_autorizacion='ACT-TRAN-002-2024',
            vigencia=timezone.now().date() - timedelta(days=30),
            creado_por=self.user
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_filtro_por_tipo_autorizacion(self):
        """Test filtrar autorizaciones por tipo"""
        response = self.client.get(
            reverse('formulario:autorizacion_list'),
            {
                'tipo_autorizacion': self.tipo_autorizacion_1.id
            }
        )
        
        autorizaciones = list(response.context['autorizaciones'])
        self.assertEqual(len(autorizaciones), 2)
        for auth in autorizaciones:
            self.assertEqual(
                auth.tipo_autorizacion,
                self.tipo_autorizacion_1
            )
    
    def test_filtro_estado_caducadas(self):
        """Test filtrar solo autorizaciones caducadas"""
        response = self.client.get(
            reverse('formulario:autorizacion_list'),
            {
                'estado': 'caducadas'
            }
        )
        
        autorizaciones = list(response.context['autorizaciones'])
        self.assertEqual(len(autorizaciones), 1)
        self.assertTrue(autorizaciones[0].esta_caducada)
    
    def test_busqueda_combinada(self):
        """Test búsqueda por placa combinada con filtros"""
        response = self.client.get(
            reverse('formulario:autorizacion_list'),
            {
                'tipo_busqueda': 'placa',
                'termino_busqueda': 'ABC',
                'solo_activas': 'on'
            }
        )
        
        autorizaciones = list(response.context['autorizaciones'])
        self.assertEqual(len(autorizaciones), 1)
        self.assertEqual(autorizaciones[0].placa, 'ABC1234')


# ============================================================================
# TEST RUNNER PERSONALIZADO (OPCIONAL)
# ============================================================================

def run_specific_tests():
    """
    Función helper para ejecutar tests específicos
    Uso: python manage.py shell < test_script.py
    """
    import sys
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Ejecutar solo tests de modelos
    failures = test_runner.run_tests([
        "apps.formulario.tests.TipoAutorizacionModelTest",
        "apps.formulario.tests.UsuarioAutorizacionModelTest",
        "apps.formulario.tests.AutorizacionModelTest",
    ])
    
    sys.exit(bool(failures))