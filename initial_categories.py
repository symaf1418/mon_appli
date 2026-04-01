#!/usr/bin/env python
"""
Script d'initialisation des catégories pour Mon Budget Poche
À exécuter après les migrations : python initial_categories.py
"""

import os
import sys
import django

def setup_django():
    """Configure l'environnement Django"""
    # Chemin absolu du projet
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Ajouter le répertoire au path
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    
    # Définir les settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monprojet.settings')
    
    try:
        django.setup()
        print("✅ Django initialisé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur d'initialisation Django: {e}")
        print(f"📁 Répertoire courant: {BASE_DIR}")
        print(f"📁 Contenu du répertoire:")
        for item in os.listdir(BASE_DIR):
            print(f"   - {item}")
        return False

def create_categories():
    """Crée les catégories par défaut"""
    from budget.models import Categorie
    
    categories = [
        {'nom': 'Alimentation', 'icone': '🍔', 'couleur': '#e74c3c', 'ordre': 10},
        {'nom': 'Logement', 'icone': '🏠', 'couleur': '#3498db', 'ordre': 20},
        {'nom': 'Électricité', 'icone': '⚡', 'couleur': '#f39c12', 'ordre': 30},
        {'nom': 'Eau', 'icone': '💧', 'couleur': '#3498db', 'ordre': 40},
        {'nom': 'Internet', 'icone': '🌐', 'couleur': '#9b59b6', 'ordre': 50},
        {'nom': 'Téléphone', 'icone': '📱', 'couleur': '#2ecc71', 'ordre': 60},
        {'nom': 'Transport', 'icone': '🚗', 'couleur': '#e67e22', 'ordre': 70},
        {'nom': 'Santé', 'icone': '🏥', 'couleur': '#1abc9c', 'ordre': 80},
        {'nom': 'Éducation', 'icone': '📚', 'couleur': '#34495e', 'ordre': 90},
        {'nom': 'Loisirs', 'icone': '🎮', 'couleur': '#9b59b6', 'ordre': 100},
        {'nom': 'Shopping', 'icone': '🛍️', 'couleur': '#e84342', 'ordre': 110},
        {'nom': 'Assurances', 'icone': '🛡️', 'couleur': '#7f8c8d', 'ordre': 120},
        {'nom': 'Divers', 'icone': '📦', 'couleur': '#95a5a6', 'ordre': 1000},
    ]
    
    print("\n🚀 Création des catégories...")
    print("-" * 40)
    
    created_count = 0
    for cat in categories:
        obj, created = Categorie.objects.get_or_create(
            nom=cat['nom'],
            defaults={
                'icone': cat['icone'],
                'couleur': cat['couleur'],
                'ordre': cat['ordre']
            }
        )
        if created:
            print(f"✅ {cat['icone']} {cat['nom']}")
            created_count += 1
        else:
            print(f"⏭️  {cat['icone']} {cat['nom']} (déjà existant)")
    
    print("-" * 40)
    print(f"✨ Résultat: {created_count} nouvelles catégories créées")
    print(f"📊 Total dans la base: {Categorie.objects.count()} catégories")
    
    return created_count

def main():
    """Fonction principale"""
    print("=" * 50)
    print("🔄 INITIALISATION DES CATÉGORIES")
    print("=" * 50)
    
    if setup_django():
        create_categories()
        print("\n✅ Initialisation terminée avec succès!")
    else:
        print("\n❌ Échec de l'initialisation")
        sys.exit(1)

if __name__ == "__main__":
    main()