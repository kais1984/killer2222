from django.urls import path
from crm.views import (
    CRMDashboardView, ClientListView, ClientCreateView,
    ClientInteractionListView, ClientInteractionCreateView,
    ContractListView, ContractDetailView, ContractCreateView, ContractUpdateView,
    ContractApproveView, ContractProductionView, ContractReadyView, ContractCompleteView
)

urlpatterns = [
    # CRM Dashboard
    path('', CRMDashboardView.as_view(), name='crm_dashboard'),
    
    # Clients
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    
    # Client Interactions
    path('contacts/', ClientInteractionListView.as_view(), name='contact_list'),
    path('contacts/create/', ClientInteractionCreateView.as_view(), name='contact_create'),
    
    # Contracts (Phase 1)
    path('contracts/', ContractListView.as_view(), name='contract_list'),
    path('contracts/create/', ContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/', ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/edit/', ContractUpdateView.as_view(), name='contract_edit'),
    path('contracts/<int:pk>/approve/', ContractApproveView.as_view(), name='contract_approve'),
    path('contracts/<int:pk>/production/', ContractProductionView.as_view(), name='contract_production'),
    path('contracts/<int:pk>/ready/', ContractReadyView.as_view(), name='contract_ready'),
    path('contracts/<int:pk>/complete/', ContractCompleteView.as_view(), name='contract_complete'),
]
