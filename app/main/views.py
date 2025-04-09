from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category

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
