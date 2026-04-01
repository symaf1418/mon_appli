from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from datetime import datetime

from .models import Transaction, Categorie, LogSysteme, Profil
from .forms import InscriptionForm, RevenuForm, DepenseForm, SeuilForm
from .utils import generer_pdf_rapport

# ================ AUTHENTIFICATION ================

def inscription(request):
    """Inscription - Crée automatiquement le profil"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profil.objects.create(user=user)
            
            LogSysteme.objects.create(
                type_evenement='INSCRIPTION',
                message=f"Nouvel utilisateur: {user.username}",
                utilisateur=user
            )
            
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    
    return render(request, 'budget/inscription.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('login')

# ================ PAGES PRINCIPALES ================

@login_required
def dashboard(request):
    """Tableau de bord"""
    profil = request.user.profil
    maintenant = timezone.now()
    
    dernieres = Transaction.objects.filter(utilisateur=request.user)[:10]
    
    transactions_mois = Transaction.objects.filter(
        utilisateur=request.user,
        date__month=maintenant.month,
        date__year=maintenant.year
    )
    
    revenus_mois = transactions_mois.filter(type='REVENU').aggregate(
        total=Sum('montant'))['total'] or 0
    depenses_mois = transactions_mois.filter(type='DEPENSE').aggregate(
        total=Sum('montant'))['total'] or 0
    
    alertes = []
    if profil.seuil_mensuel > 0 and depenses_mois > 0:
        pct = (depenses_mois / profil.seuil_mensuel) * 100
        if pct >= 100:
            alertes.append(('danger', "⚠️ Budget mensuel DÉPASSÉ !"))
        elif pct >= 80:
            alertes.append(('warning', f"⚠️ {pct:.0f}% du budget mensuel utilisé"))
    
    context = {
        'profil': profil,
        'dernieres_transactions': dernieres,
        'revenus_mois': f"{revenus_mois:.2f} FCFA".replace('.', ','),
        'depenses_mois': f"{depenses_mois:.2f} FCFA".replace('.', ','),
        'alertes': alertes,
        'seuil_mensuel_pct': min(round((depenses_mois / profil.seuil_mensuel * 100), 1) if profil.seuil_mensuel > 0 else 0, 100),
    }
    
    return render(request, 'budget/dashboard.html', context)

@login_required
def ajouter_revenu(request):
    """Ajouter un revenu"""
    if request.method == 'POST':
        form = RevenuForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.type = 'REVENU'
            transaction.utilisateur = request.user
            transaction.save()
            
            messages.success(request, f"Revenu de {transaction.montant}FCFA ajouté !")
            return redirect('dashboard')
    else:
        form = RevenuForm()
        form.initial['date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
    
    return render(request, 'budget/ajouter_revenu.html', {
        'form': form,
        'solde_actuel': request.user.profil.solde_actuel
    })

@login_required
def ajouter_depense(request):
    """Ajouter une dépense - catégories prédéfinies"""
    if request.method == 'POST':
        form = DepenseForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.type = 'DEPENSE'
            transaction.utilisateur = request.user
            transaction.save()
            
            messages.success(request, f"Dépense de {transaction.montant}FCFA enregistrée !")
            
            # Vérifier les seuils
            profil = request.user.profil
            depenses_mois = profil.total_depenses_mois()
            if profil.seuil_mensuel > 0 and depenses_mois > profil.seuil_mensuel:
                messages.warning(request, "⚠️ Attention : Budget mensuel dépassé !")
            
            return redirect('dashboard')
    else:
        form = DepenseForm()
        form.initial['date'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
    
    return render(request, 'budget/ajouter_depense.html', {
        'form': form,
        'solde_actuel': request.user.profil.solde_actuel
    })

@login_required
def journal(request):
    """Journal des transactions"""
    transactions = Transaction.objects.filter(utilisateur=request.user)
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page', 1)
    
    return render(request, 'budget/journal.html', {
        'transactions': paginator.get_page(page)
    })

@login_required
def parametres(request):
    """Paramètres utilisateur"""
    profil = request.user.profil
    
    if request.method == 'POST':
        form = SeuilForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Seuils mis à jour !")
            return redirect('parametres')
    else:
        form = SeuilForm(instance=profil)
    
    return render(request, 'budget/parametres.html', {
        'profil': profil,
        'form_seuils': form,
    })

@login_required
def rapport(request):
    """Génération de rapport PDF"""
    if request.method == 'POST':
        periode = request.POST.get('periode')
        date_fin = timezone.now().date()
        
        if periode == 'mois':
            date_debut = date_fin.replace(day=1)
        elif periode == 'trimestre':
            mois = ((date_fin.month - 1) // 3) * 3 + 1
            date_debut = date_fin.replace(month=mois, day=1)
        elif periode == 'annee':
            date_debut = date_fin.replace(month=1, day=1)
        elif periode == 'personnalise':
            try:
                date_debut = datetime.strptime(request.POST.get('date_debut'), '%Y-%m-%d').date()
                date_fin = datetime.strptime(request.POST.get('date_fin'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                messages.error(request, "Dates invalides")
                return redirect('rapport')
        else:
            messages.error(request, "Période invalide")
            return redirect('rapport')
        
        transactions = Transaction.objects.filter(
            utilisateur=request.user,
            date__date__gte=date_debut,
            date__date__lte=date_fin
        ).order_by('date')
        
        try:
            pdf = generer_pdf_rapport(transactions, request.user, date_debut, date_fin)
            
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="rapport_{date_debut.strftime("%Y%m%d")}_{date_fin.strftime("%Y%m%d")}.pdf"'
            return response
            
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
            return redirect('rapport')
    
    total_transactions = Transaction.objects.filter(utilisateur=request.user).count()
    
    return render(request, 'budget/rapport_form.html', {
        'now': timezone.now(),
        'total_transactions': total_transactions,
    })

@login_required
@require_POST
def supprimer_transaction(request, transaction_id):
    """Supprimer une transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id, utilisateur=request.user)
    
    profil = request.user.profil
    if transaction.type == 'REVENU':
        profil.solde_actuel -= transaction.montant
    else:
        profil.solde_actuel += transaction.montant
    profil.save()
    
    transaction.delete()
    messages.success(request, "Transaction supprimée")
    
    return redirect('journal')

# Create your views here.
