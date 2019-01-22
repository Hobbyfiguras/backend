from django.apps import AppConfig


class FiguresiteConfig(AppConfig):
    name = 'FigureSite'
    verbose_name = 'Hobbyfiguras'
    def ready(self):
        import FigureSite.signals.handlers