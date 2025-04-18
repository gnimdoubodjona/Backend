# Generated by Django 5.1.4 on 2025-04-05 03:34

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_categorie', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('unitee', models.CharField(blank=True, max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='CategorieDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('prenoms', models.CharField(max_length=150)),
                ('nom', models.CharField(max_length=150)),
                ('emplacement', models.CharField(blank=True, max_length=100, null=True)),
                ('role', models.CharField(choices=[('agriculteur', 'Agriculteur'), ('eleveur', 'Éleveur'), ('veterinaire', 'Vétérinaire'), ('prestataire', 'Prestataire'), ('autre', 'Autre')], default='autre', max_length=20)),
                ('disponibilite', models.CharField(choices=[('Disponible', 'Disponible'), ('Indisponible', 'Indisponible')], default='Disponible', max_length=20)),
                ('bio', models.CharField(blank=True, max_length=400, null=True)),
                ('is_connected', models.BooleanField(default=False)),
                ('type_cultures', models.JSONField(blank=True, null=True)),
                ('surface_exploitee', models.FloatField(blank=True, null=True)),
                ('certification_bio', models.BooleanField(default=False)),
                ('type_animaux', models.JSONField(blank=True, null=True)),
                ('nombre_animaux', models.PositiveIntegerField(blank=True, null=True)),
                ('infrastructure_disponible', models.TextField(blank=True, null=True)),
                ('specialites', models.JSONField(blank=True, null=True)),
                ('zone_intervention', models.CharField(blank=True, max_length=200, null=True)),
                ('tarif_horaire', models.FloatField(blank=True, null=True)),
                ('diplome_veterinaire', models.FileField(blank=True, null=True, upload_to='certifications/')),
                ('annees_experience', models.PositiveIntegerField(blank=True, null=True)),
                ('zones_de_consultation', models.CharField(blank=True, max_length=200, null=True)),
                ('photo_de_profile', models.ImageField(blank=True, null=True, upload_to='profile_photos/')),
                ('numero_telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('groups', models.ManyToManyField(related_name='utilisateurs', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text="Les permissions spécifiques à l'utilisateur.", related_name='utilisateur_set', to='auth.permission', verbose_name='utilisateur permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OffreEmploi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('type_emploi', models.CharField(max_length=20)),
                ('region', models.CharField(max_length=100)),
                ('competences_requises', models.TextField()),
                ('salaire', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date_publication', models.DateTimeField(auto_now_add=True)),
                ('date_expiration', models.DateField()),
                ('est_active', models.BooleanField(default=True)),
                ('employeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Candidature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(default='utilisateur0', max_length=100)),
                ('prenoms', models.CharField(default='utilisateur0', max_length=150)),
                ('email', models.EmailField(default='utilisateur0@gmail.com', max_length=254, unique=True)),
                ('adresse', models.TextField(default='Kégué')),
                ('numero_telephone', models.CharField(default='+228 90001212', max_length=20)),
                ('cv', models.FileField(blank=True, null=True, upload_to='cvs/')),
                ('lettre_motivation', models.TextField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('candidat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('offre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.offreemploi')),
            ],
            options={
                'unique_together': {('offre', 'candidat')},
            },
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_produit', models.CharField(max_length=100)),
                ('prix', models.FloatField()),
                ('quantite', models.PositiveIntegerField()),
                ('description', models.TextField(blank=True)),
                ('date_creation', models.DateField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('disponible', 'Disponible'), ('vendu', 'Vendu'), ('reserve', 'Réservé')], default='disponible', max_length=20)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='produits/')),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produits', to='core.categorie')),
                ('vendeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produits_en_vente', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Agriculteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupe', models.ManyToManyField(related_name='agriculteurs', to='auth.group')),
                ('permissions', models.ManyToManyField(related_name='agriculteur_permissions', to='auth.permission')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agriculteur', to=settings.AUTH_USER_MODEL)),
                ('produits', models.ManyToManyField(related_name='agriculteurs', to='core.produit')),
            ],
        ),
        migrations.CreateModel(
            name='Reponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reponse', models.BooleanField()),
                ('motifs', models.CharField(max_length=100)),
                ('candidature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reponses', to='core.candidature')),
            ],
        ),
        migrations.CreateModel(
            name='Sujet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('categorie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sujets', to='core.categoriediscussion')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu', models.TextField()),
                ('date_publication', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('sujet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='core.sujet')),
            ],
        ),
        migrations.CreateModel(
            name='Vente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('quantite', models.PositiveIntegerField()),
                ('prix_unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_vente', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('en_attente', 'En attente'), ('confirmee', 'Confirmée'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('prix_total', models.FloatField()),
                ('acheteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achats', to=settings.AUTH_USER_MODEL)),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.produit')),
                ('vendeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='core.cart')),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.produit')),
            ],
            options={
                'unique_together': {('cart', 'produit')},
            },
        ),
    ]
