from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from products.models import Product, Category


class ProductList(ListView):

    template_name = 'product/product_list.html'
    model = Product
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        # slug = self.request.GET.get('slug', '')
        object_list = self.model.objects.filter(main_category__slug=self.category, is_active=True).exclude(structure="CHILD")
        return object_list

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['category'] = self.category

        context['products'] = Product.objects.filter(
            main_category=self.category, is_active=True,
        )

        context['selected_page'] = "index"
        context['sub_selected_page'] = self.category

        return context


class ProductDetail(DetailView):
    template_name = 'product/product_detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['selected_page'] = "product"
        return context
