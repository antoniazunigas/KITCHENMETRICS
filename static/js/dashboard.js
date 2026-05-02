// dashboard.js — KitchenMetrics
// Charts · Sidebar · Módulo Reservas (texto + estado + fecha · confirmar · cancelar · eliminar)

document.addEventListener('DOMContentLoaded', function () {

    function parseJsonScript(id) {
        const el = document.getElementById(id);
        if (!el) return {};
        try { return JSON.parse(el.textContent.trim() || '{}'); }
        catch (e) { console.error('JSON parse error ' + id, e); return {}; }
    }

    const chartConsumidasData = parseJsonScript('chart-consumidas-data');
    const chartMermaData      = parseJsonScript('chart-merma-data');
    const chartPlatosData     = parseJsonScript('chart-platos-data');

    // ── 1. BAR: Consumidas ────────────────────────────────────────────────────
    const ctxConsumo = document.getElementById('chart-consumidas');
    if (ctxConsumo && typeof Chart !== 'undefined') {
        new Chart(ctxConsumo, {
            type: 'bar',
            data: {
                labels: chartConsumidasData.labels || [],
                datasets: [
                    { label: 'Consumidas',    data: chartConsumidasData.consumidas    || [], backgroundColor: '#27ae60', borderRadius: 6, borderSkipped: false },
                    { label: 'No consumidas', data: chartConsumidasData.no_consumidas || [], backgroundColor: '#df3320', borderRadius: 6, borderSkipped: false }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true } } }
        });
    }

    // ── 2. LINE: Merma % ──────────────────────────────────────────────────────
    const ctxMerma = document.getElementById('chart-merma');
    if (ctxMerma && typeof Chart !== 'undefined') {
        new Chart(ctxMerma, {
            type: 'line',
            data: {
                labels: chartMermaData.labels || [],
                datasets: [
                    { label: '% Desperdicio', data: chartMermaData.porcentaje || [], borderColor: '#df3320', backgroundColor: 'rgba(223,51,32,0.05)', borderWidth: 2, pointRadius: 5, pointBackgroundColor: '#df3320', fill: true, tension: 0.3 },
                    { label: 'Meta',          data: chartMermaData.meta       || [], borderColor: '#27ae60', borderDash: [5,5], borderWidth: 2, pointRadius: 0, fill: false, tension: 0.3 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true, max: 100 } } }
        });
    }

    // ── 3. DOUGHNUT: Platos ───────────────────────────────────────────────────
    const ctxPlatos = document.getElementById('chart-platos');
    if (ctxPlatos && typeof Chart !== 'undefined') {
        new Chart(ctxPlatos, {
            type: 'doughnut',
            data: {
                labels: chartPlatosData.labels || ['Consumidos', 'No consumidos'],
                datasets: [{ data: chartPlatosData.data || [0,0], backgroundColor: ['#27ae60','#df3320'], borderColor: '#fff', borderWidth: 2 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            generateLabels: function (chart) {
                                const d = chart.data.datasets[0].data, l = chart.data.labels;
                                const t = d.reduce((a, b) => a + b, 0);
                                return l.map((label, i) => ({ text: `${label} (${t > 0 ? ((d[i]/t)*100).toFixed(1) : 0}%)`, fillStyle: chart.data.datasets[0].backgroundColor[i], hidden: isNaN(d[i]), index: i }));
                            }
                        }
                    },
                    tooltip: { callbacks: { label: function (ctx) { const t = ctx.dataset.data.reduce((a,b)=>a+b,0); return `${ctx.label}: ${ctx.parsed} (${t>0?((ctx.parsed/t)*100).toFixed(1):0}%)`; } } }
                }
            }
        });
    }

    // ── Navegación sidebar ────────────────────────────────────────────────────
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
        item.setAttribute('tabindex', '0');
        item.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
        });
    });

});


/* -----------------------------------------------------------------------------
   RESERVAS — includes_dashboard/reservas.html
   Filtros: texto · estado · fecha (hoy/mañana/todos)
   Acciones: confirmar · cancelar · eliminar (con fade-out de fila)
   ----------------------------------------------------------------------------- */
(function () {

    const searchInput = document.getElementById('rutSearch');
    const clearBtn    = document.getElementById('clearRutSearch');
    const toggleBtn   = document.getElementById('toggleMoreBtn');
    const shownEl     = document.getElementById('shownCount');
    const totalEl     = document.getElementById('totalCount');
    const emptyRow    = document.getElementById('reservas-empty-row');

    let expanded     = false;
    let estadoFiltro = 'todos';
    let fechaFiltro  = 'todos';

    // ── filtrado ──────────────────────────────────────────────────────────────

    function getRows() { return Array.from(document.querySelectorAll('.reserva-row')); }

    function applyFilter() {
        const rows = getRows();
        const term = (searchInput ? searchInput.value : '').trim().toLowerCase();
        let shown  = 0;

        rows.forEach((row, index) => {
            const texto  = row.dataset.texto      || '';
            const estado = row.dataset.estadoRow  || '';
            const dia    = row.dataset.dia        || 'hoy';

            const pasaTexto  = !term || texto.includes(term);
            const pasaEstado = estadoFiltro === 'todos' ||
                               estado === estadoFiltro ||
                               (estadoFiltro === 'consumida' && estado === 'retirada');
            const pasaFecha  = fechaFiltro === 'todos' || dia === fechaFiltro;
            const pasaExpand = expanded || index < 10;

            const visible = pasaTexto && pasaEstado && pasaFecha && pasaExpand;
            row.classList.toggle('d-none', !visible);
            if (visible) shown++;
        });

        if (shownEl)  shownEl.textContent  = shown;
        if (totalEl)  totalEl.textContent  = rows.length;
        if (emptyRow) emptyRow.classList.toggle('d-none', shown > 0);
    }

    // ── badge HTML ────────────────────────────────────────────────────────────

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

    function actualizarEstadoFila(id, nuevoEstado) {
        const el = document.getElementById('estado-' + id);
        if (el) el.innerHTML = badgeHtml(nuevoEstado);
        const trigger = document.querySelector(`.action-btn[data-id="${id}"]`);
        const tr = trigger ? trigger.closest('tr') : null;
        if (tr) {
            tr.dataset.estadoRow = nuevoEstado;
            const bc = tr.querySelector('[data-action="confirmar"]');
            const bk = tr.querySelector('[data-action="cancelar"]');
            if (bc) bc.disabled = nuevoEstado === 'confirmada';
            if (bk) bk.disabled = nuevoEstado === 'cancelada';
        }
        applyFilter();
    }

    // ── bind confirmar/cancelar ───────────────────────────────────────────────

    function bindActionBtns() {
        document.querySelectorAll('.action-btn').forEach(btn => {
            if (btn.dataset.bound) return;
            btn.dataset.bound = '1';
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id, accion = btn.dataset.action;
                try {
                    const res  = await fetch('/admin/reserva/update_estado', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id_reserva: id, accion }),
                    });
                    const data = await res.json();
                    if (data.success) actualizarEstadoFila(id, data.nuevo_estado);
                } catch (e) { console.error('update_estado error:', e); }
            });
        });
    }

    // ── bind eliminar ─────────────────────────────────────────────────────────

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
                        method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ id_reserva: id }),
                    });
                    const data = await res.json();
                    if (data.success) {
                        const tr = btn.closest('tr');
                        if (tr) {
                            tr.style.transition = 'opacity 0.25s';
                            tr.style.opacity = '0';
                            setTimeout(() => { tr.remove(); applyFilter(); }, 260);
                        }
                    } else {
                        alert('No se pudo eliminar: ' + (data.error || 'Error desconocido'));
                        btn.disabled = false;
                    }
                } catch (e) { console.error('eliminar error:', e); btn.disabled = false; }
            });
        });
    }

    // ── búsqueda ──────────────────────────────────────────────────────────────

    if (searchInput) searchInput.addEventListener('input', applyFilter);

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            expanded = false; estadoFiltro = 'todos'; fechaFiltro = 'todos';

            // reset pills estado
            document.querySelectorAll('.reserva-pill').forEach(p => {
                const c = pillColorMap[p.dataset.estadoFiltro] || 'secondary';
                p.classList.remove('active','btn-success','btn-primary','btn-warning','btn-danger','btn-secondary');
                p.classList.add('btn-outline-' + c.replace('btn-',''));
            });
            const pe = document.querySelector('.reserva-pill[data-estado-filtro="todos"]');
            if (pe) { pe.classList.remove('btn-outline-success'); pe.classList.add('btn-success','active'); }

            // reset pills fecha
            document.querySelectorAll('.reserva-pill-fecha').forEach(p => {
                p.classList.remove('active','btn-secondary');
                p.classList.add('btn-outline-secondary');
            });
            const pf = document.querySelector('.reserva-pill-fecha[data-fecha-filtro="todos"]');
            if (pf) { pf.classList.remove('btn-outline-secondary'); pf.classList.add('btn-secondary','active'); }

            if (toggleBtn) toggleBtn.textContent = 'Mostrar más';
            applyFilter();
        });
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            expanded = !expanded;
            toggleBtn.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';
            applyFilter();
        });
    }

    // ── pills estado ──────────────────────────────────────────────────────────

    const pillColorMap = {
        todos: 'btn-success', confirmada: 'btn-primary',
        consumida: 'btn-success', no_retirada: 'btn-warning', cancelada: 'btn-danger',
    };

    document.querySelectorAll('.reserva-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            estadoFiltro = pill.dataset.estadoFiltro || 'todos';
            document.querySelectorAll('.reserva-pill').forEach(p => {
                const c = pillColorMap[p.dataset.estadoFiltro] || 'secondary';
                p.classList.remove('active','btn-success','btn-primary','btn-warning','btn-danger','btn-secondary');
                p.classList.add('btn-outline-' + c.replace('btn-',''));
            });
            const ac = pillColorMap[estadoFiltro] || 'btn-success';
            pill.classList.remove('btn-outline-' + ac.replace('btn-',''));
            pill.classList.add(ac, 'active');
            applyFilter();
        });
    });

    // ── pills fecha ───────────────────────────────────────────────────────────

    document.querySelectorAll('.reserva-pill-fecha').forEach(pill => {
        pill.addEventListener('click', () => {
            fechaFiltro = pill.dataset.fechaFiltro || 'todos';
            document.querySelectorAll('.reserva-pill-fecha').forEach(p => {
                p.classList.remove('active','btn-secondary');
                p.classList.add('btn-outline-secondary');
            });
            pill.classList.remove('btn-outline-secondary');
            pill.classList.add('btn-secondary','active');
            applyFilter();
        });
    });

    // ── init ──────────────────────────────────────────────────────────────────

    function init() {
        bindActionBtns();
        bindDeleteBtns();
        applyFilter();
    }

    const pane = document.getElementById('content-reservas');
    if (pane) pane.addEventListener('pane:shown', init);

    document.addEventListener('DOMContentLoaded', function () {
        if (document.getElementById('rutSearch')) init();
    });

    if (document.readyState !== 'loading' && document.getElementById('rutSearch')) init();

})();