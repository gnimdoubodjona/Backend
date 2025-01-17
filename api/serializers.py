from rest_framework import serializers
from core.models import Utilisateur
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()

class UtilisateurSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Utilisateur
        fields = ('id', 'nom', 'prenoms', 'email', 'emplacement', 'token')
        extra_kwargs = {
            'password': {'write_only': True},
            'photo_de_profile': {'required': False},
            'numero_telephone': {'required': False},
            'disponibilite': {'required': False},
        }

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Email ou mot de passe incorrect.")
            if not user.is_active:
                raise serializers.ValidationError("Ce compte est désactivé.")
        else:
            raise serializers.ValidationError("Veuillez fournir un email et un mot de passe.")

        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateur
        fields = (
            'nom', 'prenoms', 'email', 'password', 
            'password2', 'emplacement', 'role', 'bio',
            'photo_de_profile', 'numero_telephone', 'disponibilite',
            # Champs pour agriculteur
            'type_cultures', 'surface_exploitee', 'certification_bio',
            # Champs pour éleveur
            'type_animaux', 'nombre_animaux', 'infrastructure_disponible',
            # Champs pour prestataire
            'specialites', 'zone_intervention', 'tarif_horaire',
            # Champs pour vétérinaire
            'diplome_veterinaire', 'annees_experience', 'zones_de_consultation'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'photo_de_profile': {'required': False},
            'numero_telephone': {'required': False},
            'disponibilite': {'required': False},
            'bio': {'required': False},

        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        # Supprimer password2 du dictionnaire
        validated_data.pop('password2')
        # Extraire le mot de passe
        password = validated_data.pop('password')
        # Créer l'utilisateur avec les données validées
        user = Utilisateur.objects.create_user(
            password=password,
            **validated_data  # Ceci inclut déjà l'email et les autres champs
        )
        return user
