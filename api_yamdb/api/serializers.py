from rest_framework import serializers

from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserCreateSerializer(serializers.Serializer):
    username = serializers.RegexField(required=True,
                                      regex=r'^[\w.@+-]',
                                      max_length=150)
    email = serializers.EmailField(required=True,
                                   max_length=254)

    def validate_username(self, username):
        """Запрещает пользователям присваивать себе имя me
        и использовать повторные username и email."""
        if username == 'me':
            raise serializers.ValidationError(
                'Использовать username "me" запрещено'
            )
        return username

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        if (User.objects.filter(email=email).exists()
                and not User.objects.filter(username=username)):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        if (User.objects.filter(username=username).exists()
                and not User.objects.filter(email=email)):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        return data


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)
