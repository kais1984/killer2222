"""
Utility functions and helpers for the ERP system
"""

from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Q
import random
import string

class BusinessLogic:
    """Business logic helpers"""
    
    @staticmethod
    def calculate_invoice_total(subtotal, tax_rate, discount_amount, shipping_cost):
        """Calculate total invoice amount"""
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount - discount_amount + shipping_cost
        return total, tax_amount
    
    @staticmethod
    def calculate_profitability(cost_price, sale_price, quantity_sold):
        """Calculate profit metrics"""
        if cost_price == 0:
            return 0, 0
        
        profit_per_unit = sale_price - cost_price
        total_profit = profit_per_unit * quantity_sold
        margin_percentage = (profit_per_unit / cost_price) * 100
        
        return total_profit, margin_percentage
    
    @staticmethod
    def check_low_stock(product, threshold=10):
        """Check if product is below threshold"""
        return product.quantity_in_stock < threshold
    
    @staticmethod
    def calculate_inventory_value(products):
        """Calculate total inventory value"""
        total_value = Decimal('0')
        for product in products:
            total_value += Decimal(product.cost_price) * product.quantity_in_stock
        return total_value


class DocumentGenerator:
    """Generate document numbers"""
    
    @staticmethod
    def generate_invoice_number(company_settings):
        """Generate unique invoice number"""
        prefix = company_settings.invoice_prefix
        number = company_settings.invoice_next_number
        invoice_number = f"{prefix}{number}"
        
        # Increment for next invoice
        company_settings.invoice_next_number = number + 1
        company_settings.save()
        
        return invoice_number
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{timestamp}-{random_suffix}"
    
    @staticmethod
    def generate_rental_number():
        """Generate unique rental number"""
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.digits, k=3))
        return f"RNT-{timestamp}-{random_suffix}"
    
    @staticmethod
    def generate_sku():
        """Generate unique SKU"""
        timestamp = timezone.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"SK-{timestamp}-{random_suffix}"


class PaymentProcessor:
    """Payment processing logic"""
    
    @staticmethod
    def apply_payment(invoice, amount, payment_method, reference_number):
        """Apply payment to invoice"""
        from sales.models import Payment
        
        payment = Payment.objects.create(
            invoice=invoice,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            payment_date=timezone.now().date()
        )
        
        # Update invoice
        invoice.amount_paid += amount
        invoice.update_payment_status()
        invoice.save()
        
        return payment
    
    @staticmethod
    def get_outstanding_amount(invoice):
        """Get outstanding payment for invoice"""
        return invoice.total_amount - invoice.amount_paid
    
    @staticmethod
    def is_overdue(invoice):
        """Check if invoice is overdue"""
        if invoice.due_date and timezone.now().date() > invoice.due_date:
            if invoice.payment_status != 'paid':
                return True
        return False


class ReportHelper:
    """Report generation helpers"""
    
    @staticmethod
    def get_period_data(start_date, end_date):
        """Get data for a specific period"""
        from sales.models import Invoice
        from accounting.models import Income, Expense
        
        invoices = Invoice.objects.filter(
            invoice_date__gte=start_date,
            invoice_date__lte=end_date
        )
        
        income = Income.objects.filter(
            income_date__gte=start_date,
            income_date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return {
            'invoices': invoices,
            'total_income': income,
            'total_expenses': expenses,
            'net_profit': income - expenses,
        }
    
    @staticmethod
    def get_top_clients(limit=10):
        """Get top clients by sales"""
        from sales.models import Invoice
        
        clients = Invoice.objects.values('client').annotate(
            total_spent=Sum('total_amount'),
            invoice_count=Count('id')
        ).order_by('-total_spent')[:limit]
        
        return clients


class NotificationHelper:
    """Notification helpers"""
    
    @staticmethod
    def create_low_stock_notification(product):
        """Create notification for low stock"""
        from core.models import Notification, User
        
        admin_users = User.objects.filter(role='admin')
        
        for user in admin_users:
            Notification.objects.create(
                user=user,
                title=f"Low Stock Alert: {product.name}",
                message=f"Product {product.sku} is running low on stock. Current: {product.quantity_in_stock}",
                priority='high',
                action_url=f'/inventory/products/{product.id}/'
            )
    
    @staticmethod
    def create_payment_reminder(invoice):
        """Create payment reminder notification"""
        from core.models import Notification
        
        Notification.objects.create(
            user=invoice.client.get_user() if hasattr(invoice.client, 'get_user') else None,
            title=f"Payment Due: {invoice.invoice_number}",
            message=f"Invoice {invoice.invoice_number} is due. Outstanding: ${invoice.get_outstanding_amount()}",
            priority='medium',
        )
