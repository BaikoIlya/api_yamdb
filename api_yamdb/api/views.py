from django.db.models import Avg
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from .filters import TitleFilter
from .mixins import (
    CreateDestroyListGenericMixin,
    CreateListDestroyUpdateRetrieveMixin,
)
from .permission import UserAdminOnly, ReviewAndCommentPermission
from .serializers import (
    CategorySerializer, GenreSerializer,
    MyTokenObtainPairSerializer, TitleCreateSerializer,
    TitleViewSerializer, UserAuthSerializer,
    UserMeSerializer, UsersSerializer, ReviewSerializer,
    CommentSerializer,
)
from titles.models import Category, Genre, Title
from user.models import User
from reviews.models import Review


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_sign_up(request):
    serializer = UserAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    future_user = User.objects.get(
        username=request.data['username'],
        email=request.data['email'],
    )
    code = default_token_generator.make_token(future_user)
    to_email = request.data['email']
    sender = 'api'
    email_domen = '@email.com'
    send_mail(
        'Confirmation_code',
        "Добро пожаловать {0}!"
        " Ваш код для получения JWT-токена: {1}".format(
            request.data['username'],
            code
        ),
        sender + email_domen,
        [to_email],
        fail_silently=False,

    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def obtain_pair(request):
    serializer = MyTokenObtainPairSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cur_user = get_object_or_404(User, username=request.data['username'])
    if default_token_generator.check_token(
            cur_user, request.data['confirmation_code']
    ):
        refresh = RefreshToken.for_user(cur_user)
        token = {
            'token': str(refresh.access_token)
        }
        return Response(token, status=status.HTTP_200_OK)
    return Response(
        data='Пользователь и код не совпадают',
        status=status.HTTP_400_BAD_REQUEST
    )


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, UserAdminOnly)
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        if self.request.method == 'PATCH':
            user = self.request.user
            serializer = UserMeSerializer(user, data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                username=self.request.user.username,
                email=self.request.user.email
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = self.request.user
        serializer = UserMeSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    @action(detail=False, methods=['get'])
    def get_queryset(self):
        return Title.objects.annotate(
            rating=Round(Avg('reviews__score'), precision=1)
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewAndCommentPermission,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewAndCommentPermission,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()
