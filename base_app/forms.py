from django.forms import ModelForm
from .models import Book, User


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ['user', 'added']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'name', 'last_name', 'phone']