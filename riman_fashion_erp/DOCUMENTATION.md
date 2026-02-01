# RIMAN FASHION ERP - Complete System Documentation

## 📑 Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Design](#database-design)
3. [API Documentation](#api-documentation)
4. [User Roles & Permissions](#user-roles--permissions)
5. [Business Workflows](#business-workflows)
6. [Configuration Guide](#configuration-guide)
7. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                            │
│  Bootstrap 5 | HTML | CSS | JavaScript | Chart.js          │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Web Server Layer                          │
│  Django 4.2 | WSGI | Authentication | REST API             │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                 Business Logic Layer                         │
│  Models | Serializers | Views | Permissions | Utilities    │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                 Application Modules                          │
│  Suppliers | Inventory | Sales | Rentals | CRM |           │
│  Accounting | Reports | Core Auth                           │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Data Layer                                │
│  PostgreSQL | ORM | Migrations | Backup                    │
└─────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|-----------------|
| **core** | Authentication, user management, audit logs, company settings |
| **suppliers** | Supplier profiles, purchase invoicing, payments |
| **inventory** | Product catalog, stock tracking, warehouse management |
| **sales** | Orders, invoices, payments, promotions |
| **rentals** | Rental agreements, returns, damage tracking |
| **crm** | Client profiles, measurements, appointments, preferences |
| **accounting** | Chart of accounts, journal entries, financial tracking |
| **reports** | Analytics, reporting, business intelligence |

---

## Database Design

### Entity Relationships

```
User ──┬─→ Profile (1:1)
       ├─→ AuditLog (1:N)
       └─→ Notification (1:N)

Supplier ──→ PurchaseInvoice (1:N)
              ├─→ PurchaseInvoiceItem (1:N)
              └─→ SupplierPayment (1:N)

Product ──┬─→ StockLocation (1:N)
          ├─→ StockMovement (1:N)
          ├─→ OrderItem (1:N)
          └─→ RentalItem (1:N)

Client ──┬─→ Order (1:N)
         ├─→ Invoice (1:N)
         ├─→ RentalAgreement (1:N)
         ├─→ Measurement (1:N)
         ├─→ Appointment (1:N)
         ├─→ ClientNote (1:N)
         └─→ ClientInteraction (1:N)

Invoice ──┬─→ InvoiceItem (1:N)
          ├─→ Payment (1:N)
          └─→ RentalAgreement (1:1 optional)
```

### Key Tables

#### Users Table
- ID, Username, Email, Password Hash
- First Name, Last Name, Phone
- Role (admin, accountant, sales, inventory, manager)
- Profile Image, Is Active
- Created At, Updated At

#### Products Table
- SKU, Name, Description
- Dress Type, Category, Collection
- Size, Color, Material
- Cost Price, Sale Price, Rental Price/Day
- Quantity In Stock, Available For Rental
- Primary Image, Barcode
- Is Active, Created At

#### Invoices Table
- Invoice Number, Order Reference
- Client ID, Invoice Date, Due Date
- Subtotal, Tax Amount, Discount, Shipping
- Total Amount, Amount Paid
- Status, Payment Status
- Created At, Updated At

#### Rentals Table
- Rental Number, Client ID
- Rental Date, Return Date, Actual Return Date
- Daily Rate, Number of Days
- Rental Cost, Security Deposit
- Late Fee, Damage Cost
- Total Amount, Amount Paid
- Status, Created At

---

## API Documentation

### Authentication Endpoints

#### Login
```
POST /api/auth/login/
{
  "username": "user@example.com",
  "password": "secure_password"
}
Response: {
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "role": "sales",
    "first_name": "John"
  }
}
```

#### Get Profile
```
GET /api/auth/profile/
Headers: Authorization: Bearer {token}
Response: {
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "role": "sales",
  "phone": "+1234567890"
}
```

### Supplier Endpoints

#### List Suppliers
```
GET /api/suppliers/suppliers/?category=fabric&status=active
Response: [
  {
    "id": 1,
    "name": "Luxury Fabrics Co",
    "category": "fabric",
    "phone": "+1234567890",
    "email": "info@luxuryfabrics.com",
    "status": "active",
    "balance": 15000.00
  }
]
```

#### Create Purchase Invoice
```
POST /api/suppliers/invoices/
{
  "invoice_number": "INV-2024001",
  "supplier_id": 1,
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "items": [
    {
      "description": "Silk Fabric",
      "quantity": 50,
      "unit_price": 25.00,
      "cost_type": "fabric"
    }
  ],
  "tax_rate": 10,
  "total_amount": 1375.00
}
```

### Product Endpoints

#### List Products
```
GET /api/inventory/products/?dress_type=wedding&availability=both
Response: [
  {
    "id": 1,
    "sku": "WED-001",
    "name": "Classic White Wedding Dress",
    "dress_type": "wedding",
    "size": "M",
    "color": "white",
    "quantity_in_stock": 5,
    "sale_price": 3500.00,
    "rental_price_per_day": 150.00,
    "is_low_stock": false
  }
]
```

#### Create Product
```
POST /api/inventory/products/
{
  "sku": "WED-002",
  "name": "Blush Wedding Gown",
  "description": "Elegant A-line wedding dress",
  "dress_type": "wedding",
  "size": "S",
  "color": "blush",
  "sale_price": 4000.00,
  "rental_price_per_day": 180.00,
  "quantity_in_stock": 3,
  "availability": "both"
}
```

### Invoice Endpoints

#### Create Invoice
```
POST /api/sales/invoices/
{
  "order_id": 1,
  "client_id": 1,
  "invoice_date": "2024-01-20",
  "due_date": "2024-02-20",
  "items": [
    {
      "product_id": 1,
      "quantity": 1,
      "unit_price": 3500.00
    }
  ],
  "tax_rate": 8,
  "discount_amount": 0,
  "shipping_cost": 50.00
}
```

#### Record Payment
```
POST /api/sales/invoices/{id}/payments/
{
  "amount": 1000.00,
  "payment_method": "card",
  "reference_number": "TXN-12345",
  "payment_date": "2024-01-20"
}
```

### Rental Endpoints

#### Create Rental Agreement
```
POST /api/rentals/create/
{
  "client_id": 1,
  "rental_date": "2024-02-01",
  "return_date": "2024-02-03",
  "items": [
    {
      "product_id": 1,
      "daily_rate": 150.00
    }
  ],
  "security_deposit": 500.00
}
```

### Reports Endpoints

#### Get Dashboard Metrics
```
GET /api/reports/dashboard-metrics/
Response: {
  "total_sales_month": 25000.00,
  "active_rentals": 5,
  "inventory_value": 180000.00,
  "outstanding_payments": 8500.00,
  "monthly_profit": 12500.00
}
```

#### Get P&L Report
```
GET /api/accounting/financial-report/?year=2024&month=1
Response: {
  "period": "1/2024",
  "total_income": 35000.00,
  "total_expenses": 18000.00,
  "net_profit_loss": 17000.00,
  "profit_margin": 48.57
}
```

---

## User Roles & Permissions

### Role Matrix

| Action | Admin | Accountant | Sales | Inventory | Manager |
|--------|-------|-----------|-------|-----------|---------|
| **View Dashboard** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Create Users** | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Manage Settings** | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Create Orders** | ✓ | ✗ | ✓ | ✗ | ✓ |
| **Create Invoices** | ✓ | ✓ | ✓ | ✗ | ✓ |
| **Record Payments** | ✓ | ✓ | ✓ | ✗ | ✓ |
| **Manage Inventory** | ✓ | ✗ | ✗ | ✓ | ✓ |
| **Create Rentals** | ✓ | ✗ | ✓ | ✗ | ✓ |
| **Financial Reports** | ✓ | ✓ | ✗ | ✗ | ✓ |
| **Audit Logs** | ✓ | ✗ | ✗ | ✗ | ✗ |

---

## Business Workflows

### Sales Order Workflow
```
1. Client visits showroom or calls
2. Sales staff creates Client profile
3. Client selects dress or places custom order
4. Sales staff creates Order
5. Order approved (optional for custom orders)
6. Invoice generated automatically
7. Payment recorded
8. Inventory updated
9. Order status: Completed
```

### Rental Workflow
```
1. Client browses rental catalog
2. Staff creates Rental Agreement
3. Security deposit collected (optional)
4. Rental period confirmed
5. Dress delivered/picked up
6. Client uses dress for event
7. Dress returned
8. Condition assessed
9. Damage documented (if any)
10. Deposit refunded (minus damages)
11. Rental complete
```

### Purchase Order Workflow
```
1. Inventory manager identifies need
2. Sends purchase request to supplier
3. Supplier provides quote
4. Purchase order created
5. Goods received
6. Quality inspection
7. Stock updated in inventory
8. Supplier invoice recorded
9. Payment processed
10. Reconciliation complete
```

---

## Configuration Guide

### Environment Variables

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=riman_fashion_db
DATABASE_USER=postgres
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (optional)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Stripe (optional)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
```

### Database Configuration

```python
# PostgreSQL Setup
psql -U postgres -c "CREATE DATABASE riman_fashion_db;"
psql -U postgres -c "CREATE USER riman_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "ALTER ROLE riman_user SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE riman_user SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE riman_user SET default_transaction_deferrable TO on;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE riman_fashion_db TO riman_user;"
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed
**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Verify database exists
psql -l

# Check connection parameters in .env
# Ensure firewall allows port 5432
```

#### 2. Static Files Not Loading
**Error**: `404 error on CSS/JS files`

**Solution**:
```bash
python manage.py collectstatic --noinput
# Check STATIC_ROOT and STATIC_URL in settings.py
```

#### 3. Permission Denied
**Error**: `You don't have permission to access this resource`

**Solution**:
- Check user role in admin panel
- Verify role has required permissions
- Clear browser cache and cookies
- Re-login to get updated permissions

#### 4. Import Errors
**Error**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**:
```bash
pip install -r requirements.txt
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver
```

#### 5. Port Already in Use
**Error**: `ERROR: That port is already in use`

**Solution**:
```bash
# Use different port
python manage.py runserver 8001

# Or kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

---

## Performance Optimization

### Database Optimization
- Add indexes on frequently queried fields
- Use select_related for foreign keys
- Use prefetch_related for reverse relations
- Implement database connection pooling

### Caching Strategy
- Cache dashboard metrics (5-minute TTL)
- Cache product catalog (24-hour TTL)
- Use Redis for session storage
- Implement query result caching

### API Performance
- Pagination on list endpoints
- Filter optimization
- Response compression
- API throttling

---

## Security Considerations

### Data Protection
- Encryption at rest for sensitive data
- HTTPS/TLS for all communications
- Regular security updates
- SQL injection prevention
- XSS/CSRF protection

### Access Control
- Role-based permissions
- Token expiration (15 min for access, 7 days for refresh)
- IP whitelisting (optional)
- Audit logging for sensitive operations

### Backup Strategy
- Daily automated backups
- Test restore procedures monthly
- Encrypted backup storage
- Off-site backup copies

---

**For additional support or questions, contact the development team.**
