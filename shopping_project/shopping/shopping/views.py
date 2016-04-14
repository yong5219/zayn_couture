from django.views.generic import ListView, TemplateView
from django.db.models import Q

from homes.models import BannerSlider
from products.models import Product


class Home(ListView):

    template_name = 'home.html'
    model = Product

    def get_queryset(self, slug=None):
        search = self.request.GET.get('search', '')
        if search:
            object_list = self.model.objects.filter(Q(slug__icontains=search) | Q(tags__slug__icontains=search))
        else:
            object_list = self.model.objects.all()
        return object_list

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['banners'] = BannerSlider.objects.valid()
        context['products'] = Product.objects.all().order_by('?')[:12]
        search = self.request.GET.get('search', '')
        context['user'] = self.request.user
        if search:
            context['search'] = search
        return context
