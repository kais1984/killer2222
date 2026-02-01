' RIAMAN FASHION ERP System - VBA Main Module
' This file contains the complete VBA code structure
' This is a template to be imported into Excel VBA

' ============================================================================
' MODULE: Authentication and Login
' ============================================================================

Public gCurrentUser As String
Public gCurrentRole As String
Public gIsLoggedIn As Boolean

Sub Application_Startup()
    ' Auto-run when workbook opens
    ShowLoginForm
End Sub

Sub ShowLoginForm()
    ' Display login interface on startup
    ' This will be implemented via UserForm
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("_System")
    
    ' Show login prompt
    frmLogin.Show
    
    If Not gIsLoggedIn Then
        ThisWorkbook.Close False
    End If
    
    ' Navigate to role-based dashboard
    NavigateToRoleDashboard
End Sub

Sub NavigateToRoleDashboard()
    ' Route user to appropriate dashboard based on role
    Select Case gCurrentRole
        Case "Admin"
            ThisWorkbook.Sheets("Dashboard_Admin").Activate
        Case "Sales Person"
            ThisWorkbook.Sheets("POS").Activate
        Case "Stock Manager"
            ThisWorkbook.Sheets("Inventory").Activate
        Case "Accountant"
            ThisWorkbook.Sheets("Reports").Activate
    End Select
    
    ' Hide irrelevant sheets based on role
    UpdateSheetVisibility gCurrentRole
End Sub

Sub UpdateSheetVisibility(role As String)
    ' Control sheet visibility based on user role
    Dim ws As Worksheet
    Dim visibleSheets As Collection
    Set visibleSheets = New Collection
    
    ' Define sheets accessible by role
    Select Case role
        Case "Admin"
            ' Admin sees everything except system sheets
            For Each ws In ThisWorkbook.Sheets
                If Not ws.Name Like "_*" Then
                    ws.Visible = xlSheetVisible
                End If
            Next
        Case "Sales Person"
            visibleSheets.Add "POS"
            visibleSheets.Add "Dashboard_Sales"
            visibleSheets.Add "Customers"
        Case "Stock Manager"
            visibleSheets.Add "Inventory"
            visibleSheets.Add "Products"
            visibleSheets.Add "Stock_Movements"
        Case "Accountant"
            visibleSheets.Add "Reports"
            visibleSheets.Add "Financial_Ledger"
            visibleSheets.Add "Cash_Flow"
    End Select
    
    ' Apply visibility
    For Each ws In ThisWorkbook.Sheets
        ws.Visible = xlSheetVeryHidden
        Dim v As Variant
        On Error Resume Next
        For Each v In visibleSheets
            If ws.Name = v Then
                ws.Visible = xlSheetVisible
                Exit For
            End If
        Next
        On Error GoTo 0
    Next
End Sub

' ============================================================================
' MODULE: Product Management
' ============================================================================

Function GenerateProductID() As String
    ' Auto-generate unique Product ID
    Dim wsProducts As Worksheet
    Dim nextID As Long
    
    Set wsProducts = ThisWorkbook.Sheets("_Products_Master")
    
    ' Find next available ID
    nextID = wsProducts.Range("A2").End(xlDown).Row - 1
    nextID = nextID + 1
    
    GenerateProductID = "RIAMAN-" & Format(nextID, "00000")
End Function

Sub AddNewProduct(name As String, category As String, size As String, color As String, _
                  fabric As String, designer As String, costPrice As Double, _
                  sellingPrice As Double, rentalPrice As Double, depositAmount As Double, _
                  conditionStatus As String, imagePath As String)
    
    Dim wsProducts As Worksheet
    Dim newRow As Long
    Dim productID As String
    
    Set wsProducts = ThisWorkbook.Sheets("_Products_Master")
    
    ' Generate product ID
    productID = GenerateProductID()
    
    ' Find next empty row
    newRow = wsProducts.Range("A:A").End(xlDown).Row + 1
    
    ' Write product data
    With wsProducts
        .Cells(newRow, 1).Value = productID
        .Cells(newRow, 2).Value = name
        .Cells(newRow, 3).Value = category
        .Cells(newRow, 4).Value = size
        .Cells(newRow, 5).Value = color
        .Cells(newRow, 6).Value = fabric
        .Cells(newRow, 7).Value = designer
        .Cells(newRow, 8).Value = costPrice
        .Cells(newRow, 9).Value = sellingPrice
        .Cells(newRow, 10).Value = rentalPrice
        .Cells(newRow, 11).Value = depositAmount
        .Cells(newRow, 12).Value = conditionStatus
        .Cells(newRow, 13).Value = "Available"
        .Cells(newRow, 14).Value = Now()
        .Cells(newRow, 15).Value = imagePath
    End With
    
    ' Generate barcode (can integrate with barcode library)
    GenerateBarcode productID, newRow
    
    ' Log action
    LogAudit gCurrentUser, "ADD_PRODUCT", productID, "New product added: " & name
    
End Sub

Sub GenerateBarcode(productID As String, rowNum As Long)
    ' Generate barcode (simplified - uses Code128 or QR)
    ' In production, integrate with barcode generation library
    ' For now, store barcode value and format as Code128 font
    
    Dim wsProducts As Worksheet
    Set wsProducts = ThisWorkbook.Sheets("_Products_Master")
    
    wsProducts.Cells(rowNum, 16).Value = productID
    ' Barcode font applied to column 16
    
End Sub

' ============================================================================
' MODULE: Stock Management (Movement-Based)
' ============================================================================

Sub RecordStockMovement(productID As String, movementType As String, quantity As Long, _
                        reference As String, notes As String)
    
    Dim wsMovements As Worksheet
    Dim newRow As Long
    Dim movementID As String
    
    Set wsMovements = ThisWorkbook.Sheets("_Stock_Movements")
    
    ' Generate movement ID
    movementID = "MVT-" & Format(Now(), "yyyymmdd") & "-" & Format(CLng(Rnd() * 10000), "00000")
    
    ' Find next empty row
    newRow = wsMovements.Range("A:A").End(xlDown).Row + 1
    
    ' Record movement
    With wsMovements
        .Cells(newRow, 1).Value = movementID
        .Cells(newRow, 2).Value = productID
        .Cells(newRow, 3).Value = movementType ' "Purchase", "Sale", "Rental_Out", "Rental_Return", "Damage", "Loss"
        .Cells(newRow, 4).Value = quantity
        .Cells(newRow, 5).Value = reference
        .Cells(newRow, 6).Value = notes
        .Cells(newRow, 7).Value = Now()
        .Cells(newRow, 8).Value = gCurrentUser
    End With
    
    ' Update current stock
    UpdateStockLevel productID
    
End Sub

Sub UpdateStockLevel(productID As String)
    ' Calculate current stock from movements
    Dim wsMovements As Worksheet
    Dim wsStock As Worksheet
    Dim stockLevel As Long
    Dim lastRow As Long
    Dim i As Long
    
    Set wsMovements = ThisWorkbook.Sheets("_Stock_Movements")
    Set wsStock = ThisWorkbook.Sheets("_Stock_Current")
    
    stockLevel = 0
    lastRow = wsMovements.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If wsMovements.Cells(i, 2).Value = productID Then
            Select Case wsMovements.Cells(i, 3).Value
                Case "Purchase", "Rental_Return"
                    stockLevel = stockLevel + wsMovements.Cells(i, 4).Value
                Case "Sale", "Rental_Out", "Damage", "Loss"
                    stockLevel = stockLevel - wsMovements.Cells(i, 4).Value
            End Select
        End If
    Next i
    
    ' Update stock sheet
    Dim stockRow As Long
    stockRow = FindProductRow(productID, wsStock)
    
    If stockRow > 0 Then
        wsStock.Cells(stockRow, 3).Value = stockLevel
    Else
        ' Add new stock entry
        lastRow = wsStock.Range("A:A").End(xlDown).Row + 1
        wsStock.Cells(lastRow, 1).Value = productID
        wsStock.Cells(lastRow, 2).Value = GetProductName(productID)
        wsStock.Cells(lastRow, 3).Value = stockLevel
    End If
    
End Sub

Function GetCurrentStock(productID As String) As Long
    ' Get current stock level for a product
    Dim wsStock As Worksheet
    Dim row As Long
    
    Set wsStock = ThisWorkbook.Sheets("_Stock_Current")
    
    row = FindProductRow(productID, wsStock)
    
    If row > 0 Then
        GetCurrentStock = wsStock.Cells(row, 3).Value
    Else
        GetCurrentStock = 0
    End If
    
End Function

' ============================================================================
' MODULE: POS and Sales
' ============================================================================

Function CreateSalesTransaction(customerID As String, paymentMethod As String, _
                                transactionDate As Date) As String
    
    Dim wsTransactions As Worksheet
    Dim newRow As Long
    Dim transactionID As String
    
    Set wsTransactions = ThisWorkbook.Sheets("_Sales_Transactions")
    
    ' Generate transaction ID
    transactionID = "INV-" & Format(transactionDate, "yyyymmdd") & "-" & Format(CLng(Rnd() * 10000), "00000")
    
    ' Find next empty row
    newRow = wsTransactions.Range("A:A").End(xlDown).Row + 1
    
    ' Create transaction record
    With wsTransactions
        .Cells(newRow, 1).Value = transactionID
        .Cells(newRow, 2).Value = customerID
        .Cells(newRow, 3).Value = transactionDate
        .Cells(newRow, 4).Value = paymentMethod
        .Cells(newRow, 5).Value = 0 ' Will be updated with total
        .Cells(newRow, 6).Value = 0 ' VAT
        .Cells(newRow, 7).Value = 0 ' Discount
        .Cells(newRow, 8).Value = gCurrentUser
    End With
    
    CreateSalesTransaction = transactionID
    
End Function

Sub AddItemToTransaction(transactionID As String, productID As String, quantity As Long, _
                         unitPrice As Double, isRental As Boolean, rentalDays As Long)
    
    Dim wsTransactionItems As Worksheet
    Dim newRow As Long
    
    Set wsTransactionItems = ThisWorkbook.Sheets("_Transaction_Items")
    
    newRow = wsTransactionItems.Range("A:A").End(xlDown).Row + 1
    
    With wsTransactionItems
        .Cells(newRow, 1).Value = transactionID
        .Cells(newRow, 2).Value = productID
        .Cells(newRow, 3).Value = quantity
        .Cells(newRow, 4).Value = unitPrice
        .Cells(newRow, 5).Value = isRental
        .Cells(newRow, 6).Value = rentalDays
        .Cells(newRow, 7).Value = unitPrice * quantity
    End With
    
End Sub

Sub CompleteTransaction(transactionID As String, subtotal As Double, vat As Double, _
                        discount As Double, finalTotal As Double)
    
    Dim wsTransactions As Worksheet
    Dim row As Long
    
    Set wsTransactions = ThisWorkbook.Sheets("_Sales_Transactions")
    
    row = FindTransactionRow(transactionID, wsTransactions)
    
    If row > 0 Then
        With wsTransactions
            .Cells(row, 5).Value = subtotal
            .Cells(row, 6).Value = vat
            .Cells(row, 7).Value = discount
            .Cells(row, 9).Value = finalTotal
            .Cells(row, 10).Value = Now()
        End With
        
        ' Update inventory
        UpdateInventoryForTransaction transactionID
        
        ' Update customer
        UpdateCustomerHistory transactionID
        
        ' Record in accounting
        RecordSaleInAccounting transactionID
        
        ' Log audit
        LogAudit gCurrentUser, "COMPLETE_SALE", transactionID, "Sale completed: " & finalTotal
        
    End If
    
End Sub

Sub UpdateInventoryForTransaction(transactionID As String)
    ' Automatically update stock based on transaction items
    Dim wsItems As Worksheet
    Dim lastRow As Long
    Dim i As Long
    
    Set wsItems = ThisWorkbook.Sheets("_Transaction_Items")
    lastRow = wsItems.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If wsItems.Cells(i, 1).Value = transactionID Then
            Dim productID As String
            Dim quantity As Long
            Dim isRental As Boolean
            
            productID = wsItems.Cells(i, 2).Value
            quantity = wsItems.Cells(i, 3).Value
            isRental = wsItems.Cells(i, 5).Value
            
            If isRental Then
                RecordStockMovement productID, "Rental_Out", quantity, transactionID, "Rented out"
            Else
                RecordStockMovement productID, "Sale", quantity, transactionID, "Sold"
            End If
        End If
    Next i
    
End Sub

Sub UpdateCustomerHistory(transactionID As String)
    ' Update customer purchase history and spending
    Dim wsTransactions As Worksheet
    Dim wsCustomers As Worksheet
    Dim row As Long
    Dim customerID As String
    Dim totalAmount As Double
    
    Set wsTransactions = ThisWorkbook.Sheets("_Sales_Transactions")
    Set wsCustomers = ThisWorkbook.Sheets("_Customers_Master")
    
    row = FindTransactionRow(transactionID, wsTransactions)
    
    If row > 0 Then
        customerID = wsTransactions.Cells(row, 2).Value
        totalAmount = wsTransactions.Cells(row, 9).Value
        
        ' Find customer and update
        Dim custRow As Long
        custRow = FindCustomerRow(customerID, wsCustomers)
        
        If custRow > 0 Then
            ' Update total spending
            wsCustomers.Cells(custRow, 7).Value = wsCustomers.Cells(custRow, 7).Value + totalAmount
            ' Increment visit count
            wsCustomers.Cells(custRow, 8).Value = wsCustomers.Cells(custRow, 8).Value + 1
            ' Update last visit
            wsCustomers.Cells(custRow, 10).Value = Now()
        End If
    End If
    
End Sub

' ============================================================================
' MODULE: Customer Management (CRM)
' ============================================================================

Function CreateCustomer(name As String, phone As String, email As String, notes As String) As String
    
    Dim wsCustomers As Worksheet
    Dim newRow As Long
    Dim customerID As String
    
    Set wsCustomers = ThisWorkbook.Sheets("_Customers_Master")
    
    ' Generate customer ID
    customerID = "CUST-" & Format(CLng(Rnd() * 1000000), "000000")
    
    newRow = wsCustomers.Range("A:A").End(xlDown).Row + 1
    
    With wsCustomers
        .Cells(newRow, 1).Value = customerID
        .Cells(newRow, 2).Value = name
        .Cells(newRow, 3).Value = phone
        .Cells(newRow, 4).Value = email
        .Cells(newRow, 5).Value = notes
        .Cells(newRow, 6).Value = 0 ' Total spending
        .Cells(newRow, 7).Value = 0 ' Visit count
        .Cells(newRow, 8).Value = "" ' Preferences
        .Cells(newRow, 9).Value = "Regular" ' VIP status
        .Cells(newRow, 10).Value = Now() ' Created date
    End With
    
    CreateCustomer = customerID
    
End Function

Sub IdentifyVIPCustomers()
    ' Auto-update VIP status based on spending threshold
    Dim wsCustomers As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim vipThreshold As Double
    
    Set wsCustomers = ThisWorkbook.Sheets("_Customers_Master")
    
    vipThreshold = ThisWorkbook.Sheets("_Settings").Range("B2").Value ' VIP threshold from settings
    lastRow = wsCustomers.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If wsCustomers.Cells(i, 7).Value >= vipThreshold Then
            wsCustomers.Cells(i, 9).Value = "VIP"
        Else
            wsCustomers.Cells(i, 9).Value = "Regular"
        End If
    Next i
    
End Sub

' ============================================================================
' MODULE: Rental Management
' ============================================================================

Sub CreateRentalBooking(productID As String, customerID As String, startDate As Date, _
                        endDate As Date, depositAmount As Double) As String
    
    Dim wsRentals As Worksheet
    Dim newRow As Long
    Dim rentalID As String
    
    Set wsRentals = ThisWorkbook.Sheets("_Rental_Bookings")
    
    ' Validate rental availability
    If Not IsRentalAvailable(productID, startDate, endDate) Then
        MsgBox "Product not available for selected dates"
        Exit Sub
    End If
    
    rentalID = "RENTAL-" & Format(Now(), "yyyymmdd") & "-" & Format(CLng(Rnd() * 10000), "00000")
    
    newRow = wsRentals.Range("A:A").End(xlDown).Row + 1
    
    With wsRentals
        .Cells(newRow, 1).Value = rentalID
        .Cells(newRow, 2).Value = productID
        .Cells(newRow, 3).Value = customerID
        .Cells(newRow, 4).Value = startDate
        .Cells(newRow, 5).Value = endDate
        .Cells(newRow, 6).Value = depositAmount
        .Cells(newRow, 7).Value = "Active" ' Status
        .Cells(newRow, 8).Value = Now()
    End With
    
    ' Record stock movement
    RecordStockMovement productID, "Rental_Out", 1, rentalID, "Rented to " & customerID
    
    CreateRentalBooking = rentalID
    
End Sub

Function IsRentalAvailable(productID As String, startDate As Date, endDate As Date) As Boolean
    ' Check if product is available for rental dates
    Dim wsRentals As Worksheet
    Dim lastRow As Long
    Dim i As Long
    
    Set wsRentals = ThisWorkbook.Sheets("_Rental_Bookings")
    lastRow = wsRentals.Range("A:A").End(xlDown).Row
    
    IsRentalAvailable = True
    
    For i = 2 To lastRow
        If wsRentals.Cells(i, 2).Value = productID And wsRentals.Cells(i, 7).Value = "Active" Then
            Dim existStart As Date, existEnd As Date
            existStart = wsRentals.Cells(i, 4).Value
            existEnd = wsRentals.Cells(i, 5).Value
            
            ' Check for date overlap
            If Not (endDate < existStart Or startDate > existEnd) Then
                IsRentalAvailable = False
                Exit Function
            End If
        End If
    Next i
    
End Function

Sub ReturnRentalItem(rentalID As String, returnDate As Date, conditionStatus As String)
    ' Process rental return
    Dim wsRentals As Worksheet
    Dim row As Long
    
    Set wsRentals = ThisWorkbook.Sheets("_Rental_Bookings")
    
    row = FindRentalRow(rentalID, wsRentals)
    
    If row > 0 Then
        Dim productID As String
        Dim endDate As Date
        Dim lateDays As Long
        Dim lateFee As Double
        
        productID = wsRentals.Cells(row, 2).Value
        endDate = wsRentals.Cells(row, 5).Value
        
        ' Calculate late fees
        If returnDate > endDate Then
            lateDays = DateDiff("d", endDate, returnDate)
            lateFee = lateDays * 50 ' AED 50 per day (configurable)
            wsRentals.Cells(row, 9).Value = lateFee
        End If
        
        ' Update rental status
        wsRentals.Cells(row, 7).Value = "Returned"
        wsRentals.Cells(row, 10).Value = returnDate
        wsRentals.Cells(row, 11).Value = conditionStatus
        
        ' Update stock
        RecordStockMovement productID, "Rental_Return", 1, rentalID, "Returned - " & conditionStatus
        
        ' Update product condition
        UpdateProductCondition productID, conditionStatus
        
    End If
    
End Sub

Sub UpdateProductCondition(productID As String, conditionStatus As String)
    ' Update product condition status
    Dim wsProducts As Worksheet
    Dim row As Long
    
    Set wsProducts = ThisWorkbook.Sheets("_Products_Master")
    
    row = FindProductRow(productID, wsProducts)
    
    If row > 0 Then
        wsProducts.Cells(row, 12).Value = conditionStatus
    End If
    
End Sub

' ============================================================================
' MODULE: Accounting and Financial Reporting
' ============================================================================

Sub RecordSaleInAccounting(transactionID As String)
    ' Record sale in accounting ledger
    Dim wsAccounting As Worksheet
    Dim wsTransactions As Worksheet
    Dim row As Long
    Dim newAccRow As Long
    Dim saleAmount As Double
    Dim vat As Double
    
    Set wsAccounting = ThisWorkbook.Sheets("_Accounting_Ledger")
    Set wsTransactions = ThisWorkbook.Sheets("_Sales_Transactions")
    
    row = FindTransactionRow(transactionID, wsTransactions)
    
    If row > 0 Then
        saleAmount = wsTransactions.Cells(row, 5).Value
        vat = wsTransactions.Cells(row, 6).Value
        
        newAccRow = wsAccounting.Range("A:A").End(xlDown).Row + 1
        
        With wsAccounting
            .Cells(newAccRow, 1).Value = transactionID
            .Cells(newAccRow, 2).Value = "Sales Revenue"
            .Cells(newAccRow, 3).Value = saleAmount
            .Cells(newAccRow, 4).Value = 0
            .Cells(newAccRow, 5).Value = Now()
        End With
        
        ' Record VAT
        newAccRow = wsAccounting.Range("A:A").End(xlDown).Row + 1
        With wsAccounting
            .Cells(newAccRow, 1).Value = transactionID
            .Cells(newAccRow, 2).Value = "VAT Collected"
            .Cells(newAccRow, 3).Value = vat
            .Cells(newAccRow, 4).Value = 0
            .Cells(newAccRow, 5).Value = Now()
        End With
    End If
    
End Sub

Function CalculateProfit(startDate As Date, endDate As Date) As Double
    ' Calculate profit based on cost vs selling price
    ' This requires matching transactions with costs
    Dim wsTransactions As Worksheet
    Dim wsItems As Worksheet
    Dim wsProducts As Worksheet
    Dim totalRevenue As Double
    Dim totalCost As Double
    Dim i As Long, j As Long
    Dim lastRow As Long, itemLastRow As Long
    
    Set wsTransactions = ThisWorkbook.Sheets("_Sales_Transactions")
    Set wsItems = ThisWorkbook.Sheets("_Transaction_Items")
    Set wsProducts = ThisWorkbook.Sheets("_Products_Master")
    
    lastRow = wsTransactions.Range("A:A").End(xlDown).Row
    itemLastRow = wsItems.Range("A:A").End(xlDown).Row
    
    ' Sum all transactions in date range
    For i = 2 To lastRow
        Dim transDate As Date
        transDate = wsTransactions.Cells(i, 3).Value
        
        If transDate >= startDate And transDate <= endDate Then
            totalRevenue = totalRevenue + wsTransactions.Cells(i, 5).Value
        End If
    Next i
    
    ' Calculate cost from items
    For j = 2 To itemLastRow
        Dim transID As String
        transID = wsItems.Cells(j, 1).Value
        
        For i = 2 To lastRow
            If wsTransactions.Cells(i, 1).Value = transID Then
                Dim transDate As Date
                transDate = wsTransactions.Cells(i, 3).Value
                
                If transDate >= startDate And transDate <= endDate Then
                    Dim productID As String
                    Dim costPrice As Double
                    Dim quantity As Long
                    
                    productID = wsItems.Cells(j, 2).Value
                    quantity = wsItems.Cells(j, 3).Value
                    
                    ' Find cost price
                    Dim prodRow As Long
                    prodRow = FindProductRow(productID, wsProducts)
                    
                    If prodRow > 0 Then
                        costPrice = wsProducts.Cells(prodRow, 8).Value
                        totalCost = totalCost + (costPrice * quantity)
                    End If
                End If
                Exit For
            End If
        Next i
    Next j
    
    CalculateProfit = totalRevenue - totalCost
    
End Function

' ============================================================================
' MODULE: Audit and Logging
' ============================================================================

Sub LogAudit(username As String, action As String, reference As String, details As String)
    ' Log all important actions for audit trail
    Dim wsAudit As Worksheet
    Dim newRow As Long
    
    Set wsAudit = ThisWorkbook.Sheets("_Audit_Log")
    
    newRow = wsAudit.Range("A:A").End(xlDown).Row + 1
    
    With wsAudit
        .Cells(newRow, 1).Value = Now()
        .Cells(newRow, 2).Value = username
        .Cells(newRow, 3).Value = action
        .Cells(newRow, 4).Value = reference
        .Cells(newRow, 5).Value = details
    End With
    
End Sub

' ============================================================================
' MODULE: Helper Functions
' ============================================================================

Function FindProductRow(productID As String, ws As Worksheet) As Long
    ' Find row number for a product
    Dim lastRow As Long, i As Long
    lastRow = ws.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = productID Then
            FindProductRow = i
            Exit Function
        End If
    Next i
    
    FindProductRow = 0
End Function

Function FindCustomerRow(customerID As String, ws As Worksheet) As Long
    ' Find row number for a customer
    Dim lastRow As Long, i As Long
    lastRow = ws.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = customerID Then
            FindCustomerRow = i
            Exit Function
        End If
    Next i
    
    FindCustomerRow = 0
End Function

Function FindTransactionRow(transactionID As String, ws As Worksheet) As Long
    ' Find row number for a transaction
    Dim lastRow As Long, i As Long
    lastRow = ws.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = transactionID Then
            FindTransactionRow = i
            Exit Function
        End If
    Next i
    
    FindTransactionRow = 0
End Function

Function FindRentalRow(rentalID As String, ws As Worksheet) As Long
    ' Find row number for a rental
    Dim lastRow As Long, i As Long
    lastRow = ws.Range("A:A").End(xlDown).Row
    
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = rentalID Then
            FindRentalRow = i
            Exit Function
        End If
    Next i
    
    FindRentalRow = 0
End Function

Function GetProductName(productID As String) As String
    ' Retrieve product name from master
    Dim wsProducts As Worksheet
    Dim row As Long
    
    Set wsProducts = ThisWorkbook.Sheets("_Products_Master")
    
    row = FindProductRow(productID, wsProducts)
    
    If row > 0 Then
        GetProductName = wsProducts.Cells(row, 2).Value
    End If
    
End Function
