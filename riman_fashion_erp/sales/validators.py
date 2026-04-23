"""
Sales validators: Ensure data integrity for accounting accuracy
"""

from django.core.exceptions import ValidationError
from decimal import Decimal


def validate_payment_not_overpaid(payment):
    """Ensure payment doesn't exceed amount due on sale"""
    if not payment.sale:
        return
    
    # Calculate current amount due (excluding this payment if updating)
    amount_paid = payment.sale.payments.filter(
        reversed_by__isnull=True
    ).exclude(id=payment.id).aggregate(
        total=__import__('django.db.models', fromlist=['Sum']).Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Add this payment
    total_with_payment = amount_paid + payment.amount
    
    if total_with_payment > payment.sale.total_amount:
        raise ValidationError(
            f"Payment of {payment.amount} would exceed sale total of "
            f"{payment.sale.total_amount}. Already paid: {amount_paid}"
        )


def validate_sale_has_lines(sale):
    """Ensure sale has at least one line item"""
    if sale.pk and not sale.lines.exists():
        raise ValidationError("Sale must have at least one line item")


def validate_sale_line_quantity(sale_line):
    """Ensure we don't sell more than available stock"""
    if not sale_line.product:
        return
    
    # Get current stock
    current_stock = sale_line.product.quantity
    
    # Check if enough stock available
    if sale_line.quantity > current_stock:
        raise ValidationError(
            f"Insufficient stock for {sale_line.product.name}. "
            f"Available: {current_stock}, Requested: {sale_line.quantity}"
        )


def validate_invoice_only_one_per_sale(invoice):
    """Ensure only one invoice per sale"""
    if invoice.sale:
        existing = __import__('financeaccounting.models', fromlist=['Invoice']).objects.filter(
            sale=invoice.sale
        ).exclude(id=invoice.id)
        
        if existing.exists():
            raise ValidationError(
                f"Sale {invoice.sale.sale_number} already has an invoice"
            )


class ValidatingModelMixin:
    """Mixin to ensure clean() is called on save"""
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
