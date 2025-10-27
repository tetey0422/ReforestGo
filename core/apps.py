from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Reforest Go'

    def ready(self):
        # Importar señales o registrar comportamientos al arrancar
        # Importar aquí los módulos que registran señales para evitar import cycles
        try:
            import core.models
        except Exception:
            # Evitar que errores en imports impidan el arranque; se puede loguear si se desea
            pass