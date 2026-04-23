"""Asynchronous tasks for document handling (Celery-friendly).
This module provides an async task that performs virus scanning and post-upload processing.
If Celery is available and configured, a Celery task will be registered; otherwise a synchronous helper is exposed.
"""
from django.conf import settings
from documents.utils import scan_file
import logging

logger = logging.getLogger(__name__)

# Try to import Celery app and register a task if available
try:
    from riman_erp.celery import app  # type: ignore
    CELERY_AVAILABLE = True
except Exception:
    app = None
    CELERY_AVAILABLE = False


def _scan_and_log(template_obj, task_id=None, scanned_by='worker'):
    """Helper to scan the file, log results, update template status, and persist a scan log.
    Returns (clean, reason)"""
    f = template_obj.template_file
    # Ensure file at pointer start
    try:
        if hasattr(f, 'seek'):
            f.open()
            f.seek(0)
    except Exception:
        pass

    clean, reason = scan_file(f)

    # Update template status and create a scan log
    try:
        from .models import TemplateScanLog
        from core.models import CompanySettings
        from django.conf import settings as djsettings

        if clean:
            template_obj.scan_status = 'clean'
            logger.info('Template %s scanned clean', template_obj.slug)
            result = 'clean'
        else:
            template_obj.scan_status = 'infected'
            logger.warning('Template %s failed scan: %s', template_obj.slug, reason)
            result = 'infected'

        # Determine quarantine policy (company override if present else global setting)
        try:
            company = CompanySettings.objects.first()
            auto_quarantine = company.auto_quarantine if company is not None else djsettings.DOCUMENTS_AUTO_QUARANTINE
        except Exception:
            auto_quarantine = djsettings.DOCUMENTS_AUTO_QUARANTINE

        if result == 'infected' and auto_quarantine:
            try:
                template_obj.is_active = False
                template_obj.quarantine_reason = (reason or '')[:2000]
                template_obj.save(update_fields=['scan_status', 'is_active', 'quarantine_reason'])
            except Exception:
                # If save of active flag fails, at least set status and quarantine reason
                try:
                    template_obj.quarantine_reason = (reason or '')[:2000]
                    template_obj.save(update_fields=['scan_status', 'quarantine_reason'])
                except Exception:
                    template_obj.save(update_fields=['scan_status'])
        else:
            template_obj.save(update_fields=['scan_status'])

        # Create scan log
        TemplateScanLog.objects.create(
            template=template_obj,
            result=result,
            reason=(reason or '')[:2000],
            task_id=(task_id or '')[:255],
            scanned_by=str(scanned_by)[:255]
        )
        # Notify admins if infected
        if result == 'infected':
            try:
                from django.core.mail import send_mail
                recipients = []
                if company and company.email:
                    recipients.append(company.email)
                # Add Django ADMINS emails
                try:
                    recipients += [email for _, email in getattr(djsettings, 'ADMINS', []) if email]
                except Exception:
                    pass

                subject = f"[RIMAN ERP] Infected template detected: {template_obj.name}"
                message = f"Template '{template_obj.name}' (slug={template_obj.slug}) was marked infected during a virus scan.\nReason: {reason or 'unknown'}.\nTask: {task_id or 'N/A'}"
                from_email = getattr(djsettings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
                if recipients:
                    send_mail(subject, message, from_email, recipients, fail_silently=True)
                else:
                    logger.warning('No admin recipients configured to notify about infected template %s', template_obj.slug)
            except Exception:
                logger.exception('Failed to notify admins about infected template %s', template_obj.slug)

    except Exception:
        logger.exception('Failed to record scan result for template %s', template_obj.slug)

    return clean, reason


if CELERY_AVAILABLE:
    @app.task(bind=True)
    def scan_uploaded_template(self, template_pk):
        """Celery task to scan an uploaded template identified by pk"""
        from documents.models import DocumentTemplate
        try:
            template = DocumentTemplate.objects.get(pk=template_pk)
        except DocumentTemplate.DoesNotExist:
            logger.error('Template with pk %s not found for scanning', template_pk)
            return False, 'not_found'
        # Attempt to pass task id for logging
        task_id = None
        try:
            task_id = getattr(self.request, 'id', None)
        except Exception:
            task_id = None
        return _scan_and_log(template, task_id=task_id, scanned_by='celery')

else:
    # Provide a no-op or synchronous function for environments without Celery
    def scan_uploaded_template(template_pk_or_obj):
        """Synchronous wrapper used when Celery is not available.
        Accepts either a template instance or its pk.
        """
        from documents.models import DocumentTemplate
        if hasattr(template_pk_or_obj, 'pk'):
            template = template_pk_or_obj
            return _scan_and_log(template, task_id=None, scanned_by='sync')
        try:
            template = DocumentTemplate.objects.get(pk=template_pk_or_obj)
        except DocumentTemplate.DoesNotExist:
            logger.error('Template with pk %s not found for scanning', template_pk_or_obj)
            return False, 'not_found'
        return _scan_and_log(template, task_id=None, scanned_by='sync')
