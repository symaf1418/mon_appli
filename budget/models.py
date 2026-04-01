from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profil(models.Model):
    """Profil utilisateur - créé automatiquement à l'inscription"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    solde_actuel = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seuil_mensuel = models.DecimalField(max_digits=10, decimal_places=2, default=1200)
    seuil_annuel = models.DecimalField(max_digits=10, decimal_places=2, default=14400)
    date_creation = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def total_depenses_mois(self):
        maintenant = timezone.now()
        transactions = Transaction.objects.filter(
            utilisateur=self.user,
            type='DEPENSE',
            date__month=maintenant.month,
            date__year=maintenant.year
        )
        return sum(t.montant for t in transactions)
    
    def total_depenses_annee(self):
        maintenant = timezone.now()
        transactions = Transaction.objects.filter(
            utilisateur=self.user,
            type='DEPENSE',
            date__year=maintenant.year
        )
        return sum(t.montant for t in transactions)

class Categorie(models.Model):
    """Catégories de transactions - prédéfinies pour tous"""
    nom = models.CharField(max_length=50, unique=True)
    icone = models.CharField(max_length=10, default='📦')
    couleur = models.CharField(max_length=20, default='#3498db')
    ordre = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return f"{self.icone} {self.nom}"

class Transaction(models.Model):
    """Revenus et dépenses"""
    TYPE_CHOICES = [
        ('REVENU', 'Revenu'),
        ('DEPENSE', 'Dépense'),
    ]
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    solde_avant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    solde_apres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        signe = '+' if self.type == 'REVENU' else '-'
        libelle = self.categorie.nom if self.categorie else "Sans catégorie"
        return f"{self.date.strftime('%d/%m/%Y')} : {signe}{self.montant}€ - {libelle}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            profil = self.utilisateur.profil
            self.solde_avant = profil.solde_actuel
            
            if self.type == 'REVENU':
                profil.solde_actuel += self.montant
            else:
                profil.solde_actuel -= self.montant
            
            self.solde_apres = profil.solde_actuel
            profil.save()
        
        super().save(*args, **kwargs)

class LogSysteme(models.Model):
    """Journal des événements - pour l'admin"""
    TYPE_CHOICES = [
        ('CONNEXION', 'Connexion'),
        ('INSCRIPTION', 'Inscription'),
        ('ACTION', 'Action'),
    ]
    
    type_evenement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date']
# Create your models here.
