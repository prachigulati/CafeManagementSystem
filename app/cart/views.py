from django.shortcuts import render, get_object_or_404 # type: ignore
from .cart import Cart
from main.models import Product
from django.http import JsonResponse # type: ignore
# Create your views here.

def cart_summary(request):
    return render(request, "cart_summary.html", {})

def cart_add(request):
    #get the cart
    cart = Cart(request)
    #test for POST
    if request.POST.get('action') == 'post':
        #get stuff
        product_id = int(request.POST.get('product_id'))
        #lookup product in db
        product = get_object_or_404(Product, id=product_id) # type: ignore
        #save to session
        cart.add(product=product)
        #get cart quantity
        # cart_quantity = cart.__len__()
        #return response
        response = JsonResponse({'Product Name: ': product.name})
        # response = JsonResponse({'qty': cart_quantity})
        return response

def cart_delete(request):
    pass

def cart_update(request):
    pass
