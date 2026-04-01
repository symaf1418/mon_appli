document.addEventListener('DOMContentLoaded', function() {
    // Animation du solde
    const soldeElement = document.getElementById('soldeActuel');
    if (soldeElement) {
        const solde = parseFloat(soldeElement.textContent.replace('€', '').replace(',', '.').trim());
        animateValue(soldeElement, 0, solde, 2000);
    }
    
    // Animation des statistiques
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach(stat => {
        const value = parseFloat(stat.textContent.replace('%', '').replace(',', '.'));
        if (!isNaN(value)) {
            animateValue(stat, 0, value, 2000, stat.textContent.includes('%') ? '%' : '');
        }
    });
});

function animateValue(element, start, end, duration, suffix = '') {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value.toFixed(1).replace('.', ',') + suffix;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            element.textContent = end.toFixed(1).replace('.', ',') + suffix;
        }
    };
    window.requestAnimationFrame(step);
}