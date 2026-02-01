from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from inventory.models import Product, StockMovement, Warehouse, ProductImage
from inventory.forms import ProductForm, StockMovementForm, WarehouseForm, ProductImageForm


class InventoryDashboardView(LoginRequiredMixin, TemplateView):
    """Inventory module dashboard"""
    template_name = 'modules/inventory_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()[:10]
        context['stocks'] = StockMovement.objects.all()[:10]
        return context


class ProductListView(LoginRequiredMixin, ListView):
    """Product list view"""
    template_name = 'modules/product_list.html'
    model = Product
    paginate_by = 20
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.all().order_by('-created_at')


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Create new product"""
    model = Product
    form_class = ProductForm
    template_name = 'modules/product_form.html'
    success_url = reverse_lazy('product_list')


class StockListView(LoginRequiredMixin, ListView):
    """Stock list view"""
    template_name = 'modules/stock_list.html'
    model = StockMovement
    paginate_by = 20
    context_object_name = 'stocks'
    
    def get_queryset(self):
        return StockMovement.objects.all()


class StockCreateView(LoginRequiredMixin, CreateView):
    """Create new stock movement"""
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'modules/stock_form.html'
    success_url = reverse_lazy('stock_list')


class WarehouseListView(LoginRequiredMixin, ListView):
    """Warehouse list view"""
    template_name = 'modules/warehouse_list.html'
    model = Warehouse
    paginate_by = 20
    context_object_name = 'warehouses'
    
    def get_queryset(self):
        return Warehouse.objects.all()


class WarehouseCreateView(LoginRequiredMixin, CreateView):
    """Create new warehouse"""
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'modules/warehouse_form.html'
    success_url = reverse_lazy('warehouse_list')


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Product detail view with image gallery"""
    model = Product
    template_name = 'modules/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.gallery_images.all().order_by('order')
        context['image_form'] = ProductImageForm()
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Update product"""
    model = Product
    form_class = ProductForm
    template_name = 'modules/product_form.html'
    
    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


class ProductImageUploadView(LoginRequiredMixin, CreateView):
    """Upload image for product"""
    model = ProductImage
    form_class = ProductImageForm
    
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)
        
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.save()
            product.gallery_images.add(image)
        
        return redirect('product_detail', pk=product_id)
