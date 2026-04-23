# RIMAN FASHION ERP System

A production-ready, web-based accounting and business management system designed specifically for luxury fashion houses specializing in wedding dresses, evening gowns, rentals, custom couture, and retail sales.

## 🎭 Overview

RIMAN FASHION ERP is a comprehensive enterprise resource planning solution that combines:
- **Accounting & Finance** - Complete financial management
- **Inventory Management** - Real-time stock tracking and warehouse management
- **Sales Management** - Order processing and invoicing
- **Rental Management** - Dress rental agreements and returns
- **CRM** - Client relationship management
- **Reporting & Analytics** - Comprehensive business intelligence

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, HTML, CSS, JavaScript
- **Authentication**: JWT + Role-Based Access Control
- **API**: RESTful API with comprehensive endpoints

### Project Structure
```
riman_fashion_erp/
├── riman_erp/              # Main Django configuration
├── core/                   # Core auth and user management
├── suppliers/              # Supplier management
├── inventory/              # Inventory and warehouse management
├── sales/                  # Sales and order management
├── rentals/                # Rental management
├── crm/                    # Client relationship management
├── accounting/             # Financial management
├── reports/                # Analytics and reporting
├── static/                 # CSS, JS, images
├── templates/              # HTML templates
├── media/                  # User uploaded files
└── manage.py               # Django management script
```

## 📋 Core Features

### 1. Supplier & Purchase Management
- Supplier profiles with categorization (fabrics, tailors, accessories, logistics)
- Purchase invoice registration with automatic inventory updates
- Cost breakdown tracking (fabric, labor, accessories)
- Supplier balance and payables tracking
- Payment history and terms management

### 2. Inventory Management
- Complete product catalog with high-quality images
- SKU and barcode management
- Real-time stock tracking across multiple locations
- Warehouse management (atelier, showroom, warehouse, storage)
- Low-stock alerts and inventory valuation
- Stock movement tracking and audit trail

### 3. Sales & Invoicing
- Professional branded invoices with RIMAN FASHION logo and colors
- Order management with multiple statuses
- Support for direct sales and custom orders
- Multiple payment methods (cash, card, bank transfer, online)
- Payment tracking (partial, full, outstanding)
- Discount and promotion management

### 4. Rental Management
- Complete rental agreement system
- Rental period tracking and return management
- Late fee calculation
- Damage tracking and reporting
- Security deposit management
- Rental availability tracking per dress

### 5. Client Management (CRM)
- Comprehensive client profiles
- Client classification (walk-in, regular, VIP, bridal, corporate)
- Measurement records for custom tailoring
- Full transaction history
- Appointment scheduling
- Client preferences and notes
- Interaction tracking

### 6. Accounting & Finance
- Chart of accounts
- Journal entries with double-entry bookkeeping
- Income and expense tracking
- Asset and liability management
- Cash flow reporting
- Financial period closing
- P&L statement generation

### 7. Reports & Analytics
- Sales reports (daily, monthly, yearly)
- Purchase reports with supplier analysis
- Inventory valuation reports
- Best-selling and most-rented dresses
- Profitability analysis per dress and collection
- Interactive charts and KPI dashboard

### 8. Dashboard
- Real-time KPIs:
  - Total sales (current month)
  - Active rentals
  - Inventory value
  - Outstanding payments
  - Monthly profit
- Interactive charts showing trends
- Quick access to recent transactions
- Low-stock alerts

## 🔐 Security & Access Control

### Role-Based Access Control
- **Admin**: Full system access, user management, settings
- **Accountant**: Financial transactions, P&L reports, accounting
- **Sales Staff**: Sales orders, invoices, client management
- **Inventory Manager**: Stock management, warehouse operations
- **Manager**: View-all access, reports, strategic analytics

### Security Features
- JWT authentication for API endpoints
- Session-based authentication for web interface
- CSRF protection
- SQL injection prevention
- Role-based permission decorators
- Audit logging for all transactions
- Secure password hashing

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip (Python package manager)

### Installation

1. **Clone and Setup**
```bash
cd riman_fashion_erp
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Setup Database**
```bash
python manage.py migrate
```

5. **Create Superuser**
```bash
python manage.py createsuperuser
```

6. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

7. **Run Development Server**
```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin/ (Django Admin)
Visit: http://localhost:8000/ (Dashboard)

## 📊 Database Schema

### Core Models
- **User**: Extended user model with role-based access
- **CompanySettings**: RIMAN FASHION branding and configuration
  - **Document upload settings (new):** `upload_max_size`, `allowed_extensions`, `enforce_mime`, `use_s3`, `virus_scan` (configurable via Admin / Company Settings)
- **AuditLog**: Track all system changes

### Suppliers
- **Supplier**: Supplier information and categorization
- **PurchaseInvoice**: Purchase orders with payment tracking
- **PurchaseInvoiceItem**: Line items with cost breakdown
- **SupplierPayment**: Payment records

### Inventory
- **Product**: Dress catalog with pricing and images
- **Category**: Product categories
- **Collection**: Fashion collections/seasons
- **Warehouse**: Storage locations
- **StockLocation**: Inventory at each warehouse
- **StockMovement**: Audit trail of all inventory changes
- **LowStockAlert**: Stock threshold monitoring

### Sales
- **Order**: Sales orders
- **OrderItem**: Items in orders
- **Invoice**: Sales invoices with payment status
- **InvoiceItem**: Invoice line items
- **Payment**: Payment records
- **Promotion**: Discounts and special offers
- **CustomOrder**: Custom couture orders

### Rentals
- **RentalAgreement**: Rental contracts
- **RentalItem**: Dresses in rental agreement
- **RentalReturn**: Return and damage tracking
- **RentalPayment**: Rental payments
- **RentalInventory**: Availability tracking

### CRM
- **Client**: Customer profiles with financial tracking
- **Measurement**: Customer measurements for tailoring
- **Appointment**: Scheduling and follow-ups
- **ClientNote**: Interaction records
- **ClientPreference**: Style preferences and budget
- **ClientInteraction**: Communication log

### Accounting
- **ChartOfAccounts**: Account structure
- **JournalEntry**: Double-entry transactions
- **JournalEntryLine**: Transaction line items
- **Income**: Revenue tracking
- **Expense**: Expense tracking
- **Asset**: Fixed asset management
- **Liability**: Debt and obligations
- **FinancialPeriod**: Accounting periods

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get current user
- `POST /api/auth/register/` - Create new user

### Suppliers
- `GET /api/suppliers/suppliers/` - List suppliers
- `POST /api/suppliers/suppliers/` - Create supplier
- `GET /api/suppliers/invoices/` - List purchase invoices

### Inventory
- `GET /api/inventory/products/` - List products
- `GET /api/inventory/warehouses/` - List warehouses
- `GET /api/inventory/movements/` - Stock movements

### Sales
- `GET /api/sales/invoices/` - List invoices
- `GET /api/sales/orders/` - List orders

### Rentals
- `GET /api/rentals/list/` - List rentals

### CRM
- `GET /api/crm/clients/` - List clients
- `POST /api/crm/clients/` - Create client

### Accounting
- `GET /api/accounting/financial-report/` - P&L report

### Reports
- `GET /api/reports/dashboard-metrics/` - Dashboard KPIs

## 🎨 Frontend Features

### Dashboard
- Responsive luxury design with elegant color scheme
- Real-time KPI cards
- Interactive charts using Chart.js
- Recent transactions summary
- Quick navigation

### Navigation
- Top navigation bar with system branding
- Left sidebar for quick access
- Mobile-responsive design
- Role-based menu visibility

### UI Components
- Data tables with sorting and filtering
- Form validation and error handling
- Modal dialogs for confirmations
- Toast notifications
- Loading states

## 📈 Reporting Capabilities

### Financial Reports
- Profit & Loss statements
- Cash flow analysis
- Balance sheet
- Account statements

### Operational Reports
- Sales analysis by period/category
- Rental utilization reports
- Inventory valuation
- Supplier performance
- Client lifetime value

### Custom Reports
- Extensible report framework
- Export to Excel/PDF
- Scheduled report generation
- Email delivery

## 🛠️ Admin Features

### System Administration
- User management with role assignment
- Company settings and branding
- System configuration
- Data backup and restoration
- Audit log review

### Business Configuration
- Tax settings (VAT, GST, etc.)
- Currency and localization
- Financial year settings
- Invoice numbering
- Stock thresholds

## 🔄 Integration Points

### Ready for Integration
- **POS System**: Point of sale integration
- **E-commerce**: Online store connection
- **Mobile App**: REST API for mobile clients
- **Email**: Invoice and report delivery
- **Payment Gateway**: Multiple payment processors
- **Accounting Software**: Data export capabilities
- **Communication**: WhatsApp, SMS, Email notifications

## 📝 Luxury ERP Customization

### Branding
- Logo upload and configuration
- Color scheme customization
- Invoice template personalization
- Report branding

### Fashion-Specific Features
- Collection management
- Size and color variants
- Material tracking
- Designer/creator attribution
- Seasonal inventory management

## 🧪 Testing & Validation

### Implemented Validations
- Business rule enforcement
- Data integrity checks
- Inventory consistency
- Financial accuracy
- Permission validation

### Sample Data
Management command for loading sample data:
```bash
python manage.py load_sample_data
```

## 📚 Documentation

- **API Documentation**: Available at `/api/docs/` (when configured)
- **User Guide**: In `/docs/USER_GUIDE.md`
- **Admin Guide**: In `/docs/ADMIN_GUIDE.md`
- **Developer Guide**: In `/docs/DEVELOPER_GUIDE.md`

## 🚀 Deployment

### Production Checklist
- [ ] Set DEBUG=False in settings
- [ ] Configure SECRET_KEY securely
- [ ] Setup PostgreSQL database
- [ ] Configure allowed hosts
- [ ] Setup CORS properly
- [ ] Enable HTTPS
- [ ] Configure email backend
- [ ] Setup static file serving
- [ ] Configure media file storage
- [ ] Setup monitoring and logging
- [ ] Create database backups strategy
- [ ] Configure caching (Redis)

### Deployment Options
- **Heroku**: Procfile included
- **AWS**: EC2, RDS, S3 compatible
- **DigitalOcean**: App Platform ready
- **Docker**: Containerization ready
- **VPS**: Traditional server deployment

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Verify PostgreSQL is running
# Check DATABASE settings in .env
# Ensure database exists
psql -U postgres -c "CREATE DATABASE riman_fashion_db;"
```

**Static Files Not Loading**
```bash
python manage.py collectstatic --noinput
```

**Permission Denied**
- Check user role in admin panel
- Verify role-based permissions
- Check URL permission decorators

## 📞 Support & Maintenance

### Regular Maintenance
- Daily: Monitor system logs
- Weekly: Backup database
- Monthly: Review audit logs
- Quarterly: System updates

### Performance Optimization
- Database indexing
- Query optimization
- Caching strategy
- API throttling

## 📄 License

RIMAN FASHION ERP - Custom Enterprise Solution

## 👥 Credits

Designed and developed for luxury fashion business operations.

## 🎯 Future Enhancements

- [ ] Mobile application (iOS/Android)
- [ ] Advanced AI-powered recommendations
- [ ] Predictive inventory management
- [ ] Real-time collaboration features
- [ ] Social media integration
- [ ] Advanced analytics with BI tools
- [ ] Multi-language support
- [ ] Advanced customization engine

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Status**: Production Ready
