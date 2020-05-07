from django.contrib import admin
from .models import Item, OrderItem, Order, Coupon, Payment, ShippingAddress


def make_refund_granted(modeladmin, request, queryset):
    queryset.update(refund_granted=True, refund_requested=False)


make_refund_granted.short_description = 'Mark as refund granted'


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'default']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'dispatched', 'delivered',
                    'refund_requested', 'refund_granted', 'payment', 'shipping_address']
    search_fields = ['user__username', 'order_id']
    list_display_links = ['user']
    list_filter = ['ordered', 'dispatched', 'delivered',
                   'refund_requested', 'refund_granted']
    actions = [make_refund_granted]


admin.site.register(Coupon, CouponAdmin)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(ShippingAddress, AddressAdmin)
