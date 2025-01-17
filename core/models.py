from django.db import models
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
    

    username = None  # Désactiver le champ username
    email = models.EmailField(unique=True)
    prenoms = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)
    emplacement = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='autre')
    bio = models.CharField(max_length=400, null=True, blank=True)


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
    #disponibilite = models.BooleanField(default=True)
    disponibilite = models.CharField(max_length=20, null=True, blank=True)

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
        
