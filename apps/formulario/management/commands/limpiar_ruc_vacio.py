from django.core.management.base import BaseCommand
from apps.formulario.models import UsuarioAutorizacion

class Command(BaseCommand):
    help = 'Limpia los registros con RUC vacío'

    def handle(self, *args, **kwargs):
        # Actualizar registros con RUC vacío a NULL
        usuarios = UsuarioAutorizacion.objects.filter(ruc='')
        count = usuarios.count()
        usuarios.update(ruc=None)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Se actualizaron {count} registros con RUC vacío a NULL'
            )
        )