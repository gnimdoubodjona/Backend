from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Utilisateur(AbstractUser):

    ROLE_CHOICES = [
        ('agriculteur', 'Agriculteur'),
        ('eleveur', 'Éleveur'),
        ('veterinaire', 'Vétérinaire'),
        ('prestataire', 'Prestataire'),
        ('autre', 'Autre'),
    ]
    
    DISPONIBILITE_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Indisponible', 'Indisponible'),
    ]

    username = None  # Désactiver le champ username
    email = models.EmailField(unique=True)
    prenoms = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)
    emplacement = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='autre')
    disponibilite = models.CharField(max_length=20, choices=DISPONIBILITE_CHOICES, default='Disponible')
    bio = models.CharField(max_length=400, null=True, blank=True)
    is_connected = models.BooleanField(default=False)  # Nouveau champ pour suivre l'état de connexion

    #champs pour les agriculteurs
    type_cultures = models.JSONField(null=True, blank= True)
    surface_exploitee = models.FloatField(null = True, blank= True)
    certification_bio = models.BooleanField(default = False) 

    #champs pour eleveur
    type_animaux = models.JSONField(null=True, blank=True)  
    nombre_animaux = models.PositiveIntegerField(null=True, blank=True)  
    infrastructure_disponible = models.TextField(null=True, blank=True)

    #champs pour prestataire : 
    specialites = models.JSONField(null=True, blank=True)  # Liste de spécialités
    zone_intervention = models.CharField(max_length=200, null=True, blank=True)  # Zones d'intervention
    tarif_horaire = models.FloatField(null=True, blank=True) 

    # Champs spécifiques pour Vétérinaire
    diplome_veterinaire = models.FileField(upload_to='certifications/', null=True, blank=True) # Diplôme ou certification
    annees_experience = models.PositiveIntegerField(null=True, blank=True)  # Nombre d'années d'expérience
    zones_de_consultation = models.CharField(max_length=200, null=True, blank=True) 

    photo_de_profile = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    numero_telephone = models.CharField(max_length=20, null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name='utilisateurs')

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='utilisateur_set',
        blank=True,
        help_text='Les permissions spécifiques à l\'utilisateur.',
        verbose_name='utilisateur permissions',
    )

    USERNAME_FIELD = 'email'  # Utiliser l'email comme champ d'identification
    REQUIRED_FIELDS = ['nom', 'prenoms', 'emplacement', 'role' ]  # Champs requis lors de la création

    objects = UtilisateurManager()

    def __str__(self):
        return self.email


class Categorie(models.Model):
    nom_categorie= models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unitee = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f'{self.nom_categorie}'


class Produit(models.Model):
    STATUS_CHOICES = [
        ('disponible', 'Disponible'),
        ('vendu', 'Vendu'),
        ('reserve', 'Réservé'),
    ]

    nom_produit = models.CharField(max_length=100)
    prix = models.FloatField()
    quantite = models.PositiveIntegerField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    description = models.TextField(blank=True)
    vendeur = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='produits_en_vente')
    date_creation = models.DateField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponible')
    photo = models.ImageField(upload_to='produits/', blank=True, null=True)

    def __str__(self):
        return f'{self.nom_produit} '
    
    def ajuster_stock(self, quantite, operation ='ajouter'):
        if operation=='ajouter':
            self.quantite +=quantite
        elif operation == 'reduire':
            if self.quantite >= quantite:
                self.quantite -=quantite
            else:
                print("Stock insuffisant")
        self.save()
        return self.quantite



class Cart(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())

    def __str__(self):
        return f"Panier de {self.user.email}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return self.produit.prix * self.quantity

    class Meta:
        unique_together = ('cart', 'produit')

    def __str__(self):
        return f"{self.quantity} x {self.produit.nom_produit}"


class Agriculteur(models.Model):
    produits = models.ManyToManyField(Produit, related_name='agriculteurs')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='agriculteur')
    
    groupe = models.ManyToManyField(Group, related_name='agriculteurs')
    permissions = models.ManyToManyField(Permission, related_name='agriculteur_permissions')


class Vente(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée')
    ]
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    acheteur = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='achats')
    vendeur = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='ventes')
    date = models.DateField()
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    date_vente = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='en_attente')
    prix_total = models.FloatField()

    def save(self, *args, **kwargs):
        if not self.prix_total:
            self.prix_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
    
    def confirmer_vente(self):
        if self.status == 'en_attente':
            self.status = 'confirmee'
            self.produit.ajuster_stock(self.quantite, 'reduire')
            self.save()

    def annuler_vente(self):
        if self.status == 'en_attente':
            self.status = 'annulee'
            self.save()

    def __str__(self):
        return f'{self.produit.nom_produit} - {self.date} - {self.quantite} - {self.prix_total}'




class OffreEmploi(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_emploi = models.CharField(max_length=20)
    region = models.CharField(max_length=100)
    competences_requises = models.TextField()
    salaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField()
    employeur = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    est_active = models.BooleanField(default=True)

class Candidature(models.Model):
    offre = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE)
    candidat = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100, default='utilisateur0')
    prenoms = models.CharField(max_length=150, default='utilisateur0')
    email = models.EmailField(unique=True, default='utilisateur0@gmail.com')
    adresse = models.TextField(default='Kégué')
    numero_telephone = models.CharField(max_length=20, default='+228 90001212')  # Ajouter un validateur pour le format
    # date_candidature = models.DateTimeField(auto_now_add=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    lettre_motivation = models.TextField()
    #statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    # notes = models.TextField(blank=True)
    is_deleted = models.BooleanField(default= False)


    def __str__(self):
        return f"Candidature de {self.nom} {self.prenoms} pour {self.offre}"

    class Meta:
        # Ajouter cette contrainte unique
        unique_together = ('offre', 'candidat')

#pour la gestion du forum
class CategorieDiscussion(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.nom

class Sujet(models.Model):
    titre = models.CharField(max_length=200)
    categorie = models.ForeignKey(CategorieDiscussion, related_name='sujets', on_delete=models.CASCADE)
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class Message(models.Model):
    contenu = models.TextField()
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    sujet = models.ForeignKey(Sujet, related_name='messages', on_delete=models.CASCADE)
    date_publication = models.DateTimeField(auto_now_add=True)
