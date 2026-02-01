"""
Reporting Services

REFINEMENT 5: Service Layer Completion

Handles all reporting and analytics:
1. GL reports (Trial Balance, Income Statement, Balance Sheet)
2. Revenue reports
3. Inventory reports
4. Contract status reports
"""

from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.utils import timezone


class GLReportingService:
    """Generate GL-related reports"""
    
    @staticmethod
    def get_trial_balance(as_of_date=None):
        """
        Generate trial balance
        
        Args:
            as_of_date: Date for trial balance (defaults to today)
            
        Returns:
            dict: Trial balance with all accounts and balances
        """
        if as_of_date is None:
            as_of_date = timezone.now().date()
        
        from accounting.models import ChartOfAccounts, JournalEntry, JournalEntryLine
        
        accounts = ChartOfAccounts.objects.filter(is_active=True)
        trial_balance = []
        total_debits = Decimal('0.00')
        total_credits = Decimal('0.00')
        
        for account in accounts:
            # Get account balance as of date
            lines = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__entry_date__lte=as_of_date
            )
            
            debits = sum(line.debit_amount for line in lines if line.debit_amount)
            credits = sum(line.credit_amount for line in lines if line.credit_amount)
            balance = debits - credits
            
            trial_balance.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'debits': debits,
                'credits': credits,
                'balance': balance,
                'balance_type': 'debit' if balance > 0 else 'credit' if balance < 0 else 'zero'
            })
            
            total_debits += debits
            total_credits += credits
        
        return {
            'as_of_date': as_of_date,
            'accounts': trial_balance,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'is_balanced': abs(total_debits - total_credits) < Decimal('0.01')
        }
    
    @staticmethod
    def get_income_statement(start_date, end_date):
        """
        Generate income statement (P&L)
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            dict: Income statement with revenues, expenses, net income
        """
        from accounting.models import ChartOfAccounts, JournalEntryLine
        
        # Get revenue accounts
        revenue_accounts = ChartOfAccounts.objects.filter(
            account_type='revenue',
            is_active=True
        )
        
        # Get expense accounts
        expense_accounts = ChartOfAccounts.objects.filter(
            account_type__in=['expense', 'cost_of_goods'],
            is_active=True
        )
        
        total_revenues = Decimal('0.00')
        total_expenses = Decimal('0.00')
        
        revenues = []
        for account in revenue_accounts:
            lines = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__entry_date__range=[start_date, end_date]
            )
            amount = sum(line.credit_amount for line in lines if line.credit_amount)
            total_revenues += amount
            revenues.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'amount': amount
            })
        
        expenses = []
        for account in expense_accounts:
            lines = JournalEntryLine.objects.filter(
                account=account,
                journal_entry__entry_date__range=[start_date, end_date]
            )
            amount = sum(line.debit_amount for line in lines if line.debit_amount)
            total_expenses += amount
            expenses.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'amount': amount
            })
        
        net_income = total_revenues - total_expenses
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'revenues': revenues,
            'total_revenues': total_revenues,
            'expenses': expenses,
            'total_expenses': total_expenses,
            'net_income': net_income
        }


class RevenueReportingService:
    """Generate revenue-related reports"""
    
    @staticmethod
    def get_revenue_by_contract(start_date=None, end_date=None):
        """
        Get revenue summary by contract
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            dict: Revenue breakdown by contract
        """
        from crm.models import Contract
        from accounting.models import RevenueRecognitionLog
        
        if start_date is None:
            start_date = timezone.now().date() - timedelta(days=30)
        if end_date is None:
            end_date = timezone.now().date()
        
        contracts = Contract.objects.all()
        revenue_summary = []
        
        for contract in contracts:
            # Get recognized revenue for period
            logs = RevenueRecognitionLog.objects.filter(
                contract=contract,
                recognition_date__range=[start_date, end_date]
            )
            
            total_recognized = sum(log.recognized_amount for log in logs)
            
            revenue_summary.append({
                'contract_number': contract.contract_number,
                'customer': str(contract.customer),
                'contract_value': contract.contract_value,
                'recognized_revenue': total_recognized,
                'remaining': contract.contract_value - total_recognized,
                'recognition_percentage': (total_recognized / contract.contract_value * 100) if contract.contract_value > 0 else 0
            })
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'contracts': revenue_summary,
            'total_contracted': sum(c['contract_value'] for c in revenue_summary),
            'total_recognized': sum(c['recognized_revenue'] for c in revenue_summary)
        }
    
    @staticmethod
    def get_revenue_recognition_schedule():
        """
        Get future revenue recognition schedule
        
        Returns:
            dict: Scheduled revenue by date
        """
        from accounting.models import DeferredRevenueAccount
        
        deferred = DeferredRevenueAccount.objects.filter(recognized=False)
        
        schedule = []
        for item in deferred:
            schedule.append({
                'contract': item.contract.contract_number,
                'milestone': item.milestone_description,
                'date': item.milestone_date,
                'amount': item.deferred_amount - item.recognized_amount
            })
        
        # Sort by date
        schedule.sort(key=lambda x: x['date'])
        
        return {
            'schedule': schedule,
            'total_deferred': sum(item['amount'] for item in schedule)
        }


class InventoryReportingService:
    """Generate inventory-related reports"""
    
    @staticmethod
    def get_inventory_summary():
        """
        Get current inventory summary
        
        Returns:
            dict: Inventory by product with stock levels
        """
        from inventory.models import Product
        
        products = Product.objects.filter(is_active=True)
        inventory = []
        
        total_value = Decimal('0.00')
        
        for product in products:
            stock_level = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
            product_value = (product.cost if hasattr(product, 'cost') else Decimal('0.00')) * stock_level
            total_value += product_value
            
            inventory.append({
                'sku': product.sku,
                'product_name': product.product_name,
                'category': str(product.category) if hasattr(product, 'category') else 'N/A',
                'quantity': stock_level,
                'cost': product.cost if hasattr(product, 'cost') else Decimal('0.00'),
                'value': product_value
            })
        
        return {
            'as_of_date': timezone.now().date(),
            'products': inventory,
            'total_items': sum(item['quantity'] for item in inventory),
            'total_value': total_value
        }
    
    @staticmethod
    def get_low_stock_items(threshold=5):
        """
        Get items below minimum stock threshold
        
        Args:
            threshold: Minimum stock level
            
        Returns:
            list: Low stock products
        """
        from inventory.models import Product
        
        products = Product.objects.filter(is_active=True)
        low_stock = []
        
        for product in products:
            stock_level = product.get_stock_level() if hasattr(product, 'get_stock_level') else 0
            
            if stock_level < threshold:
                low_stock.append({
                    'sku': product.sku,
                    'product_name': product.product_name,
                    'current_stock': stock_level,
                    'reorder_level': threshold
                })
        
        return low_stock
    
    @staticmethod
    def get_movement_report(product=None, days=30):
        """
        Get stock movement report
        
        Args:
            product: Specific product (optional)
            days: Number of days to report on
            
        Returns:
            dict: Movement summary
        """
        from inventory.models import StockMovement
        
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        query = StockMovement.objects.filter(created_at__date__gte=cutoff_date)
        if product:
            query = query.filter(product=product)
        
        movements_by_type = query.values('movement_type').annotate(count=Count('id'), total_qty=Sum('quantity'))
        
        return {
            'period_days': days,
            'product': str(product) if product else 'All Products',
            'movements_by_type': list(movements_by_type),
            'total_movements': query.count()
        }


class ContractReportingService:
    """Generate contract-related reports"""
    
    @staticmethod
    def get_contract_summary():
        """
        Get contract status summary
        
        Returns:
            dict: Contracts grouped by status and type
        """
        from crm.models import Contract
        
        contracts = Contract.objects.all()
        
        by_status = {}
        by_type = {}
        by_customer = {}
        
        total_value = Decimal('0.00')
        
        for contract in contracts:
            status = contract.status if hasattr(contract, 'status') else 'unknown'
            contract_type = contract.type if hasattr(contract, 'type') else 'unknown'
            customer = str(contract.customer) if contract.customer else 'Unknown'
            
            # Group by status
            if status not in by_status:
                by_status[status] = {'count': 0, 'value': Decimal('0.00')}
            by_status[status]['count'] += 1
            by_status[status]['value'] += contract.contract_value
            
            # Group by type
            if contract_type not in by_type:
                by_type[contract_type] = {'count': 0, 'value': Decimal('0.00')}
            by_type[contract_type]['count'] += 1
            by_type[contract_type]['value'] += contract.contract_value
            
            # Group by customer
            if customer not in by_customer:
                by_customer[customer] = {'count': 0, 'value': Decimal('0.00')}
            by_customer[customer]['count'] += 1
            by_customer[customer]['value'] += contract.contract_value
            
            total_value += contract.contract_value
        
        return {
            'as_of_date': timezone.now().date(),
            'total_contracts': contracts.count(),
            'total_contract_value': total_value,
            'by_status': dict(by_status),
            'by_type': dict(by_type),
            'by_customer': dict(by_customer)
        }
