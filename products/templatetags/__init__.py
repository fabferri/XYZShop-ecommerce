from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary"""
    if dictionary:
        return dictionary.get(int(key), 0)
    return 0
