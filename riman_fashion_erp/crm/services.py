"""
Contract and Revenue Services

REFINEMENT 5: Service Layer Completion

Handles all contract revenue operations and validations:
1. Revenue recognition schedules
2. Contract validation business rules
3. Design approval workflows
"""

from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta


class ContractRevenueService:
    """
    Manage revenue recognition per contract
    
    Calculates revenue schedules for different contract types:
    - Standard rental: monthly installments
    - Custom sale: milestone-based (50% deposit, 50% final)
    - Custom rental: upfront security deposit + rental payments
    """
    
    @staticmethod
    def calculate_revenue_recognition_schedule(contract):
        """
        Generate revenue schedule for contract based on type
        
        Args:
            contract: Contract instance
            
        Returns:
            list: Revenue milestones with dates and amounts
        """
        schedule = []
        
        if contract.contract_type == 'custom_sale':
            # Custom sale: 50% on signing, 50% on completion
            schedule = [
                {
                    'date': contract.created_at.date(),
                    'amount': contract.total_price * Decimal('0.5'),
                    'type': 'deposit',
                    'description': 'Deposit on custom sale contract'
                },
                {
                    'date': contract.estimated_completion if hasattr(contract, 'estimated_completion') else contract.created_at.date() + timedelta(days=30),
                    'amount': contract.total_price * Decimal('0.5'),
                    'type': 'final',
                    'description': 'Final payment on custom sale contract'
                }
            ]
        
        elif contract.contract_type == 'custom_rent':
            # Custom rent: deposit upfront, rental revenue per month
            schedule = [
                {
                    'date': contract.rental_start_date if hasattr(contract, 'rental_start_date') else contract.created_at.date(),
                    'amount': contract.security_deposit,
                    'type': 'deposit',
                    'description': 'Security deposit for custom rental'
                }
            ]
            
            # Add monthly rental payments if applicable
            if hasattr(contract, 'rental_end_date') and hasattr(contract, 'monthly_rental'):
                start = contract.rental_start_date
                end = contract.rental_end_date
                current = start
                
                while current < end:
                    schedule.append({
                        'date': current,
                        'amount': contract.monthly_rental,
                        'type': 'monthly',
                        'description': f'Monthly rental for {current.strftime("%B %Y")}'
                    })
                    current = current + timedelta(days=30)
        
        elif contract.contract_type == 'rental':
            # Standard rental: monthly fixed amount
            if hasattr(contract, 'rental_start_date') and hasattr(contract, 'rental_end_date') and hasattr(contract, 'monthly_rental'):
                start = contract.rental_start_date
                end = contract.rental_end_date
                current = start
                
                while current < end:
                    schedule.append({
                        'date': current,
                        'amount': contract.monthly_rental,
                        'type': 'monthly',
                        'description': f'Monthly rental for {current.strftime("%B %Y")}'
                    })
                    current = current + timedelta(days=30)
        
        return schedule
    
    @staticmethod
    def get_total_revenue_to_recognize(contract):
        """
        Calculate total revenue to be recognized for contract
        
        Args:
            contract: Contract instance
            
        Returns:
            Decimal: Total revenue amount
        """
        schedule = ContractRevenueService.calculate_revenue_recognition_schedule(contract)
        return sum(item['amount'] for item in schedule)
    
    @staticmethod
    def recognize_revenue_for_invoice(invoice, user):
        """
        Recognize revenue when invoice conditions are met
        
        Args:
            invoice: Invoice instance
            user: User performing the recognition
            
        Raises:
            ValueError: If revenue cannot be recognized yet
        """
        if not hasattr(invoice, 'can_recognize_revenue'):
            raise ValueError("Invoice does not support revenue recognition")
        
        if not invoice.can_recognize_revenue():
            raise ValueError("Revenue cannot be recognized yet")
        
        # Call invoice's revenue recognition method
        if hasattr(invoice, 'recognize_revenue'):
            invoice.recognize_revenue(user)
        else:
            raise ValueError("Invoice does not support revenue recognition method")


class ContractValidationService:
    """
    Validate all contract business rules
    
    Ensures contracts meet:
    - Required fields for type
    - Date consistency
    - Stock availability for rentals
    - Pricing validation
    """
    
    @staticmethod
    def validate_contract_before_approval(contract):
        """
        Check all rules before contract approval
        
        Args:
            contract: Contract instance to validate
            
        Returns:
            list: List of error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        if not contract.client:
            errors.append("Client is required")
        if not contract.product:
            errors.append("Product is required")
        if contract.total_price <= 0:
            errors.append("Contract value must be greater than 0")
        
        # Type-specific validation
        if contract.contract_type in ['rental', 'custom_rent']:
            if not hasattr(contract, 'rental_start_date') or not contract.rental_start_date:
                errors.append("Rental start date required")
            if not hasattr(contract, 'rental_end_date') or not contract.rental_end_date:
                errors.append("Rental end date required")
            
            if hasattr(contract, 'rental_end_date') and hasattr(contract, 'rental_start_date') and contract.rental_start_date and contract.rental_end_date:
                if contract.rental_end_date <= contract.rental_start_date:
                    errors.append("End date must be after start date")
            
            if not hasattr(contract, 'security_deposit') or contract.security_deposit <= 0:
                errors.append("Security deposit required for rentals")
        
        if contract.contract_type in ['custom_sale', 'custom_rent']:
            if not hasattr(contract, 'design_notes') or not contract.design_notes:
                errors.append("Design specifications required for custom items")
            if not hasattr(contract, 'measurements') or not contract.measurements:
                errors.append("Measurements required for custom items")
        
        # Check rental date conflicts
        if contract.contract_type == 'rental' and hasattr(contract, 'validate_rental_dates'):
            if not contract.validate_rental_dates():
                errors.append("Rental dates conflict with existing rental")
        
        # Verify stock availability
        errors.extend(ContractValidationService._validate_stock_availability(contract))
        
        return errors
    
    @staticmethod
    def _validate_stock_availability(contract):
        """
        Check if product stock is available for rental
        
        Args:
            contract: Contract to validate
            
        Returns:
            list: Error messages if stock unavailable
        """
        errors = []
        
        if contract.contract_type in ['rental', 'custom_rent']:
            try:
                from inventory.models import Product
                product = contract.product
                
                if not product:
                    errors.append("Product not found")
                    return errors
                
                # For rentals, we need to check available quantity during rental period
                if hasattr(product, 'get_available_quantity'):
                    available = product.get_available_quantity()
                    if available < 1:
                        errors.append(f"Product not in stock. Available: {available}")
            
            except Exception as e:
                errors.append(f"Error checking stock availability: {str(e)}")
        
        return errors
    
    @staticmethod
    def validate_contract_modification(contract):
        """
        Validate that contract can be modified
        
        Args:
            contract: Contract to validate for modification
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if hasattr(contract, 'status') and contract.status in ['approved', 'completed', 'cancelled']:
            return False, f"Cannot modify contract in {contract.status} status"
        
        if hasattr(contract, 'is_locked') and contract.is_locked:
            return False, "Contract is locked and cannot be modified"
        
        return True, "Contract can be modified"


class DesignApprovalService:
    """
    Manage design approval workflow for custom contracts
    
    Handles:
    - Design creation and updates
    - Customer approval requests
    - Design locking after approval
    - Design history tracking
    """
    
    @staticmethod
    def can_approve_design(contract, user):
        """
        Check if user can approve design for contract
        
        Args:
            contract: Contract with design to approve
            user: User attempting approval
            
        Returns:
            tuple: (can_approve: bool, reason: str)
        """
        if not hasattr(contract, 'design_notes') or not contract.design_notes:
            return False, "Design notes not provided"
        
        if hasattr(contract, 'design_approved') and contract.design_approved:
            return False, "Design already approved"
        
        # Check if user has permission (customer or admin)
        if hasattr(user, 'is_staff') and user.is_staff:
            return True, "Admin can approve designs"
        
        if hasattr(contract, 'customer') and contract.customer:
            if hasattr(contract.customer, 'user') and contract.customer.user == user:
                return True, "Customer can approve their own design"
        
        return False, "User does not have permission to approve this design"
    
    @staticmethod
    def approve_design(contract, user):
        """
        Approve design for contract
        
        Args:
            contract: Contract with design to approve
            user: User approving
            
        Returns:
            bool: Success status
        """
        can_approve, reason = DesignApprovalService.can_approve_design(contract, user)
        
        if not can_approve:
            raise ValueError(reason)
        
        if hasattr(contract, 'approve_design'):
            contract.approve_design(user)
            return True
        else:
            raise ValueError("Contract does not support design approval")
    
    @staticmethod
    def request_design_revision(contract, revision_notes, user):
        """
        Request design revision from customer
        
        Args:
            contract: Contract needing revision
            revision_notes: What needs to be revised
            user: User requesting revision
            
        Returns:
            bool: Success status
        """
        if hasattr(contract, 'design_approved') and contract.design_approved:
            raise ValueError("Cannot request revision on approved design")
        
        # Store revision request
        if hasattr(contract, 'design_notes'):
            contract.design_notes = f"{contract.design_notes}\n\n[REVISION REQUEST - {user.username}]: {revision_notes}"
            contract.save()
            return True
        
        raise ValueError("Contract does not support design revisions")
