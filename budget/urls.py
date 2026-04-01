from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentification
    path('', auth_views.LoginView.as_view(template_name='budget/login.html'), name='login'),
    path('logout/', views.deconnexion, name='logout'),
    path('inscription/', views.inscription, name='inscription'),
    
    # Pages principales
    path('dashboard/', views.dashboard, name='dashboard'),
    path('revenu/ajouter/', views.ajouter_revenu, name='ajouter_revenu'),
    path('depense/ajouter/', views.ajouter_depense, name='ajouter_depense'),
    path('journal/', views.journal, name='journal'),
    path('parametres/', views.parametres, name='parametres'),
    path('rapport/', views.rapport, name='rapport'),
    
    # Actions
    path('transaction/<int:transaction_id>/supprimer/', views.supprimer_transaction, name='supprimer_transaction'),
]