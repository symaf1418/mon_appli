from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profil, Categorie, LogSysteme

class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    readonly_fields = ['solde_actuel', 'date_creation']

class CustomUserAdmin(UserAdmin):
    inlines = [ProfilInline]
    list_display = ['username', 'email', 'date_joined', 'last_login']
    readonly_fields = ['date_joined', 'last_login']

class CategorieAdmin(admin.ModelAdmin):
    list_display = ['ordre', 'icone', 'nom', 'couleur']  # Champs affichés
    list_display_links = ['nom']  # 🟢 Le champ 'nom' sera le lien cliquable
    list_editable = ['ordre']  # 🟢 'ordre' sera éditable directement
    ordering = ['ordre']
    
    # Optionnel : rendre l'icône et la couleur aussi éditables
    # list_editable = ['ordre', 'icone', 'couleur']

class LogSystemeAdmin(admin.ModelAdmin):
    list_display = ['date', 'type_evenement', 'utilisateur', 'message_truncated']
    list_filter = ['type_evenement']
    readonly_fields = ['type_evenement', 'message', 'date', 'utilisateur']
    
    def message_truncated(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_truncated.short_description = 'Message'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# Désenregistrer l'admin User par défaut
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Enregistrer nos modèles
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(LogSysteme, LogSystemeAdmin)