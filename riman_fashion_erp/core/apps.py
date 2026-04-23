from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Apply runtime monkeypatches to handle known compatibility issues
        try:
            from . import monkeypatch
            applied = monkeypatch.apply_basecontext_copy_patch()
            # Log patch application status for debugging startup issues
            try:
                import logging
                log = logging.getLogger(__name__)
                if applied:
                    log.info('Applied BaseContext.__copy__ monkeypatch')
                else:
                    log.info('BaseContext.__copy__ monkeypatch not required')
            except Exception:
                # Fallback to silent fail if logging is unavailable
                pass
        except Exception:
            # Avoid breaking startup if patch application fails
            pass
