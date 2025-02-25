from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from Backend import settings
from api.views import *
# from api.views import (
#     RegisterView, LoginView, LogoutView, ProfileView,
#     UtilisateurViewSet, CategorieViewSet, ProduitViewSet, VenteViewSet,
#     OnlineUsersView, UpdateActivityView, ConnectionStateView, ConnectionStatesView,CandidatureViewSet, OffreEmploiViewSet,
#     get_available_roles, get_disponibilite, list_users, recherche
# )

router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet)
router.register(r'categories', CategorieViewSet)
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'ventes', VenteViewSet, basename='vente')

router.register(r'categorie_discussions', CategorieDiscussionViewSet)
router.register(r'sujets', SujetViewSet)
router.register(r'messages', MessageViewSet)

router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include([
        path('register/', RegisterView.as_view(), name='register'),
        path('login/', LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('roles/', get_available_roles, name='available-roles'),
        path('disponibilite/', get_disponibilite, name='get_disponibilite'),
    ])),
    path('users', list_users, name='list-users'),
    path('recherche', recherche, name='recherche'),
    path('api/utilisateurs/<int:utilisateur_id>/', ProfileView.as_view(), name='ProfileView'),
    path('online-users/', OnlineUsersView.as_view(), name='online-users'),
    path('update-activity/', UpdateActivityView.as_view(), name='update-activity'),
    path('users/<int:utilisateur_id>/connection-state', ConnectionStateView.as_view(), name='connection-state'),
    path('users/connection-states', ConnectionStatesView.as_view(), name='connection-states'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)