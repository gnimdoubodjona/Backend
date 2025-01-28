from django.contrib import admin
from core.models import Categorie, Produit, Vente, Utilisateur, Agriculteur

# Register your models here.
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom_categorie', 'description')
    search_fields = ('nom_categorie',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'prix', 'quantite', 'categorie', 'vendeur', 'status')
    list_filter = ('categorie', 'status')
    search_fields = ('nom_produit', 'vendeur__nom')

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('produit', 'acheteur', 'vendeur', 'quantite', 'prix_total', 'status')
    list_filter = ('status',)
    search_fields = ('produit__nom_produit', 'acheteur__nom', 'vendeur__nom')

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'prenoms', 'role', 'disponibilite')
    list_filter = ('role', 'disponibilite')
    search_fields = ('email', 'nom', 'prenoms')

@admin.register(Agriculteur)
class AgriculteurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur',)
    search_fields = ('utilisateur__nom', 'utilisateur__email')
