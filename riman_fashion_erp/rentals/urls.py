from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rentals.models import RentalAgreement

class RentalListView(APIView):
    """List rentals"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        rentals = RentalAgreement.objects.all().order_by('-rental_date')
        data = [{
            'id': r.id,
            'rental_number': r.rental_number,
            'client_name': r.client.name,
            'rental_date': r.rental_date.isoformat(),
            'return_date': r.return_date.isoformat(),
            'status': r.status,
            'rental_cost': str(r.rental_cost),
        } for r in rentals]
        return Response(data)


urlpatterns = [
    path('list/', RentalListView.as_view(), name='rental-list'),
]
