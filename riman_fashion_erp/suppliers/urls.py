from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from suppliers.models import Supplier, PurchaseInvoice

class SupplierListView(APIView):
    """List and create suppliers"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        suppliers = Supplier.objects.all()
        data = [{
            'id': s.id,
            'name': s.name,
            'category': s.category,
            'phone': s.phone,
            'email': s.email,
            'status': s.status,
        } for s in suppliers]
        return Response(data)
    
    def post(self, request):
        if not request.user.role in ['admin', 'inventory']:
            return Response({'error': 'Permission denied'}, status=403)
        
        try:
            supplier = Supplier.objects.create(
                name=request.data.get('name'),
                category=request.data.get('category'),
                phone=request.data.get('phone'),
                email=request.data.get('email'),
                address=request.data.get('address'),
                city=request.data.get('city'),
                country=request.data.get('country'),
            )
            return Response({'id': supplier.id, 'message': 'Supplier created'}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class PurchaseInvoiceListView(APIView):
    """List and create purchase invoices"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        invoices = PurchaseInvoice.objects.all()
        data = [{
            'id': i.id,
            'invoice_number': i.invoice_number,
            'supplier': i.supplier.name,
            'total_amount': str(i.total_amount),
            'amount_paid': str(i.amount_paid),
            'status': i.status,
        } for i in invoices]
        return Response(data)


urlpatterns = [
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('invoices/', PurchaseInvoiceListView.as_view(), name='purchase-invoice-list'),
]
