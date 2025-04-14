from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from .cart import Cart
from main.models import Product, Profile
from cart.models import  Order, OrderItem
from django.http import JsonResponse # type: ignore
from django.contrib import messages
import datetime
# Create your views here.


def orders(request, pk):
	if request.user.is_authenticated and request.user.is_superuser:
		# Get the order
		order = Order.objects.get(id=pk)
		# Get the order items
		items = OrderItem.objects.filter(order=pk)

		if request.POST:
			status = request.POST['shipping_status']
			# Check if true or false
			if status == "true":
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				now = datetime.datetime.now()
				order.update(shipped=True, date_shipped=now)
			else:
				# Get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				order.update(shipped=False)
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, 'orders.html', {"order":order, "items":items})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')


def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# Get the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=True, date_shipped=now)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')

		return render(request, "not_shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# grab the order
			order = Order.objects.filter(id=num)
			# grab Date and time
			now = datetime.datetime.now()
			# update order
			order.update(shipped=False)
			# redirect
			messages.success(request, "Shipping Status Updated")
			return redirect('home')


		return render(request, "shipped_dash.html", {"orders":orders})
	else:
		messages.success(request, "Access Denied")
		return redirect('home')



def process_order(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Get Shipping Session Data
        my_shipping = request.session.get('my_shipping')

        # Check if my_shipping exists
        if not my_shipping:
            messages.error(request, "Shipping information is missing. Please try again.")
            return redirect('checkout')  # Redirect the user to an appropriate page

        # Gather Order Info
        full_name = my_shipping.get('shipping_full_name', 'Default Name')  # Use a default value if key doesn't exist
        email = my_shipping.get('shipping_email', 'default@example.com')
        shipping_address = f"{my_shipping.get('shipping_address1', '')}\n" \
                           f"{my_shipping.get('shipping_address2', '')}\n" \
                           f"{my_shipping.get('shipping_city', '')}\n" \
                           f"{my_shipping.get('shipping_state', '')}\n" \
                           f"{my_shipping.get('shipping_zipcode', '')}\n" \
                           f"{my_shipping.get('shipping_country', '')}"
        amount_paid = totals

        # Create an Order
        if request.user.is_authenticated:
            # Logged in user
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            order_id = create_order.pk
            for product in cart_products():
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price
                for key, value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            # Delete the cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            # Remove old_cart from the Profile
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")

            messages.success(request, "Order Placed!")
            return redirect('home')

        else:
            # Not logged in
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # Add order items
            order_id = create_order.pk
            for product in cart_products():
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price
                for key, value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            # Delete the cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "Order Placed!")
            return redirect('home')

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def checkout(request):
    if not request.user.is_authenticated:
        # Redirect to the same page and automatically show the registration modal
        messages.info(request, "You need to register or log in before proceeding to checkout.")
        return redirect('/?show_register_modal=true')  # Passing a query param to trigger the modal
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    # Get user profile if logged in
    profile = None
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None

    return render(request, "checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "profile": profile,  # Pass profile to template
    })

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
        cart_quantity =len(cart)
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
