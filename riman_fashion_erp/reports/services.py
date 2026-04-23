"""
Reports and Analytics Views
"""

from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

class SalesReportService:
    """Generate sales reports"""
    
    @staticmethod
    def daily_sales(date):
        """Get sales for a specific day"""
        from sales.models import Invoice
        
        invoices = Invoice.objects.filter(invoice_date=date, status='paid')
        total_sales = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        return {
            'date': date,
            'total_sales': total_sales,
            'invoice_count': invoices.count(),
            'average_invoice_value': Decimal(total_sales) / invoices.count() if invoices.count() > 0 else 0,
        }
    
    @staticmethod
    def monthly_sales(year, month):
        """Get monthly sales report"""
        from sales.models import Invoice
        
        invoices = Invoice.objects.filter(
            invoice_date__year=year,
            invoice_date__month=month,
            status__in=['paid', 'partial']
        )
        
        sales_by_day = invoices.extra(select={'day': 'DATE(invoice_date)'}).values('day').annotate(
            daily_total=Sum('total_amount')
        )
        
        return {
            'year': year,
            'month': month,
            'total_sales': invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'total_invoices': invoices.count(),
            'sales_by_day': sales_by_day,
        }
    
    @staticmethod
    def best_selling_products(limit=10):
        """Get best-selling products"""
        from sales.models import InvoiceItem
        
        products = InvoiceItem.objects.values('product').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_total'),
        ).order_by('-total_revenue')[:limit]
        
        return products


class RentalReportService:
    """Generate rental reports"""
    
    @staticmethod
    def active_rentals():
        """Get currently active rentals"""
        from rentals.models import RentalAgreement
        today = timezone.now().date()
        
        rentals = RentalAgreement.objects.filter(
            rental_date__lte=today,
            return_date__gte=today,
            status='active'
        )
        
        return {
            'count': rentals.count(),
            'total_value': rentals.aggregate(Sum('rental_cost'))['rental_cost__sum'] or 0,
            'rentals': rentals,
        }
    
    @staticmethod
    def overdue_rentals():
        """Get overdue rental returns"""
        from rentals.models import RentalAgreement
        today = timezone.now().date()
        
        rentals = RentalAgreement.objects.filter(
            return_date__lt=today,
            actual_return_date__isnull=True,
            status__in=['active', 'returned']
        )
        
        return rentals


class InventoryReportService:
    """Generate inventory reports"""
    
    @staticmethod
    def low_stock_items(threshold=10):
        """Get items below stock threshold"""
        from inventory.models import Product
        
        items = Product.objects.filter(quantity_in_stock__lt=threshold, is_active=True)
        
        return items
    
    @staticmethod
    def inventory_value():
        """Calculate total inventory value"""
        from inventory.models import Product
        
        products = Product.objects.filter(is_active=True)
        total_value = Decimal('0')
        
        for product in products:
            total_value += product.cost_price * product.quantity_in_stock
        
        return total_value
    
    @staticmethod
    def inventory_by_category():
        """Get inventory value breakdown by category"""
        from inventory.models import Product
        from django.db.models import F, DecimalField, ExpressionWrapper
        
        categories = Product.objects.filter(is_active=True).values('category').annotate(
            total_items=Sum('quantity_in_stock'),
            total_value=Sum(ExpressionWrapper(F('cost_price') * F('quantity_in_stock'), 
                                             output_field=DecimalField())),
        )
        
        return categories


class FinancialReportService:
    """Generate financial reports"""
    
    @staticmethod
    def profit_and_loss(year, month):
        """Generate P&L statement"""
        from accounting.models import Income, Expense
        
        incomes = Income.objects.filter(
            income_date__year=year,
            income_date__month=month
        )
        
        expenses = Expense.objects.filter(
            expense_date__year=year,
            expense_date__month=month
        )
        
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        net_profit = total_income - total_expenses
        
        return {
            'period': f"{month}/{year}",
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit_loss': net_profit,
            'profit_margin': (net_profit / total_income * 100) if total_income > 0 else 0,
        }
    
    @staticmethod
    def cash_flow(year, month):
        """Generate cash flow report"""
        from sales.models import Payment
        from suppliers.models import SupplierPayment
        from rentals.models import RentalPayment
        
        customer_payments = Payment.objects.filter(
            payment_date__year=year,
            payment_date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        supplier_payments = SupplierPayment.objects.filter(
            payment_date__year=year,
            payment_date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        rental_payments = RentalPayment.objects.filter(
            payment_date__year=year,
            payment_date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        net_cash_flow = customer_payments + rental_payments - supplier_payments
        
        return {
            'period': f"{month}/{year}",
            'customer_inflows': customer_payments,
            'rental_inflows': rental_payments,
            'supplier_outflows': supplier_payments,
            'net_cash_flow': net_cash_flow,
        }


class DashboardMetricsService:
    """Generate dashboard KPIs"""
    
    @staticmethod
    def get_kpis():
        """Get all key performance indicators"""
        from sales.models import Invoice
        from rentals.models import RentalAgreement
        from inventory.models import Product
        from crm.models import Client
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Total sales this month
        monthly_sales = Invoice.objects.filter(
            invoice_date__gte=month_start,
            status__in=['paid', 'partial']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Active rentals
        active_rentals = RentalAgreement.objects.filter(
            rental_date__lte=today,
            return_date__gte=today,
            status='active'
        ).count()
        
        # Inventory value
        inventory_value = InventoryReportService.inventory_value()
        
        # Outstanding payments
        outstanding = Invoice.objects.filter(
            status__in=['partial', 'unpaid'],
            payment_status__in=['unpaid', 'partial', 'overdue']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Monthly profit (simplified)
        from accounting.models import Income, Expense
        income = Income.objects.filter(
            income_date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        expenses = Expense.objects.filter(
            expense_date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_profit = income - expenses
        
        return {
            'total_sales_month': monthly_sales,
            'active_rentals': active_rentals,
            'inventory_value': inventory_value,
            'outstanding_payments': outstanding,
            'monthly_profit': monthly_profit,
        }
