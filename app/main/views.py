from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category, Profile
from django import forms
import json
from cart.cart import Cart

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
        else:
            login(request, user)
            #do some shopping cart stuff
            current_user = Profile.objects.get(user__id = request.user.id)
            #get their saved cart from database
            saved_cart = current_user.old_cart
            #convert databse string to python dictionary
            if saved_cart:
                #convert to dictionaryusing json
                converted_cart = json.loads(saved_cart)
                #add the loaded cart dictionary to our session
                #get the cart
                cart= Cart(request)
                #loop through the cart and add the items from tha database
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

        user = User.objects.filter(username=username)

        if user.exists():
            messages.error(request, 'Username already in use')
            return redirect('/register/')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        user.set_password(password)
        user.save()

        # 🔒 Auto-login after registration
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')  # or any page you want after login

    return render(request, 'register.html')
