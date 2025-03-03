from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Фильтр для умножения двух чисел (например, количество * цена).
    """
    try:
        value = float(value) if value is not None else 0
        arg = float(arg) if arg is not None else 0
        return value * arg
    except (ValueError, TypeError):
        return 0