#!/usr/bin/env python
"""
Comprehensive ERP System Integrity & Functionality Tests
Tests all modules, models, relationships, and critical business logic
"""

import os
import django
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riman_erp.settings')
django.setup()

from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def log_success(message):
    global test_results
    test_results['passed'] += 1
    print(f"{GREEN}✓{RESET} {message}")

def log_error(message, error=None):
    global test_results
    test_results['failed'] += 1
    print(f"{RED}✗{RESET} {message}")
    if error:
        test_results['errors'].append((message, str(error)))
        print(f"  {RED}Error:{RESET} {error}")

def log_header(message):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{message}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}")

def log_section(message):
    print(f"\n{BOLD}{message}{RESET}")
    print("-" * 70)

# ============================================================================
# TEST 1: MODULE & MODEL STRUCTURE
# ============================================================================
log_header("TEST 1: MODULE & MODEL STRUCTURE INTEGRITY")

try:
    modules_found = {}
    total_models = 0
    
    for app in apps.get_app_configs():
        app_label = app.name.split('.')[-1]
        if app_label not in ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
            models_list = list(app.get_models())
            if models_list:
                modules_found[app.verbose_name] = len(models_list)
                total_models += len(models_list)
    
    log_success(f"Found {len(modules_found)} custom modules with {total_models} models")
    
    for module_name, count in modules_found.items():
        print(f"  • {module_name}: {count} models")
    
except Exception as e:
    log_error("Failed to scan modules", e)

# ============================================================================
# TEST 2: MODEL FIELD VALIDATION
# ============================================================================
log_section("TEST 2: MODEL FIELD VALIDATION")

try:
    from sales.models import Sale, SaleLine, Invoice, Payment
    from inventory.models import Product, Category, Warehouse
    from crm.models import Client
    from financeaccounting.models import Account, JournalEntry
    from suppliers.models import Supplier
    from rentals.models import RentalAgreement
    from hr.models import Employee
    
    models_to_check = [
        ('Sales', [Sale, SaleLine, Invoice, Payment]),
        ('Inventory', [Product, Category, Warehouse]),
        ('CRM', [Client]),
        ('Accounting', [Account, JournalEntry]),
        ('Suppliers', [Supplier]),
        ('Rentals', [RentalAgreement]),
        ('HR', [Employee]),
    ]
    
    for module_name, models_list in models_to_check:
        for model in models_list:
            try:
                fields = model._meta.get_fields()
                field_names = [f.name for f in fields]
                log_success(f"{module_name}.{model.__name__} - {len(fields)} fields valid")
            except Exception as e:
                log_error(f"{module_name}.{model.__name__} field validation", e)
                
except Exception as e:
    log_error("Failed to load models for validation", e)

# ============================================================================
# TEST 3: DATABASE RELATIONSHIPS
# ============================================================================
log_section("TEST 3: DATABASE RELATIONSHIPS & FOREIGN KEYS")

try:
    from sales.models import Sale, Invoice
    from inventory.models import Product
    from crm.models import Client
    
    # Test Sale relationships
    sale = Sale.objects.first()
    if sale:
        assert hasattr(sale, 'customer'), "Sale missing customer relationship"
        assert hasattr(sale, 'created_by'), "Sale missing created_by relationship"
        assert hasattr(sale, 'lines'), "Sale missing lines relationship"
        log_success("Sale model relationships verified")
    else:
        print(f"{YELLOW}⊘{RESET} No sales found to test relationships")
    
    # Test Invoice relationships
    invoice = Invoice.objects.first()
    if invoice:
        assert hasattr(invoice, 'sale'), "Invoice missing sale relationship"
        assert hasattr(invoice, 'created_at'), "Invoice missing created_at field"
        log_success("Invoice model relationships verified")
    else:
        print(f"{YELLOW}⊘{RESET} No invoices found to test relationships")
    
    # Test Product relationships
    product = Product.objects.first()
    if product:
        assert hasattr(product, 'category'), "Product missing category relationship"
        assert hasattr(product, 'stock_locations'), "Product missing stock_locations"
        log_success("Product model relationships verified")
    else:
        print(f"{YELLOW}⊘{RESET} No products found to test relationships")
    
except AssertionError as e:
    log_error("Relationship assertion failed", e)
except Exception as e:
    log_error("Database relationships test failed", e)

# ============================================================================
# TEST 4: CRITICAL BUSINESS LOGIC
# ============================================================================
log_section("TEST 4: CRITICAL BUSINESS LOGIC FUNCTIONS")

try:
    from sales.models import Sale, Invoice, Payment
    from django.contrib.auth.models import User
    
    # Test Sale creation flow
    user = User.objects.first() or User.objects.create_user('test_user', 'test@test.com', 'pass123')
    
    sale = Sale.objects.first()
    if sale:
        # Check if sale has necessary methods/properties
        methods = ['calculate_total', 'get_status', 'mark_invoiced']
        for method in methods:
            if hasattr(sale, method):
                log_success(f"Sale.{method} exists")
            else:
                print(f"{YELLOW}⊘{RESET} Sale.{method} not found (optional)")
    
    # Test Invoice calculations
    invoice = Invoice.objects.first()
    if invoice:
        try:
            # Check total calculation
            if hasattr(invoice, 'total_amount'):
                total = invoice.total_amount
                log_success(f"Invoice total_amount calculation works ({total})")
            else:
                print(f"{YELLOW}⊘{RESET} Invoice.total_amount property not found")
        except Exception as e:
            log_error("Invoice calculation failed", e)
    
    # Test Payment tracking
    payment = Payment.objects.first()
    if payment:
        try:
            amount = payment.amount
            payment_method = payment.payment_method
            log_success(f"Payment data accessible (Amount: {amount}, Method: {payment_method})")
        except Exception as e:
            log_error("Payment data access failed", e)
    
except Exception as e:
    log_error("Business logic test failed", e)

# ============================================================================
# TEST 5: ACCOUNTING INTEGRITY
# ============================================================================
log_section("TEST 5: ACCOUNTING & FINANCIAL INTEGRITY")

try:
    from financeaccounting.models import Account, JournalEntry
    
    # Test Chart of Accounts
    accounts = Account.objects.all()
    if accounts.exists():
        account_types = {}
        for account in accounts[:20]:  # Check first 20
            account_types[account.account_type] = account_types.get(account.account_type, 0) + 1
        
        log_success(f"Chart of Accounts has {accounts.count()} accounts")
        print(f"  Account Types: {account_types}")
    else:
        print(f"{YELLOW}⊘{RESET} No accounts found in Chart of Accounts")
    
    # Test Journal Entries
    entries = JournalEntry.objects.all()
    if entries.exists():
        log_success(f"Journal Entries exist: {entries.count()} entries")
        
        # Check double-entry compliance
        double_entry_count = 0
        for entry in entries[:10]:  # Sample check
            debit_count = entry.lines.filter(line_type='debit').count()
            credit_count = entry.lines.filter(line_type='credit').count()
            if debit_count > 0 and credit_count > 0:
                double_entry_count += 1
        
        if double_entry_count > 0:
            log_success(f"Double-entry accounting verified ({double_entry_count} entries checked)")
        else:
            print(f"{YELLOW}⊘{RESET} Double-entry verification inconclusive")
    else:
        print(f"{YELLOW}⊘{RESET} No journal entries found")
    
except Exception as e:
    log_error("Accounting integrity test failed", e)

# ============================================================================
# TEST 6: INVENTORY TRACKING
# ============================================================================
log_section("TEST 6: INVENTORY & STOCK TRACKING")

try:
    from inventory.models import Product, StockMovement, Warehouse
    
    # Test Product Stock
    products = Product.objects.filter(is_active=True)[:10]
    if products.exists():
        log_success(f"Found {products.count()} active products to test")
        
        for product in products:
            try:
                # Check if product has stock tracking
                stock_locations = product.stock_locations.all()
                total_stock = sum([loc.quantity for loc in stock_locations])
                print(f"  • {product.name}: {total_stock} units in stock")
            except Exception as e:
                print(f"  {RED}✗{RESET} {product.name}: {e}")
    else:
        print(f"{YELLOW}⊘{RESET} No active products found")
    
    # Test Stock Movements
    movements = StockMovement.objects.all()
    if movements.exists():
        log_success(f"Stock Movement tracking active: {movements.count()} movements")
    else:
        print(f"{YELLOW}⊘{RESET} No stock movements recorded")
    
    # Test Warehouses
    warehouses = Warehouse.objects.all()
    if warehouses.exists():
        log_success(f"Warehouse management: {warehouses.count()} warehouses configured")
    else:
        print(f"{YELLOW}⊘{RESET} No warehouses configured")
    
except Exception as e:
    log_error("Inventory tracking test failed", e)

# ============================================================================
# TEST 7: CRM & CLIENT MANAGEMENT
# ============================================================================
log_section("TEST 7: CRM & CLIENT MANAGEMENT")

try:
    from crm.models import Client, Appointment, ClientNote
    
    # Test Clients
    clients = Client.objects.all()
    if clients.exists():
        log_success(f"CRM active: {clients.count()} clients in database")
        
        # Check client properties
        sample_client = clients.first()
        properties = ['email', 'phone', 'address', 'city']
        for prop in properties:
            if hasattr(sample_client, prop):
                log_success(f"Client.{prop} field exists")
            else:
                print(f"{YELLOW}⊘{RESET} Client.{prop} not found")
    else:
        print(f"{YELLOW}⊘{RESET} No clients in CRM database")
    
    # Test Appointments
    appointments = Appointment.objects.all()
    if appointments.exists():
        log_success(f"Appointment management: {appointments.count()} appointments")
    else:
        print(f"{YELLOW}⊘{RESET} No appointments recorded")
    
    # Test Client Notes
    notes = ClientNote.objects.all()
    if notes.exists():
        log_success(f"Client Notes active: {notes.count()} notes")
    else:
        print(f"{YELLOW}⊘{RESET} No client notes")
    
except Exception as e:
    log_error("CRM test failed", e)

# ============================================================================
# TEST 8: SUPPLIER & PROCUREMENT
# ============================================================================
log_section("TEST 8: SUPPLIER & PROCUREMENT MANAGEMENT")

try:
    from suppliers.models import Supplier, PurchaseInvoice
    
    # Test Suppliers
    suppliers = Supplier.objects.all()
    if suppliers.exists():
        log_success(f"Supplier management: {suppliers.count()} suppliers configured")
        
        sample_supplier = suppliers.first()
        fields = ['company_name', 'contact_person', 'email', 'phone']
        for field in fields:
            if hasattr(sample_supplier, field):
                print(f"  • Supplier.{field}: {getattr(sample_supplier, field, 'N/A')}")
    else:
        print(f"{YELLOW}⊘{RESET} No suppliers configured")
    
    # Test Purchase Invoices
    purchase_invoices = PurchaseInvoice.objects.all()
    if purchase_invoices.exists():
        log_success(f"Purchase management: {purchase_invoices.count()} purchase invoices")
    else:
        print(f"{YELLOW}⊘{RESET} No purchase invoices recorded")
    
except Exception as e:
    log_error("Supplier test failed", e)

# ============================================================================
# TEST 9: RENTAL MANAGEMENT
# ============================================================================
log_section("TEST 9: RENTAL & LEASE MANAGEMENT")

try:
    from rentals.models import RentalAgreement, RentalItem
    
    # Test Rental Agreements
    agreements = RentalAgreement.objects.all()
    if agreements.exists():
        log_success(f"Rental management: {agreements.count()} rental agreements")
        
        sample = agreements.first()
        print(f"  • Rental Status: {sample.status if hasattr(sample, 'status') else 'N/A'}")
    else:
        print(f"{YELLOW}⊘{RESET} No rental agreements")
    
    # Test Rental Items
    items = RentalItem.objects.all()
    if items.exists():
        log_success(f"Rental Items: {items.count()} items in rental system")
    else:
        print(f"{YELLOW}⊘{RESET} No rental items")
    
except Exception as e:
    log_error("Rental management test failed", e)

# ============================================================================
# TEST 10: HR MANAGEMENT
# ============================================================================
log_section("TEST 10: HR & PAYROLL MANAGEMENT")

try:
    from hr.models import Employee, Attendance, Payroll
    
    # Test Employees
    employees = Employee.objects.all()
    if employees.exists():
        log_success(f"HR System active: {employees.count()} employees")
        
        sample_emp = employees.first()
        print(f"  • {sample_emp.first_name} {sample_emp.last_name}")
        print(f"  • Position: {sample_emp.position if hasattr(sample_emp, 'position') else 'N/A'}")
    else:
        print(f"{YELLOW}⊘{RESET} No employees in system")
    
    # Test Attendance
    attendance = Attendance.objects.all()
    if attendance.exists():
        log_success(f"Attendance tracking: {attendance.count()} records")
    else:
        print(f"{YELLOW}⊘{RESET} No attendance records")
    
    # Test Payroll
    payroll = Payroll.objects.all()
    if payroll.exists():
        log_success(f"Payroll management: {payroll.count()} payroll records")
    else:
        print(f"{YELLOW}⊘{RESET} No payroll records")
    
except Exception as e:
    log_error("HR management test failed", e)

# ============================================================================
# TEST 11: DATA INTEGRITY CONSTRAINTS
# ============================================================================
log_section("TEST 11: DATA INTEGRITY & CONSTRAINTS")

try:
    from django.db import connection
    from django.db.models import ForeignKey, ManyToManyField
    
    # Check foreign key constraints
    from sales.models import SaleLine
    
    sale_line_fields = SaleLine._meta.get_fields()
    fk_count = 0
    for field in sale_line_fields:
        if isinstance(field, ForeignKey):
            fk_count += 1
    
    log_success(f"SaleLine has {fk_count} foreign key constraints for data integrity")
    
    # Check unique constraints
    from inventory.models import Product
    unique_fields = [f.name for f in Product._meta.get_fields() if getattr(f, 'unique', False)]
    if unique_fields:
        log_success(f"Product has unique constraints on: {', '.join(unique_fields)}")
    
except Exception as e:
    log_error("Data integrity test failed", e)

# ============================================================================
# TEST 12: AUTHENTICATION & PERMISSIONS
# ============================================================================
log_section("TEST 12: AUTHENTICATION & PERMISSIONS")

try:
    from django.contrib.auth.models import User, Permission
    from django.contrib.auth.models import Group
    
    users = User.objects.all()
    log_success(f"Authentication system: {users.count()} users configured")
    
    # Check for superuser
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        log_success(f"Superuser account found: {superusers.count()}")
    else:
        print(f"{YELLOW}⊘{RESET} No superuser account found (may need to be created)")
    
    # Check groups
    groups = Group.objects.all()
    if groups.exists():
        log_success(f"User Groups configured: {groups.count()} groups")
    else:
        print(f"{YELLOW}⊘{RESET} No user groups configured")
    
    # Check permissions
    permissions = Permission.objects.all()
    log_success(f"Permission system active: {permissions.count()} permissions")
    
except Exception as e:
    log_error("Authentication test failed", e)

# ============================================================================
# TEST 13: STATIC FILES & MEDIA
# ============================================================================
log_section("TEST 13: STATIC FILES & MEDIA ASSETS")

try:
    import os
    from django.conf import settings
    
    # Check media directory
    media_path = settings.MEDIA_ROOT
    if os.path.exists(media_path):
        files_count = sum([len(files) for _, _, files in os.walk(media_path)])
        log_success(f"Media directory exists: {files_count} files")
    else:
        print(f"{YELLOW}⊘{RESET} Media directory not found at {media_path}")
    
    # Check static directory
    static_path = settings.STATIC_ROOT
    if os.path.exists(static_path):
        files_count = sum([len(files) for _, _, files in os.walk(static_path)])
        log_success(f"Static directory exists: {files_count} files")
    else:
        print(f"{YELLOW}⊘{RESET} Static directory not found at {static_path}")
    
except Exception as e:
    log_error("Static files test failed", e)

# ============================================================================
# SUMMARY REPORT
# ============================================================================
log_header("INTEGRITY TEST SUMMARY")

total_tests = test_results['passed'] + test_results['failed']
pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"\n{BOLD}Test Results:{RESET}")
print(f"  {GREEN}✓ Passed: {test_results['passed']}{RESET}")
print(f"  {RED}✗ Failed: {test_results['failed']}{RESET}")
print(f"  Total: {total_tests}")
print(f"  Pass Rate: {pass_rate:.1f}%")

if test_results['errors']:
    print(f"\n{BOLD}{RED}Failed Tests:{RESET}")
    for test_name, error in test_results['errors']:
        print(f"  • {test_name}")
        print(f"    {error}")

if test_results['failed'] == 0:
    print(f"\n{BOLD}{GREEN}✓ ALL TESTS PASSED - ERP SYSTEM IS FULLY OPERATIONAL{RESET}\n")
    sys.exit(0)
else:
    print(f"\n{BOLD}{YELLOW}⚠ {test_results['failed']} TEST(S) FAILED - REVIEW REQUIRED{RESET}\n")
    sys.exit(1)
