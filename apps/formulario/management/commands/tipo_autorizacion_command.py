from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.formulario.models import TipoAutorizacion

class Command(BaseCommand):
    help = 'Inserta tipos de autorización en la base de datos'

    def handle(self, *args, **kwargs):
        # Definir los datos de tipos de autorización
        tipos_autorizacion = [
            {
                'codigo': 'AUT-001',
                'nombre': 'Estacionamiento Liviano',
                'descripcion': 'Autorización de Estacionamiento Liviano'
            },
            {
                'codigo': 'AUT-002',
                'nombre': 'Estacionamiento Pesado',
                'descripcion': 'Autorización de Estacionamiento Pesado'
            },
            {
                'codigo': 'AUT-003',
                'nombre': 'Carga y Descarga Liviana',
                'descripcion': 'Autorización de Carga y Descarga Liviana'
            },
            {
                'codigo': 'AUT-004',
                'nombre': 'Carga y Descarga Pesada',
                'descripcion': 'Autorización de Carga y Descarga Pesada'
            },
            {
                'codigo': 'AUT-005',
                'nombre': 'Circulación Pesada',
                'descripcion': 'Autorización de Circulación Pesada'
            },
            {
                'codigo': 'AUT-006',
                'nombre': 'Circulación Liviana',
                'descripcion': 'Autorización de Circulación Liviana'
            },
            {
                'codigo': 'AUT-007',
                'nombre': 'Circulación Escolar Pesado',
                'descripcion': 'Autorización de Circulación Escolar Pesado'
            },
            {
                'codigo': 'AUT-008',
                'nombre': 'Circulación Escolar Liviano',
                'descripcion': 'Autorización de Circulación Escolar Liviano'
            },
        ]
        
        # Contar tipos existentes antes de insertar
        tipos_existentes_antes = TipoAutorizacion.objects.count()
        
        # Lista para almacenar los nuevos tipos insertados
        nuevos_insertados = []
        ya_existentes = []
        
        # Insertar tipos de autorización
        for tipo_data in tipos_autorizacion:
            tipo, creado = TipoAutorizacion.objects.get_or_create(
                codigo=tipo_data['codigo'],
                defaults={
                    'nombre': tipo_data['nombre'],
                    'descripcion': tipo_data['descripcion'],
                    'activo': True
                }
            )
            
            if creado:
                nuevos_insertados.append(tipo)
            else:
                ya_existentes.append(tipo)
        
        # Contar tipos después de insertar
        tipos_existentes_despues = TipoAutorizacion.objects.count()
        
        # Calcular cantidad de nuevos insertados
        cantidad_nuevos = tipos_existentes_despues - tipos_existentes_antes
        
        # Mostrar resultado en consola
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        
        if cantidad_nuevos > 0:
            self.stdout.write(self.style.SUCCESS('NUEVOS TIPOS DE AUTORIZACIÓN INSERTADOS:'))
            self.stdout.write(self.style.SUCCESS('-'*60))
            
            for tipo in nuevos_insertados:
                self.stdout.write(self.style.SUCCESS(f'  • {tipo.nombre}'))
            
            self.stdout.write(self.style.SUCCESS('-'*60))
            self.stdout.write(self.style.SUCCESS(f'Se insertaron {cantidad_nuevos} nuevos tipos de autorización.\n'))
        else:
            self.stdout.write(self.style.WARNING('No se insertaron nuevos tipos de autorización.'))
            self.stdout.write(self.style.WARNING('(Todos los tipos ya existen en la base de datos)\n'))
        
        # Mostrar todos los tipos existentes
        self.stdout.write(self.style.SUCCESS('TIPOS DE AUTORIZACIÓN EN LA BASE DE DATOS:'))
        self.stdout.write(self.style.SUCCESS('-'*60))
        
        todos_tipos = TipoAutorizacion.objects.all().order_by('codigo')
        for tipo in todos_tipos:
            estado = '✓' if tipo.activo else '✗'
            self.stdout.write(self.style.SUCCESS(f'  [{estado}] {tipo.codigo} - {tipo.nombre}'))
        
        self.stdout.write(self.style.SUCCESS('-'*60))
        self.stdout.write(self.style.SUCCESS(f'Total de tipos de autorización: {todos_tipos.count()}\n'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))