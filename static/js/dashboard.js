// Dashboard JS: charts, data parsing and sidebar navigation
document.addEventListener('DOMContentLoaded', function () {

    function parseJsonScript(id) {
        const el = document.getElementById(id);
        if (!el) return {};
        try {
            return JSON.parse(el.textContent.trim() || '{}');
        } catch (error) {
            console.error('Error al parsear JSON en ' + id, error);
            return {};
        }
    }

    const chartConsumidasData = parseJsonScript('chart-consumidas-data');
    const chartMermaData = parseJsonScript('chart-merma-data');
    const chartPlatosData = parseJsonScript('chart-platos-data');

    // =========================
    // 1. BAR: Consumidas vs No consumidas
    // =========================
    const ctxConsumo = document.getElementById('chart-consumidas');
    if (ctxConsumo && typeof Chart !== 'undefined') {
        new Chart(ctxConsumo, {
            type: 'bar',
            data: {
                labels: chartConsumidasData.labels || [],
                datasets: [
                    {
                        label: 'Consumidas',
                        data: chartConsumidasData.consumidas || [],
                        backgroundColor: '#27ae60',
                        borderRadius: 6,
                        borderSkipped: false
                    },
                    {
                        label: 'No consumidas',
                        data: chartConsumidasData.no_consumidas || [],
                        backgroundColor: '#df3320',
                        borderRadius: 6,
                        borderSkipped: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // =========================
    // 2. LINE: Merma %
    // =========================
    const ctxMerma = document.getElementById('chart-merma');
    if (ctxMerma && typeof Chart !== 'undefined') {
        new Chart(ctxMerma, {
            type: 'line',
            data: {
                labels: chartMermaData.labels || [],
                datasets: [
                    {
                        label: '% Desperdicio',
                        data: chartMermaData.porcentaje || [],
                        borderColor: '#df3320',
                        backgroundColor: 'rgba(223, 51, 32, 0.05)',
                        borderWidth: 2,
                        pointRadius: 5,
                        pointBackgroundColor: '#df3320',
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Meta',
                        data: chartMermaData.meta || [],
                        borderColor: '#27ae60',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                scales: { y: { beginAtZero: true, max: 100 } }
            }
        });
    }

    // =========================
    // 3. DOUGHNUT: Platos
    // =========================
    const ctxPlatos = document.getElementById('chart-platos');
    if (ctxPlatos && typeof Chart !== 'undefined') {
        new Chart(ctxPlatos, {
            type: 'doughnut',
            data: {
                labels: chartPlatosData.labels || ['Consumidos', 'No consumidos'],
                datasets: [{
                    data: chartPlatosData.data || [0, 0],
                    backgroundColor: ['#27ae60', '#df3320'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            generateLabels: function (chart) {
                                const data = chart.data.datasets[0].data;
                                const labels = chart.data.labels;
                                const total = data.reduce((a, b) => a + b, 0);

                                return labels.map((label, i) => {
                                    const value = data[i];
                                    const percent = total > 0 ? ((value / total) * 100).toFixed(1) : 0;

                                    return {
                                        text: `${label} (${percent}%)`,
                                        fillStyle: chart.data.datasets[0].backgroundColor[i],
                                        hidden: isNaN(value),
                                        index: i
                                    };
                                });
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.parsed;
                                const percent = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${context.label}: ${value} (${percent}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Navegación entre tabs (sidebar)
    const navItems = document.querySelectorAll('.sidebar .nav-item');
    const panes = document.querySelectorAll('.content-pane');

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const target = this.dataset.target;
            if (!target) return;

            // Actualizar estado activo en la barra lateral
            document.querySelectorAll('.sidebar .nav-item').forEach(n => n.classList.remove('active'));
            this.classList.add('active');

            // Ocultar todas las pestañas y mostrar la seleccionada
            panes.forEach(p => p.classList.add('d-none'));
            const pane = document.getElementById('content-' + target);
            if (pane) {
                pane.classList.remove('d-none');
                pane.classList.add('fade-in');
                setTimeout(() => pane.classList.remove('fade-in'), 350);
            }
        });
    });

    // Soporte de teclado para accesibilidad
    navItems.forEach(item => {
        item.setAttribute('tabindex', '0');
        item.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

});
