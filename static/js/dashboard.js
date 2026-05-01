// dashboard.js — KitchenMetrics
// Charts, sidebar navigation + módulo Reservas (filtro, acciones, eliminar)

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
    const chartMermaData      = parseJsonScript('chart-merma-data');
    const chartPlatosData     = parseJsonScript('chart-platos-data');

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
                                const data   = chart.data.datasets[0].data;
                                const labels = chart.data.labels;
                                const total  = data.reduce((a, b) => a + b, 0);
                                return labels.map((label, i) => {
                                    const value   = data[i];
                                    const percent = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return {
                                        text:      `${label} (${percent}%)`,
                                        fillStyle: chart.data.datasets[0].backgroundColor[i],
                                        hidden:    isNaN(value),
                                        index:     i
                                    };
                                });
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const total   = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value   = context.parsed;
                                const percent = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${context.label}: ${value} (${percent}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // =========================
    // Navegación entre tabs (sidebar)
    // =========================
    const navItems = document.querySelectorAll('.sidebar .nav-item');
    const panes    = document.querySelectorAll('.content-pane');

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const target = this.dataset.target;
            if (!target) return;

            document.querySelectorAll('.sidebar .nav-item').forEach(n => n.classList.remove('active'));
            this.classList.add('active');

            panes.forEach(p => p.classList.add('d-none'));
            const pane = document.getElementById('content-' + target);
            if (pane) {
                pane.classList.remove('d-none');
                pane.classList.add('fade-in');
                setTimeout(() => pane.classList.remove('fade-in'), 350);
                pane.dispatchEvent(new CustomEvent('pane:shown'));
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


/* -----------------------------------------------------------------------------
   RESERVAS — includes_dashboard/reservas.html
   Filtro por texto (nombre + RUT) + estado, confirmar/cancelar, eliminar.
   Se inicializa al cargar el DOM y re-sincroniza en pane:shown.
   ----------------------------------------------------------------------------- */
(function () {

    // ── referencias DOM ──────────────────────────────────────────────────────
    const searchInput = document.getElementById('rutSearch');
    const clearBtn    = document.getElementById('clearRutSearch');
    const toggleBtn   = document.getElementById('toggleMoreBtn');
    const shownEl     = document.getElementById('shownCount');
    const totalEl     = document.getElementById('totalCount');
    const emptyRow    = document.getElementById('reservas-empty-row');

    let rows     = [];     // se recarga cada vez (puede cambiar por eliminación)
    let expanded = false;
    let estadoFiltro = 'todos';

    // ── utilidades ───────────────────────────────────────────────────────────

    function getRows() {
        return Array.from(document.querySelectorAll('.reserva-row'));
    }

    function actualizarContador() {
        rows = getRows();
        const visible = rows.filter(r => r.style.display !== 'none' && !r.classList.contains('d-none'));
        if (shownEl) shownEl.textContent = visible.length;
        if (totalEl) totalEl.textContent = rows.length;
        if (emptyRow) emptyRow.classList.toggle('d-none', visible.length > 0);
    }

    function applyFilter() {
        rows = getRows();
        const term = (searchInput ? searchInput.value : '').trim().toLowerCase();
        let shown  = 0;

        rows.forEach((row, index) => {
            const texto  = (row.dataset.texto  || row.dataset.nombre || '') + ' ' + (row.dataset.rut || '');
            const estado = row.dataset.estadoRow || '';

            const pasaTexto   = !term || texto.includes(term);
            const pasaEstado  = estadoFiltro === 'todos' || estado === estadoFiltro ||
                                (estadoFiltro === 'consumida' && estado === 'retirada');
            const pasaExpand  = expanded || index < 10;

            const visible = pasaTexto && pasaEstado && pasaExpand;
            row.classList.toggle('d-none', !visible);
            if (visible) shown++;
        });

        if (shownEl) shownEl.textContent = shown;
        if (totalEl) totalEl.textContent = rows.length;
        if (emptyRow) emptyRow.classList.toggle('d-none', shown > 0);
    }

    // ── badge HTML por estado ─────────────────────────────────────────────────

    function badgeHtml(estado) {
        const map = {
            confirmada:  '<span class="badge rounded-pill bg-primary-subtle text-primary px-3 py-2">Confirmada</span>',
            consumida:   '<span class="badge rounded-pill bg-success-subtle text-success px-3 py-2">Consumida</span>',
            retirada:    '<span class="badge rounded-pill bg-success-subtle text-success px-3 py-2">Consumida</span>',
            no_retirada: '<span class="badge rounded-pill bg-warning-subtle text-warning px-3 py-2">No retirada</span>',
            cancelada:   '<span class="badge rounded-pill bg-danger-subtle text-danger px-3 py-2">Cancelada</span>',
        };
        return map[estado] || `<span class="badge bg-light text-dark">${estado}</span>`;
    }

    // ── actualizar estado de fila tras acción confirm/cancel ──────────────────

    function actualizarEstadoFila(id, nuevoEstado) {
        const el = document.getElementById('estado-' + id);
        if (el) el.innerHTML = badgeHtml(nuevoEstado);

        const row = document.querySelector(`.reserva-row .action-btn[data-id="${id}"]`);
        const tr  = row ? row.closest('tr') : null;
        if (tr) {
            tr.dataset.estadoRow = nuevoEstado;
            const btnConfirmar = tr.querySelector('[data-action="confirmar"]');
            const btnCancelar  = tr.querySelector('[data-action="cancelar"]');
            if (btnConfirmar) btnConfirmar.disabled = nuevoEstado === 'confirmada';
            if (btnCancelar)  btnCancelar.disabled  = nuevoEstado === 'cancelada';
        }

        applyFilter();
    }

    // ── confirmar / cancelar ──────────────────────────────────────────────────

    function bindActionBtns() {
        document.querySelectorAll('.action-btn').forEach(btn => {
            // evitar listeners duplicados
            if (btn.dataset.bound) return;
            btn.dataset.bound = '1';

            btn.addEventListener('click', async () => {
                const id     = btn.dataset.id;
                const accion = btn.dataset.action;
                try {
                    const res  = await fetch('/admin/reserva/update_estado', {
                        method:  'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body:    JSON.stringify({ id_reserva: id, accion: accion }),
                    });
                    const data = await res.json();
                    if (data.success) actualizarEstadoFila(id, data.nuevo_estado);
                } catch (err) {
                    console.error('Error al actualizar estado:', err);
                }
            });
        });
    }

    // ── eliminar reserva ──────────────────────────────────────────────────────

    function bindDeleteBtns() {
        document.querySelectorAll('.delete-reserva-btn').forEach(btn => {
            if (btn.dataset.bound) return;
            btn.dataset.bound = '1';

            btn.addEventListener('click', async () => {
                const id     = btn.dataset.id;
                const nombre = btn.dataset.nombre || 'esta reserva';

                if (!confirm(`¿Eliminar la reserva de ${nombre}?\nEsta acción no se puede deshacer.`)) return;

                btn.disabled = true;
                try {
                    const res  = await fetch('/admin/reserva/eliminar', {
                        method:  'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body:    JSON.stringify({ id_reserva: id }),
                    });
                    const data = await res.json();
                    if (data.success) {
                        const tr = btn.closest('tr');
                        if (tr) {
                            tr.style.transition = 'opacity 0.25s';
                            tr.style.opacity    = '0';
                            setTimeout(() => { tr.remove(); applyFilter(); }, 260);
                        }
                    } else {
                        alert('No se pudo eliminar: ' + (data.error || 'Error desconocido'));
                        btn.disabled = false;
                    }
                } catch (err) {
                    console.error('Error al eliminar reserva:', err);
                    btn.disabled = false;
                }
            });
        });
    }

    // ── búsqueda por texto ────────────────────────────────────────────────────

    if (searchInput) {
        searchInput.addEventListener('input', applyFilter);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            expanded     = false;
            estadoFiltro = 'todos';
            document.querySelectorAll('.reserva-pill').forEach(p => p.classList.remove('active', 'btn-success', 'btn-primary', 'btn-warning', 'btn-danger'));
            const todosBtn = document.querySelector('.reserva-pill[data-estado-filtro="todos"]');
            if (todosBtn) todosBtn.classList.add('active', 'btn-success');
            if (toggleBtn) toggleBtn.textContent = 'Mostrar más';
            applyFilter();
        });
    }

    // ── toggle mostrar más ────────────────────────────────────────────────────

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            expanded              = !expanded;
            toggleBtn.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';
            applyFilter();
        });
    }

    // ── pills de estado ───────────────────────────────────────────────────────

    const pillColorMap = {
        todos:       'btn-success',
        confirmada:  'btn-primary',
        consumida:   'btn-success',
        no_retirada: 'btn-warning',
        cancelada:   'btn-danger',
    };

    document.querySelectorAll('.reserva-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            estadoFiltro = pill.dataset.estadoFiltro || 'todos';

            // Reset visual de todas las pills
            document.querySelectorAll('.reserva-pill').forEach(p => {
                const color = pillColorMap[p.dataset.estadoFiltro] || 'btn-secondary';
                p.classList.remove('active', 'btn-success', 'btn-primary', 'btn-warning', 'btn-danger', 'btn-secondary');
                p.classList.add('btn-outline-' + color.replace('btn-', ''));
            });

            // Activar la pill seleccionada
            const activeColor = pillColorMap[estadoFiltro] || 'btn-success';
            pill.classList.remove('btn-outline-' + activeColor.replace('btn-', ''));
            pill.classList.add(activeColor, 'active');

            applyFilter();
        });
    });

    // ── inicializar ───────────────────────────────────────────────────────────

    function init() {
        bindActionBtns();
        bindDeleteBtns();
        applyFilter();
    }

    // Init cuando el pane de reservas se muestra (lazy, sincroniza estado real)
    var reservasPane = document.getElementById('content-reservas');
    if (reservasPane) {
        reservasPane.addEventListener('pane:shown', init);
    }

    // Init inmediato si el DOM ya cargó y el pane es visible (evita pantalla vacía)
    document.addEventListener('DOMContentLoaded', function () {
        if (document.getElementById('rutSearch')) init();
    });

    // Llamar init ahora si el DOM ya está listo
    if (document.readyState !== 'loading') {
        if (document.getElementById('rutSearch')) init();
    }

})();