from django.apps import AppConfig


class RegistryConfig(AppConfig):
    name = 'registry'

    def ready(self):
        # noinspection unused,PyUnresolvedReferences
        import registry.signals
