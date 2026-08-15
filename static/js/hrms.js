function initHRMS() {
    const wrapper = document.getElementById('wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function closeMobileSidebar() {
        sidebar?.classList.remove('show');
        sidebarOverlay?.classList.remove('show');
    }

    function openMobileSidebar() {
        sidebar?.classList.add('show');
        sidebarOverlay?.classList.add('show');
    }

    if (sidebarToggle && wrapper && !sidebarToggle.dataset.bound) {
        sidebarToggle.dataset.bound = '1';
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar?.classList.contains('show') ? closeMobileSidebar() : openMobileSidebar();
            } else {
                wrapper.classList.toggle('sidebar-collapsed');
            }
        });
    }

    if (sidebarOverlay && !sidebarOverlay.dataset.bound) {
        sidebarOverlay.dataset.bound = '1';
        sidebarOverlay.addEventListener('click', closeMobileSidebar);
    }

    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle && !themeToggle.dataset.bound) {
        themeToggle.dataset.bound = '1';
        const html = document.documentElement;
        const savedTheme = localStorage.getItem('hrms-theme') || html.getAttribute('data-bs-theme') || 'light';
        html.setAttribute('data-bs-theme', savedTheme);
        updateThemeIcon(savedTheme);
        themeToggle.addEventListener('click', function() {
            const next = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('hrms-theme', next);
            updateThemeIcon(next);
        });
    }

    function updateThemeIcon(theme) {
        const icon = document.getElementById('themeToggle')?.querySelector('i');
        if (icon) icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }

    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch && !globalSearch.dataset.bound) {
        globalSearch.dataset.bound = '1';
        globalSearch.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && this.value.trim()) {
                window.location.href = '/module/employees/?q=' + encodeURIComponent(this.value.trim());
            }
        });
    }

    if (!document.body.dataset.kbdBound) {
        document.body.dataset.kbdBound = '1';
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('globalSearch')?.focus();
            }
        });
    }

    updateSidebarActive();
    initPageScripts();
}

function updateSidebarActive() {
    const path = window.location.pathname;
    document.querySelectorAll('#sidebarNav a[data-path]').forEach(function(link) {
        const p = link.getAttribute('data-path');
        const alt = link.getAttribute('data-path-alt');
        const match = path === p || path.startsWith(p + '/') || (alt && path === alt);
        link.classList.toggle('active', match);
    });
}

function initPageScripts() {
    document.querySelectorAll('form[data-confirm]').forEach(function(form) {
        if (form.dataset.confirmBound) return;
        form.dataset.confirmBound = '1';
        form.addEventListener('submit', function(e) {
            if (!confirm(form.getAttribute('data-confirm'))) e.preventDefault();
        });
    });
    if (typeof window.initPageCharts === 'function') window.initPageCharts();
}

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
}

document.addEventListener('turbo:before-fetch-request', function(event) {
    const token = getCsrfToken();
    if (!token) return;
    event.detail.fetchOptions.headers['X-CSRFToken'] = token;
});

document.addEventListener('DOMContentLoaded', initHRMS);
document.addEventListener('turbo:load', initHRMS);
document.addEventListener('turbo:render', updateSidebarActive);
