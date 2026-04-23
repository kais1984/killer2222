"""
Management command to create default templates
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from documents.models import DocumentTemplate, InvoiceTemplate, ContractTemplate


class Command(BaseCommand):
    help = 'Creates default invoice and contract templates'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating default templates...')
        
        # Create Invoice Template
        invoice_template_html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .header h1 { color: #333; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th { background-color: #f0f0f0; padding: 10px; text-align: left; border-bottom: 2px solid #333; }
                td { padding: 8px; border-bottom: 1px solid #ddd; }
                .total { font-weight: bold; font-size: 18px; }
                .signature { margin-top: 40px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>INVOICE</h1>
                <p>Invoice #: <strong>[INVOICE_NUMBER]</strong></p>
            </div>
            
            <table>
                <tr>
                    <th colspan="2">Bill To</th>
                </tr>
                <tr>
                    <td colspan="2">
                        Company: [CLIENT_NAME]<br>
                        Email: [CLIENT_EMAIL]<br>
                        Phone: [CLIENT_PHONE]
                    </td>
                </tr>
            </table>
            
            <table>
                <tr>
                    <th>Description</th>
                    <th>Qty</th>
                    <th>Unit Price</th>
                    <th>Amount</th>
                </tr>
                <tr>
                    <td>[ITEM_DESCRIPTION]</td>
                    <td>[QUANTITY]</td>
                    <td>[UNIT_PRICE]</td>
                    <td>[AMOUNT]</td>
                </tr>
            </table>
            
            <table>
                <tr>
                    <td colspan="3" style="text-align: right;">Subtotal:</td>
                    <td class="total">[SUBTOTAL]</td>
                </tr>
                <tr>
                    <td colspan="3" style="text-align: right;">Tax (5%):</td>
                    <td class="total">[TAX]</td>
                </tr>
                <tr>
                    <td colspan="3" style="text-align: right; font-size: 18px;">Total:</td>
                    <td class="total" style="font-size: 18px;">[TOTAL]</td>
                </tr>
            </table>
            
            <div style="margin-top: 40px;">
                <p><strong>Payment Terms:</strong> Net 30</p>
                <p><strong>Notes:</strong> Thank you for your business!</p>
            </div>
            
            <div class="signature">
                <table>
                    <tr>
                        <td style="border-bottom: 1px solid black; width: 45%; text-align: center;">Authorized Signature</td>
                        <td style="width: 10%;"></td>
                        <td style="border-bottom: 1px solid black; width: 45%; text-align: center;">Date</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        invoice_template, created = DocumentTemplate.objects.get_or_create(
            slug='standard_invoice',
            defaults={
                'template_type': 'invoice',
                'name': 'Standard Invoice Template',
                'description': 'Professional standard invoice template with customizable fields',
                'content': invoice_template_html,
                'is_active': True,
                'is_default': True,
                'version': 1,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {invoice_template.name}'))
            
            # Create Invoice Template Config
            InvoiceTemplate.objects.get_or_create(
                template=invoice_template,
                defaults={
                    'invoice_prefix': 'INV-',
                    'invoice_number_format': '{prefix}{year}-{sequence}',
                    'show_po_number': True,
                    'show_tax': True,
                    'show_discount': True,
                    'show_notes': True,
                    'show_terms': True,
                    'company_logo_position': 'top_left',
                    'color_scheme': 'blue',
                    'font_family': 'Arial',
                    'payment_terms_text': 'Net 30',
                }
            )
        else:
            self.stdout.write(f'✓ Already exists: {invoice_template.name}')
        
        # Create Contract Template
        contract_template_html = """
        <html>
        <head>
            <style>
                body { font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }
                .header { text-align: center; margin-bottom: 40px; }
                .header h1 { font-size: 24px; font-weight: bold; }
                .section { margin-bottom: 30px; }
                .section h2 { font-size: 14px; font-weight: bold; text-decoration: underline; }
                .parties { margin: 20px 0; }
                .signature { margin-top: 60px; }
                .signature-line { border-top: 1px solid black; width: 300px; height: 60px; display: inline-block; margin: 10px; }
                table { width: 100%; border-collapse: collapse; }
                td { padding: 5px; border: 1px solid #999; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SERVICE AGREEMENT</h1>
                <p>Effective Date: [DATE]</p>
            </div>
            
            <div class="section parties">
                <h2>PARTIES</h2>
                <p>
                    <strong>Service Provider:</strong> RIMAN FASHION<br>
                    <strong>Client:</strong> [CLIENT_NAME]<br>
                    <strong>Email:</strong> [CLIENT_EMAIL]
                </p>
            </div>
            
            <div class="section">
                <h2>1. SERVICES</h2>
                <p>
                    The Service Provider agrees to provide the following services:
                </p>
                <p style="margin-left: 20px;">
                    [SERVICE_DESCRIPTION]
                </p>
            </div>
            
            <div class="section">
                <h2>2. PAYMENT TERMS</h2>
                <p>
                    Total Amount: [AMOUNT]<br>
                    Payment Schedule:<br>
                </p>
                <table style="margin-left: 20px; width: 80%;">
                    <tr>
                        <td><strong>Payment</strong></td>
                        <td><strong>Amount</strong></td>
                        <td><strong>Due Date</strong></td>
                    </tr>
                    <tr>
                        <td>Advance Payment</td>
                        <td>50%</td>
                        <td>Upon Signing</td>
                    </tr>
                    <tr>
                        <td>Final Payment</td>
                        <td>50%</td>
                        <td>Upon Completion</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>3. TERM & TERMINATION</h2>
                <p>
                    This agreement shall commence on [START_DATE] and continue until [END_DATE] or upon completion of services.
                    Either party may terminate with 30 days written notice.
                </p>
            </div>
            
            <div class="section">
                <h2>4. CONFIDENTIALITY</h2>
                <p>
                    Both parties agree to maintain confidentiality of all business information and designs shared under this agreement.
                </p>
            </div>
            
            <div class="section">
                <h2>5. DISPUTE RESOLUTION</h2>
                <p>
                    Any disputes shall be resolved through mutual agreement or binding arbitration.
                </p>
            </div>
            
            <div class="signature">
                <p><strong>AGREED AND ACCEPTED:</strong></p>
                <div style="display: inline-block; margin-right: 50px;">
                    <p>Client Signature:</p>
                    <div class="signature-line"></div>
                    <p>Name: ____________________</p>
                    <p>Date: ____________________</p>
                </div>
                <div style="display: inline-block;">
                    <p>RIMAN FASHION Authorized Rep:</p>
                    <div class="signature-line"></div>
                    <p>Name: ____________________</p>
                    <p>Date: ____________________</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        contract_template, created = DocumentTemplate.objects.get_or_create(
            slug='standard_contract',
            defaults={
                'template_type': 'contract',
                'name': 'Standard Service Agreement',
                'description': 'Professional service agreement with customizable terms and payment schedule',
                'content': contract_template_html,
                'is_active': True,
                'is_default': True,
                'version': 1,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created: {contract_template.name}'))
            
            # Create Contract Template Config
            ContractTemplate.objects.get_or_create(
                template=contract_template,
                defaults={
                    'contract_type': 'master_service',
                    'includes_payment_terms': True,
                    'includes_liability': True,
                    'includes_confidentiality': True,
                    'includes_termination': True,
                    'includes_dispute_resolution': True,
                    'company_name_required': True,
                    'client_name_required': True,
                    'date_fields_required': True,
                    'amount_fields_required': True,
                }
            )
        else:
            self.stdout.write(f'✓ Already exists: {contract_template.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Default templates created successfully!'))
        self.stdout.write(self.style.WARNING('→ Visit /templates/ to view and manage templates'))
        self.stdout.write(self.style.WARNING('→ Visit /admin/documents/ to edit template configuration'))
