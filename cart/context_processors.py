"""
Cart Context Processor
Makes the Cart instance available as {{ cart }} in all templates.
"""
from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}
