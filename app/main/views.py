from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category, Profile
from django import forms
import json
from cart.cart import Cart
from django.core.exceptions import ObjectDoesNotExist

def update_info(request):
    if request.user.is_authenticated:
        try:
            current_user = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            current_user = Profile(user=request.user)

        if request.method == 'POST':
            current_user.phone = request.POST.get('phone')
            current_user.address1 = request.POST.get('address1')
            current_user.address2 = request.POST.get('address2')
            current_user.city = request.POST.get('city')
            current_user.state = request.POST.get('state')
            current_user.zipcode = request.POST.get('zipcode')
            current_user.country = request.POST.get('country')
            current_user.save()
            request.session['my_shipping'] = {
                'shipping_full_name': request.POST.get('full_name', request.user.get_full_name()),
                'shipping_email': request.POST.get('email', request.user.email),
                'shipping_address1': request.POST.get('address1'),
                'shipping_address2': request.POST.get('address2'),
                'shipping_city': request.POST.get('city'),
                'shipping_state': request.POST.get('state'),
                'shipping_zipcode': request.POST.get('zipcode'),
                'shipping_country': request.POST.get('country'),
            }
            messages.success(request, "Your info has been updated")
            return redirect('home')

        return redirect('home')
    else:
        messages.error(request, "You must be logged in")
        return redirect('home')


def category(request, food):
    #grab the category from the url
    try:
        category = Category.objects.get(name=food)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html',{'products':products, 'category':category} )
    except:
        messages.success(request, ("The category does.nt exist."))
        return redirect('menu')

def menu(request):
    products = Product.objects.all()
    return render(request, 'menu.html', {'products':products})

def home(request):
    return render(request, 'home.html', {})

def faqs(request):
    return render(request, 'faqs.html', {})

def about(request):
    return render(request, 'about.html', {})

def logout_view(request):
    if request.user.is_authenticated:
        cart = Cart(request)

        # ✅ Prevent crash by always ensuring Profile exists
        profile, created = Profile.objects.get_or_create(user=request.user)

        # Save the cart to Profile
        profile.old_cart = json.dumps(cart.cart)  # assuming cart.cart returns a dict
        profile.save()

        logout(request)

    return redirect('/')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Username does not exist')
            return render(request, 'home.html', {'show_login': True})

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid password')
            return render(request, 'home.html', {'show_login': True})

        login(request, user)

        # ✅ Ensure Profile always exists
        profile, created = Profile.objects.get_or_create(user=user)

        # 🛒 Restore cart from saved data
        saved_cart = profile.old_cart
        if saved_cart:
            converted_cart = json.loads(saved_cart)
            cart = Cart(request)
            for key, value in converted_cart.items():
                cart.db_add(product=key, quantity=value)

        return redirect('/home/')

    return redirect('/home/')


def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already in use')
            return redirect('/')

        # Create user and save
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # ✅ Ensure Profile is created only if it doesn't exist
        if not Profile.objects.filter(user=user).exists():
            Profile.objects.create(user=user, old_cart=json.dumps({}))

        # Auto login
        login(request, user)
        return redirect('/')
        
    return render(request, 'register.html')
