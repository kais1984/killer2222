"""
Document Views: Contracts, Templates, and Documents Management
"""

from django.http import FileResponse, HttpResponse, JsonResponse
from django.views.generic import TemplateView, View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.conf import settings
from documents.contract_generator import ContractGenerator
from documents.models import DocumentTemplate, InvoiceTemplate, ContractTemplate, TemplateUsageLog
from documents.utils import detect_file_type, scan_file
import mimetypes
import os


class ContractListView(LoginRequiredMixin, TemplateView):
    """Display available contracts for download"""
    template_name = 'contracts/contract_list.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = [
            {
                'id': 'test_contract',
                'name': 'Test/Sample Contract',
                'description': 'Professional sample contract with demo data',
                'date': '2026-01-28',
                'type': 'Master Services Agreement',
            },
            {
                'id': 'rental_contract',
                'name': 'Rental Agreement Template',
                'description': 'Template for dress rental contracts',
                'date': '2026-01-28',
                'type': 'Rental Agreement',
            },
            {
                'id': 'custom_dress_contract',
                'name': 'Custom Dress Agreement',
                'description': 'Template for custom dress design & manufacturing',
                'date': '2026-01-28',
                'type': 'Service Agreement',
            },
        ]
        return context


class DownloadContractView(LoginRequiredMixin, View):
    """Download contract as PDF"""
    login_url = '/admin/login/'
    
    def get(self, request, contract_id):
        try:
            generator = ContractGenerator()
            
            # Generate appropriate contract
            if contract_id == 'test_contract':
                pdf_buffer = generator.generate_test_contract()
                filename = 'RIMAN_Fashion_Test_Contract.pdf'
            else:
                pdf_buffer = generator.generate_test_contract()
                filename = f'RIMAN_Fashion_{contract_id}.pdf'
            
            # Return PDF file
            response = FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=filename,
                content_type='application/pdf'
            )
            return response
            
        except Exception as e:
            return HttpResponse(
                f'Error generating contract: {str(e)}',
                status=500,
                content_type='text/plain'
            )


class ViewContractView(LoginRequiredMixin, TemplateView):
    """Display contract preview in browser"""
    template_name = 'contracts/contract_preview.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract_id = self.kwargs.get('contract_id', 'test_contract')
        
        context['contract_id'] = contract_id
        context['contract_name'] = {
            'test_contract': 'Test/Sample Contract',
            'rental_contract': 'Rental Agreement',
            'custom_dress_contract': 'Custom Dress Agreement',
        }.get(contract_id, 'Contract')
        
        context['contract_preview'] = True
        return context


# Template Management Views

class TemplateLibraryView(LoginRequiredMixin, TemplateView):
    """Display template library with all templates"""
    template_name = 'templates/template_library.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all active templates grouped by type
        context['invoice_templates'] = DocumentTemplate.objects.filter(
            template_type='invoice',
            is_active=True
        ).prefetch_related('invoice_template')
        
        context['contract_templates'] = DocumentTemplate.objects.filter(
            template_type='contract',
            is_active=True
        ).prefetch_related('contract_template')
        
        context['receipt_templates'] = DocumentTemplate.objects.filter(
            template_type='receipt',
            is_active=True
        )
        
        context['purchase_order_templates'] = DocumentTemplate.objects.filter(
            template_type='purchase_order',
            is_active=True
        )
        
        return context


class TemplateDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a specific template"""
    model = DocumentTemplate
    template_name = 'templates/template_detail.html'
    context_object_name = 'template'
    login_url = '/admin/login/'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.get_object()
        
        # Get specialized template if exists
        if template.template_type == 'invoice':
            try:
                context['invoice_config'] = template.invoice_template
            except:
                pass
        elif template.template_type == 'contract':
            try:
                context['contract_config'] = template.contract_template
            except:
                pass
        
        # Log this view
        TemplateUsageLog.objects.create(
            template=template,
            user=self.request.user,
            action='view'
        )
        
        return context


class TemplatePreviewView(LoginRequiredMixin, View):
    """Preview template as HTML"""
    login_url = '/admin/login/'
    
    def get(self, request, slug):
        template = get_object_or_404(DocumentTemplate, slug=slug, is_active=True)
        
        # Log usage
        TemplateUsageLog.objects.create(
            template=template,
            user=request.user,
            action='view'
        )
        
        # Return template content as HTML
        return HttpResponse(
            template.content,
            content_type='text/html'
        )


class TemplateDownloadView(LoginRequiredMixin, View):
    """Download template as file"""
    login_url = '/admin/login/'
    
    def get(self, request, slug):
        template = get_object_or_404(DocumentTemplate, slug=slug, is_active=True)
        
        # Log usage
        TemplateUsageLog.objects.create(
            template=template,
            user=request.user,
            action='download'
        )
        
        # Determine file format and return
        if template.template_type == 'invoice':
            filename = f"template_invoice_{template.slug}.html"
        elif template.template_type == 'contract':
            filename = f"template_contract_{template.slug}.html"
        else:
            filename = f"template_{template.slug}.html"
        
        response = HttpResponse(
            template.content,
            content_type='text/html'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class InvoiceTemplateListView(LoginRequiredMixin, ListView):
    """List all invoice templates"""
    model = DocumentTemplate
    template_name = 'templates/invoice_templates.html'
    context_object_name = 'templates'
    login_url = '/admin/login/'
    paginate_by = 12
    
    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            template_type='invoice',
            is_active=True
        ).select_related('invoice_template').order_by('-is_default', '-created_at')


class ContractTemplateListView(LoginRequiredMixin, ListView):
    """List all contract templates"""
    model = DocumentTemplate
    template_name = 'templates/contract_templates.html'
    context_object_name = 'templates'
    login_url = '/admin/login/'
    paginate_by = 12
    
    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            template_type='contract',
            is_active=True
        ).select_related('contract_template').order_by('-is_default', '-created_at')


class UploadTemplateView(LoginRequiredMixin, View):
    """Upload a custom invoice or contract file as a template"""
    login_url = '/admin/login/'
    
    def get(self, request):
        """Show upload form"""
        return TemplateView.as_view(template_name='templates/upload_template.html')(request)
    
    def post(self, request):
        """Handle file upload"""
        try:
            template_type = request.POST.get('template_type', 'invoice')
            template_name = request.POST.get('template_name', '')
            file_obj = request.FILES.get('template_file')
            
            if not file_obj or not template_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing file or template name'
                }, status=400)
            
            # Get file extension and size
            file_ext = os.path.splitext(file_obj.name)[1].lower().strip('.')
            file_size = getattr(file_obj, 'size', None)

            # Server-side validation using settings when available
            MAX_UPLOAD_SIZE = getattr(settings, 'DOCUMENT_UPLOAD_MAX_SIZE', 5 * 1024 * 1024)
            ALLOWED_EXTS = set(getattr(settings, 'DOCUMENT_ALLOWED_EXTENSIONS', [k for k, _ in DocumentTemplate.FILE_TYPE_CHOICES]))

            # Allow company-level overrides
            try:
                from core.models import CompanySettings
                company = CompanySettings.objects.first()
                if company:
                    MAX_UPLOAD_SIZE = company.upload_max_size or MAX_UPLOAD_SIZE
                    ALLOWED_EXTS = set([s.strip() for s in (company.allowed_extensions or '').split(',') if s.strip()]) or ALLOWED_EXTS
                    # Company flags can override global settings for MIME scanning and virus scan
                    settings.DOCUMENTS_ENFORCE_MIME = company.enforce_mime
                    settings.DOCUMENTS_VIRUS_SCAN = company.virus_scan
            except Exception:
                pass

            if file_ext not in ALLOWED_EXTS:
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported file type: .{file_ext}. Allowed: {", ".join(sorted(ALLOWED_EXTS))}'
                }, status=400)

            if file_size is not None and file_size > MAX_UPLOAD_SIZE:
                return JsonResponse({
                    'success': False,
                    'error': f'File too large. Maximum allowed size is {MAX_UPLOAD_SIZE // (1024*1024)} MB.'
                }, status=400)

            # MIME/content-based sniffing
            if getattr(settings, 'DOCUMENTS_ENFORCE_MIME', True):
                detected = detect_file_type(file_obj)
                if detected != 'other' and detected != file_ext:
                    return JsonResponse({
                        'success': False,
                        'error': f'File content does not match extension. Detected: {detected}, Provided: {file_ext}'
                    }, status=400)

            # Optional virus scan
            # If virus scanning is enabled and Celery is available, we enqueue an async scan after saving.
            # If Celery is not available, perform a synchronous scan as a fallback to prevent saving malicious files.
            VIRUS_SCAN_ENABLED = getattr(settings, 'DOCUMENTS_VIRUS_SCAN', False)
            from documents import tasks as document_tasks
            perform_sync_scan = False
            enqueue_scan = False
            if VIRUS_SCAN_ENABLED:
                if getattr(document_tasks, 'CELERY_AVAILABLE', False):
                    enqueue_scan = True
                else:
                    # Fallback to synchronous scan (no Celery)
                    perform_sync_scan = True

            if perform_sync_scan:
                clean, reason = scan_file(file_obj)
                if not clean:
                    return JsonResponse({
                        'success': False,
                        'error': f'File failed virus scan: {reason}'
                    }, status=400)

            # Create slug from template name
            slug = slugify(template_name)
            
            # Check if slug already exists
            counter = 1
            original_slug = slug
            while DocumentTemplate.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            # Create template record
            template = DocumentTemplate.objects.create(
                template_type=template_type,
                name=template_name,
                slug=slug,
                template_file=file_obj,
                file_type=file_ext if file_ext in dict(DocumentTemplate.FILE_TYPE_CHOICES) else 'other',
                created_by=request.user,
                description=f"Uploaded {file_ext.upper()} template"
            )
            
            # Log usage
            TemplateUsageLog.objects.create(
                template=template,
                user=request.user,
                action='upload'
            )

            # Enqueue or perform scan depending on configuration
            scan_enqueued = False
            scan_result = None
            try:
                if perform_sync_scan:
                    # Synchronous scan will run now and update status & logs
                    try:
                        document_tasks.scan_uploaded_template(template)
                    except Exception:
                        # If anything goes wrong, still allow upload but mark error
                        import logging
                        logging.getLogger(__name__).exception('Synchronous scan failed')
                        template.scan_status = 'error'
                        template.save(update_fields=['scan_status'])
                elif enqueue_scan:
                    # Mark pending and enqueue background task
                    try:
                        template.scan_status = 'pending'
                        template.save(update_fields=['scan_status'])
                        document_tasks.scan_uploaded_template.delay(template.pk)
                        scan_enqueued = True
                    except AttributeError:
                        # If the task isn't a Celery task, call synchronously
                        document_tasks.scan_uploaded_template(template.pk)
                # else: scanning disabled, leave status as default
            except Exception as e:
                # Do not fail the upload if enqueueing fails; log and continue
                import logging
                logging.getLogger(__name__).exception('Failed to enqueue or run scan: %s', e)

            return JsonResponse({
                'success': True,
                'message': f'Template "{template_name}" uploaded successfully',
                'template_id': str(template.id),
                'template_url': reverse_lazy('template_detail', kwargs={'slug': template.slug}),
                'scan_enqueued': scan_enqueued
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ReinstateTemplateView(LoginRequiredMixin, View):
    """Quick action to reinstate a quarantined template (staff only)"""
    login_url = '/admin/login/'

    def post(self, request, slug):
        if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

        template = get_object_or_404(DocumentTemplate, slug=slug)
        template.is_active = True
        template.scan_status = 'unknown'
        template.quarantine_reason = ''
        template.save(update_fields=['is_active', 'scan_status', 'quarantine_reason'])

        # Record a scan log entry to indicate manual reinstatement
        try:
            from .models import TemplateScanLog
            TemplateScanLog.objects.create(
                template=template,
                result='unknown',
                reason=f'Reinstated by {request.user.username}',
                scanned_by=f'user:{request.user.username}'
            )
        except Exception:
            pass

        return JsonResponse({'success': True})


class DownloadTemplateFileView(LoginRequiredMixin, View):
    """Download uploaded template file"""
    login_url = '/admin/login/'
    
    def get(self, request, slug):
        """Download the template file"""
        template = get_object_or_404(DocumentTemplate, slug=slug)
        
        if not template.template_file:
            return HttpResponse('File not found', status=404)
        
        # Log download
        TemplateUsageLog.objects.create(
            template=template,
            user=request.user,
            action='download_file'
        )
        
        # Open and return file
        file_path = template.template_file.path
        file_name = os.path.basename(file_path)
        
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=file_name
        )
        return response
