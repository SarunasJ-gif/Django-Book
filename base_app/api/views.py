from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from base_app.models import Book, User
from rest_framework import status
from .serializers import BookSerializer, UserSerializer
import jwt, datetime
from rest_framework.decorators import api_view
from django.db.models import Q


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email).first()
    if user is None:
        raise AuthenticationFailed('User not found')
    if not user.check_password(password):
        raise AuthenticationFailed('Incorect password!')
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'email': user.email
    }
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    response = Response()
    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'jwt': token
    }
    return response


def is_authenticated(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AttributeError("Unauthenticated!")
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AttributeError("Unauthenticated!")
    user = User.objects.filter(id=payload['id']).first()
    return user


@api_view(['POST'])
def logout(request):
    response = Response()
    response.delete_cookie('jwt')
    response.data = {
        'message': 'success'
    }
    return response


@api_view(['GET'])
def get_users(request):
    is_authenticated(request)
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_user(request, id):
    user = is_authenticated(request)
    get_user = User.objects.get(id=id)
    if user != get_user and not user.is_superuser:
        return Response({'error': 'You are not allowed'}, status=status.HTTP_403_FORBIDDEN)
    serializer = UserSerializer(get_user, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
def update_user(request, id):
    user = is_authenticated(request)
    try:
        get_user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error': 'Book not found...'}, status=status.HTTP_404_NOT_FOUND)
    if user != get_user and not user.is_superuser:
        return Response({'error': 'You are not allowed!'}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'PUT':
        serializer = UserSerializer(get_user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'error': 'Invalid data!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_user(request, id):
    user = is_authenticated(request)
    try:
        get_user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error': 'User not found...'}, status=status.HTTP_404_NOT_FOUND)
    if user != get_user and not user.is_superuser:
        return Response({'error': 'You are not allowed!'}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':      
        if get_user == user:
            get_user.delete()
            response = Response()
            response.delete_cookie('jwt')
            response.data = {
                'message': 'User deleted successfully! Logout successfully!',
            }
            return response
        get_user.delete()
        return Response({'message': 'User deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_books(request):
    is_authenticated(request)
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_book(request, id):
    is_authenticated(request)
    book = Book.objects.get(id=id)
    serializer = BookSerializer(book, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def get_books_by(request):
    is_authenticated(request)
    q = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    books = Book.objects.filter(
        Q(name__icontains=q)
    )
    if date_from and date_to:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        books = books.filter(added__range=[date_from, date_to])
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_paginated_books(request):
    is_authenticated(request)
    books = Book.objects.all()
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('page_size', 10)
    result_page = paginator.paginate_queryset(books, request)
    serializer = BookSerializer(result_page, many=True)    
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
def add_book(request):
    user = is_authenticated(request)
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user)
        return Response(serializer.data)
    return Response({'error': 'Invalid data!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_book(request, id):
    user = is_authenticated(request)
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found...'}, status=status.HTTP_404_NOT_FOUND)
    if user != book.user and not user.is_superuser:
        return Response({'error': 'You are not allowed!'}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'error': 'Invalid data!'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['DELETE'])
def delete_book(request, id):
    user = is_authenticated(request)
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found...'}, status=status.HTTP_404_NOT_FOUND)
    if user != book.user and not user.is_superuser:
        return Response({'error': 'You are not allowed!'}, status=status.HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        book.delete()
        return Response({'message': 'Book deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    
