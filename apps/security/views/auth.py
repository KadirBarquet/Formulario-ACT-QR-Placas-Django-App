from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import redirect

class AdminLoginView(LoginView):
    """Vista de login personalizada para administradores"""
    template_name = 'security/login.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Permitir login solo si el usuario es superusuario"""
        user = form.get_user()
        if not user.is_superuser:
            messages.error(self.request, 'Acceso denegado. Solo el administrador puede iniciar sesión.')
            return redirect('security:login')  # o redirige donde quieras
        
        messages.success(self.request, f'Bienvenido {user.get_full_name() or user.username}')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('formulario:inicio')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales inválidas. Por favor, intente nuevamente.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_date'] = timezone.now().strftime('%d/%m/%Y, %H:%M')
        return context

class AdminLogoutView(LogoutView):
    """Vista de logout personalizada"""
    next_page = reverse_lazy('security:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)