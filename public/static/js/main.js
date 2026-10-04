// Logistics Management System - Main JS

document.addEventListener('DOMContentLoaded', function () {

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Stagger cards and count dashboard metrics into view.
    const animatedCards = document.querySelectorAll('.stat-card, .page-content > .row > [class*="col-"] > .card');
    animatedCards.forEach(function (card, index) {
        card.style.setProperty('--stagger-index', Math.min(index, 8));
    });

    if (!reduceMotion) {
        document.querySelectorAll('.stat-number').forEach(function (element) {
            const text = element.textContent.trim();
            if (!/^\d+(\.\d+)?$/.test(text)) return;

            const target = Number(text);
            const decimals = (text.split('.')[1] || '').length;
            const start = performance.now();
            const duration = 850;

            function countUp(now) {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                element.textContent = (target * eased).toFixed(decimals);
                if (progress < 1) requestAnimationFrame(countUp);
            }

            element.textContent = (0).toFixed(decimals);
            requestAnimationFrame(countUp);
        });
    }

    // Let the hero's muted gold glow follow the pointer without affecting layout.
    document.querySelectorAll('.dashboard-hero').forEach(function (hero) {
        hero.addEventListener('pointermove', function (event) {
            const bounds = hero.getBoundingClientRect();
            const x = ((event.clientX - bounds.left) / bounds.width) * 100;
            const y = ((event.clientY - bounds.top) / bounds.height) * 100;
            hero.style.setProperty('--pointer-x', x + '%');
            hero.style.setProperty('--pointer-y', y + '%');
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Highlight active sidebar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Confirm before form submissions with data-confirm attribute
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    console.log('LMS - Logistics Management System loaded.');
});
