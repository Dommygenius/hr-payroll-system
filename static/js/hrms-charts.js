/**
 * HRMS chart builders — Workforce by Department & related analytics
 */
window.HRMSCharts = (function () {
    'use strict';

    const PALETTE = [
        '#0d9488', '#0891b2', '#6366f1', '#8b5cf6',
        '#f97316', '#eab308', '#10b981', '#ec4899',
        '#14b8a6', '#64748b',
    ];

    const FONT = "'DM Sans', system-ui, sans-serif";
    const DISPLAY = "'Outfit', system-ui, sans-serif";

    function isDark() {
        return document.documentElement.getAttribute('data-bs-theme') === 'dark';
    }

    function themeColors() {
        return isDark()
            ? { text: '#94a3b8', grid: 'rgba(255,255,255,0.06)', muted: '#64748b' }
            : { text: '#64748b', grid: 'rgba(12,25,41,0.06)', muted: '#94a3b8' };
    }

    function normalizeDeptData(raw) {
        if (!raw || !raw.length) {
            return [{ name: 'No data yet', count: 0 }];
        }
        return raw.map(function (d) {
            return {
                name: d.department__name || d.name || 'Unassigned',
                count: Number(d.count) || 0,
            };
        }).sort(function (a, b) { return b.count - a.count; });
    }

    function totalCount(items) {
        return items.reduce(function (sum, d) { return sum + d.count; }, 0);
    }

    function pct(count, total) {
        if (!total) return 0;
        return Math.round((count / total) * 100);
    }

    /** Draw total in doughnut center */
    const centerTotalPlugin = {
        id: 'centerTotal',
        beforeDraw: function (chart) {
            const opts = chart.options.plugins.centerTotal;
            if (!opts) return;
            const meta = chart.getDatasetMeta(0);
            if (!meta || !meta.data.length) return;

            const ctx = chart.ctx;
            const center = meta.data[0];
            const x = center.x;
            const y = center.y;

            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = opts.valueColor || '#0c1929';
            ctx.font = '700 2rem ' + DISPLAY;
            ctx.fillText(String(opts.total), x, y - 8);
            ctx.fillStyle = opts.labelColor || '#64748b';
            ctx.font = '500 0.6875rem ' + FONT;
            ctx.fillText(opts.label || 'Employees', x, y + 18);
            ctx.restore();
        },
    };

    if (typeof Chart !== 'undefined') {
        Chart.register(centerTotalPlugin);
    }

    function renderLegend(container, items, total) {
        if (!container) return;
        container.innerHTML = '';

        if (!total) {
            container.innerHTML = '<div class="workforce-legend-empty">Add employees to departments to see distribution.</div>';
            return;
        }

        items.forEach(function (item, i) {
            const color = PALETTE[i % PALETTE.length];
            const share = pct(item.count, total);
            const row = document.createElement('div');
            row.className = 'workforce-legend-row';
            row.innerHTML =
                '<div class="workforce-legend-rank">' + (i + 1) + '</div>' +
                '<div class="workforce-legend-dot" style="background:' + color + '"></div>' +
                '<div class="workforce-legend-info">' +
                    '<div class="workforce-legend-top">' +
                        '<span class="workforce-legend-name">' + escapeHtml(item.name) + '</span>' +
                        '<span class="workforce-legend-count">' + item.count + '</span>' +
                    '</div>' +
                    '<div class="workforce-legend-bar">' +
                        '<div class="workforce-legend-fill" style="width:' + share + '%;background:' + color + '"></div>' +
                    '</div>' +
                    '<span class="workforce-legend-pct">' + share + '% of workforce</span>' +
                '</div>';
            container.appendChild(row);
        });
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function updateSummary(container, items, total) {
        if (!container) return;
        const top = items[0];
        const deptCount = items.filter(function (d) { return d.count > 0; }).length;
        container.innerHTML =
            '<div class="workforce-summary-item">' +
                '<span class="workforce-summary-value">' + total + '</span>' +
                '<span class="workforce-summary-label">Total</span>' +
            '</div>' +
            '<div class="workforce-summary-item">' +
                '<span class="workforce-summary-value">' + deptCount + '</span>' +
                '<span class="workforce-summary-label">Departments</span>' +
            '</div>' +
            (top && top.count
                ? '<div class="workforce-summary-item workforce-summary-highlight">' +
                    '<span class="workforce-summary-value">' + escapeHtml(top.name) + '</span>' +
                    '<span class="workforce-summary-label">Largest · ' + top.count + ' people</span>' +
                  '</div>'
                : '');
    }

    /**
     * Premium workforce breakdown: doughnut + ranked legend
     */
    function renderWorkforceByDepartment(options) {
        const canvas = document.getElementById(options.canvasId);
        if (!canvas || typeof Chart === 'undefined') return null;

        const items = normalizeDeptData(options.data);
        const total = totalCount(items);
        const colors = items.map(function (_, i) { return PALETTE[i % PALETTE.length]; });
        const tc = themeColors();

        renderLegend(document.getElementById(options.legendId), items, total);
        updateSummary(document.getElementById(options.summaryId), items, total);

        const layoutEl = canvas.closest('.workforce-chart-layout');
        const summaryEl = document.getElementById(options.summaryId);

        if (options.emptyId) {
            const emptyEl = document.getElementById(options.emptyId);
            if (emptyEl) emptyEl.style.display = total ? 'none' : 'flex';
        }
        if (layoutEl) layoutEl.style.display = total ? 'grid' : 'none';
        if (summaryEl) summaryEl.style.display = total ? 'flex' : 'none';

        if (!total) return null;

        const existing = typeof Chart !== 'undefined' ? Chart.getChart(canvas) : null;
        if (existing) existing.destroy();

        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: items.map(function (d) { return d.name; }),
                datasets: [{
                    data: items.map(function (d) { return d.count; }),
                    backgroundColor: colors,
                    borderWidth: 3,
                    borderColor: isDark() ? '#0f1a24' : '#ffffff',
                    hoverBorderColor: isDark() ? '#0f1a24' : '#ffffff',
                    hoverOffset: 8,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                layout: { padding: 8 },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark() ? '#0f1a24' : '#0c1929',
                        titleFont: { family: DISPLAY, size: 13, weight: '600' },
                        bodyFont: { family: FONT, size: 12 },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function (ctx) {
                                const v = ctx.raw;
                                return ' ' + v + ' employees (' + pct(v, total) + '%)';
                            },
                        },
                    },
                    centerTotal: {
                        total: total,
                        label: 'Employees',
                        valueColor: isDark() ? '#f1f5f9' : '#0c1929',
                        labelColor: tc.muted,
                    },
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 900,
                    easing: 'easeOutQuart',
                },
            },
        });
    }

    /**
     * Horizontal bar chart for reports page (full width)
     */
    function renderDeptBarChart(canvasId, rawData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === 'undefined') return null;

        const items = normalizeDeptData(rawData);
        const total = totalCount(items);
        const tc = themeColors();
        const ctx = canvas.getContext('2d');

        if (!total) {
            const wrap = canvas.closest('.workforce-bar-chart-wrap');
            if (wrap) wrap.style.display = 'none';
            return null;
        }

        const existing = typeof Chart !== 'undefined' ? Chart.getChart(canvas) : null;
        if (existing) existing.destroy();

        const gradients = items.map(function (_, i) {
            const g = ctx.createLinearGradient(0, 0, canvas.parentElement.offsetWidth || 400, 0);
            const base = PALETTE[i % PALETTE.length];
            g.addColorStop(0, base);
            g.addColorStop(1, base + '88');
            return g;
        });

        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: items.map(function (d) { return d.name; }),
                datasets: [{
                    data: items.map(function (d) { return d.count; }),
                    backgroundColor: gradients.length ? gradients : PALETTE[0],
                    borderRadius: { topRight: 8, bottomRight: 8 },
                    borderSkipped: false,
                    barThickness: 22,
                }],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                layout: { padding: { right: 48 } },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark() ? '#0f1a24' : '#0c1929',
                        titleFont: { family: DISPLAY, weight: '600' },
                        bodyFont: { family: FONT },
                        cornerRadius: 8,
                        callbacks: {
                            label: function (c) {
                                return ' ' + c.raw + ' (' + pct(c.raw, total) + '%)';
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: tc.grid, drawBorder: false },
                        ticks: {
                            stepSize: 1,
                            font: { family: FONT, size: 11 },
                            color: tc.text,
                        },
                    },
                    y: {
                        grid: { display: false, drawBorder: false },
                        ticks: {
                            font: { family: FONT, size: 12, weight: '500' },
                            color: isDark() ? '#cbd5e1' : '#334155',
                        },
                    },
                },
                animation: { duration: 800, easing: 'easeOutQuart' },
            },
            plugins: [{
                id: 'barValueLabels',
                afterDatasetsDraw: function (chart) {
                    const c = chart.ctx;
                    chart.getDatasetMeta(0).data.forEach(function (bar, i) {
                        const val = chart.data.datasets[0].data[i];
                        c.save();
                        c.fillStyle = tc.text;
                        c.font = '600 11px ' + FONT;
                        c.textAlign = 'left';
                        c.textBaseline = 'middle';
                        c.fillText(String(val), bar.x + 8, bar.y);
                        c.restore();
                    });
                },
            }],
        });
    }

    function renderLeaveDonut(canvasId, rawData) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === 'undefined') return null;

        const items = (rawData || []).map(function (d) {
            return { name: (d.status || 'unknown').replace(/_/g, ' '), count: Number(d.count) || 0 };
        });
        const total = totalCount(items);
        const statusColors = {
            approved: '#10b981', pending: '#f59e0b', rejected: '#ef4444',
            draft: '#64748b', cancelled: '#94a3b8',
        };
        const colors = items.map(function (d, i) {
            const key = (d.name || '').replace(/ /g, '_');
            return statusColors[key] || PALETTE[i % PALETTE.length];
        });
        const tc = themeColors();

        const existing = typeof Chart !== 'undefined' ? Chart.getChart(canvas) : null;
        if (existing) existing.destroy();

        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: items.map(function (d) { return d.name; }),
                datasets: [{
                    data: items.map(function (d) { return d.count; }),
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: isDark() ? '#0f1a24' : '#fff',
                    hoverOffset: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 16,
                            font: { family: FONT, size: 11 },
                            color: tc.text,
                        },
                    },
                    tooltip: {
                        backgroundColor: isDark() ? '#0f1a24' : '#0c1929',
                        cornerRadius: 8,
                        callbacks: {
                            label: function (c) {
                                return ' ' + c.raw + ' (' + pct(c.raw, total) + '%)';
                            },
                        },
                    },
                    centerTotal: total ? {
                        total: total,
                        label: 'Requests',
                        valueColor: isDark() ? '#f1f5f9' : '#0c1929',
                        labelColor: tc.muted,
                    } : undefined,
                },
            },
        });
    }

    return {
        renderWorkforceByDepartment: renderWorkforceByDepartment,
        renderDeptBarChart: renderDeptBarChart,
        renderLeaveDonut: renderLeaveDonut,
        palette: PALETTE,
    };
})();
