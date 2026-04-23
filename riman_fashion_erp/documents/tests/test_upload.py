from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import DocumentTemplate


class UploadTemplateTest(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user('testuploader', 'test@example.com', 'testpwd')

    def test_upload_template_via_client(self):
        c = Client()
        logged_in = c.login(username='testuploader', password='testpwd')
        self.assertTrue(logged_in)
        sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')
        resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Automated Test Invoice','template_file': sample}, follow=True)
        self.assertIn(resp.status_code, (200, 302))
        self.assertTrue(DocumentTemplate.objects.filter(name__icontains='Automated Test Invoice').exists())

    def test_reject_large_file(self):
        c = Client()
        c.login(username='testuploader', password='testpwd')
        large = SimpleUploadedFile('big.pdf', b'A' * (6 * 1024 * 1024), content_type='application/pdf')
        resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Large File','template_file': large}, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('File too large', resp.content.decode())

    def test_reject_invalid_type(self):
        c = Client()
        c.login(username='testuploader', password='testpwd')
        bad = SimpleUploadedFile('malware.exe', b'MZ...binary', content_type='application/octet-stream')
        resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Bad File','template_file': bad}, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Unsupported file type', resp.content.decode())

    def test_mime_mismatch_is_rejected(self):
        c = Client()
        c.login(username='testuploader', password='testpwd')
        # name says pdf but contents are not a PDF
        fake_pdf = SimpleUploadedFile('fake.pdf', b'NOTAPDF_DATA', content_type='application/pdf')
        resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Fake PDF','template_file': fake_pdf}, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('File content does not match extension', resp.content.decode())

    def test_docx_detection(self):
        import io, zipfile
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w') as zf:
            zf.writestr('word/document.xml', '<w:document/>')
        bio.seek(0)
        docx_file = SimpleUploadedFile('sample.docx', bio.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        c = Client()
        c.login(username='testuploader', password='testpwd')
        resp = c.post('/templates/upload/', {'template_type':'contract','template_name':'Docx Contract','template_file': docx_file}, follow=True)
        self.assertIn(resp.status_code, (200,302))
        self.assertTrue(DocumentTemplate.objects.filter(name__icontains='Docx Contract').exists())

    def test_max_size_configurable(self):
        from django.test.utils import override_settings
        with override_settings(DOCUMENT_UPLOAD_MAX_SIZE=10):
            c = Client()
            c.login(username='testuploader', password='testpwd')
            small = SimpleUploadedFile('tiny.pdf', b'A' * 20, content_type='application/pdf')
            resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Tiny','template_file': small}, follow=True)
            self.assertEqual(resp.status_code, 400)
            self.assertIn('File too large', resp.content.decode())

    def test_company_settings_override(self):
        from core.models import CompanySettings
        company = CompanySettings.objects.create(upload_max_size=10, allowed_extensions='pdf')
        c = Client()
        c.login(username='testuploader', password='testpwd')
        small = SimpleUploadedFile('tiny.pdf', b'A' * 20, content_type='application/pdf')
        # Because company max size is 10 bytes, even a 20-byte file should be rejected
        resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Tiny Company','template_file': small}, follow=True)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('File too large', resp.content.decode())

    def test_s3_flag_allows_configured_storage(self):
        from django.test.utils import override_settings
        with override_settings(DOCUMENTS_USE_S3=True, DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'):
            c = Client()
            c.login(username='testuploader', password='testpwd')
            sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')
            resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'S3 Flag Test','template_file': sample}, follow=True)
            self.assertIn(resp.status_code, (200,302))
            self.assertTrue(DocumentTemplate.objects.filter(name__icontains='S3 Flag Test').exists())

    def test_enqueue_scan_when_celery_available(self):
        from django.test.utils import override_settings
        from unittest.mock import patch, MagicMock
        import json

        c = Client()
        c.login(username='testuploader', password='testpwd')
        sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')

        with override_settings(DOCUMENTS_VIRUS_SCAN=True):
            # Simulate Celery being available and scanning as a background task
            with patch('documents.tasks.CELERY_AVAILABLE', True):
                mock_task = MagicMock()
                mock_task.delay = MagicMock()
                with patch('documents.tasks.scan_uploaded_template', mock_task):
                    resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Celery Scan Test','template_file': sample}, follow=True)
                    self.assertEqual(resp.status_code, 200)
                    data = json.loads(resp.content.decode())
                    self.assertTrue(data.get('scan_enqueued'))
                    mock_task.delay.assert_called_once()

    def test_sync_scan_sets_clean_status(self):
        from django.test.utils import override_settings
        from unittest.mock import patch

        c = Client()
        c.login(username='testuploader', password='testpwd')
        sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')

        with override_settings(DOCUMENTS_VIRUS_SCAN=True):
            # Force no Celery available so synchronous scan will run
            with patch('documents.tasks.CELERY_AVAILABLE', False):
                # Patch the low-level scanner to report clean
                with patch('documents.views.scan_file', return_value=(True, 'ok')):
                    resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Sync Clean Test','template_file': sample}, follow=True)
                    self.assertIn(resp.status_code, (200,302))
                    # Check DB entry and status
                    from documents.models import DocumentTemplate
                    t = DocumentTemplate.objects.get(name__icontains='Sync Clean Test')
                    self.assertEqual(t.scan_status, 'clean')

    def test_task_marks_infected(self):
        from django.test.utils import override_settings
        from unittest.mock import patch

        c = Client()
        c.login(username='testuploader', password='testpwd')
        sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')

        # Ensure Celery appears available so upload enqueues
        with override_settings(DOCUMENTS_VIRUS_SCAN=True):
            with patch('documents.tasks.CELERY_AVAILABLE', True):
                resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Task Infected Test','template_file': sample}, follow=True)
                self.assertIn(resp.status_code, (200,302))
                from documents.models import DocumentTemplate
                t = DocumentTemplate.objects.get(name__icontains='Task Infected Test')
                # Simulate the worker scan reporting infected
                with patch('documents.tasks.scan_file', return_value=(False, 'EICAR')):
                    # Call the task function directly to simulate worker processing
                    from documents import tasks as document_tasks
                    document_tasks.scan_uploaded_template(t.pk)
                    t.refresh_from_db()
                    self.assertEqual(t.scan_status, 'infected')
                    # Ensure the template was quarantined (deactivated)
                    self.assertFalse(t.is_active)
                    # Ensure quarantine reason persisted
                    self.assertIn('EICAR', t.quarantine_reason)
                    # Ensure a scan log was written
                    from documents.models import TemplateScanLog
                    self.assertTrue(TemplateScanLog.objects.filter(template=t, result='infected').exists())

    def test_infected_triggers_notification(self):
        from unittest.mock import patch
        from django.test.utils import override_settings

        c = Client()
        c.login(username='testuploader', password='testpwd')
        sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')

        with override_settings(DOCUMENTS_VIRUS_SCAN=True, DOCUMENTS_AUTO_QUARANTINE=True, ADMINS=[('Admin', 'admin@example.com')]):
            with patch('documents.tasks.CELERY_AVAILABLE', True):
                resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Notify Test','template_file': sample}, follow=True)
                self.assertIn(resp.status_code, (200,302))
                from documents.models import DocumentTemplate
                t = DocumentTemplate.objects.get(name__icontains='Notify Test')
                # Simulate infected scan
                with patch('documents.tasks.scan_file', return_value=(False, 'EICAR')):
                    with patch('django.core.mail.send_mail') as mock_mail:
                        from documents import tasks as document_tasks
                        document_tasks.scan_uploaded_template(t.pk)
                        mock_mail.assert_called()
                        t.refresh_from_db()
                        self.assertFalse(t.is_active)

    def test_reinstate_endpoint(self):
        from unittest.mock import patch
        from django.test.utils import override_settings

        c = Client()
        c.login(username='testuploader', password='testpwd')
        # Make the user staff so they can reinstate
        from django.contrib.auth import get_user_model
        User = get_user_model()
        u = User.objects.get(username='testuploader')
        u.is_staff = True
        u.save()

        sample = SimpleUploadedFile('sample_invoice.pdf', b'%PDF-1.4\nTest', content_type='application/pdf')

        with override_settings(DOCUMENTS_VIRUS_SCAN=True, DOCUMENTS_AUTO_QUARANTINE=True):
            with patch('documents.tasks.CELERY_AVAILABLE', True):
                resp = c.post('/templates/upload/', {'template_type':'invoice','template_name':'Reinstate Test','template_file': sample}, follow=True)
                self.assertIn(resp.status_code, (200,302))
                from documents.models import DocumentTemplate
                t = DocumentTemplate.objects.get(name__icontains='Reinstate Test')
                # Simulate infected scan
                with patch('documents.tasks.scan_file', return_value=(False, 'EICAR')):
                    from documents import tasks as document_tasks
                    document_tasks.scan_uploaded_template(t.pk)
                    t.refresh_from_db()
                    self.assertFalse(t.is_active)
                    # Call reinstate endpoint
                    resp = c.post(f'/templates/{t.slug}/reinstate/', follow=True)
                    self.assertEqual(resp.status_code, 200)
                    t.refresh_from_db()
                    self.assertTrue(t.is_active)
                    self.assertEqual(t.scan_status, 'unknown')
