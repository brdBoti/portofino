from django.contrib import admin
from .models import Employee, Book, Review, Publication, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'date_ordered']
    list_filter = ['status', 'date_ordered']
    inlines = [OrderItemInline]

class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'stock']
    search_fields = ['title']

admin.site.register(Employee)
admin.site.register(Book)
admin.site.register(Review)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Order, OrderAdmin)
