from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OrderItem, Order
from .forms import OrderCreateForm, PaymentForm
from cart.cart import Cart
import uuid

# Create your views here.

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Link order to user if authenticated
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
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
