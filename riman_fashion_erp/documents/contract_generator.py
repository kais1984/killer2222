"""
Contract Generator for RIMAN Fashion
Generates professional PDF contracts with sample data
"""

from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
import io


class ContractGenerator:
    """Generate professional contracts as PDF"""
    
    def __init__(self):
        self.pagesize = A4
        self.width, self.height = self.pagesize
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            fontName='Helvetica'
        ))
    
    def generate_test_contract(self):
        """Generate a test contract with sample data"""
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
        )
        
        # Build story (content)
        story = []
        
        # Header
        story.append(Paragraph("RIMAN FASHION", self.styles['CustomTitle']))
        story.append(Paragraph("Master Services Agreement", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Contract Info
        contract_data = [
            ['Contract Number:', 'RIMAN-TEST-2026-001'],
            ['Date:', datetime.now().strftime('%B %d, %Y')],
            ['Effective Date:', datetime.now().strftime('%B %d, %Y')],
        ]
        contract_table = Table(contract_data, colWidths=[1.5*inch, 4*inch])
        contract_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contract_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Parties
        story.append(Paragraph("PARTIES TO THIS AGREEMENT", self.styles['CustomHeading']))
        
        parties_data = [
            ['SERVICE PROVIDER:', 'CLIENT:'],
            ['Riman Fashion\nP.O. Box 45179\nSharjah, UAE\nEmail: info@rimanfashion.com\nMobile: +971 6 5234701', 
             'Test Client\n123 Test Street\nSharjah, UAE\nEmail: client@test.com\nMobile: +971 55 1234567'],
        ]
        parties_table = Table(parties_data, colWidths=[3.5*inch, 3.5*inch])
        parties_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, 1), 'Helvetica', 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Services
        story.append(Paragraph("SERVICES PROVIDED", self.styles['CustomHeading']))
        story.append(Paragraph("""
        <b>Service Type:</b> Custom-Made Dress Design and Manufacturing<br/>
        <b>Description:</b> Riman shall design and manufacture a custom dress based on Client specifications.<br/>
        <b>Delivery Date:</b> February 15, 2026<br/>
        <b>Status:</b> Sample/Test Contract - Not Binding
        """, self.styles['CustomBody']))
        story.append(Spacer(1, 0.15*inch))
        
        # Payment Terms
        story.append(Paragraph("PAYMENT TERMS", self.styles['CustomHeading']))
        
        payment_data = [
            ['Item', 'Amount (AED)', 'Description'],
            ['Dress Price', '2,500', 'Custom-made dress design & manufacturing'],
            ['Advance Payment (50%)', '1,250', 'Due upon order placement'],
            ['Final Payment (50%)', '1,250', 'Due upon delivery'],
            ['VAT (5%)', '125', 'Value Added Tax'],
            ['TOTAL', '2,625', 'Total amount due'],
        ]
        payment_table = Table(payment_data, colWidths=[1.8*inch, 1.2*inch, 2.5*inch])
        payment_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10, colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Key Terms
        story.append(Paragraph("KEY TERMS & CONDITIONS", self.styles['CustomHeading']))
        
        terms_text = """
        <b>1. Deposit:</b> 50% advance payment is non-refundable unless Riman cancels the order.<br/>
        <b>2. Timeline:</b> Design consultation and Prova sessions to be scheduled within 7 days of contract execution.<br/>
        <b>3. Cancellation:</b> If cancelled before production, 80% of deposit is refundable. If cancelled after production begins, deposit is non-refundable.<br/>
        <b>4. Security Deposit:</b> An additional security deposit may be required for rental services.<br/>
        <b>5. Late Return Fees:</b> For rentals, 10% of daily rental value applies for each day of delay.<br/>
        <b>6. Damage:</b> Client is responsible for damage to the dress while in their possession. Repair costs or full replacement value may be deducted from Security Deposit.<br/>
        <b>7. Governing Law:</b> This agreement is governed by the laws of the United Arab Emirates.
        """
        story.append(Paragraph(terms_text, self.styles['CustomSmall']))
        story.append(Spacer(1, 0.2*inch))
        
        # Notes
        story.append(Paragraph("""
        <i><b>NOTICE:</b> This is a sample/test contract for demonstration purposes only. 
        It is not a binding agreement unless signed by authorized representatives of both parties.</i>
        """, self.styles['CustomSmall']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_custom_contract(self, contract_data):
        """Generate a custom contract with provided data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
        )
        
        story = []
        
        # Header
        story.append(Paragraph("RIMAN FASHION", self.styles['CustomTitle']))
        story.append(Paragraph("Master Services Agreement", self.styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Use provided data or defaults
        contract_number = contract_data.get('contract_number', 'RIMAN-CUSTOM-2026-001')
        client_name = contract_data.get('client_name', 'Client Name')
        service_type = contract_data.get('service_type', 'Custom Dress Service')
        delivery_date = contract_data.get('delivery_date', (datetime.now() + timedelta(days=30)).strftime('%B %d, %Y'))
        total_amount = contract_data.get('total_amount', '2,500')
        
        # Contract Info
        contract_data_table = [
            ['Contract Number:', contract_number],
            ['Date:', datetime.now().strftime('%B %d, %Y')],
            ['Effective Date:', datetime.now().strftime('%B %d, %Y')],
        ]
        contract_table = Table(contract_data_table, colWidths=[1.5*inch, 4*inch])
        contract_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(contract_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Parties
        story.append(Paragraph("PARTIES TO THIS AGREEMENT", self.styles['CustomHeading']))
        
        parties_data = [
            ['SERVICE PROVIDER:', 'CLIENT:'],
            ['Riman Fashion\nP.O. Box 45179\nSharjah, UAE\nEmail: info@rimanfashion.com\nMobile: +971 6 5234701', 
             f'{client_name}\nClient Address\nSharjah, UAE'],
        ]
        parties_table = Table(parties_data, colWidths=[3.5*inch, 3.5*inch])
        parties_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, 1), 'Helvetica', 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Services
        story.append(Paragraph("SERVICES PROVIDED", self.styles['CustomHeading']))
        story.append(Paragraph(f"""
        <b>Service Type:</b> {service_type}<br/>
        <b>Delivery Date:</b> {delivery_date}<br/>
        <b>Total Amount:</b> AED {total_amount}
        """, self.styles['CustomBody']))
        story.append(Spacer(1, 0.15*inch))
        
        # Signature
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("SIGNATURE BLOCK", self.styles['CustomHeading']))
        
        sig_data = [
            ['FOR RIMAN FASHION:', 'FOR THE CLIENT:'],
            ['', ''],
            ['_______________________', '_______________________'],
            ['Authorized Signature', 'Client Signature'],
            ['Date: _______________', 'Date: _______________'],
        ]
        sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sig_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
