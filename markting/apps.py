from django.apps import AppConfig


class MarktingConfig(AppConfig):
    name = 'markting'

    def ready(self):
        import markting.signals
