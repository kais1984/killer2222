"""
PDF Generation Services for invoices, reports, and statements
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime, date
from io import BytesIO
from django.conf import settings
import os


class InvoicePDFGenerator:
    """Generate professional PDF invoices"""
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.pagesize = letter
        self.width, self.height = self.pagesize
        
    def generate(self):
        """Generate and return PDF as BytesIO"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=self.pagesize,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        elements.append(self._create_header(styles))
        elements.append(Spacer(1, 0.2*inch))
        
        # Invoice info
        elements.append(self._create_invoice_info(styles))
        elements.append(Spacer(1, 0.2*inch))
        
        # Line items
        elements.append(self._create_line_items_table(styles))
        elements.append(Spacer(1, 0.2*inch))
        
        # Totals
        elements.append(self._create_totals_table(styles))
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(self._create_footer(styles))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _create_header(self, styles):
        """Create invoice header with company info"""
        company_name = getattr(settings, 'COMPANY_NAME', 'RIAMAN FASHION')
        company_phone = getattr(settings, 'COMPANY_PHONE', '')
        company_email = getattr(settings, 'COMPANY_EMAIL', '')
        
        header_text = f"""
        <b>{company_name}</b><br/>
        {company_phone} | {company_email}<br/>
        <b>INVOICE</b>
        """
        
        para = Paragraph(header_text, styles['Normal'])
        
        data = [
            [para, Paragraph(f"<b>Invoice #{self.invoice.invoice_number}</b><br/>Date: {self.invoice.invoice_date.strftime('%m/%d/%Y')}", styles['Normal'])],
        ]
        
        table = Table(data, colWidths=[3.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 12),
        ]))
        
        return table
    
    def _create_invoice_info(self, styles):
        """Create customer and sale info section"""
        customer = self.invoice.sale.customer
        sale = self.invoice.sale
        
        bill_text = f"""
        <b>BILL TO:</b><br/>
        {customer.first_name} {customer.last_name}<br/>
        {getattr(customer, 'email', 'N/A')}<br/>
        {getattr(customer, 'phone', 'N/A')}
        """
        
        sale_text = f"""
        <b>SALE #:</b> {sale.sale_number}<br/>
        <b>SALE DATE:</b> {sale.sale_date.strftime('%m/%d/%Y')}<br/>
        <b>DUE DATE:</b> {(self.invoice.invoice_date).strftime('%m/%d/%Y')}
        """
        
        data = [
            [
                Paragraph(bill_text, styles['Normal']),
                Paragraph(sale_text, styles['Normal'])
            ]
        ]
        
        table = Table(data, colWidths=[3.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return table
    
    def _create_line_items_table(self, styles):
        """Create table of line items"""
        data = [
            ['Description', 'Quantity', 'Unit Price', 'Total']
        ]
        
        for line in self.invoice.sale.lines.all():
            data.append([
                f"{line.product.name}",
                f"{line.quantity}",
                f"${line.unit_price:.2f}",
                f"${line.line_total:.2f}"
            ])
        
        table = Table(data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        return table
    
    def _create_totals_table(self, styles):
        """Create totals summary"""
        data = [
            ['Subtotal:', f"${self.invoice.sale.subtotal:.2f}"],
            ['Tax ({:.1f}%):'.format(getattr(settings, 'DEFAULT_TAX_RATE', 0)), f"${self.invoice.sale.tax_amount:.2f}"],
            ['Total:', f"${self.invoice.sale.total_amount:.2f}"],
        ]
        
        table = Table(data, colWidths=[4.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 12),
            ('TOPPADDING', (0, 2), (-1, 2), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 2), 6),
            ('GRID', (0, 2), (-1, 2), 1, colors.black),
        ]))
        
        return table
    
    def _create_footer(self, styles):
        """Create footer with thank you message"""
        footer_text = "Thank you for your business!"
        return Paragraph(f"<i>{footer_text}</i>", ParagraphStyle(
            'footer',
            parent=styles['Normal'],
            alignment=1  # Center
        ))


class SalesReportPDFGenerator:
    """Generate sales reports as PDF"""
    
    def __init__(self, sales, date_from=None, date_to=None):
        self.sales = sales
        self.date_from = date_from
        self.date_to = date_to
        self.pagesize = letter
        
    def generate(self):
        """Generate sales report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = f"Sales Report - {self.date_from.strftime('%m/%d/%Y') if self.date_from else 'All Time'}"
        elements.append(Paragraph(f"<b>{title}</b>", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary stats
        total_sales = sum(s.total_amount for s in self.sales)
        total_items = sum(len(s.lines.all()) for s in self.sales)
        
        stats_text = f"""
        <b>Summary:</b><br/>
        Total Sales: {len(self.sales)}<br/>
        Total Items Sold: {total_items}<br/>
        Total Revenue: ${total_sales:.2f}
        """
        elements.append(Paragraph(stats_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Sales table
        data = [['Sale #', 'Customer', 'Date', 'Items', 'Total']]
        
        for sale in self.sales:
            data.append([
                sale.sale_number,
                f"{sale.customer.first_name} {sale.customer.last_name}",
                sale.sale_date.strftime('%m/%d/%Y'),
                str(len(sale.lines.all())),
                f"${sale.total_amount:.2f}"
            ])
        
        table = Table(data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 1*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer


class GLReportPDFGenerator:
    """Generate General Ledger reports"""
    
    def __init__(self, journal_entries, date_from=None, date_to=None):
        self.journal_entries = journal_entries
        self.date_from = date_from
        self.date_to = date_to
        self.pagesize = letter
        
    def generate(self):
        """Generate GL report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=6,
            alignment=1,  # CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=10,
            spaceBefore=10,
        )
        
        # Company Header
        elements.append(Paragraph("RIMAN FASHION ERP", title_style))
        elements.append(Paragraph("General Ledger Report", ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,
            textColor=colors.HexColor('#666666')
        )))
        elements.append(Spacer(1, 0.3*inch))
        
        # Report Details
        date_range = f"{self.date_from.strftime('%m/%d/%Y')} to {self.date_to.strftime('%m/%d/%Y')}" if self.date_from and self.date_to else "All Dates"
        report_info = f"<b>Report Date:</b> {date.today().strftime('%m/%d/%Y')} | <b>Period:</b> {date_range}"
        elements.append(Paragraph(report_info, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary Section
        total_debits = sum(sum(line.amount for line in entry.lines.filter(line_type='debit')) for entry in self.journal_entries)
        total_credits = sum(sum(line.amount for line in entry.lines.filter(line_type='credit')) for entry in self.journal_entries)
        is_balanced = abs(total_debits - total_credits) < 0.01
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Journal Entries', str(len(self.journal_entries))],
            ['Total Debits', f"${total_debits:,.2f}"],
            ['Total Credits', f"${total_credits:,.2f}"],
            ['Difference', f"${abs(total_debits - total_credits):,.2f}"],
            ['Status', '<b>BALANCED</b>' if is_balanced else '<b>UNBALANCED</b>'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(Paragraph("Summary", heading_style))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Journal Entries Table with comprehensive ledger format
        elements.append(Paragraph("Complete Ledger", heading_style))
        
        data = [['Transaction ID', 'Type', 'Payment Mode', 'Processed By', 'IN (Debit)', 'OUT (Credit)', 'Running Balance', 'Status']]
        
        running_balance = 0
        payment_map = {}
        
        # Get all payments for reference
        from sales.models import Payment
        for payment in Payment.objects.all():
            payment_map[payment.id] = payment
        
        for entry in self.journal_entries[:100]:  # Show up to 100 entries
            is_entry_balanced = entry.is_balanced()
            
            for idx, line in enumerate(entry.lines.all()):
                # Calculate running balance
                if line.line_type == 'debit':
                    running_balance += line.amount
                    in_amount = f"${line.amount:,.2f}"
                    out_amount = ''
                else:
                    running_balance -= line.amount
                    in_amount = ''
                    out_amount = f"${line.amount:,.2f}"
                
                # Get payment mode from journal entry if it exists
                payment_mode = entry.entry_type if idx == 0 else ''
                
                # Get user name if available
                processed_by = entry.created_by.first_name if entry.created_by else 'System'
                
                data.append([
                    str(entry.journal_number) if idx == 0 else '',
                    entry.entry_type if idx == 0 else '',
                    payment_mode,
                    processed_by if idx == 0 else '',
                    in_amount,
                    out_amount,
                    f"${running_balance:,.2f}",
                    ('✓' if is_entry_balanced else '✗') if idx == 0 else '',
                ])
        
        table = Table(data, colWidths=[1.1*inch, 0.8*inch, 1*inch, 1*inch, 0.9*inch, 0.9*inch, 1.2*inch, 0.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (3, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=1,
        )
        elements.append(Paragraph("Report generated automatically by RIMAN Fashion ERP", footer_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
