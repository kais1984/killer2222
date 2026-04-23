# Template Management System - Quick Reference

## 🚀 Quick Start

### Access Templates
- **View all templates**: http://localhost:8000/templates/
- **Invoice templates**: http://localhost:8000/templates/invoices/
- **Contract templates**: http://localhost:8000/templates/contracts/

### From Dashboard
Click on **"Contracts & Documents"** card → **"Template Library"**

---

## 📋 What Can You Do?

### View Templates
1. Go to `/templates/`
2. Browse templates by category
3. See template name, description, and status

### Preview a Template
1. Click **"Preview"** button on any template
2. View full template content in browser
3. Click **"Open in New Tab"** for full-screen view

### Download a Template
1. Click **"Download"** button
2. File downloads as HTML
3. Use for reference or customization

### View Template Details
1. Click **"Details"** link
2. See template configuration
3. View creation date and version info

---

## 🛠️ Managing Templates (Admin)

### Access Admin Panel
- Go to: http://localhost:8000/admin/
- Login with admin credentials
- Navigate to **Documents** section

### Edit Invoice Template
1. Go to Admin → Documents → Invoice Templates
2. Click on template to edit
3. Configure:
   - Invoice prefix (INV-, BILL-, etc)
   - Number format ({prefix}{year}-{sequence})
   - Color scheme and font
   - Field visibility (PO, Tax, Discount, etc)
   - Payment terms

### Edit Contract Template
1. Go to Admin → Documents → Contract Templates
2. Click on template to edit
3. Configure:
   - Contract type (Master Service, Rental, etc)
   - Included clauses (check/uncheck as needed)
   - Required fields

### Create New Template
1. Go to Admin → Documents → Document Templates
2. Click **"Add Document Template"**
3. Fill in:
   - Name (e.g., "Premium Invoice")
   - Type (Invoice, Contract, etc)
   - Slug (unique identifier - auto-generated from name)
   - Description
   - Content (HTML/Template code)
   - Mark as Active/Default if needed
4. Save
5. If Invoice: Create Invoice Template config
   - Go to Invoice Templates
   - Add configuration for your template
6. If Contract: Create Contract Template config
   - Go to Contract Templates
   - Add configuration for your template

### Set Template as Default
1. Go to Admin → Documents → Document Templates
2. Select template(s)
3. Use "Set as default template" action
4. Click "Go"

### Deactivate/Hide Templates
1. Go to Admin → Documents → Document Templates
2. Uncheck "is_active" checkbox
3. Save
4. Template won't appear in library

### View Usage Analytics
1. Go to Admin → Documents → Template Usage Logs
2. See:
   - Which templates were viewed/downloaded
   - Which users accessed them
   - When they were accessed
   - Associated documents

---

## 📝 Default Templates

### Standard Invoice Template
**Location**: `/templates/standard_invoice/`  
**Type**: Invoice  
**Features**:
- Customer/Client section
- Line items with qty × price
- Tax calculation (5%)
- Payment terms
- Signature blocks
- Customizable placeholders

**Edit at**: Admin → Invoice Templates → Standard Invoice Template

### Standard Service Agreement
**Location**: `/templates/standard_contract/`  
**Type**: Contract  
**Features**:
- Parties section (Provider + Client)
- Services description
- Payment schedule (50% advance, 50% final)
- Term & termination
- Confidentiality clause
- Dispute resolution
- Signature blocks

**Edit at**: Admin → Contract Templates → Standard Service Agreement

---

## 🔧 Common Tasks

### Add Your Company Logo
1. Admin → Document Templates → [Your Invoice Template]
2. Upload image in "preview_image" field
3. It will display in template library

### Change Invoice Prefix
1. Admin → Invoice Templates → [Template]
2. Change "invoice_prefix" field (e.g., BILL-, INV-, etc)
3. Example: BILL-2026-001

### Create Multiple Invoice Versions
1. Create first template (Standard Invoice)
2. Admin → Document Templates → Add new
3. Give it different name (Premium Invoice, Minimal Invoice, etc)
4. Slug must be unique (premium-invoice, minimal-invoice)
5. Copy content from standard and modify
6. Create Invoice Template config for new template

### Make Template Unavailable
1. Admin → Document Templates
2. Uncheck "is_active"
3. Save
4. Template no longer shows in library

### Check Who Used a Template
1. Admin → Template Usage Logs
2. Filter by template name
3. See user, action (view/download), and timestamp

---

## 📊 Data Structure

### Template Content Tips
- Use **[PLACEHOLDERS]** for dynamic content
- Example placeholders:
  - `[CLIENT_NAME]` - Customer name
  - `[INVOICE_NUMBER]` - Invoice ID
  - `[AMOUNT]` - Total amount
  - `[DATE]` - Invoice date
  - `[DESCRIPTION]` - Item description

### Template HTML Format
Templates are stored as HTML. You can:
- Edit directly in admin
- Use standard HTML tags
- Add inline CSS
- Include tables, images, etc

---

## 🔒 Security & Access

- **Login Required**: All template operations require authentication
- **Admin Panel**: Only admins can create/edit template configuration
- **Usage Logs**: All actions logged with user attribution
- **Backups**: Always backup templates before major edits

---

## 💡 Best Practices

1. **Version Your Templates**
   - Keep parent template as original
   - Create versions for different clients/scenarios
   - Use descriptive names (v1, v2, Premium, etc)

2. **Test Before Deploying**
   - Preview template before marking as default
   - Check all placeholder values
   - Verify formatting on different browsers

3. **Keep Templates Updated**
   - Update payment terms when they change
   - Add new clauses to contracts as needed
   - Keep company info current

4. **Use Defaults Wisely**
   - Only one default per template type
   - Default is used for bulk operations
   - Users can select alternatives when needed

5. **Document Changes**
   - Add version number to template name
   - Include change notes in description
   - Update related processes

---

## 🆘 Troubleshooting

### Template Not Showing in Library
- Check if **is_active** is True
- Check template_type is set correctly
- Reload page (clear browser cache)

### Can't Edit Template Content
- Make sure you're in Admin → Document Templates
- Click the template name to open edit page
- Look for "Content" field (may need to expand)

### Missing Invoice Template Config
- Created DocumentTemplate but no InvoiceTemplate
- Go to Admin → Invoice Templates
- Click "Add Invoice Template"
- Select your document template
- Fill in invoice configuration

### Preview Not Loading
- Check HTML syntax in content
- Look for unclosed tags
- Test in plain HTML validator

---

## 📞 Support

For questions about templates:
1. Check this guide first
2. Look at existing templates for examples
3. Check admin interface inline help
4. Review database models documentation

---

**Ready to use!** 🎉

Start by visiting `/templates/` to browse all available templates.
