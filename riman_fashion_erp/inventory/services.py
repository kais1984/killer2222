"""
Inventory Services

REFINEMENT 5: Service Layer Completion

Handles all inventory operations:
1. Stock reservation for rentals
2. Stock release and returns
3. Sale inventory movements
4. Stock level tracking and validation
"""

from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError


class InventoryService:
    """
    Manage all inventory operations
    
    Provides atomic operations for:
    - Stock reservation for rentals
    - Stock release and returns
    - Sale transactions
    - Transfer between warehouses
"""
    
    @staticmethod
    def reserve_stock(product, quantity, contract, created_by, warehouse=None):
        """
        Reserve stock for rental contract
        
        Args:
            product: Product to reserve
            quantity: Quantity to reserve
            contract: Contract associated with reservation
            created_by: User performing reservation
            warehouse: Warehouse to reserve from (optional)
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity <= 0:
            raise ValueError("Reservation quantity must be positive")
        
        # Get current stock level
        current_balance = product.quantity_in_stock
        
        if current_balance < quantity:
            raise ValueError(f"Insufficient stock. Available: {current_balance}, Requested: {quantity}")
        
        new_balance = current_balance - quantity
        
        movement = StockMovement(
            product=product,
            movement_type='reserve',
            quantity=quantity,
            from_warehouse=warehouse,
            reference_type='contract',
            reference_number=contract.contract_number if hasattr(contract, 'contract_number') else str(contract.id),
            balance_before=current_balance,
            balance_after=new_balance,
            created_by=created_by,
            notes=f"Reserved for contract {contract.contract_number if hasattr(contract, 'contract_number') else contract.id}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def release_stock(product, quantity, contract, reason, created_by, warehouse=None):
        """
        Release reserved stock back to inventory
        
        Args:
            product: Product to release
            quantity: Quantity to release
            contract: Contract associated with release
            reason: Reason for release (return, cancellation, etc.)
            created_by: User performing release
            warehouse: Warehouse to release to (optional)
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity <= 0:
            raise ValueError("Release quantity must be positive")
        
        # Get current stock level
        current_balance = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
        new_balance = current_balance + quantity
        
        movement = StockMovement(
            product=product,
            movement_type='release',
            quantity=quantity,
            to_warehouse=warehouse,
            reference_type='contract',
            reference_number=contract.contract_number if hasattr(contract, 'contract_number') else str(contract.id),
            balance_before=current_balance,
            balance_after=new_balance,
            created_by=created_by,
            notes=f"Released from contract {contract.contract_number if hasattr(contract, 'contract_number') else contract.id}: {reason}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def record_sale(product, quantity, sale, created_by, warehouse=None):
        """
        Record stock movement for sale
        
        Args:
            product: Product sold
            quantity: Quantity sold
            sale: Sale associated with movement
            created_by: User recording sale
            warehouse: Warehouse stock taken from (optional)
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity <= 0:
            raise ValueError("Sale quantity must be positive")
        
        # Get current stock level
        current_balance = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
        
        if current_balance < quantity:
            raise ValueError(f"Insufficient stock for sale. Available: {current_balance}, Requested: {quantity}")
        
        new_balance = current_balance - quantity
        sale_number = sale.sale_number if hasattr(sale, 'sale_number') else sale.id
        
        movement = StockMovement(
            product=product,
            movement_type='sale',
            quantity=quantity,
            from_warehouse=warehouse,
            reference_type='sale',
            reference_number=str(sale_number),
            balance_before=current_balance,
            balance_after=new_balance,
            created_by=created_by,
            notes=f"Sale transaction {sale_number}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def record_purchase(product, quantity, warehouse, purchase_order, created_by):
        """
        Record stock receipt from purchase
        
        Args:
            product: Product received
            quantity: Quantity received
            warehouse: Warehouse receiving stock
            purchase_order: Purchase order for receipt
            created_by: User recording receipt
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity <= 0:
            raise ValueError("Purchase quantity must be positive")
        
        # Get current stock level
        current_balance = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
        new_balance = current_balance + quantity
        
        po_number = purchase_order if isinstance(purchase_order, str) else str(purchase_order)
        
        movement = StockMovement(
            product=product,
            movement_type='purchase',
            quantity=quantity,
            to_warehouse=warehouse,
            reference_type='purchase',
            reference_number=po_number,
            balance_before=current_balance,
            balance_after=new_balance,
            created_by=created_by,
            notes=f"Purchase receipt for PO {po_number}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def record_return(product, quantity, sale, reason, created_by, warehouse=None):
        """
        Record stock return from customer
        
        Args:
            product: Product being returned
            quantity: Quantity returned
            sale: Original sale transaction
            reason: Reason for return (damage, defect, wrong item, etc.)
            created_by: User recording return
            warehouse: Warehouse to receive return (optional)
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity <= 0:
            raise ValueError("Return quantity must be positive")
        
        # Get current stock level
        current_balance = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
        new_balance = current_balance + quantity
        
        sale_number = sale.sale_number if hasattr(sale, 'sale_number') else sale.id
        
        movement = StockMovement(
            product=product,
            movement_type='return',
            quantity=quantity,
            to_warehouse=warehouse,
            reference_type='sale',
            reference_number=str(sale_number),
            balance_before=current_balance,
            balance_after=new_balance,
            created_by=created_by,
            notes=f"Return from sale {sale_number}: {reason}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def transfer_between_warehouses(product, quantity, from_warehouse, to_warehouse, created_by):
        """
        Record transfer between warehouses
        
        Args:
            product: Product to transfer
            quantity: Quantity to transfer
            from_warehouse: Source warehouse
            to_warehouse: Destination warehouse
            created_by: User performing transfer
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity <= 0:
            raise ValueError("Transfer quantity must be positive")
        
        if from_warehouse == to_warehouse:
            raise ValueError("Source and destination warehouses cannot be the same")
        
        # Get current stock level
        current_balance = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
        
        # Balance doesn't change on transfer, but we record it for audit
        movement = StockMovement(
            product=product,
            movement_type='transfer',
            quantity=quantity,
            from_warehouse=from_warehouse,
            to_warehouse=to_warehouse,
            reference_type='transfer',
            reference_number=f"{from_warehouse.code}-to-{to_warehouse.code}" if hasattr(from_warehouse, 'code') else "TRANSFER",
            balance_before=current_balance,
            balance_after=current_balance,  # Balance unchanged, just location changes
            created_by=created_by,
            notes=f"Transfer from {from_warehouse} to {to_warehouse}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def adjust_stock(product, quantity_change, warehouse, reason, created_by):
        """
        Record stock adjustment (damage, loss, reconciliation)
        
        Args:
            product: Product being adjusted
            quantity_change: Quantity change (positive or negative)
            warehouse: Warehouse with adjustment
            reason: Reason for adjustment
            created_by: User performing adjustment
            
        Returns:
            StockMovement: The created movement record
        """
        from inventory.models import StockMovement
        
        if quantity_change == 0:
            raise ValueError("Adjustment quantity cannot be zero")
        
        # Get current stock level
        current_balance = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
        new_balance = current_balance + quantity_change
        
        if new_balance < 0:
            raise ValueError(f"Adjustment would result in negative stock: {new_balance}")
        
        # Determine movement type based on change direction
        if quantity_change < 0:
            movement_type = 'damage' if 'damage' in reason.lower() or 'loss' in reason.lower() else 'adjustment'
        else:
            movement_type = 'adjustment'
        
        movement = StockMovement(
            product=product,
            movement_type=movement_type,
            quantity=abs(quantity_change),
            from_warehouse=warehouse if quantity_change < 0 else None,
            to_warehouse=warehouse if quantity_change > 0 else None,
            reference_type='adjustment',
            reference_number=f"ADJ-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            balance_before=current_balance,
            balance_after=new_balance,
            created_by=created_by,
            notes=f"Stock adjustment: {reason}"
        )
        
        movement.save()
        return movement
    
    @staticmethod
    def get_stock_level(product):
        """
        Get current stock level for product
        
        Args:
            product: Product to check
            
        Returns:
            int: Current stock quantity
        """
        if hasattr(product, 'get_stock_level'):
            return product.get_stock_level()
        
        from inventory.models import StockMovement
        
        # Calculate from movements
        movements = StockMovement.objects.filter(product=product)
        total = 0
        
        for movement in movements:
            if hasattr(movement, 'balance_after'):
                total = movement.balance_after
        
        return max(0, total)
    
    @staticmethod
    def get_movement_history(product, limit=50):
        """
        Get movement history for product
        
        Args:
            product: Product to get history for
            limit: Maximum number of records to return
            
        Returns:
            QuerySet: Recent movements ordered by date
        """
        from inventory.models import StockMovement
        
        return StockMovement.objects.filter(product=product).order_by('-created_at')[:limit]
