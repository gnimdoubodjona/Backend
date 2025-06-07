from rest_framework import serializers
from core.models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile  # Correction de l'import
import base64
import uuid
from django.core.files import File


User = get_user_model()

class UtilisateurSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Utilisateur
        fields = (
            # Champs de base
            'id', 'nom', 'prenoms', 'email', 'emplacement', 'token',
            'role', 'disponibilite', 'bio', 'photo_de_profile', 'numero_telephone',
            
            # Champs spécifiques aux agriculteurs
            'type_cultures', 'surface_exploitee', 'certification_bio',
            
            # Champs spécifiques aux éleveurs
            'type_animaux', 'nombre_animaux', 'infrastructure_disponible',
            
            # Champs spécifiques aux prestataires
            'specialites', 'zone_intervention', 'tarif_horaire',
            
            # Champs spécifiques aux vétérinaires
            'diplome_veterinaire', 'annees_experience', 'zones_de_consultation'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            # Champs de base optionnels
            'bio': {'required': False},
            'role': {'required': False},
            'disponibilite': {'required': False},
            'photo_de_profile': {'required': False},
            'numero_telephone': {'required': False},
            
            # Champs optionnels pour les agriculteurs
            'type_cultures': {'required': False},
            'surface_exploitee': {'required': False},
            'certification_bio': {'required': False},
            
            # Champs optionnels pour les éleveurs
            'type_animaux': {'required': False},
            'nombre_animaux': {'required': False},
            'infrastructure_disponible': {'required': False},
            
            # Champs optionnels pour les prestataires
            'specialites': {'required': False},
            'zone_intervention': {'required': False},
            'tarif_horaire': {'required': False},
            
            # Champs optionnels pour les vétérinaires
            'diplome_veterinaire': {'required': False},
            'annees_experience': {'required': False},
            'zones_de_consultation': {'required': False}
        }

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)
        
    def to_representation(self, instance):
        """Personnaliser la représentation en fonction du rôle"""
        data = super().to_representation(instance)
        
        # Définir les champs spécifiques pour chaque rôle
        role_specific_fields = {
            'agriculteur': ['type_cultures', 'surface_exploitee', 'certification_bio'],
            'eleveur': ['type_animaux', 'nombre_animaux', 'infrastructure_disponible'],
            'prestataire': ['specialites', 'zone_intervention', 'tarif_horaire'],
            'veterinaire': ['diplome_veterinaire', 'annees_experience', 'zones_de_consultation']
        }
        
        # Champs communs à conserver pour tous les rôles
        common_fields = [
            'id', 'nom', 'prenoms', 'email', 'emplacement', 'token',
            'role', 'disponibilite', 'bio', 'photo_de_profile', 'numero_telephone'
        ]
        
        # Obtenir les champs spécifiques pour le rôle de l'utilisateur
        role_fields = role_specific_fields.get(instance.role, [])
        fields_to_keep = common_fields + role_fields
        
        # Retirer tous les champs qui ne sont pas dans fields_to_keep
        all_specific_fields = []
        for fields in role_specific_fields.values():
            all_specific_fields.extend(fields)
            
        # Supprimer les champs non pertinents pour ce rôle
        for field in all_specific_fields:
            if field not in role_fields and field in data:
                data.pop(field, None)
        
        return data

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

class CategorieSerializer(serializers.ModelSerializer):
    nombre_produits = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom_categorie', 'description', 'nombre_produits', 'unitee']
        
    def get_nombre_produits(self, obj):
        return obj.produits.count()

class ProduitSerializer(serializers.ModelSerializer):
    #pour les champs de foreign key
    vendeur_nom = serializers.CharField(source='vendeur.nom',read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom_categorie', read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'nom_produit', 'description', 'prix', 'quantite',
            'categorie', 'categorie_nom', 'vendeur', 'vendeur_nom',
            'date_creation', 'date_modification', 'status', 'photo'
        ]
        read_only_fields = ['vendeur', 'date_creation', 'date_modification']

    def create(self, validated_data):
        validated_data['vendeur'] = self.context['request'].user 
        return super().create(validated_data)

class AgriculteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agriculteur
        fields = '__all__'

class VenteSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom_produit', read_only=True)
    vendeur_nom = serializers.CharField(source='vendeur.nom', read_only=True)
    acheteur_nom = serializers.CharField(source='acheteur.nom', read_only=True)

    class Meta:
        model = Vente
        fields = [
            'id', 'produit', 'produit_nom', 'acheteur', 'acheteur_nom',
            'vendeur', 'vendeur_nom', 'quantite', 'prix_unitaire',
            'prix_total', 'date_vente', 'status'
        ]
        read_only_fields = ['vendeur', 'prix_total', 'date_vente']

    def validate(self, data):
        if data['quantite'] > data['produit'].quantite:
            raise serializers.ValidationError("Quantité demandée non disponible en stock")
        if data['produit'].status != 'disponible':
            raise serializers.ValidationError("Ce produit n'est plus disponible à la vente")
        return data

    def create(self, validated_data):
        validated_data['vendeur'] = validated_data['produit'].vendeur
        validated_data['prix_unitaire'] = validated_data['produit'].prix
        return super().create(validated_data)



class OffreEmploiSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = OffreEmploi
        fields = '__all__'



class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"

class CandidatureSerializer(serializers.ModelSerializer):
    #j'ajoute le champs là ici pour aller facilement recupérer les offres des candidatures dans le serializer de reponse tu vois un peu, sa recupère mes champs de la table offre
    #offre_id = serializers.PrimaryKeyRelatedField(queryset=OffreEmploi.objects.all())  # Accepte uniquement l'ID
    
    offre_id = serializers.PrimaryKeyRelatedField(queryset=OffreEmploi.objects.all(), source='offre')  # 🔁 mappe 'offre_id' à l'attribut 'offre'
    offre = OffreEmploiSerializer(read_only=True)

    class Meta:
        model = Candidature
        fields = [
            'id', 'offre_id', 'offre', 'candidat', 'adresse', 
             'cv', 'nom', 'prenoms', 'email', 'numero_telephone', 'lettre_motivation',
        ]


    cv = serializers.CharField(required=True)  # Pour accepter la chaîne base64

    def create(self, validated_data):
        cv_base64 = validated_data.get('cv')
        try:
            # Assurez-vous que c'est une chaîne base64 valide
            if cv_base64:
                # Décodage du base64
                file_data = base64.b64decode(cv_base64)
                # Création d'un nom de fichier unique
                file_name = f"cv_{uuid.uuid4()}.pdf"
                # Création du fichier
                validated_data['cv'] = ContentFile(file_data, name=file_name)
            
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({
                'cv': f'Erreur lors du traitement du fichier: {str(e)}'
            })



class ReponseSerializer(serializers.ModelSerializer):
    #pour que le serializer puisse accepter l'ID de la candidature
    candidature_id = serializers.PrimaryKeyRelatedField(queryset=Candidature.objects.all())  # Accepte uniquement l'ID
    #offre_id = serializers.PrimaryKeyRelatedField(queryset=OffreEmploi.objects.all(), source='offre')  # 🔁 mappe 'offre_id' à l'attribut 'offre'
    candidature_id_details = CandidatureSerializer(source='candidature_id', read_only=True) 
    #candidature_id = CandidatureSerializer(read_only=True)
    auteur = serializers.StringRelatedField()
    

    class Meta:
        model = Reponse
        fields = '__all__'

#pour forum
class CategorieDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieDiscussion
        fields = '__all__'

class SujetSerializer(serializers.ModelSerializer):
    auteur = serializers.ReadOnlyField(source='auteur.username')

    class Meta:
        model = Sujet
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    auteur = serializers.ReadOnlyField(source='auteur.username')

    class Meta:
        model = Message
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    produit_id = serializers.IntegerField(write_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'produit', 'produit_id', 'quantity', 'total', 'added_at']
        read_only_fields = ['cart', 'added_at']

    def get_total(self, obj):
        return obj.get_total()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_total(self, obj):
        return obj.get_total()