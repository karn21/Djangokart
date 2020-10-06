from django import template
from core.models import Order


register = template.Library()


@register.filter
def cart_items_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            count = 0
            for items in qs[0].items.all():
                count += items.quantity
            return count
        else:
            return 0
    else:
        return 0
