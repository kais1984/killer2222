from django.views.generic import TemplateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from rentals.models import RentalAgreement, RentalItem
from rentals.forms import RentalForm


class RentalsDashboardView(LoginRequiredMixin, TemplateView):
    """Rentals module dashboard"""
    template_name = 'modules/rentals_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rentals'] = RentalAgreement.objects.all()[:10]
        context['rental_items'] = RentalItem.objects.all()[:10]
        return context


class RentalListView(LoginRequiredMixin, ListView):
    """Rental list view"""
    template_name = 'modules/rental_list.html'
    model = RentalAgreement
    paginate_by = 20
    context_object_name = 'rentals'
    
    def get_queryset(self):
        return RentalAgreement.objects.all().order_by('-created_at')


class RentalCreateView(LoginRequiredMixin, CreateView):
    """Create new rental"""
    model = RentalAgreement
    form_class = RentalForm
    template_name = 'modules/rental_form.html'
    success_url = reverse_lazy('rental_list')
