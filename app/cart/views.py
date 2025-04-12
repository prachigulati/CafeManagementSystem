from django.shortcuts import render, get_object_or_404 # type: ignore
from .cart import Cart
from main.models import Product
from django.http import JsonResponse # type: ignore
from django.contrib import messages
# Create your views here.

def cart_summary(request):
    #get the cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, "cart_summary.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals})

def cart_add(request):
    #get the cart
    cart = Cart(request)
    #test for POST
    if request.POST.get('action') == 'post':
        #get stuff
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        #lookup product in db
        product = get_object_or_404(Product, id=product_id) # type: ignore
        #save to session
        cart.add(product=product, quantity=product_qty)
        #get cart quantity
        cart_quantity = cart.__len__()
        #return response
        # response = JsonResponse({'Product Name: ': product.name})
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request,("Item added to cart"))
        return response

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        #get stuff
        product_id = int(request.POST.get('product_id'))
        #call delete function in cart
        cart.delete(product=product_id)
        response = JsonResponse({'product':product_id})
        return response


# def cart_update(request):
#     cart = Cart(request)
#     if request.POST.get('action') == 'post':
#         #get stuff
#         product_id = int(request.POST.get('product_id'))
#         product_qty = int(request.POST.get('product_qty'))
#         cart.update(product=product_id, quantity=product_qty)
#         response = JsonResponse({'qty':product_qty})
#         return response


def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = request.POST.get('product_qty')
        if product_id and product_qty and product_qty.isdigit():
            product_id = int(product_id)
            product_qty = int(product_qty)
            cart.update(product=product_id, quantity=product_qty)
            return JsonResponse({'qty': product_qty})
        else:
            return JsonResponse({'error': 'Invalid product ID or quantity'}, status=400)
