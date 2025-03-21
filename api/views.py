from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, filters, status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from datetime import timedelta
from api.serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from core.models import *
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from . import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver



def print_urls(urlpatterns, depth=0):
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            print("  " * depth + str(pattern.pattern))
        elif isinstance(pattern, URLResolver):
            print("  " * depth + str(pattern.pattern))
            print_urls(pattern.url_patterns, depth + 1)


class ProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, utilisateur_id):
        try:
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            serializer = UtilisateurSerializer(utilisateur)
            return Response(serializer.data)
        except Utilisateur.DoesNotExist:
            raise NotFound("Utilisateur non trouvé")


class RegisterView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print("Données reçues pour l'inscription:", request.data)  # Debug log
        serializer = RegisterSerializer(data=request.data)
        
        try:
            if serializer.is_valid():
                # Créer l'utilisateur
                user = serializer.save()
                print(f"Utilisateur créé avec succès: {user.email}")  # Debug log
                
                # Créer le token JWT
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "message": "Inscription réussie",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "nom": user.nom,
                        "prenoms": user.prenoms,
                        "role": user.role
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                print("Erreurs de validation:", serializer.errors)  # Debug log
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"Erreur lors de l'inscription: {str(e)}")  # Debug log
            return Response(
                {"error": "Une erreur est survenue lors de l'inscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([AllowAny])
def recherche(request):
    #recupérer les paramètres de recherche
    emplacement = request.query_params.get('emplacement', '').lower()
    disponibilite = request.query_params.get('disponibilite', '')  # Ne pas convertir en lower() car sensible à la casse
    role = request.query_params.get('role', '')

    print(f"Paramètres de recherche reçus: emplacement='{emplacement}', disponibilite='{disponibilite}', role='{role}'")

    #commencer avec tous les utilisateurs
    queryset = Utilisateur.objects.all()
    print(f"Nombre total d'utilisateurs avant filtrage: {queryset.count()}")

    # Appliquer les filtres un par un et vérifier les résultats à chaque étape
    if emplacement:
        location_filter = (
            Q(emplacement__icontains=emplacement) |
            Q(zone_intervention__icontains=emplacement) |
            Q(zones_de_consultation__icontains=emplacement)
        )
        queryset = queryset.filter(location_filter)
        print(f"Après filtre emplacement: {queryset.count()} utilisateurs")
        for user in queryset:
            print(f"- {user.nom} ({user.role}) à {user.emplacement}")

    if disponibilite:
        print(f"Application du filtre disponibilité: '{disponibilite}'")
        queryset = queryset.filter(disponibilite=disponibilite)
        print(f"Après filtre disponibilité: {queryset.count()} utilisateurs")
        for user in queryset:
            print(f"- {user.nom} ({user.role}) disponibilité: {user.disponibilite}")

    if role and role.lower() != 'none':
        print(f"Application du filtre rôle: '{role}'")
        queryset = queryset.filter(role=role)
        print(f"Après filtre rôle: {queryset.count()} utilisateurs")
        for user in queryset:
            print(f"- {user.nom} (rôle: {user.role})")

    print(f"Nombre final d'utilisateurs trouvés: {queryset.count()}")

    users_data = []
    for user in queryset:
        user_data = {
            'id': user.id,
            'nom': user.nom,
            'prenoms': user.prenoms,
            'role': user.role,
            'emplacement': user.emplacement,
            'disponibilite': user.disponibilite
        }

        if user.role == 'prestataire':
            user_data.update({
                'specialites': user.specialites,
            })
        elif user.role == 'agriculteur':
            user_data.update({
                'type_cultures': user.type_cultures,
            })
        elif user.role == 'eleveur':
            user_data.update({
                'type_animaux': user.type_animaux,
            })
        users_data.append(user_data)
    
    return Response({'results': users_data})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_users(request):
    users = Utilisateur.objects.all()
    return Response({
        'users': [
            {
                'id': user.id,
                'email': user.email,
                'nom': user.nom,
                'prenoms': user.prenoms,
                'role': user.role
            } for user in users
        ]
    })



class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            # Mettre à jour le statut en ligne de l'utilisateur
            #user.update_online_status(True)
            
            serializer_user = UtilisateurSerializer(user)
            return Response({
                'token': str(refresh.access_token),
                'user': serializer_user.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Mettre à jour le statut en ligne de l'utilisateur
        request.user.update_online_status(False)
        return Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)

class OnlineUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Considérer un utilisateur comme hors ligne s'il n'a pas eu d'activité depuis 5 minutes
        timeout = timezone.now() - timedelta(minutes=5)
        
        # Récupérer tous les utilisateurs en ligne (excluant l'utilisateur actuel)
        online_users = Utilisateur.objects.filter(
            Q(is_online=True) & 
            Q(last_activity__gte=timeout) & 
            ~Q(id=request.user.id)
        ).order_by('-last_activity')

        serializer = UtilisateurSerializer(online_users, many=True)
        return Response(serializer.data)

class UpdateActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.update_last_activity()
        return Response({"message": "Activité mise à jour"}, status=status.HTTP_200_OK)

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def get_liste_roles(self):
        return Utilisateur.ROLE_CHOICES

#méthode pour recupérer la liste des roles

@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_roles(request):
    #endpoint pour recupérer la liste des roles
    roles = Utilisateur.ROLE_CHOICES
    roles_list = [{'value': role[0], 'label': role[1] } for role in roles]
    print("Rôles disponibles:", roles_list)
    return Response(roles_list)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_disponibilite(request):
    disponibilites = Utilisateur.DISPONIBILITE_CHOICES
    disponibilite_list = [{'value': disponibilite[0], 'label': disponibilite[1] } for disponibilite in disponibilites]
    print("Disponibilité disponible:", disponibilite_list)
    return Response(disponibilite_list)

class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # Désactive l'authentification pour cette vue

class ProduitViewSet(viewsets.ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]  # Permet l'accès public
    
    def get_permissions(self):
        """
        Permet l'accès public pour list et retrieve,
        mais requiert l'authentification pour les autres actions
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Produit.objects.all()
        categorie = self.request.query_params.get('categorie', None)
        status = self.request.query_params.get('status', None)
        
        if categorie:
            queryset = queryset.filter(categorie=categorie)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def perform_create(self, serializer):
        # Associe automatiquement le vendeur à l'utilisateur connecté
        serializer.save(vendeur=self.request.user)

    @action(detail=False, methods=['get'], url_path='mes-produits')
    def mes_produits(self, request):
        try:
            produits = Produit.objects.filter(vendeur=request.user)
            serializer = self.get_serializer(produits, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"Erreur dans mes_produits: {str(e)}")
            return Response(
                {"detail": "Erreur lors de la récupération des produits"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def modifier_status(self, request, pk=None):
        produit = self.get_object()
        if produit.vendeur != request.user:
            return Response(
                {"detail": "Non autorisé"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        nouveau_status = request.data.get('status')
        if nouveau_status in dict(Produit.STATUS_CHOICES):
            produit.status = nouveau_status
            produit.save()
            return Response({"status": nouveau_status})
        return Response(
            {"detail": "Status invalide"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class VenteViewSet(viewsets.ModelViewSet):
    serializer_class = VenteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Vente.objects.all()

    @action(detail=True, methods=['post'])
    def confirmer(self, request, pk=None):
        vente = self.get_object()
        vente.confirmer_vente()
        return Response({'status': 'vente confirmée'})

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        vente = self.get_object()
        vente.annuler_vente()
        return Response({'status': 'vente annulée'})

# Nouvelles vues pour gérer l'état de connexion
class ConnectionStateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, utilisateur_id):
        try:
            utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            utilisateur.is_connected = True
            utilisateur.save()
            return Response({'status': 'success', 'message': 'État de connexion mis à jour'})
        except Utilisateur.DoesNotExist:
            raise NotFound("Utilisateur non trouvé")

class ConnectionStatesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        utilisateurs = Utilisateur.objects.all()
        connection_states = {user.id: user.is_connected for user in utilisateurs}
        return Response(connection_states)



class OffreEmploiViewSet(viewsets.ModelViewSet):
    queryset = OffreEmploi.objects.all()
    serializer_class = OffreEmploiSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['region', 'type_emploi']
    search_fields = ['titre', 'description', 'competences_requises']

    def create(self, request, *args, **kwargs):
        print("Headers:", request.headers)  # 🔥 Voir le Content-Type
        print("Données brutes:", request.body)  # 🔥 Voir ce qui est envoyé
        try:
            data_json = json.loads(request.body)
            print("JSON détecté:", data_json)  # 🔥 Voir si Django reçoit du JSON
        except json.JSONDecodeError:
            print("⚠️ Django n'a pas pu parser du JSON ! Il reçoit autre chose.")
        
        return super().create(request, *args, **kwargs)

class CandidatureViewSet(viewsets.ModelViewSet):
    queryset = Candidature.objects.all()
    serializer_class = CandidatureSerializer

    # Dans votre CandidatureViewSet, ajoutez cette méthode
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #print("\nToutes les URLs disponibles:")
        #print_urls(get_resolver().url_patterns)

    def retrieve(self, request, *args, **kwargs):
        # recupérer une candidature spécifique par id
        try:
            #recupérer la candidtaure en utilisant l'id
            candidature = self.get_object() 
            serializer = self.get_serializer(candidature)
            return Response(serializer.data)
        except Candidature.DoesNotExist:
            return Response(
                {'detail': 'candidature non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
            print("*************************candidature non trouvé")


    @action(detail=False, methods=['get'], url_path='by-offre/(?P<offre_id>\d+)')
    def get_candidature_by_offre(self, request, offre_id=None):
        try:
            candidature = Candidature.objects.get(
                offre_id=offre_id,
                candidat=request.user
            )
            serializer = self.get_serializer(candidature)
            return Response(serializer.data)
        except Candidature.DoesNotExist:
            return Response(
                {'detail': 'Candidature non trouvée'}, 
                status=status.HTTP_404_NOT_FOUND
            )


    @action(detail=False, methods=['GET'], url_path='check_status', url_name='check_status')
    def check_status(self, request):
        """
        Vérifie si une candidature existe pour une offre donnée
        """
        print("Méthode check_status appelée")
        offre_id = request.query_params.get('offre_id')
        print(f"Vérification pour offre_id: {offre_id}")

        if not offre_id:
            return Response({'error': 'offre_id est requis'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Convertir `offre_id` en entier pour éviter les erreurs
        try:
            offre_id = int(offre_id)
        except ValueError:
            return Response({'error': 'offre_id doit être un entier valide'}, status=status.HTTP_400_BAD_REQUEST)

        try:
        # Vérification si l'offre existe
            if not OffreEmploi.objects.filter(id=offre_id).exists():  # Utilisation de OffreEmploi
                return Response({'error': 'Offre introuvable'}, status=status.HTTP_404_NOT_FOUND)

        # Vérification pour un utilisateur authentifié
            if request.user.is_authenticated:
                print(f"Vérification pour l'utilisateur authentifié: {request.user}")
                candidature_exists = Candidature.objects.filter(
                    offre_id=offre_id,
                    candidat=request.user
                ).exists()
            else:
            # Vérification par email si non authentifié
                email = request.session.get('email')
                print(f"Vérification avec l'email: {email}")
                candidature_exists = Candidature.objects.filter(
                    offre_id=offre_id,
                    email=email
                ).exists() if email else False

            print(f"Résultat de la vérification: {candidature_exists}")
            return Response({'exists': candidature_exists})

        except Exception as e:
            print(f"Erreur dans check_status: {str(e)}")
            return Response(
                {'error': 'Une erreur interne est survenue'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['DELETE'], url_path='delete')
    def delete_candidature(self, request, pk=None):
        try:
            candidature = Candidature.objects.get(id=pk, candidat=request.user)

        # ✅ Ne pas supprimer mais marquer comme supprimée
            candidature.is_deleted = True
            candidature.save()

            return Response(
                {'detail': 'Votre candidature a été supprimée. Vous pouvez repostuler.'},
                status=status.HTTP_200_OK
            )
        except Candidature.DoesNotExist:
            return Response(
                {'detail': 'Candidature non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )



    def create(self, request, *args, **kwargs):
        # Vérifier si une candidature existe déjà
        offre_id = request.data.get('offre')
        candidat_id = request.user.id

        existing_candidature = Candidature.objects.filter(
            offre_id=offre_id,
            candidat_id=candidat_id,
            is_deleted= False #vérifier uniquement les candidatures actives
        ).exists()

        if existing_candidature:
            return Response(
                {'detail': 'Vous avez déjà postulé à cette offre'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

# def create(self, request, *args, **kwargs):
#     print("✅ Requête reçue :", request.data)
    
#     offre_id = request.data.get('offre_id')
    
#     # Vérification de l'offre_id
#     if offre_id is None:
#         return Response({'error': 'offre_id est requis'}, status=400)
    
#     try:
#         # Convertir en entier si ce n'est pas déjà le cas
#         offre_id = int(offre_id)
#     except (ValueError, TypeError):
#         return Response({'error': 'offre_id doit être un nombre valide'}, status=400)
    
#     # Continuer avec le reste de la logique
#     try:
#         offre = OffreEmploi.objects.get(id=offre_id)
#     except OffreEmploi.DoesNotExist:
#         return Response({'error': 'Offre non trouvée'}, status=404)
    
#     # Ajouter l'offre aux données
#     request.data['offre'] = offre_id
    
    #return super().create(request, *args, **kwargs)


#pour la gestion des discussion
class CategorieDiscussionViewSet(viewsets.ModelViewSet):
    queryset = CategorieDiscussion.objects.all()
    serializer_class = CategorieDiscussionSerializer
    permission_classes = [IsAuthenticated]

class SujetViewSet(viewsets.ModelViewSet):
    queryset = Sujet.objects.all()
    serializer_class = SujetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)


from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.models import Produit
from .serializers import ProduitSerializer

@api_view(['GET'])
def liste_produits(request):
    """
    Récupère la liste de tous les produits disponibles.
    """
    try:
        # Récupérer tous les produits
        produits = Produit.objects.all().order_by('-date_creation')
        
        # Sérialiser les données
        serializer = ProduitSerializer(produits, many=True)
        
        return Response({
            'status': 'success',
            'message': 'Liste des produits récupérée avec succès',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return Cart.objects.filter(user=self.request.user)

    # def get_queryset(self):
    #     if not self.request.user.is_authenticated:
    #         return Cart.objects.none()  # Retourne un queryset vide si l'utilisateur n'est pas connecté
    #     return Cart.objects.filter(user=self.request.user)

    def get_queryset(self):
        # Ajoutez la logique pour Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        # Si l'utilisateur n'est pas authentifié, renvoyer un queryset vide
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        # Sinon, renvoyer les objets du panier pour l'utilisateur authentifié
        return Cart.objects.filter(user=self.request.user)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return CartItem.objects.filter(cart__user=self.request.user)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user)

    # def get_queryset(self):
    #     if not self.request.user.is_authenticated:
    #         return CartItem.objects.none()
    #     return CartItem.objects.filter(cart__user=self.request.user)


    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        produit_id = request.data.get('produit_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            produit = Produit.objects.get(id=produit_id)
            if produit.quantite < quantity:
                return Response(
                    {'detail': 'Quantité non disponible'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                produit=produit,
                defaults={'quantity': quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            serializer = self.get_serializer(cart_item)
            return Response(serializer.data)

        except Produit.DoesNotExist:
            return Response(
                {'detail': 'Produit non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


