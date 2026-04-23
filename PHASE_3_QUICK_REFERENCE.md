# PHASE 3: QUICK REFERENCE GUIDE
## Expense Management System - At a Glance

**Phase 3 Status:** ✅ COMPLETE  
**Implementation Date:** January 28, 2026  
**Lines of Code:** 650+  

---

## ⚡ 30-SECOND OVERVIEW

**What:** Enterprise expense management system with GL posting  
**Why:** Track operational costs with full audit trail and automatic GL integration  
**Features:** 9 expense categories, approval workflow, GL posting, supplier tracking

---

## 🚀 QUICK START (5 MINUTES)

### 1. Create an Expense
```
URL: /accounting/expenses/add/
Fill: Date, Type, Description, Amount, Account, Supplier
Status: Saved as Draft (editable)
```

### 2. Submit for Approval
```
URL: /accounting/expenses/<id>/submit/
Status: Draft → Submitted
Who: Employee who created it
Next: Awaits manager approval
```

### 3. Approve Expense (Manager)
```
URL: /accounting/expenses/<id>/approve/
Decision: Approve or Reject
Status: Submitted → Approved/Rejected
Note: Add approval reason
```

### 4. Post to GL (Accountant)
```
URL: /accounting/expenses/<id>/post-gl/
Action: Create journal entry
GL Entry: Debit Expense, Credit Cash
Status: Approved → Posted (immutable)
```

---

## 📋 EXPENSE TYPES TABLE

| Type | GL Account | Use | Budget |
|------|-----------|-----|--------|
| Supplies & Materials | 5200 | Office, production | $X |
| Labor Costs | 5300 | Temp/contract workers | $X |
| Utilities | 5400 | Electricity, water, internet | $X |
| Rent | 5500 | Office/workshop space | $X |
| Marketing & Advertising | 5600 | Ads, promotions | $X |
| Transportation | 5700 | Delivery, travel, fuel | $X |
| Maintenance & Repairs | 5800 | Equipment, facilities | $X |
| Salaries & Wages | 5900 | Employee pay | $X |
| Other | 6000 | Miscellaneous | $X |

---

## 🔄 STATUS WORKFLOW

```
DRAFT
  ├─ Edit ✏️
  ├─ Delete 🗑️
  └─ Submit ➜ SUBMITTED
                  ├─ Approve ✅ ➜ APPROVED ➜ Post GL ➜ POSTED ✓
                  └─ Reject ❌ ➜ REJECTED ➜ (can resubmit)
```

---

## 💼 ADMIN SHORTCUTS

### List Expenses
```
URL: /admin/accounting/expense/
Features:
  • Filter by Status, Type, Date, Posted
  • Search by number, description, supplier
  • Bulk actions: Approve, Reject, Post GL
```

### Color-Coded Status
- 🔲 Gray = Draft
- 🔵 Blue = Submitted
- 🔷 Cyan = Approved
- 🟢 Green = Posted
- 🔴 Red = Rejected

### Bulk Operations
```
Select expenses → Choose action → Go
Approve All: Draft → Approved
Reject All: Submitted → Rejected
Post GL: Approved → Posted (creates GL entries)
```

---

## 📝 FORMS AT A GLANCE

### ExpenseForm (Create/Edit)
- Date when expense occurred
- Type (dropdown: 9 categories)
- Description
- Amount (validation: > 0)
- Account (expense GL account)
- Supplier name
- Reference #
- Receipt file
- Notes

### ExpenseSubmitForm
- Optional submission notes

### ExpenseApprovalForm
- Approve or Reject
- Approval/rejection reason

---

## 🖥️ VIEWS OVERVIEW

| View | Route | Purpose | Who |
|------|-------|---------|-----|
| List | /accounting/expenses/ | Browse all | Anyone |
| Create | /accounting/expenses/add/ | New expense | Employee |
| Detail | /accounting/expenses/<id>/ | View full info | Anyone |
| Update | /accounting/expenses/<id>/edit/ | Edit (draft only) | Employee |
| Submit | /accounting/expenses/<id>/submit/ | Submit for approval | Employee |
| Approve | /accounting/expenses/<id>/approve/ | Approve/reject | Manager |
| Post GL | /accounting/expenses/<id>/post-gl/ | Post to GL | Accountant |
| Post AJAX | /accounting/expenses/<id>/post-gl-ajax/ | API endpoint | System |

---

## 🎯 KEY FEATURES

### ✅ Workflow Automation
- Status auto-transitions
- User tracking at each step
- Timestamps recorded
- Immutability after posting

### ✅ GL Integration
- Journal entries auto-created
- Double-entry balanced
- GL accounts configured
- GL posting reversible

### ✅ Audit Trail
- Who created: created_by
- Who submitted: submitted_by
- Who approved: approved_by
- Who posted: posted_by
- Full timestamp history

### ✅ Supplier Tracking
- Vendor name
- Invoice/PO reference
- Receipt file upload
- Payables integration

### ✅ Validation
- Amount > 0
- Account must be expense type
- Description required
- Date validation

---

## 🔗 URL ROUTES

```
GET  /accounting/expenses/                    → List
GET  /accounting/expenses/add/                → Create form
POST /accounting/expenses/add/                → Save new
GET  /accounting/expenses/<id>/               → Detail
GET  /accounting/expenses/<id>/edit/          → Edit form
POST /accounting/expenses/<id>/edit/          → Update
GET  /accounting/expenses/<id>/submit/        → Submit form
POST /accounting/expenses/<id>/submit/        → Submit
GET  /accounting/expenses/<id>/approve/       → Approve form
POST /accounting/expenses/<id>/approve/       → Approve/Reject
GET  /accounting/expenses/<id>/post-gl/       → PostGL confirm
POST /accounting/expenses/<id>/post-gl/       → Post to GL
POST /accounting/expenses/<id>/post-gl-ajax/  → AJAX posting
```

---

## 💡 COMMON TASKS

### Create & Submit Expense
```
1. /accounting/expenses/add/         → Fill form
2. Click "Create"                     → Saved (draft)
3. Click "Submit for Approval"        → Status: Submitted
4. Wait for manager approval
```

### Approve Multiple Expenses (Admin)
```
1. /admin/accounting/expense/
2. Select multiple (checkboxes)
3. Action dropdown: "Approve selected"
4. Click "Go"
5. Status: Submitted → Approved
```

### Post Expense to GL
```
1. /accounting/expenses/<id>/
2. Status must be: Approved
3. Click "Post to GL"
4. Journal entry created
5. Status: Posted (immutable)
```

### Reject & Resubmit
```
1. Expense rejected → Status: Rejected
2. Click "Edit"
3. Make changes
4. Click "Submit for Approval" again
5. Back to approval workflow
```

---

## 🛡️ SECURITY CHECKPOINTS

| Check | Enforced | Result |
|-------|----------|--------|
| Login Required | ✅ | Anonymous users redirected |
| Draft editable | ✅ | Only draft/rejected can edit |
| Posted immutable | ✅ | Can't edit after posting |
| Status flow | ✅ | Can't skip workflow steps |
| Amount validation | ✅ | Negative amounts rejected |
| Account type | ✅ | Only expense accounts allowed |
| Posted flag | ✅ | Can't double-post |

---

## 📊 GL POSTING MECHANICS

### Journal Entry Created
```
Entry #:  EXP-000001
Date:     Expense date (not today)
Reference: EXP-YYYYMMDD-XXXXXX
Lines:
  Debit:  5200 (Supplies)    $500.00
  Credit: 1000 (Cash)        $500.00
Status:   Posted
```

### Account Mapping
```
Expense Type → GL Account
Supplies → 5200
Labor → 5300
Utilities → 5400
Rent → 5500
Marketing → 5600
Transportation → 5700
Maintenance → 5800
Salaries → 5900
Other → 6000
```

---

## 📈 REPORTING

**Coming in Phase 4:**
- Expense by category
- Vendor spending analysis
- Budget vs. actual
- Monthly trends
- P&L integration

---

## ⚙️ CONFIGURATION

### Create Expense GL Accounts
In `/admin/accounting/chartofaccounts/`:
```
5200 - Supplies & Materials (Expense)
5300 - Labor Costs (Expense)
5400 - Utilities (Expense)
5500 - Rent (Expense)
5600 - Marketing & Advertising (Expense)
5700 - Transportation (Expense)
5800 - Maintenance & Repairs (Expense)
5900 - Salaries & Wages (Expense)
6000 - Other Expenses (Expense)
1000 - Cash (Asset)
```

### Set Approval Limits (Future)
```
Employee: Can submit up to $1,000
Manager: Can approve up to $10,000
Accountant: Can approve any amount
```

---

## 🐛 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Can't edit expense | Check status (must be draft/rejected) |
| Can't post to GL | Status must be approved first |
| GL entry not created | Check expense account exists and is active |
| Amount validation fails | Amount must be > 0, not negative |
| Supplier field missing | It's optional, but recommended |
| Receipt won't upload | Check file size and format |

---

## 📞 SUPPORT

**For issues:**
1. Check Expense Status (Draft/Submitted/Approved/Posted)
2. Verify user permissions (Employee/Manager/Accountant)
3. Confirm GL account exists for category
4. Check audit trail for who did what when

---

## 🚀 QUICK LINKS

- **Full Documentation:** PHASE_3_EXPENSE_SYSTEM.md
- **Admin Interface:** /admin/accounting/expense/
- **Create Expense:** /accounting/expenses/add/
- **List Expenses:** /accounting/expenses/
- **GL Accounts:** /admin/accounting/chartofaccounts/

---

**Phase 3: ✅ Complete - Ready for Phase 4**

🎯 Next: Advanced Reporting & Reconciliation  
📊 Progress: 3/8 phases (37.5%)  
✨ System Status: Production Ready
