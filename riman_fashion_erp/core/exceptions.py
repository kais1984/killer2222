"""
REFINEMENT 7: Custom Exception Hierarchy

Centralized error handling for all ERP operations.

Exception hierarchy:
- RimanERPException (base)
  - ContractException
    - ContractLocked
    - ContractValidationError
    - ContractNotFound
  - InventoryException
    - NegativeStockException
    - InsufficientStockException
    - StockMovementLocked
  - RevenueRecognitionException
    - InvalidRevenueRecognition
    - DeferredRevenueError
  - GLException
    - GLMismatchException
    - GLPostingError
    - UnbalancedEntry
  - PaymentException
    - InvalidPaymentAmount
    - PaymentNotFound
  - ValidationException
    - MissingRequiredField
    - InvalidFieldValue
    - BusinessRuleViolation
  - AccountingException
    - JournalEntryError
    - AccountNotFound
"""


class RimanERPException(Exception):
    """
    Base exception for all ERP errors
    
    All custom exceptions inherit from this to allow catching
    all ERP-specific errors with a single except clause.
    """
    
    def __init__(self, message, error_code=None, context=None):
        """
        Initialize exception with message, error code, and context
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., 'INV-001')
            context: Additional context dict for logging
        """
        self.message = message
        self.error_code = error_code or 'UNKNOWN'
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code and self.error_code != 'UNKNOWN':
            return f"[{self.error_code}] {self.message}"
        return self.message


class ContractException(RimanERPException):
    """Contract-related errors"""
    pass


class ContractLocked(ContractException):
    """
    Contract cannot be modified because it is locked
    
    Occurs when attempting to modify a contract that has been
    approved, completed, or explicitly locked.
    """
    
    def __init__(self, contract_number, reason=None):
        message = f"Contract {contract_number} is locked and cannot be modified."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(message, 'CTR-001', {'contract_number': contract_number})


class ContractValidationError(ContractException):
    """
    Contract fails validation before approval
    
    Occurs when contract doesn't meet business rule requirements
    """
    
    def __init__(self, contract_number, errors):
        if isinstance(errors, list):
            errors_str = "; ".join(errors)
        else:
            errors_str = str(errors)
        message = f"Contract {contract_number} validation failed: {errors_str}"
        super().__init__(message, 'CTR-002', {
            'contract_number': contract_number,
            'errors': errors if isinstance(errors, list) else [errors]
        })


class ContractNotFound(ContractException):
    """Contract reference not found"""
    
    def __init__(self, contract_id):
        message = f"Contract {contract_id} not found"
        super().__init__(message, 'CTR-003', {'contract_id': contract_id})


class InventoryException(RimanERPException):
    """Inventory-related errors"""
    pass


class NegativeStockException(InventoryException):
    """
    Operation would result in negative stock
    
    Occurs when attempting to remove more stock than available
    """
    
    def __init__(self, product_sku, current_stock, requested):
        message = f"Cannot create negative stock for {product_sku}. Current: {current_stock}, Requested removal: {requested}"
        super().__init__(message, 'INV-001', {
            'product_sku': product_sku,
            'current_stock': current_stock,
            'requested': requested
        })


class InsufficientStockException(InventoryException):
    """
    Stock is not available for requested operation
    
    Occurs when trying to reserve or sell more than available
    """
    
    def __init__(self, product_sku, available, requested):
        message = f"Insufficient stock for {product_sku}. Available: {available}, Requested: {requested}"
        super().__init__(message, 'INV-002', {
            'product_sku': product_sku,
            'available': available,
            'requested': requested
        })


class StockMovementLocked(InventoryException):
    """
    Stock movement cannot be modified (immutable)
    
    All stock movements are locked after creation for audit trail integrity
    """
    
    def __init__(self, movement_number):
        message = f"Stock movement {movement_number} is locked and cannot be modified or deleted"
        super().__init__(message, 'INV-003', {'movement_number': movement_number})


class RevenueRecognitionException(RimanERPException):
    """Revenue recognition errors"""
    pass


class InvalidRevenueRecognition(RevenueRecognitionException):
    """
    Revenue cannot be recognized due to unmet conditions
    
    Occurs when conditions for revenue recognition are not met
    """
    
    def __init__(self, invoice_id, reason):
        message = f"Revenue cannot be recognized for invoice {invoice_id}: {reason}"
        super().__init__(message, 'REV-001', {
            'invoice_id': invoice_id,
            'reason': reason
        })


class DeferredRevenueError(RevenueRecognitionException):
    """
    Error processing deferred revenue
    
    Occurs during deferred revenue recognition operations
    """
    
    def __init__(self, contract_id, error_detail):
        message = f"Deferred revenue processing failed for contract {contract_id}: {error_detail}"
        super().__init__(message, 'REV-002', {
            'contract_id': contract_id,
            'error_detail': error_detail
        })


class GLException(RimanERPException):
    """GL integrity errors"""
    pass


class GLMismatchException(GLException):
    """
    Journal entry debits do not equal credits
    
    All journal entries must balance (debits = credits)
    """
    
    def __init__(self, journal_number, debits, credits):
        discrepancy = abs(debits - credits)
        message = f"Journal entry {journal_number} does not balance. Debits: {debits}, Credits: {credits}, Discrepancy: {discrepancy}"
        super().__init__(message, 'GL-001', {
            'journal_number': journal_number,
            'debits': debits,
            'credits': credits,
            'discrepancy': discrepancy
        })


class GLPostingError(GLException):
    """
    Error posting to General Ledger
    
    Occurs during GL posting from accounting entries
    """
    
    def __init__(self, source_type, source_id, reason):
        message = f"GL posting failed for {source_type} {source_id}: {reason}"
        super().__init__(message, 'GL-002', {
            'source_type': source_type,
            'source_id': source_id,
            'reason': reason
        })


class UnbalancedEntry(GLException):
    """Entry would create unbalanced GL"""
    
    def __init__(self, entry_id, details):
        message = f"Entry {entry_id} creates unbalanced GL: {details}"
        super().__init__(message, 'GL-003', {
            'entry_id': entry_id,
            'details': details
        })


class PaymentException(RimanERPException):
    """Payment processing errors"""
    pass


class InvalidPaymentAmount(PaymentException):
    """
    Payment amount is invalid
    
    Occurs when payment amount is zero, negative, or exceeds maximum
    """
    
    def __init__(self, amount, reason):
        message = f"Invalid payment amount ${amount}: {reason}"
        super().__init__(message, 'PAY-001', {
            'amount': amount,
            'reason': reason
        })


class PaymentNotFound(PaymentException):
    """Payment record not found"""
    
    def __init__(self, payment_id):
        message = f"Payment {payment_id} not found"
        super().__init__(message, 'PAY-002', {'payment_id': payment_id})


class ValidationException(RimanERPException):
    """Business rule validation errors"""
    pass


class MissingRequiredField(ValidationException):
    """
    Required field is missing
    
    Occurs when required fields are not provided
    """
    
    def __init__(self, model_name, field_name):
        message = f"Required field missing on {model_name}: {field_name}"
        super().__init__(message, 'VAL-001', {
            'model_name': model_name,
            'field_name': field_name
        })


class InvalidFieldValue(ValidationException):
    """
    Field value does not meet validation rules
    
    Occurs when field value fails validation checks
    """
    
    def __init__(self, model_name, field_name, value, reason):
        message = f"Invalid value for {model_name}.{field_name}: {value} - {reason}"
        super().__init__(message, 'VAL-002', {
            'model_name': model_name,
            'field_name': field_name,
            'value': value,
            'reason': reason
        })


class BusinessRuleViolation(ValidationException):
    """
    Business rule has been violated
    
    Occurs when operation violates ERP business rules
    """
    
    def __init__(self, rule_name, details):
        message = f"Business rule violation: {rule_name} - {details}"
        super().__init__(message, 'VAL-003', {
            'rule_name': rule_name,
            'details': details
        })


class AccountingException(RimanERPException):
    """Accounting-specific errors"""
    pass


class JournalEntryError(AccountingException):
    """
    Error creating or processing journal entry
    
    General journal entry processing error
    """
    
    def __init__(self, reference, reason):
        message = f"Journal entry processing failed for {reference}: {reason}"
        super().__init__(message, 'ACC-001', {
            'reference': reference,
            'reason': reason
        })


class AccountNotFound(AccountingException):
    """GL account not found"""
    
    def __init__(self, account_code):
        message = f"GL account {account_code} not found"
        super().__init__(message, 'ACC-002', {'account_code': account_code})


class UnauthorizedException(RimanERPException):
    """
    User does not have permission for operation
    
    Occurs when attempting operation without proper authorization
    """
    
    def __init__(self, user, operation, resource=None):
        message = f"User '{user}' is not authorized to {operation}"
        if resource:
            message += f" on {resource}"
        super().__init__(message, 'AUTH-001', {
            'user': user,
            'operation': operation,
            'resource': resource
        })


class DatabaseIntegrityError(RimanERPException):
    """
    Database integrity error
    
    Occurs when database constraints or referential integrity is violated
    """
    
    def __init__(self, model_name, reason):
        message = f"Database integrity error on {model_name}: {reason}"
        super().__init__(message, 'DB-001', {
            'model_name': model_name,
            'reason': reason
        })
