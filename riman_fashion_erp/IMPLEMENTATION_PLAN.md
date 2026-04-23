# RIMAN FASHION ERP - Implementation Plan
**Status**: IN PROGRESS | **Date**: January 26, 2026 | **Version**: 1.0

---

## PHASE 1: CORE BUSINESS FLOW (CRITICAL - FOUNDATION)
**Objective**: Perfect Sale → Invoice → Payment → Inventory Update → Accounting Entries

### 1.1 Validate Sale Model Structure ✓
- [x] Sale model exists with sale_number, customer, subtotal, tax, total_amount
- [x] SaleLine model links product, quantity, unit_price, line_total
- [x] Read-only calculated fields (subtotal, tax, total_amount, line_total)
- [x] Soft delete support (cancelled_at, cancelled_by)
- [x] Status derivation from payments (not stored)
- [x] Payment status derivation (unpaid, partial, paid)

### 1.2 Validate Invoice Model ✓
**Files to check**: sales/models.py (Invoice, InvoiceLine)
- [ ] Invoice auto-generated from Sale (one sale → one invoice)
- [ ] Invoice number auto-generated (INV-YYYYMMDD-XXXXX)
- [ ] Invoice immutable once created
- [ ] Invoice.total_amount copies Sale.total_amount (immutable snapshot)
- [ ] Invoice status derived from payments
- [ ] Prevent duplicate invoicing of same sale

### 1.3 Validate Payment Model ✓
**Files to check**: sales/models.py (Payment)
- [ ] Payment method (cash, check, bank transfer, credit)
- [ ] Payment date, amount, reference
- [ ] Link to Invoice and Sale
- [ ] Payment reversals (reversal tracking, not deletion)
- [ ] Payment reconciliation (matched, unmatched)

### 1.4 Enforce Accounting Entries on Payment
**Files to check**: sales/models.py (Payment.save()), financeaccounting/models.py
- [ ] Payment creation triggers JournalEntry
  - Debit: Cash/Bank Account (+payment method)
  - Credit: Accounts Receivable (-invoice balance)
- [ ] Payment reversal triggers reversal JournalEntry
  - Debit: Accounts Receivable (reverse credit)
  - Credit: Cash/Bank (reverse debit)
- [ ] JournalEntry is IMMUTABLE (no editing after creation)

### 1.5 Enforce Stock Reduction on Sale Invoicing
**Files to check**: sales/models.py (Invoice.save()), financeaccounting/models.py (StockMovement)
- [ ] Invoice creation triggers StockMovement for each line item
- [ ] StockMovement reduces Product.quantity_on_hand
- [ ] StockMovement creates JournalEntry:
  - Debit: COGS (Cost of Goods Sold)
  - Credit: Inventory (product cost)
- [ ] Stock movement is traceable and reversible (via reversal entry)

### 1.6 Enforce Revenue & COGS on Sale Invoicing
**Files to check**: sales/models.py (Invoice.save()), financeaccounting/models.py
- [ ] Sale invoicing triggers JournalEntry:
  - Debit: Accounts Receivable (total invoice amount)
  - Credit: Sales Revenue (sale revenue)
- [ ] Tax amount posted separately:
  - Debit: Accounts Receivable (tax portion)
  - Credit: Sales Tax Payable

---

## PHASE 2: EXPENSE SYSTEM (CRITICAL)
**Objective**: Implement expense categories, GL mapping, and auto-posting

### 2.1 Enhance Expense Model
**Files**: accounting/models.py → Enhance Expense class
```
REQUIREMENTS:
- expense_date
- expense_category (FK to ExpenseCategory)
- amount
- payment_method (cash, bank, payable)
- supplier (optional FK)
- product_id (optional - for inventory-creating expenses)
- rental_id (optional - for maintenance/cleaning)
- status (draft, posted, reversed)
- notes
- receipt_file (media upload)
- created_by, approved_by (audit trail)
```

### 2.2 Create ExpenseCategory Model
**Files**: accounting/models.py → Add ExpenseCategory class
```
FIELDS:
- category_name (e.g., "Operating Expenses", "COGS", "Marketing")
- gl_account (FK to ChartOfAccounts - expense account)
- payment_account (FK to ChartOfAccounts - asset/liability account)
- affects_inventory (boolean)
- description
- is_active
```

MAPPINGS:
- Operating Expenses → Account 6100
- COGS → Account 5100
- Marketing → Account 6200
- Maintenance & Cleaning → Account 6300
- Administrative → Account 6400

### 2.3 Expense Posting Logic
**Files**: accounting/models.py → Expense.post() method
```
LOGIC:
1. Only "posted" expenses create journal entries
2. Cannot edit posted expenses (reversals only)
3. Posting creates JournalEntry:
   - Debit: Expense category GL account
   - Credit: Payment method account (cash, bank, or AP)
4. If inventory-creating:
   - Additional Debit: Inventory Asset
   - Additional Credit: Expense account
5. JournalEntry marked with reference to Expense ID
6. audit_trail logs who posted, when
```

### 2.4 Expense Reversal Logic
**Files**: accounting/models.py → Expense.reverse() method
```
LOGIC:
1. Create new Expense with reversed=True
2. Original JournalEntry marked with reversal reference
3. Reversal JournalEntry created:
   - Opposite of original (flip debits/credits)
4. Both entries remain immutable in ledger
5. Net effect cancels but audit trail preserved
```

---

## PHASE 3: ACCOUNTING INTEGRITY (NON-NEGOTIABLE)
**Objective**: Enforce double-entry, prevent data corruption

### 3.1 Enhance Account Model
**Files**: financeaccounting/models.py → Account class
- [x] Chart of Accounts structure exists
- [ ] Normal balance derivation (debit/credit based on account type)
- [ ] Account.get_balance() calculation is correct
- [ ] Add account.get_balance_as_of(date) for period reporting

### 3.2 Enhance JournalEntry Model
**Files**: financeaccounting/models.py → JournalEntry class
- [x] Structure exists
- [ ] JournalEntry.is_balanced property (debits == credits)
- [ ] Prevent unbalanced JournalEntry saves
- [ ] Make JournalEntry immutable (no .delete() or .update())
- [ ] Add audit_trail (created_by, created_at, posted_at)

### 3.3 Add StockMovement Model
**Files**: financeaccounting/models.py → Add StockMovement class
```
FIELDS:
- stock_movement_number (auto-generated)
- product (FK)
- quantity_change (positive or negative)
- movement_type (sale, purchase, adjustment, return)
- reference_type (sale_id, invoice_id, purchase_order_id)
- movement_date
- created_by, created_at
- journal_entry (FK to JournalEntry - immutable link)

IMMUTABLE: No edits after creation. Corrections via reversal.
```

### 3.4 Add Reconciliation Tracking
**Files**: financeaccounting/models.py → Add BankReconciliation class
```
FIELDS:
- reconciliation_month
- bank_statement_balance
- reconciliation_items (M2M to JournalEntry)
- reconciled_by, reconciled_at
- status (draft, reconciled, locked)

PURPOSE: Match bank statement to ledger entries
AUDIT: Preserve reconciliation history
```

### 3.5 Trial Balance & Financial Statements
**Files**: financeaccounting/views.py & financeaccounting/services.py
- [ ] TrialBalance service (sums all accounts, debits == credits)
- [ ] IncomeStatement service (revenues - expenses = net income)
- [ ] BalanceSheet service (assets = liabilities + equity)
- [ ] CashFlowStatement service (operations, investing, financing)
- [ ] All must reconcile to JournalEntry totals

---

## PHASE 4: DATABASE & MODELS AUDIT
**Objective**: Ensure all models are properly structured

### 4.1 Model Inventory
- [x] Sale → sales/models.py
- [x] SaleLine → sales/models.py
- [x] Invoice → sales/models.py (verify exists)
- [x] Payment → sales/models.py (verify exists)
- [x] Product → inventory/models.py
- [x] StockMovement → financeaccounting/models.py (create if missing)
- [x] Expense → accounting/models.py
- [x] ExpenseCategory → accounting/models.py (create if missing)
- [x] Account (ChartOfAccounts) → accounting/models.py OR financeaccounting/models.py
- [x] JournalEntry → accounting/models.py OR financeaccounting/models.py
- [x] Client → crm/models.py
- [x] Supplier → suppliers/models.py

### 4.2 Model Relationships Review
- [ ] Sale.customer → Client (FK, PROTECT)
- [ ] SaleLine.sale → Sale (FK, CASCADE)
- [ ] SaleLine.product → Product (FK, PROTECT)
- [ ] Invoice.sale → Sale (FK, PROTECT, one-to-one)
- [ ] InvoiceLine.invoice → Invoice (FK, CASCADE)
- [ ] InvoiceLine.product → Product (FK, PROTECT)
- [ ] Payment.invoice → Invoice (FK, CASCADE)
- [ ] Payment.sale → Sale (FK, CASCADE)
- [ ] StockMovement.product → Product (FK, CASCADE)
- [ ] StockMovement.journal_entry → JournalEntry (FK, PROTECT)
- [ ] Expense.category → ExpenseCategory (FK, PROTECT)
- [ ] Expense.gl_account → Account (FK, PROTECT)
- [ ] JournalEntry.lines → JournalEntryLine (M2M or reverse FK)
- [ ] JournalEntryLine.account → Account (FK, PROTECT)

### 4.3 Database Indexes
- [ ] Sale: (customer, -sale_date), (sale_number)
- [ ] SaleLine: (sale, product)
- [ ] Invoice: (sale, invoice_number), (-invoice_date)
- [ ] Payment: (invoice, -payment_date), (status)
- [ ] StockMovement: (product, -movement_date), (movement_type)
- [ ] Expense: (category, -expense_date), (status)
- [ ] JournalEntry: (entry_type, -entry_date), (status)
- [ ] JournalEntryLine: (account, journal_entry)

---

## PHASE 5: MOBILE-FRIENDLY DESIGN
**Objective**: 100% responsive, Bootstrap 5, no horizontal scroll

### 5.1 Responsive Layouts
**Files**: templates/modules/*
- [ ] Base template: sidebar collapse on mobile
- [ ] Sale list: card view on mobile, table on desktop
- [ ] Invoice view: centered single-column on mobile
- [ ] Payment form: large inputs, mobile date picker
- [ ] Expense form: stacked fields on mobile
- [ ] Report view: card-based on mobile, table on desktop

### 5.2 Navigation & Menus
- [ ] Top navbar: hamburger menu on mobile
- [ ] Sidebar: collapses to icon menu on mobile
- [ ] Breadcrumbs: adjust font size on mobile
- [ ] Action buttons: stack vertically on mobile (< 576px)
- [ ] Forms: full width, 1 column on mobile, 2+ on desktop

### 5.3 Data Tables
- [ ] All tables: responsive.css or custom breakpoints
- [ ] Mobile: convert to card layout (not horizontal scroll)
- [ ] Desktop: maintain table with horizontal scroll for overflow
- [ ] Forms: large input fields (padding: 12px, font: 16px)

### 5.4 Keyboard & Input
- [ ] Date inputs: mobile date picker (type="date")
- [ ] Numeric inputs: numeric keyboard (type="number", inputmode="decimal")
- [ ] Select dropdowns: touch-friendly (height >= 44px)
- [ ] Buttons: touch-friendly (height >= 44px, width >= 44px)

---

## PHASE 6: PRINT & PDF ARCHITECTURE
**Objective**: Preview + print-ready + PDF export

### 6.1 Print Templates
**Files**: templates/print/* (new folder)
- [ ] invoice_print.html (sales invoice)
- [ ] rental_invoice_print.html
- [ ] expense_print.html
- [ ] statement_print.html (client/supplier)
- [ ] report_print.html (P&L, balance sheet, cash flow)

### 6.2 Print Styling
**Files**: static/css/print.css (new)
- [ ] A4 page size (210mm x 297mm)
- [ ] No colors (grayscale)
- [ ] No sidebars/navigation
- [ ] Company logo + branding
- [ ] Margins: 20mm all sides
- [ ] Font: standard print-safe (Arial, Times, Courier)
- [ ] Page break rules

### 6.3 PDF Generation
**Library**: WeasyPrint (HTML → PDF)
**Files**: utils/pdf_generator.py (new)
- [ ] generate_invoice_pdf(invoice_id)
- [ ] generate_report_pdf(report_type, period)
- [ ] generate_statement_pdf(entity_type, entity_id)
- [ ] Return file for download or email

### 6.4 Print Preview
**Files**: templates/modules/* → add print preview modal
- [ ] Preview button on every printable document
- [ ] Modal shows full print version
- [ ] Print button opens browser print dialog
- [ ] Download PDF button

---

## PHASE 7: REPORTING SYSTEM (TIME-BASED)
**Objective**: Weekly, monthly, yearly, custom reports

### 7.1 Report Service Layer
**Files**: financeaccounting/services/report_service.py (new)
```
CLASSES:
- ReportGenerator (base class)
- SalesReportGenerator(ReportGenerator)
- ExpenseReportGenerator(ReportGenerator)
- ProfitLossReportGenerator(ReportGenerator)
- CashFlowReportGenerator(ReportGenerator)
- InventoryReportGenerator(ReportGenerator)
- ClientBalanceReportGenerator(ReportGenerator)
- SupplierBalanceReportGenerator(ReportGenerator)
```

### 7.2 Report Period Support
**Files**: financeaccounting/services/report_service.py
- [ ] This Week (Monday - Sunday)
- [ ] This Month (1st - last day)
- [ ] This Year (Jan 1 - Dec 31)
- [ ] Custom Date Range
- [ ] Fiscal Year (if applicable)

### 7.3 Report Views
**Files**: financeaccounting/views.py & reports/views.py
- [ ] SalesReportView (sales, rentals, discounts)
- [ ] ExpenseReportView (by category, by supplier)
- [ ] ProfitLossReportView (period comparison)
- [ ] CashFlowReportView (operations, investing, financing)
- [ ] InventoryReportView (valuation, movement)
- [ ] ClientBalanceReportView (outstanding, paid)
- [ ] SupplierBalanceReportView (outstanding, paid)

### 7.4 Report Export
**Files**: financeaccounting/views.py
- [ ] CSV export (views + data)
- [ ] Excel export (formatted with formulas)
- [ ] PDF export (print-ready)
- [ ] JSON export (API use)

---

## PHASE 8: DASHBOARD REPORT SHORTCUTS
**Objective**: KPI → click → detailed report

### 8.1 KPI Cards
**Files**: templates/modules/sales_dashboard.html, etc.
```
CARDS:
1. Sales This Week
   - Value: sum(sale.total_amount WHERE week)
   - Link: /reports/sales/?period=week
   
2. Revenue This Month
   - Value: sum(invoice.total WHERE month AND status=paid)
   - Link: /reports/sales/?period=month
   
3. Expenses This Month
   - Value: sum(expense.amount WHERE month AND status=posted)
   - Link: /reports/expenses/?period=month
   
4. Cash on Hand (Today)
   - Value: account(1100).balance
   - Link: /reports/balance-sheet/
   
5. Accounts Receivable (Total)
   - Value: account(1200).balance
   - Link: /reports/client-balances/
   
6. Inventory Valuation
   - Value: sum(product.quantity * unit_cost)
   - Link: /reports/inventory/
```

### 8.2 Dashboard Data Accuracy
- [ ] KPI values calculated from JournalEntry (source of truth)
- [ ] KPI values match detailed reports exactly
- [ ] KPI values recalculated on each page load
- [ ] Consider caching for high-volume systems

---

## PHASE 9: EXCEL IMPORT & EXPORT
**Objective**: Bulk operations with validation, audit trail

### 9.1 Excel Import Service
**Files**: utils/excel_importer.py (new)
**Library**: openpyxl or pandas

#### Import Templates
- [ ] products_template.xlsx
- [ ] clients_template.xlsx
- [ ] suppliers_template.xlsx
- [ ] expenses_template.xlsx
- [ ] opening_inventory_template.xlsx

#### Import Workflow
```
STEPS:
1. User uploads file
2. System validates schema (required columns, data types)
3. System validates data (required fields, ranges, lookups)
4. Show preview (5 rows) + error summary
5. User reviews and confirms
6. System imports atomically (all or nothing)
7. Audit log records import + user + timestamp
```

### 9.2 Excel Export Service
**Files**: utils/excel_exporter.py (new)
**Library**: openpyxl

#### Export Items
- [ ] Reports (P&L, balance sheet, cash flow)
- [ ] Inventory list
- [ ] Clients & contact info
- [ ] Suppliers & contact info
- [ ] Invoice summaries
- [ ] Expense summaries
- [ ] Journal entries (for auditors)

### 9.3 Import Validations
```
RULES:
- Prevent duplicates (by SKU, email, phone)
- Validate currency amounts (2 decimals)
- Validate dates (YYYY-MM-DD format)
- Validate required fields
- Validate foreign keys (product IDs, category codes)
- Show specific error cell (row, column)
- Allow partial import (skip invalid rows, import valid)
```

### 9.4 Import Reversibility
```
RULES:
- Track all imported items (metadata: import_batch_id)
- Allow user to "undo import" within 24 hours
- Undo deletes all items from batch + audit log
- After 24 hours, permanent (archive mode only)
```

---

## PHASE 10: BUSINESS RULES & CONSTRAINTS
**Objective**: Prevent data corruption, enforce business logic

### 10.1 Sale Rules
- [ ] Cannot modify sale after invoice created
- [ ] Cannot delete sale with payments
- [ ] Can only cancel sale (soft delete)
- [ ] Sale must have ≥1 line item
- [ ] Sale line quantity must be ≥1
- [ ] Sale line unit_price must be >0

### 10.2 Invoice Rules
- [ ] One sale creates exactly one invoice
- [ ] Invoice number unique and immutable
- [ ] Invoice amount = sale amount (immutable)
- [ ] Cannot delete invoice with payments
- [ ] Cannot edit invoice after creation
- [ ] Can only cancel invoice (soft delete)

### 10.3 Payment Rules
- [ ] Payment amount ≤ outstanding balance
- [ ] Payment date ≤ today
- [ ] Cannot edit posted payment
- [ ] Can only reverse (not delete) posted payment
- [ ] Reversal creates offsetting journal entries

### 10.4 Stock Movement Rules
- [ ] Stock cannot go negative
- [ ] Stock movements immutable (no edits)
- [ ] Stock corrections via adjustments (new movement)
- [ ] Adjustment requires approval + reason
- [ ] All movements linked to journal entries

### 10.5 Expense Rules
- [ ] Cannot edit posted expense
- [ ] Posted expense requires GL account mapping
- [ ] Reversals only (not edits) for corrections
- [ ] Expense date cannot be > 30 days old (configurable)
- [ ] Receipt file required (configurable)

### 10.6 Accounting Rules
- [ ] JournalEntry must be balanced (debits == credits)
- [ ] JournalEntry immutable (no deletes, no updates)
- [ ] No manual revenue entries (auto from invoice)
- [ ] No manual COGS entries (auto from stock movement)
- [ ] All transactions must reference source document

---

## PHASE 11: IMPLEMENTATION CHECKLIST
**Track detailed progress**

### Models & Migrations
- [ ] Review all models in each app
- [ ] Create missing models (StockMovement, ExpenseCategory, BankReconciliation)
- [ ] Create/update migrations
- [ ] Run migrations successfully
- [ ] Verify no orphaned data

### Views & Templates
- [ ] Audit existing views
- [ ] Create missing views (reports, imports)
- [ ] Create/update responsive templates
- [ ] Add print templates
- [ ] Add mobile navigation

### Services & Utilities
- [ ] Create reporting service layer
- [ ] Create PDF generation service
- [ ] Create Excel import/export services
- [ ] Create accounting validation service
- [ ] Create audit logging service

### Testing
- [ ] Unit tests for models
- [ ] Unit tests for services
- [ ] Integration tests (full business flows)
- [ ] Data integrity tests
- [ ] Report accuracy tests
- [ ] Mobile responsive tests

### Documentation
- [ ] Update models docstrings
- [ ] Update API documentation
- [ ] Create user guides (sales, accounting, reports)
- [ ] Create admin guides (reconciliation, GL setup)
- [ ] Create troubleshooting guide

---

## DEPENDENCIES & VERSIONS

```
Django==6.0.1
Python==3.14.2
Bootstrap==5.3.0
openpyxl==3.10.0 (Excel)
WeasyPrint==59.0 (PDF)
Pillow==10.0.0 (Image handling)
pandas==2.0.0 (optional, for import/export)
celery==5.3.0 (optional, for async report generation)
```

---

## SUCCESS CRITERIA

### Phase 1: Core Business Flow
- ✅ Sale → Invoice → Payment → Inventory → Accounting flow works end-to-end
- ✅ All accounting entries auto-generated (no manual journal entries for standard sales)
- ✅ Payment updates invoice status correctly
- ✅ Stock reduced on invoice (not on sale)

### Phase 2: Expense System
- ✅ Expenses post to GL automatically
- ✅ Expense categories map to GL accounts correctly
- ✅ Reversals create offset entries (not edits)
- ✅ Inventory-aware expenses update assets correctly

### Phase 3: Accounting Integrity
- ✅ Trial balance balances (debits == credits)
- ✅ Profit & Loss matches revenue - expenses
- ✅ Balance Sheet = Assets (Liabilities + Equity)
- ✅ All entries traceable to source documents

### Phase 4-11: Features
- ✅ Mobile-responsive all pages
- ✅ Print/PDF works for all documents
- ✅ Reports time-based (week/month/year/custom)
- ✅ Dashboard KPIs match reports exactly
- ✅ Excel import/export with validation
- ✅ All business rules enforced

---

## TIMELINE ESTIMATE

| Phase | Task | Est. Hours | Actual | Status |
|-------|------|-----------|--------|--------|
| 1 | Core Flow | 16 | - | Not Started |
| 2 | Expenses | 12 | - | Not Started |
| 3 | Accounting | 12 | - | Not Started |
| 4 | Models | 8 | - | Not Started |
| 5 | Mobile | 10 | - | Not Started |
| 6 | Print/PDF | 8 | - | Not Started |
| 7 | Reporting | 16 | - | Not Started |
| 8 | Dashboard | 6 | - | Not Started |
| 9 | Excel | 10 | - | Not Started |
| 10 | Rules | 8 | - | Not Started |
| 11 | Testing | 20 | - | Not Started |
| **TOTAL** | | **126** | - | - |

---

## NEXT STEPS

1. **Review this plan** with stakeholder
2. **Prioritize phases** (likely: 1, 2, 3, 4 first)
3. **Start Phase 1** - Validate core flow works
4. **Create migrations** for any missing models
5. **Test end-to-end** business flows
6. **Move to Phase 2** - Expense system
7. **Implement remaining phases** in priority order

---

**Prepared by**: AI Assistant
**For**: RIMAN FASHION ERP
**Date**: January 26, 2026
