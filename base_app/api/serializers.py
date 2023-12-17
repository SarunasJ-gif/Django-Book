from rest_framework.serializers import ModelSerializer
from base_app.models import Book, User


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'description']



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username', 'name', 'last_name', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

