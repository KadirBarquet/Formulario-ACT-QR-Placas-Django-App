from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.formulario.models import UsuarioAutorizacion, Autorizacion, TipoAutorizacion

class TipoIdentificacionForm(forms.Form):
    """Form para el tipo de identificación"""
    TIPO_IDENTIFICACION_CHOICES = [
        ('', 'Seleccione...'),
        ('cedula', 'Cédula'),
        ('ruc', 'RUC'),
        ('ambos', 'Ambos'),
    ]
    
    tipo_identificacion = forms.ChoiceField(
        choices=TIPO_IDENTIFICACION_CHOICES,
        required=True,
        label='Tipo de identificación'
    )

class UsuarioAutorizacionForm(forms.ModelForm):
    """Form para los datos del usuario"""
    placa = forms.CharField(
        max_length=20,
        required=True,
        label='Placa',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: OBM0979-ABC1234',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = UsuarioAutorizacion
        fields = ['nombres', 'cedula', 'ruc', 'correo', 'telefono']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'placeholder': 'Nombres completos',
                'class': 'form-control',
                'required': 'required'
            }),
            'cedula': forms.TextInput(attrs={
                'placeholder': 'Cédula (10 dígitos)',
                'class': 'form-control',
                'pattern': '^09\d{10}$',
                'title': 'La cédula debe comenzar con 09 y tener 10 dígitos'
            }),
            'ruc': forms.TextInput(attrs={
                'placeholder': 'RUC (13 dígitos)',
                'class': 'form-control',
                'pattern': '^\d{13}$',
                'title': 'El RUC debe tener 13 dígitos'
            }),
            'correo': forms.EmailInput(attrs={
                'placeholder': 'Correo electrónico',
                'class': 'form-control',
                'required': 'required'
            }),
            'telefono': forms.TextInput(attrs={
                'placeholder': 'Teléfono',
                'class': 'form-control',
                'pattern': '^09\d{10}$',
                'title': 'El teléfono debe comenzar con 09 y tener 10 dígitos',
                'required': 'required'
            }),
        }
        labels = {
            'nombres': 'Nombres',
            'cedula': 'Cédula',
            'ruc': 'RUC',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono',
        }

class AutorizacionForm(forms.ModelForm):
    """Form para los datos de la autorización"""
    tipo_autorizacion_personalizado = forms.CharField(
        max_length=50,
        required=False,
        label='Especifique el tipo de autorización',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el tipo de autorización',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Autorizacion
        fields = ['tipo_autorizacion', 'numero_autorizacion', 'vigencia']
        widgets = {
            'tipo_autorizacion': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
                'onchange': 'mostrarInputAutorizacion()'
            }),
            'numero_autorizacion': forms.TextInput(attrs={
                'placeholder': 'Ej: ACT-EP-DPOTTTM-016-2025-ACVIL',
                'class': 'form-control',
                'maxlength': '30',
                'required': 'required'
            }),
            'vigencia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
        }
        labels = {
            'tipo_autorizacion': 'Tipo de Autorización',
            'numero_autorizacion': 'Número de Autorización',
            'vigencia': 'Vigencia',
        }

class FormularioCompletoQRForm(forms.Form):
    """Formulario completo para generar QR - Combina todos los forms"""
    
    # Información del vehículo
    placa = forms.CharField(
        max_length=20,
        required=True,
        label='Placa',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: OBM0979-ABC1234',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    # Información personal
    nombres = forms.CharField(
        max_length=100,
        required=True,
        label='Nombres',
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombres completos',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    # Tipo de identificación
    TIPO_IDENTIFICACION_CHOICES = [
        ('', 'Seleccione...'),
        ('cedula', 'Cédula'),
        ('ruc', 'RUC'),
        ('ambos', 'Ambos'),
    ]
    
    tipo_identificacion = forms.ChoiceField(
        choices=TIPO_IDENTIFICACION_CHOICES,
        required=True,
        label='Tipo de identificación',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required',
            'onchange': 'mostrarInputID()'
        })
    )
    
    cedula = forms.CharField(
        max_length=10,
        required=False,  # ← Hacer opcional, se valida en clean()
        label='Cédula (10 dígitos)',
        validators=[  # ← AÑADIR validadores aquí también
            RegexValidator(
                regex=r'^09\d{10}$',
                message='La cédula debe comenzar con 09 y tener 10 dígitos'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 0956305672',
            'class': 'form-control',
            'pattern': '^09\d{10}$',
            'title': 'La cédula debe comenzar con 09 y tener 10 dígitos'
        })
    )
    
    ruc = forms.CharField(
        max_length=13,
        required=False,  # ← Hacer opcional, se valida en clean()
        label='RUC (13 dígitos)',
        validators=[  # ← AÑADIR validadores aquí también
            RegexValidator(
                regex=r'^\d{13}$',
                message='El RUC debe tener 13 dígitos'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 1234567890123',
            'class': 'form-control',
            'pattern': '^\d{13}$',
            'title': 'El RUC debe tener 13 dígitos'
        })
    )
    
    # Contacto
    correo = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo electrónico',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    telefono = forms.CharField(
        max_length=10,
        required=True,
        label='Teléfono',
        validators=[
            RegexValidator(
                regex=r'^09\d{10}$',
                message='El teléfono debe comenzar con 09 y tener 10 dígitos'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Teléfono',
            'class': 'form-control',
            'pattern': '^09\d{10}$',
            'title': 'El teléfono debe comenzar con 09 y tener 10 dígitos',
            'required': 'required'
        })
    )
    
    # Autorización
    tipo_autorizacion = forms.ModelChoiceField(
        queryset=TipoAutorizacion.objects.filter(activo=True),
        required=True,
        label='Tipo de Autorización',
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required',
            'onchange': 'mostrarInputAutorizacion()'
        })
    )
    
    tipo_autorizacion_otro = forms.CharField(
        max_length=50,
        required=False,
        label='Especifique el tipo de autorización',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el tipo de autorización',
            'class': 'form-control'
        })
    )
    
    numero_autorizacion = forms.CharField(
        max_length=30,
        required=True,
        label='Número de Autorización',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: ACT-EP-DPOTTTM-016-2025-ACVIL',
            'class': 'form-control',
            'maxlength': '30',
            'required': 'required'
        })
    )
    
    vigencia = forms.DateField(
        required=True,
        label='Vigencia',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_identificacion = cleaned_data.get('tipo_identificacion')
        cedula = cleaned_data.get('cedula', '').strip()
        ruc = cleaned_data.get('ruc', '').strip()
        
        # Validaciones de identificación
        if tipo_identificacion == 'cedula':
            if not cedula:
                raise forms.ValidationError({
                    'cedula': 'La cédula es requerida para este tipo de identificación'
                })
            # Validar formato de cédula
            if cedula and (len(cedula) != 10 or not cedula.startswith('09')):
                raise forms.ValidationError({
                    'cedula': 'La cédula debe comenzar con 09 y tener exactamente 10 dígitos'
                })
        
        elif tipo_identificacion == 'ruc':
            if not ruc:
                raise forms.ValidationError({
                    'ruc': 'El RUC es requerido para este tipo de identificación'
                })
            # Validar formato de RUC
            if ruc and (len(ruc) != 13 or not ruc.isdigit()):
                raise forms.ValidationError({
                    'ruc': 'El RUC debe tener exactamente 13 dígitos numéricos'
                })
        
        elif tipo_identificacion == 'ambos':
            if not cedula or not ruc:
                raise forms.ValidationError({
                    'cedula': 'Ambos campos de identificación son requeridos',
                    'ruc': 'Ambos campos de identificación son requeridos'
                })
            # Validar formatos
            if cedula and (len(cedula) != 10 or not cedula.startswith('09')):
                raise forms.ValidationError({
                    'cedula': 'La cédula debe comenzar con 09 y tener exactamente 10 dígitos'
                })
            if ruc and (len(ruc) != 13 or not ruc.isdigit()):
                raise forms.ValidationError({
                    'ruc': 'El RUC debe tener exactamente 13 dígitos numéricos'
                })
        
        # Validar que al menos un campo de identificación tenga valor
        if not cedula and not ruc:
            raise forms.ValidationError(
                'Debe proporcionar al menos una cédula o RUC.'
            )
        
        return cleaned_data
    
    def clean_cedula(self):
        """Validación específica para cédula"""
        cedula = self.cleaned_data.get('cedula', '').strip()
        if cedula:
            # Remover espacios y validar formato
            cedula = cedula.replace(' ', '')
            if len(cedula) != 10:
                raise forms.ValidationError('La cédula debe tener exactamente 10 dígitos')
            if not cedula.startswith('09'):
                raise forms.ValidationError('La cédula debe comenzar con 09')
            if not cedula.isdigit():
                raise forms.ValidationError('La cédula debe contener solo números')
        return cedula
    
    def clean_ruc(self):
        """Validación específica para RUC"""
        ruc = self.cleaned_data.get('ruc', '').strip()
        if ruc:
            # Remover espacios y validar formato
            ruc = ruc.replace(' ', '')
            if len(ruc) != 13:
                raise forms.ValidationError('El RUC debe tener exactamente 13 dígitos')
            if not ruc.isdigit():
                raise forms.ValidationError('El RUC debe contener solo números')
        return ruc
    
    def clean_vigencia(self):
        vigencia = self.cleaned_data.get('vigencia')
        if vigencia:
            from django.utils import timezone
            hoy = timezone.now().date()
            if vigencia < hoy:
                raise forms.ValidationError('La fecha de vigencia no puede ser anterior a la fecha actual.')
        return vigencia

class BusquedaAutorizacionForm(forms.Form):
    """Form para buscar autorizaciones en el CRUD"""
    TIPO_BUSQUEDA_CHOICES = [
        ('placa', 'Placa'),
        ('nombres', 'Nombres'),
        ('cedula', 'Cédula'),
        ('ruc', 'RUC'),
        ('correo', 'Correo'),
        ('telefono', 'Teléfono'),
        ('numero_autorizacion', 'Número de Autorización'),
        ('tipo_autorizacion', 'Tipo de Autorización'),
    ]
    
    tipo_busqueda = forms.ChoiceField(
        choices=TIPO_BUSQUEDA_CHOICES,
        required=True,
        label='Buscar por',
        initial='placa',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    termino_busqueda = forms.CharField(
        required=True,
        label='Término de búsqueda',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el término de búsqueda...',
            'class': 'form-control'
        })
    )
    
    solo_activas = forms.BooleanField(
        required=False,
        initial=True,
        label='Solo autorizaciones activas',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class FiltroAutorizacionForm(forms.Form):
    """Form para filtrar autorizaciones"""
    tipo_autorizacion = forms.ModelChoiceField(
        queryset=TipoAutorizacion.objects.filter(activo=True),
        required=False,
        label='Tipo de Autorización',
        empty_label='Todos los tipos',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    estado = forms.ChoiceField(
        choices=[
            ('', 'Todos los estados'),
            ('activas', 'Solo activas'),
            ('caducadas', 'Solo caducadas'),
            ('inactivas', 'Solo inactivas'),
        ],
        required=False,
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        label='Desde',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        label='Hasta',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )