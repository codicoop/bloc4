from django import template

register = template.Library()


@register.filter
def calculate_discount(price, discount):
    total = price + (price * discount)
    if total.is_integer():
        return int(total)
    return round(total, 2)
