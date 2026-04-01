from django.utils import timezone
from django.db.models import Sum
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def generer_pdf_rapport(transactions, utilisateur, date_debut, date_fin):
    """Génère un PDF de rapport"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Titre
    elements.append(Paragraph("Rapport financier", styles['Title']))
    elements.append(Paragraph(f"Période: {date_debut.strftime('%d/%m/%Y')} - {date_fin.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))
    
    # Statistiques
    total_revenus = transactions.filter(type='REVENU').aggregate(total=Sum('montant'))['total'] or 0
    total_depenses = transactions.filter(type='DEPENSE').aggregate(total=Sum('montant'))['total'] or 0
    
    data_stats = [
        ['Description', 'Montant'],
        ['Total revenus', f"{total_revenus:.2f} FCFA"],
        ['Total dépenses', f"{total_depenses:.2f} FCFA"],
        ['Solde actuel', f"{utilisateur.profil.solde_actuel:.2f} FCFA"],
    ]
    
    table_stats = Table(data_stats, colWidths=[250, 150])
    table_stats.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table_stats)
    elements.append(Spacer(1, 0.5*cm))
    
    # Liste des transactions
    if transactions.exists():
        elements.append(Paragraph("Détail des transactions", styles['Heading2']))
        elements.append(Spacer(1, 0.3*cm))
        
        data = [['Date', 'Description', 'Catégorie', 'Montant']]
        for t in transactions[:50]:
            data.append([
                t.date.strftime('%d/%m/%Y'),
                t.description[:30] if t.description else '-',
                t.categorie.nom if t.categorie else '-',
                f"{'+' if t.type == 'REVENU' else '-'}{t.montant:.2f} FCFA"
            ])
        
        table = Table(data, colWidths=[70, 150, 80, 80])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def formater_euros(montant):
    """Formate un montant en euros"""
    return f"{montant:.2f} FCFA".replace('.', ',')