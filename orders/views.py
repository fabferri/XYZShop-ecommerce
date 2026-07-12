"""
Orders Views
Function-based views for order creation from cart, payment simulation,
and payment confirmation page.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from .models import OrderItem, Order
from .forms import OrderCreateForm, PaymentForm
from products.models import Product
from cart.cart import Cart
import uuid


class InsufficientStock(Exception):
    """Raised when a cart item's quantity exceeds available product stock."""

    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(product_name)


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            if len(cart) == 0:
                messages.error(request, 'Your cart is empty.')
                return redirect('cart:cart_detail')
            try:
                with transaction.atomic():
                    # Lock the product rows to prevent overselling under concurrency.
                    product_ids = [item['product'].id for item in cart]
                    locked = {
                        p.id: p for p in
                        Product.objects.select_for_update().filter(id__in=product_ids)
                    }
                    # Validate stock before creating the order.
                    for item in cart:
                        product = locked.get(item['product'].id)
                        if product is None or product.stock < item['quantity']:
                            raise InsufficientStock(item['product'].name)

                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.save()

                    for item in cart:
                        product = locked[item['product'].id]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=item['price'],
                            quantity=item['quantity'],
                        )
                        # Atomic decrement at the database level.
                        Product.objects.filter(id=product.id).update(
                            stock=F('stock') - item['quantity']
                        )
            except InsufficientStock as exc:
                messages.error(
                    request,
                    f'Sorry, "{exc.product_name}" does not have enough stock.',
                )
                return redirect('cart:cart_detail')

            # clear the cart
            cart.clear()
            # Redirect to payment page
            return redirect('orders:payment', order_id=order.id)
    else:
        # Pre-fill form with user data if authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            
            # Simulate payment processing
            # In a real application, you would integrate with Stripe, PayPal, etc.
            order.payment_method = payment_method
            order.paid = True
            order.status = 'processing'
            
            # Generate a unique payment ID
            order.payment_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
            order.save()
            
            messages.success(request, 'Payment successful! Your order has been confirmed.')
            return redirect('orders:payment_done', order_id=order.id)
    else:
        form = PaymentForm()
    
    return render(request, 'orders/order/payment.html', {
        'order': order,
        'form': form
    })


def payment_done(request, order_id):
    order = get_object_or_404(Order, id=order_id, paid=True)
    return render(request, 'orders/order/payment_done.html', {'order': order})
