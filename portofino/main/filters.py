from django.db.models import Q

class PublicationFilter:
    def __init__(self, request_GET, queryset):
        self.queryset = queryset
        self.GET = request_GET
        self.form = self.get_form()

    def get_form(self):
        return {
            'title': self.GET.get('title', ''),
            'min_price': self.GET.get('min_price', ''),
            'max_price': self.GET.get('max_price', ''),
            'in_stock': self.GET.get('in_stock', '')
        }

    @property
    def qs(self):
        queryset = self.queryset
        title = self.GET.get('title')
        min_price = self.GET.get('min_price')
        max_price = self.GET.get('max_price')
        in_stock = self.GET.get('in_stock')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        if in_stock:
            queryset = queryset.filter(stock__gt=0)

        return queryset 