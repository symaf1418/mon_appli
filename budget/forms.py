from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, Categorie, Profil

class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class RevenuForm(forms.ModelForm):
    """Formulaire pour revenus"""
    class Meta:
        model = Transaction
        fields = ['montant', 'description', 'date']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salaire, Freelance...'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être positif")
        return montant

class DepenseForm(forms.ModelForm):
    """Formulaire pour dépenses - catégories prédéfinies"""
    class Meta:
        model = Transaction
        fields = ['montant', 'categorie', 'date']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].queryset = Categorie.objects.all()
        self.fields['categorie'].empty_label = "--- Choisir une catégorie ---"
        self.fields['categorie'].required = True
    
    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être positif")
        return montant

class SeuilForm(forms.ModelForm):
    """Formulaire pour modifier les seuils"""
    class Meta:
        model = Profil
        fields = ['seuil_mensuel', 'seuil_annuel']
        widgets = {
            'seuil_mensuel': forms.NumberInput(attrs={'class': 'form-control', 'step': '10'}),
            'seuil_annuel': forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
        }