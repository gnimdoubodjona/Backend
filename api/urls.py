from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from Backend import settings
from api.views import *
#from views import *

router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include([
        path('register/', RegisterView.as_view(), name='register'),
        path('login/', LoginView.as_view(), name='login'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('roles/', get_available_roles, name='available-roles'),
    ])),
    path('users/', list_users, name='list-users'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)