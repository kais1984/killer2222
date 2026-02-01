"""
REFINEMENT 8: API Validation Framework

Centralized validation utilities for all views and API endpoints.

Provides:
1. User authentication and authorization checks
2. Form and data validation
3. Request/response validation
4. Error response formatting
"""

from django.contrib.auth.models import AnonymousUser
from core.exceptions import (
    UnauthorizedException,
    ValidationException,
    MissingRequiredField,
    InvalidFieldValue,
    BusinessRuleViolation,
)


class APIValidator:
    """
    Centralized validation for API requests
    
    Handles:
    - User authentication
    - Permission checks
    - Data validation
    - Error formatting
    """
    
    @staticmethod
    def validate_authenticated_user(user):
        """
        Verify user is authenticated
        
        Args:
            user: Django user object
            
        Raises:
            UnauthorizedException: If user not authenticated
        """
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            raise UnauthorizedException(
                user if user else 'Anonymous',
                'access system',
                'ERP'
            )
    
    @staticmethod
    def validate_user_permission(user, permission_name):
        """
        Check if user has specific permission
        
        Args:
            user: Django user object
            permission_name: Permission string (e.g., 'accounting.add_journalentry')
            
        Raises:
            UnauthorizedException: If user lacks permission
        """
        APIValidator.validate_authenticated_user(user)
        
        if not user.has_perm(permission_name) and not user.is_staff:
            raise UnauthorizedException(
                user.username,
                f'perform operation {permission_name}'
            )
    
    @staticmethod
    def validate_user_group(user, group_name):
        """
        Check if user is in specific group
        
        Args:
            user: Django user object
            group_name: Group name to check
            
        Raises:
            UnauthorizedException: If user not in group
        """
        APIValidator.validate_authenticated_user(user)
        
        if not user.groups.filter(name=group_name).exists() and not user.is_staff:
            raise UnauthorizedException(
                user.username,
                f'access {group_name} group'
            )
    
    @staticmethod
    def validate_required_fields(data, required_fields, model_name='Model'):
        """
        Validate all required fields are present
        
        Args:
            data: Dictionary of data to validate
            required_fields: List of required field names
            model_name: Name of model for error messages
            
        Raises:
            MissingRequiredField: If required field missing
        """
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                raise MissingRequiredField(model_name, field)
    
    @staticmethod
    def validate_field_type(field_value, field_name, expected_type, model_name='Model'):
        """
        Validate field has correct data type
        
        Args:
            field_value: Value to validate
            field_name: Field name for error messages
            expected_type: Expected type (int, str, float, etc.)
            model_name: Name of model for error messages
            
        Raises:
            InvalidFieldValue: If field type incorrect
        """
        if field_value is None:
            return  # Skip None values
        
        if not isinstance(field_value, expected_type):
            raise InvalidFieldValue(
                model_name,
                field_name,
                field_value,
                f'Expected {expected_type.__name__}, got {type(field_value).__name__}'
            )
    
    @staticmethod
    def validate_field_range(field_value, field_name, min_value=None, max_value=None, model_name='Model'):
        """
        Validate numeric field is within range
        
        Args:
            field_value: Value to validate
            field_name: Field name for error messages
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            model_name: Name of model for error messages
            
        Raises:
            InvalidFieldValue: If field outside range
        """
        if field_value is None:
            return  # Skip None values
        
        if min_value is not None and field_value < min_value:
            raise InvalidFieldValue(
                model_name,
                field_name,
                field_value,
                f'Must be >= {min_value}'
            )
        
        if max_value is not None and field_value > max_value:
            raise InvalidFieldValue(
                model_name,
                field_name,
                field_value,
                f'Must be <= {max_value}'
            )
    
    @staticmethod
    def validate_email_format(email, field_name='email', model_name='Model'):
        """
        Validate email format
        
        Args:
            email: Email string to validate
            field_name: Field name for error messages
            model_name: Name of model for error messages
            
        Raises:
            InvalidFieldValue: If email format invalid
        """
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, email):
            raise InvalidFieldValue(
                model_name,
                field_name,
                email,
                'Invalid email format'
            )
    
    @staticmethod
    def validate_positive_amount(amount, field_name='amount', model_name='Model'):
        """
        Validate amount is positive
        
        Args:
            amount: Amount to validate
            field_name: Field name for error messages
            model_name: Name of model for error messages
            
        Raises:
            InvalidFieldValue: If amount not positive
        """
        from decimal import Decimal
        
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        if amount <= 0:
            raise InvalidFieldValue(
                model_name,
                field_name,
                amount,
                'Amount must be positive'
            )
    
    @staticmethod
    def validate_form(form, raise_exception=True):
        """
        Validate Django form
        
        Args:
            form: Django form to validate
            raise_exception: Whether to raise exception on error
            
        Returns:
            tuple: (is_valid, errors_dict)
            
        Raises:
            ValidationException: If raise_exception=True and form invalid
        """
        if not form.is_valid():
            if raise_exception:
                errors_list = []
                for field, errors in form.errors.items():
                    errors_list.append(f"{field}: {', '.join(errors)}")
                raise ValidationException('; '.join(errors_list))
            return False, form.errors
        
        return True, {}
    
    @staticmethod
    def format_error_response(exception, include_traceback=False):
        """
        Format exception as API error response
        
        Args:
            exception: Exception to format
            include_traceback: Whether to include full traceback
            
        Returns:
            dict: Formatted error response
        """
        from core.exceptions import RimanERPException
        import traceback
        
        response = {
            'success': False,
            'error': str(exception)
        }
        
        # Add error code if available
        if isinstance(exception, RimanERPException):
            response['error_code'] = exception.error_code
            if exception.context:
                response['context'] = exception.context
        
        # Add traceback if requested
        if include_traceback:
            response['traceback'] = traceback.format_exc()
        
        return response
    
    @staticmethod
    def format_success_response(data, message='Success', status_code=200):
        """
        Format successful API response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            
        Returns:
            dict: Formatted success response
        """
        return {
            'success': True,
            'message': message,
            'data': data,
            'status_code': status_code
        }


class ContractValidator:
    """Validation specific to contracts"""
    
    @staticmethod
    def validate_contract_dates(start_date, end_date):
        """
        Validate contract date range
        
        Args:
            start_date: Contract start date
            end_date: Contract end date
            
        Raises:
            InvalidFieldValue: If dates invalid
        """
        if end_date <= start_date:
            raise InvalidFieldValue(
                'Contract',
                'rental_end_date',
                end_date,
                'End date must be after start date'
            )
    
    @staticmethod
    def validate_contract_value(value):
        """
        Validate contract value
        
        Args:
            value: Contract value
            
        Raises:
            InvalidFieldValue: If value invalid
        """
        APIValidator.validate_positive_amount(value, 'contract_value', 'Contract')


class InvoiceValidator:
    """Validation specific to invoices"""
    
    @staticmethod
    def validate_invoice_totals(subtotal, tax, total):
        """
        Validate invoice calculations
        
        Args:
            subtotal: Invoice subtotal
            tax: Tax amount
            total: Total amount
            
        Raises:
            BusinessRuleViolation: If calculations don't match
        """
        from decimal import Decimal
        
        calculated_total = Decimal(str(subtotal)) + Decimal(str(tax))
        
        if abs(calculated_total - Decimal(str(total))) > Decimal('0.01'):
            raise BusinessRuleViolation(
                'Invoice Total Calculation',
                f'Calculated total ({calculated_total}) does not match provided total ({total})'
            )


class PaymentValidator:
    """Validation specific to payments"""
    
    @staticmethod
    def validate_payment_amount(amount, invoice_total):
        """
        Validate payment amount against invoice
        
        Args:
            amount: Payment amount
            invoice_total: Invoice total amount
            
        Raises:
            InvalidFieldValue: If payment invalid
        """
        from decimal import Decimal
        
        APIValidator.validate_positive_amount(amount, 'amount', 'Payment')
        
        # Note: Payment can exceed invoice for overpayment scenarios
        # but should not be less than invoice due
