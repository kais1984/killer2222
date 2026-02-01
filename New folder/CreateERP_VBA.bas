'  RIAMAN FASHION ERP - Complete Excel Workbook Build Script
' This script is designed to be run in Excel VBA to create the entire ERP system

Sub CreateRiamanFashionERP()
    ' Main initialization routine
    ' Call this from Excel to build the entire system
    
    Dim wb As Workbook
    Dim wsTemp As Worksheet
    
    ' Create new workbook or use active
    Set wb = ThisWorkbook
    
    ' Remove all default sheets except one
    Application.DisplayAlerts = False
    Dim ws As Worksheet
    For Each ws In wb.Sheets
        If ws.Name <> "Sheet1" Then
            ws.Delete
        End If
    Next
    Application.DisplayAlerts = True
    
    ' Rename first sheet
    On Error Resume Next
    wb.Sheets(1).Name = "_System"
    On Error GoTo 0
    
    ' Create all backend sheets
    CreateSystemSheet wb
    CreateProductsMasterSheet wb
    CreateStockMovementsSheet wb
    CreateStockCurrentSheet wb
    CreateCustomersMasterSheet wb
    CreateSalesTransactionsSheet wb
    CreateTransactionItemsSheet wb
    CreateRentalBookingsSheet wb
    CreateAccountingLedgerSheet wb
    CreateAuditLogSheet wb
    CreateUsersMasterSheet wb
    CreateSettingsSheet wb
    
    ' Create frontend sheets
    CreateDashboardAdminSheet wb
    CreatePOSSheet wb
    CreateInventorySheet wb
    CreateProductsUISheet wb
    CreateCustomersUISheet wb
    CreateReportsSheet wb
    CreateFinancialLedgerSheet wb
    CreateCashFlowSheet wb
    CreateDashboardSalesSheet wb
    CreateStockMovementsUISheet wb
    
    ' Add VBA modules (must be done manually)
    ' Configure workbook security and settings
    ConfigureWorkbookSettings wb
    
    ' Save and complete
    MsgBox "RIAMAN FASHION ERP System created successfully!" & vbCrLf & _
            "All sheets have been configured." & vbCrLf & _
            "Next: Import VBA modules and protect sheets.", vbInformation
    
End Sub

' ============================================================================
' BACKEND SHEET CREATION ROUTINES
' ============================================================================

Sub CreateSystemSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets("_System")
    
    ws.Range("A1").Value = "RIAMAN FASHION ERP System"
    ws.Range("A2").Value = "Configuration Sheet"
    ws.Range("A4").Value = "Setting"
    ws.Range("B4").Value = "Value"
    
    ws.Range("A5").Value = "App Name"
    ws.Range("B5").Value = "RIAMAN FASHION ERP"
    ws.Range("A6").Value = "Version"
    ws.Range("B6").Value = "1.0"
    ws.Range("A7").Value = "Created"
    ws.Range("B7").Value = Now()
    
    ws.Sheet_State = xlSheetHidden
    
End Sub

Sub CreateProductsMasterSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Products_Master"
    
    Dim headers As Variant
    headers = Array("Product ID", "Name", "Category", "Size", "Color", "Fabric", _
                    "Designer/Collection", "Cost Price (AED)", "Selling Price (AED)", _
                    "Rental Price (AED/day)", "Deposit (AED)", "Condition", _
                    "Availability", "Created Date", "Image Path", "Barcode")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116) ' Gold
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ' Add sample product
    ws.Range("A2").Value = "RIAMAN-00001"
    ws.Range("B2").Value = "Eternal Dreams Bridal Gown"
    ws.Range("C2").Value = "Wedding"
    ws.Range("D2").Value = "US 6"
    ws.Range("E2").Value = "White"
    ws.Range("F2").Value = "Silk Tulle"
    ws.Range("G2").Value = "RIAMAN Couture"
    ws.Range("H2").Value = 3500
    ws.Range("I2").Value = 8500
    ws.Range("J2").Value = 800
    ws.Range("K2").Value = 2500
    ws.Range("L2").Value = "New"
    ws.Range("M2").Value = "Available"
    ws.Range("N2").Value = Now()
    ws.Range("O2").Value = "[image_path]"
    ws.Range("P2").Value = "RIAMAN-00001"
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateStockMovementsSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Stock_Movements"
    
    Dim headers As Variant
    headers = Array("Movement ID", "Product ID", "Movement Type", "Quantity", _
                    "Reference", "Notes", "Date", "User")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateStockCurrentSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Stock_Current"
    
    Dim headers As Variant
    headers = Array("Product ID", "Product Name", "Current Stock", "Low Stock Alert", "Last Updated")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateCustomersMasterSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Customers_Master"
    
    Dim headers As Variant
    headers = Array("Customer ID", "Name", "Phone", "Email", "Notes", _
                    "Total Spending (AED)", "Visit Count", "Preferences", _
                    "VIP Status", "Created Date", "Last Visit")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateSalesTransactionsSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Sales_Transactions"
    
    Dim headers As Variant
    headers = Array("Transaction ID", "Customer ID", "Transaction Date", "Payment Method", _
                    "Subtotal (AED)", "VAT (AED)", "Discount (AED)", "User", _
                    "Total (AED)", "Completed Time")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateTransactionItemsSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Transaction_Items"
    
    Dim headers As Variant
    headers = Array("Transaction ID", "Product ID", "Quantity", "Unit Price (AED)", _
                    "Is Rental", "Rental Days", "Line Total (AED)")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateRentalBookingsSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Rental_Bookings"
    
    Dim headers As Variant
    headers = Array("Rental ID", "Product ID", "Customer ID", "Start Date", "End Date", _
                    "Deposit (AED)", "Status", "Created Date", "Late Fee (AED)", _
                    "Return Date", "Condition on Return")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateAccountingLedgerSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Accounting_Ledger"
    
    Dim headers As Variant
    headers = Array("Reference", "Account Type", "Debit (AED)", "Credit (AED)", _
                    "Date", "Description", "User")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateAuditLogSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Audit_Log"
    
    Dim headers As Variant
    headers = Array("Timestamp", "User", "Action", "Reference", "Details")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateUsersMasterSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Users_Master"
    
    Dim headers As Variant
    headers = Array("User ID", "Username", "Password", "Full Name", "Role", _
                    "Email", "Active", "Created Date")
    
    Dim i As Integer
    For i = LBound(headers) To UBound(headers)
        ws.Cells(1, i + 1).Value = headers(i)
        With ws.Cells(1, i + 1)
            .Font.Bold = True
            .Interior.Color = RGB(212, 165, 116)
            .Font.Color = RGB(255, 255, 255)
        End With
    Next i
    
    ' Add default users
    ws.Range("A2").Value = "USR001"
    ws.Range("B2").Value = "admin"
    ws.Range("C2").Value = "admin123"
    ws.Range("D2").Value = "Administrator"
    ws.Range("E2").Value = "Admin"
    ws.Range("F2").Value = "admin@riaman.ae"
    ws.Range("G2").Value = True
    ws.Range("H2").Value = Now()
    
    ws.Range("A3").Value = "USR002"
    ws.Range("B3").Value = "sales"
    ws.Range("C3").Value = "sales123"
    ws.Range("D3").Value = "Sales Staff"
    ws.Range("E3").Value = "Sales Person"
    ws.Range("F3").Value = "sales@riaman.ae"
    ws.Range("G3").Value = True
    ws.Range("H3").Value = Now()
    
    ws.Sheet_State = xlSheetHidden
End Sub

Sub CreateSettingsSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "_Settings"
    
    ws.Range("A1").Value = "Setting"
    ws.Range("B1").Value = "Value"
    With ws.Range("A1:B1")
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
        .Font.Color = RGB(255, 255, 255)
    End With
    
    ws.Range("A2").Value = "VIP Threshold (AED)"
    ws.Range("B2").Value = 50000
    
    ws.Range("A3").Value = "VAT Rate (%)"
    ws.Range("B3").Value = 5
    
    ws.Range("A4").Value = "Default Rental Late Fee (AED/day)"
    ws.Range("B4").Value = 50
    
    ws.Range("A5").Value = "Low Stock Alert Level"
    ws.Range("B5").Value = 2
    
    ws.Range("A6").Value = "Company Name"
    ws.Range("B6").Value = "RIAMAN FASHION"
    
    ws.Range("A7").Value = "Currency"
    ws.Range("B7").Value = "AED"
    
    ws.Range("A8").Value = "Country"
    ws.Range("B8").Value = "UAE"
    
    ws.Sheet_State = xlSheetHidden
End Sub

' ============================================================================
' FRONTEND SHEET CREATION ROUTINES
' ============================================================================

Sub CreateDashboardAdminSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Dashboard_Admin"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "ADMIN DASHBOARD", "Executive Overview & Business Intelligence", 1)
    
    ' KPIs Section
    ws.Range("A" & row).Value = "KEY PERFORMANCE INDICATORS"
    ws.Range("A" & row).Font.Bold = True
    ws.Range("A" & row).Interior.Color = RGB(212, 165, 116)
    ws.Merge ws.Range("A" & row & ":D" & row)
    row = row + 1
    
    ws.Range("A" & row).Value = "Metric"
    ws.Range("B" & row).Value = "Value"
    ws.Range("C" & row).Value = "Target"
    ws.Range("D" & row).Value = "Status"
    row = row + 1
    
    ws.Range("A" & row).Value = "Today's Revenue"
    ws.Range("B" & row).Value = "AED 45,000"
    ws.Range("C" & row).Value = "AED 40,000"
    ws.Range("D" & row).Value = "✓ On Track"
    row = row + 1
    
    ws.Range("A" & row).Value = "Monthly Revenue"
    ws.Range("B" & row).Value = "AED 850,000"
    ws.Range("C" & row).Value = "AED 800,000"
    ws.Range("D" & row).Value = "✓ Exceeding"
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreatePOSSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "POS"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "POINT OF SALE", "Fast & Intuitive Sales Interface", 1)
    
    ws.Range("A" & row).Value = "CUSTOMER"
    ws.Range("A" & row).Font.Bold = True
    ws.Range("B" & row).Value = "[Select or Create]"
    row = row + 2
    
    ws.Range("A" & row).Value = "ITEMS"
    row = row + 1
    
    ' Items table headers
    ws.Range("A" & row).Value = "Product"
    ws.Range("B" & row).Value = "Qty"
    ws.Range("C" & row).Value = "Price (AED)"
    ws.Range("D" & row).Value = "Type"
    ws.Range("E" & row).Value = "Total (AED)"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
        .Font.Color = RGB(255, 255, 255)
    End With
    row = row + 10
    
    ws.Range("A" & row).Value = "SUBTOTAL"
    ws.Range("B" & row).Value = 0
    ws.Range("B" & row).NumberFormat = "AED #,##0.00"
    row = row + 1
    
    ws.Range("A" & row).Value = "VAT (5%)"
    ws.Range("B" & row).Value = 0
    ws.Range("B" & row).NumberFormat = "AED #,##0.00"
    row = row + 1
    
    ws.Range("A" & row).Value = "DISCOUNT"
    ws.Range("B" & row).Value = 0
    ws.Range("B" & row).NumberFormat = "AED #,##0.00"
    row = row + 1
    
    ws.Range("A" & row).Value = "TOTAL"
    ws.Range("A" & row).Font.Bold = True
    ws.Range("B" & row).Value = 0
    ws.Range("B" & row).Font.Bold = True
    ws.Range("B" & row).NumberFormat = "AED #,##0.00"
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateInventorySheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Inventory"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "INVENTORY MANAGEMENT", "Stock Levels & Movement Control", 1)
    
    ws.Range("A" & row).Value = "Current Inventory"
    ws.Range("A" & row).Font.Bold = True
    ws.Merge ws.Range("A" & row & ":E" & row)
    row = row + 1
    
    ws.Range("A" & row).Value = "Product ID"
    ws.Range("B" & row).Value = "Product Name"
    ws.Range("C" & row).Value = "Current Stock"
    ws.Range("D" & row).Value = "Low Stock Level"
    ws.Range("E" & row).Value = "Last Updated"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateProductsUISheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Products"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "PRODUCT CATALOG", "Manage Dresses, Images & Barcodes", 1)
    
    ws.Range("A" & row).Value = "Product ID"
    ws.Range("B" & row).Value = "Name"
    ws.Range("C" & row).Value = "Category"
    ws.Range("D" & row).Value = "Size"
    ws.Range("E" & row).Value = "Color"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateCustomersUISheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Customers"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "CUSTOMER RELATIONSHIP MANAGEMENT", _
                            "Track Clients, Preferences & History", 1)
    
    ws.Range("A" & row).Value = "Customer ID"
    ws.Range("B" & row).Value = "Name"
    ws.Range("C" & row).Value = "Phone"
    ws.Range("D" & row).Value = "Email"
    ws.Range("E" & row).Value = "Total Spending"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateReportsSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Reports"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "BUSINESS REPORTS", "Analytics, Insights & Trends", 1)
    
    ws.Range("A" & row).Value = "Daily Sales Summary"
    ws.Range("A" & row).Font.Bold = True
    row = row + 2
    
    ws.Range("A" & row).Value = "Time"
    ws.Range("B" & row).Value = "Transaction ID"
    ws.Range("C" & row).Value = "Customer"
    ws.Range("D" & row).Value = "Amount"
    With ws.Range("A" & row & ":D" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateFinancialLedgerSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Financial_Ledger"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "ACCOUNTING LEDGER", "Financial Transactions & Balance Sheet", 1)
    
    ws.Range("A" & row).Value = "Date"
    ws.Range("B" & row).Value = "Reference"
    ws.Range("C" & row).Value = "Debit (AED)"
    ws.Range("D" & row).Value = "Credit (AED)"
    ws.Range("E" & row).Value = "Balance (AED)"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateCashFlowSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Cash_Flow"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "CASH FLOW ANALYSIS", "Daily, Weekly & Monthly Tracking", 1)
    
    ws.Range("A" & row).Value = "Date"
    ws.Range("B" & row).Value = "Description"
    ws.Range("C" & row).Value = "Cash In (AED)"
    ws.Range("D" & row).Value = "Cash Out (AED)"
    ws.Range("E" & row).Value = "Net (AED)"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateDashboardSalesSheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Dashboard_Sales"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "SALES DASHBOARD", "Personal Sales Performance & Targets", 1)
    
    ws.Range("A" & row).Value = "Your Performance Today"
    ws.Range("A" & row).Font.Bold = True
    row = row + 2
    
    ws.Range("A" & row).Value = "Sales Count"
    ws.Range("B" & row).Value = 0
    row = row + 1
    ws.Range("A" & row).Value = "Total Revenue"
    ws.Range("B" & row).Value = 0
    ws.Range("B" & row).NumberFormat = "AED #,##0.00"
    
    ws.DisplayGridlines = False
    
End Sub

Sub CreateStockMovementsUISheet(wb As Workbook)
    Dim ws As Worksheet
    Set ws = wb.Sheets.Add(, wb.Sheets(wb.Sheets.Count))
    ws.Name = "Stock_Movements"
    
    Dim row As Integer
    row = CreateLuxuryHeader(ws, "STOCK MOVEMENTS LOG", _
                            "Complete History of Inventory Changes", 1)
    
    ws.Range("A" & row).Value = "Movement ID"
    ws.Range("B" & row).Value = "Product ID"
    ws.Range("C" & row).Value = "Product Name"
    ws.Range("D" & row).Value = "Type"
    ws.Range("E" & row).Value = "Quantity"
    With ws.Range("A" & row & ":E" & row)
        .Font.Bold = True
        .Interior.Color = RGB(212, 165, 116)
    End With
    
    ws.DisplayGridlines = False
    
End Sub

' ============================================================================
' HELPER FUNCTIONS
' ============================================================================

Function CreateLuxuryHeader(ws As Worksheet, title As String, subtitle As String, startRow As Integer) As Integer
    ' Create luxury branded header
    Dim row As Integer
    row = startRow
    
    ' Brand name
    ws.Merge ws.Range("A" & row & ":H" & row)
    With ws.Range("A" & row)
        .Value = "RIAMAN FASHION"
        .Font.Name = "Garamond"
        .Font.Size = 16
        .Font.Bold = True
        .Font.Color = RGB(212, 165, 116)
        .Interior.Color = RGB(44, 44, 44)
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
    End With
    ws.Row_Height(row) = 30
    row = row + 1
    
    ' Title
    ws.Merge ws.Range("A" & row & ":H" & row)
    With ws.Range("A" & row)
        .Value = title
        .Font.Bold = True
        .Font.Size = 12
        .Font.Color = RGB(212, 165, 116)
        .Interior.Color = RGB(245, 245, 240)
        .HorizontalAlignment = xlCenter
    End With
    ws.Row_Height(row) = 25
    row = row + 1
    
    ' Subtitle
    ws.Merge ws.Range("A" & row & ":H" & row)
    With ws.Range("A" & row)
        .Value = subtitle
        .Font.Italic = True
        .Font.Size = 9
        .Interior.Color = RGB(232, 227, 216)
        .HorizontalAlignment = xlCenter
    End With
    ws.Row_Height(row) = 20
    row = row + 2
    
    CreateLuxuryHeader = row
    
End Function

Sub ConfigureWorkbookSettings(wb As Workbook)
    ' Configure overall workbook settings
    
    ' Set to show "Dashboard_Admin" first
    wb.Sheets("Dashboard_Admin").Activate
    
    ' Disable gridlines on all visible sheets
    Dim ws As Worksheet
    For Each ws In wb.Sheets
        If ws.Visible Then
            ws.DisplayGridlines = False
        End If
    Next
    
    ' Protect sheets (will be done after VBA import)
    
End Sub

