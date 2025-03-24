from django import template

register = template.Library()


@register.filter
def calculate_discount(price, discount):
    """
    The discount is related to the logged in user, so it comes in the request
    information. By using this filter, we can iterate over all the rooms directly
    in the template without having to first iterate them to calculate the
    discounted prices and then pass them through the context.
    This solution feels a bit weird, please refactor if it causes any problems.
    """
    return price + (price * discount)
