import datetime

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from user.models import User


class UserAuthSerializer(serializers.ModelSerializer):
    """Сериализатор для авторизации пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise ValidationError('Пользователь c таким именем существует')
        if data['username'] == 'me':
            raise ValidationError(
                'Пользователь c таким именем нельзя зарегистрировать'
            )
        if User.objects.filter(email=data['email']).exists():
            return ValidationError(
                'Такая электронная почта уже зарегистрирована'
            )
        return data


class MyTokenObtainPairSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=10)


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра собственной информации."""
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для поиска пользователей Админом."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        lookup_field = 'username'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""
    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title для методов POST и PATCH.
    """
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    description = serializers.CharField(
        required=False
    )

    def validator_year(self, value):
        if value > datetime.datetime.now().year:
            raise serializers.ValidationError(
                '%(value)s is not a correcrt year!!!'
            )
        return value

    class Meta:
        model = Title
        fields = '__all__'


class TitleViewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title для метода GET.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(max_value=10, min_value=0)
    rating = serializers.IntegerField(read_only=True)

    def validate_score(self, value):
        if not 0 < value < 11:
            raise serializers.ValidationError(
                'Оценка должна быть целым числом от 0 до 10.'
            )
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Вы уже оставляли отзыв.')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'rating',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
