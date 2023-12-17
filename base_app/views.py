from datetime import datetime
from http.client import responses
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Book, User
from .forms import BookForm, UserForm
import jwt
import datetime


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')   
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User doesn't exist")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'email': user.email
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response = redirect('home')
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token
            }
            login(request, user)
            
            return response
        else:
            messages.error(request, "Bad credentials...")
    context = {'page': page}
    return render(request, 'base_app/login_page.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


def register_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'email': user.email
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response = redirect('home')
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token
            }
            login(request, user)
            return response 
        else:
            messages.error(request, 'An error occured durring registration...') 
    return render(request, 'base_app/login_page.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    books = Book.objects.filter(
        Q(name__icontains=q)
    )
    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        books = books.filter(added__range=[date_from, date_to])
    books_count = books.count()
    context = {'books': books, 'books_count': books_count}
    return render(request, 'base_app/home.html', context)

def book(request, id):
    book = Book.objects.get(id=id)
    context = {'book': book}
    return render(request, 'base_app/book.html', context)


@login_required(login_url='login')
def add_book(request):
    form = BookForm()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base_app/book_form.html', context)


@login_required(login_url='login')
def update_book(request, id):
    book = Book.objects.get(id=id)
    form = BookForm(instance=book)
    if request.user != book.user and not request.user.is_superuser:
        return HttpResponse('You are not allow...')
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base_app/book_form.html', context)


@login_required(login_url='login')
def delete_book(request, id):
    book = Book.objects.get(id=id)
    if request.user != book.user and not request.user.is_superuser:
        return HttpResponse('You are not allow...')
    if request.method == 'POST':
        book.delete()
        return redirect('home')
    return render(request, 'base_app/delete.html', {'obj': book})


def user_profile(request, id):
    user = User.objects.get(id=id)
    books = user.book_set.all()
    context = {'user': user, 'books': books}
    return render(request, 'base_app/user_profile.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', id = user.id)
    context = {'form': form}
    return render(request, 'base_app/update_user.html', context)
