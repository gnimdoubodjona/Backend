from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, filters, status
from rest_framework.parsers import MultiPartParser, FormParser
from api.serializers import UtilisateurSerializer, LoginSerializer, RegisterSerializer
from core.models import Utilisateur
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from . import serializers
from rest_framework.exceptions import ValidationError



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
        try:
            print("Données reçues:", request.data)  # Debug log
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                refresh = RefreshToken.for_user(user)
                
                print("Connexion réussie pour:", user.email)  # Debug log
                
                return Response({
                    'user': {
                        'nom': user.nom,
                        'prenoms': user.prenoms,
                        'email': user.email,
                        'id': user.id,
                        'role': user.role
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_200_OK)
            else:
                print("Erreurs de validation:", serializer.errors)  # Debug log
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except ValidationError as e:
            print("Erreur de validation:", str(e))  # Debug log
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print("Erreur inattendue:", str(e))  # Debug log
            return Response(
                {'error': 'Une erreur inattendue est survenue'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# class LoginView(generics.GenericAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = LoginSerializer

#     def post(self, request):
#         print("=== Données reçues par le backend ===")
#         print(request.data)  # Vérifie les données envoyées depuis le frontend
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             print("=== Données validées ===")
#             print(serializer.validated_data)
#         else:
#             print("=== Erreurs de validation ===")
#             print(serializer.errors)
#         return Response(serializer.validated_data)  
    

    # def post(self, request):
    #     print("=== Données reçues par le backend ===")
    #     print(request.data)  # Affiche les données envoyées par le frontend
        
    #     # serializer = self.get_serializer(data=request.data)
    #     # try:
    #     #     serializer.is_valid(raise_exception=True)
    #     # except serializers.ValidationError as e:
    #     #     print("=== Erreurs de validation ===")
    #     #     print(e.detail)
    #     #     return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    #     # user = serializer.validated_data['user']
    #     # refresh = RefreshToken.for_user(user)
    #     # return Response({
    #     #     'user': UtilisateurSerializer(user).data,
    #     #     'token': str(refresh.access_token)
    #     # })

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data['user']
    #     refresh = RefreshToken.for_user(user)
    #     return Response({
    #     'user': UtilisateurSerializer(user).data,
    #     'token': str(refresh.access_token)
    # })


    # # def post(self, request):


    # #     serializer = self.get_serializer(data=request.data)
    # #     serializer.is_valid(raise_exception=True)
    # #     user = serializer.validated_data['user']
    # #     refresh = RefreshToken.for_user(user)
    # #     return Response({
    # #         'user': UtilisateurSerializer(user).data,
    # #         'token': str(refresh.access_token)
    # #     })



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