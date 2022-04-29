from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import UserSignUp, ObtainPairView, UserMe, UsersViewSet


router = SimpleRouter()

router.register('users', UsersViewSet)

urlpatterns = [
    path(
        'v1/auth/token/',
        ObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'v1/auth/signup/',
        UserSignUp.as_view(),
    ),
    path(
        'v1/users/me/',
        UserMe.as_view(),
    ),
    path('v1/', include(router.urls)),
]
