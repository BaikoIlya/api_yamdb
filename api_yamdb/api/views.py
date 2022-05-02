import random

from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .filters import TitleFilter
from .mixins import (
    CreateDestroyListGenericMixin,
    CreateListDestroyUpdateRetrieveMixin,
)
from .permission import UserAdminOnly
from .serializers import (
    CategorySerializer, GenreSerializer,
    MyTokenObtainPairSerializer, TitleCreateSerializer,
    TitleViewSerializer, UserAuthSerializer,
    UserMeSerializer, UsersSerializer,
)
from titles.models import Category, Genre, Title
from user.models import Confirmation, User


def generate_code():
    random.seed()
    value = str(random.randint(10000, 99999))
    if Confirmation.objects.filter(confirmation_code=value).exists():
        return generate_code()
    return value


class UserSignUp(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=request.data['username']).exists():
                return Response(
                    data='Пользователь c таким именем существует',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if request.data['username'] == 'me':
                return Response(
                    data='Пользователь c таким именем нельзя зарегистрировать',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if User.objects.filter(email=request.data['email']).exists():
                return Response(
                    data='Такая электронная почта уже зарегистрирована',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            code = generate_code()
            future_user = User.objects.get(
                username=request.data['username'],
                email=request.data['email'],
            )
            Confirmation.objects.create(
                user=future_user,
                confirmation_code=code,
            )
            mail_subject = 'Confirmation_code'
            message = (
                "Добро пожаловать {0}!"
                " Ваш код для получения JWT-токена: {1}".format(
                    self.request.data['username'],
                    code
                )
            )
            to_email = request.data['email']
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainPairView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(username=request.data['username']).exists():
                cur_user = User.objects.get(username=request.data['username'])
                if Confirmation.objects.filter(
                        user=cur_user,
                        confirmation_code=request.data['confirmation_code']
                ).exists():
                    user = Confirmation.objects.get(
                        user=cur_user,
                        confirmation_code=request.data['confirmation_code']
                    )
                    refresh = RefreshToken.for_user(user)
                    token = {
                        'token': str(refresh.access_token)
                    }
                    return Response(token, status=status.HTTP_200_OK)
                return Response(
                    data='Пользователь и код не совпадают',
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                data='Нет такого пользователя',
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMe(APIView):
    def get(self, request):
        user = request.user
        serializer = UserMeSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserMeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(
                username=self.request.user.username,
                email=self.request.user.email
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, UserAdminOnly,)
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class CategoryViewSet(CreateDestroyListGenericMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'DELETE':
            return permissions.IsAuthenticated(), UserAdminOnly(),
        return super().get_permissions()


class GenreViewSet(CreateDestroyListGenericMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'DELETE':
            return permissions.IsAuthenticated(), UserAdminOnly(),
        return super().get_permissions()


class TitleViewSet(CreateListDestroyUpdateRetrieveMixin):
    queryset = Title.objects.all()
    serializer_class = TitleViewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleCreateSerializer
        return TitleViewSerializer

    def get_permissions(self):
        if (self.request.method == 'POST'
           or self.request.method == 'PATCH'
           or self.request.method == 'DELETE'):
            return permissions.IsAuthenticatedOrReadOnly(), UserAdminOnly(),
        return super().get_permissions()
