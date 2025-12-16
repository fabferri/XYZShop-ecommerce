from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product
from cart.forms import CartAddProductForm

# Create your views here.

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True, is_online=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'products/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True, is_online=True)
    cart_product_form = CartAddProductForm()
    
    # Get reviews for this product
    reviews = product.reviews.all()
    average_rating = product.get_average_rating()
    rating_count = product.get_rating_count()
    rating_distribution = product.get_rating_distribution()
    
    return render(request, 'products/product/detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
        'average_rating': average_rating,
        'rating_count': rating_count,
        'rating_distribution': rating_distribution,
    })


def product_search(request):
    query = request.GET.get('q', '')
    products = []
    categories = Category.objects.all()
    
    if query:
        # Search primarily in product name, with weighted relevance
        # First get products with name matches (higher priority)
        name_matches = Product.objects.filter(
            name__icontains=query,
            available=True,
            is_online=True
        )
        
        # Then get products with description matches (lower priority)
        # Split query into words for better matching
        query_words = query.lower().split()
        
        if len(query_words) == 1:
            # Single word: only search if it's substantial (more than 3 chars)
            if len(query_words[0]) > 3:
                desc_matches = Product.objects.filter(
                    description__icontains=query,
                    available=True,
                    is_online=True
                ).exclude(id__in=name_matches.values_list('id', flat=True))
            else:
                desc_matches = Product.objects.none()
        else:
            # Multiple words: require at least 2 words to match in description
            desc_query = Q()
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    desc_query &= Q(description__icontains=word)
            
            desc_matches = Product.objects.filter(
                desc_query,
                available=True,
                is_online=True
            ).exclude(id__in=name_matches.values_list('id', flat=True))
        
        # Combine results: name matches first, then description matches
        products = list(name_matches) + list(desc_matches)
    
    return render(request, 'products/product/search.html', {
        'query': query,
        'products': products,
        'categories': categories,
        'product_count': len(products)
    })
