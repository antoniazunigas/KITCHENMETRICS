/* -----------------------------------------------------------------------------
   HELPER — leer un blob JSON embebido en el template de forma segura
   ----------------------------------------------------------------------------- */
function _parseBlob(id, fallback) {
  const el = document.getElementById(id);
  if (!el) return fallback;
  try { return JSON.parse(el.textContent.trim() || JSON.stringify(fallback)); }
  catch { return fallback; }
}


/* =============================================================================
   JEFE_COCINA.HTML — Sidebar + Gráficas principales
   ============================================================================= */
document.addEventListener('DOMContentLoaded', function () {

  /* ── Navegación del sidebar ── */
  const navItems = document.querySelectorAll('.sidebar .nav-item');
  const panes    = document.querySelectorAll('.content-pane');

  navItems.forEach(item => {
    item.addEventListener('click', function (e) {
      e.preventDefault();
      const target = this.dataset.target;
      if (!target) return;

      navItems.forEach(n => n.classList.remove('active'));
      this.classList.add('active');

      panes.forEach(p => p.classList.add('d-none'));
      const pane = document.getElementById('content-' + target);
      if (pane) {
        pane.classList.remove('d-none');
        pane.dispatchEvent(new CustomEvent('pane:shown'));
      }
    });

    // Soporte de teclado
    item.setAttribute('tabindex', '0');
    item.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        item.click();
      }
    });
  });

  /* ── Gráficas del panel principal JC ── */
  const ccData = _parseBlob('chart-consumidas-data', {});
  const cmData = _parseBlob('chart-merma-data',      {});
  const cpData = _parseBlob('chart-platos-data',     {});

  const ctxC = document.getElementById('jc-chart-consumidas');
  if (ctxC && typeof Chart !== 'undefined') {
    new Chart(ctxC, {
      type: 'bar',
      data: {
        labels:   ccData.labels || [],
        datasets: [
          { label: 'Consumidas',    data: ccData.consumidas    || [], backgroundColor: '#27ae60', borderRadius: 6 },
          { label: 'No consumidas', data: ccData.no_consumidas || [], backgroundColor: '#df3320', borderRadius: 6 },
        ],
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        scales:  { y: { beginAtZero: true } },
      },
    });
  }

  const ctxM = document.getElementById('jc-chart-merma');
  if (ctxM && typeof Chart !== 'undefined') {
    new Chart(ctxM, {
      type: 'line',
      data: {
        labels:   cmData.labels || [],
        datasets: [
          { label: '% Desperdicio', data: cmData.porcentaje || [], borderColor: '#df3320', backgroundColor: 'rgba(223,51,32,.05)', fill: true,  tension: .3, pointRadius: 4 },
          { label: 'Meta',          data: cmData.meta       || [], borderColor: '#27ae60', borderDash: [5, 5], borderWidth: 2, pointRadius: 0, fill: false },
        ],
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        scales:  { y: { beginAtZero: true, max: 100 } },
      },
    });
  }

  const ctxP = document.getElementById('jc-chart-platos');
  if (ctxP && typeof Chart !== 'undefined') {
    new Chart(ctxP, {
      type: 'doughnut',
      data: {
        labels:   cpData.labels || ['Preparados', 'No consumidos'],
        datasets: [{
          data:            cpData.data || [0, 0],
          backgroundColor: ['#27ae60', '#df3320'],
          borderColor:     '#fff',
          borderWidth:     2,
        }],
      },
      options: {
        responsive:          true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: { legend: { position: 'bottom' } },
      },
    });
  }

});


/* =============================================================================
   PLANIFICACION_JC.HTML — Calendario de menús + modal crear/editar/eliminar
   ============================================================================= */
document.addEventListener('DOMContentLoaded', function () {
  (function () {

    // Datos del servidor (expuestos como blobs JSON en el template)
    const menusPorFecha = _parseBlob('menus-por-fecha-data', {});
    const platosDisp    = _parseBlob('platos-list-data',     []);

    // Salida rápida si el pane no existe en esta página
    if (!document.getElementById('jc-calendar')) return;

    const modal          = new bootstrap.Modal(document.getElementById('menuDayModal'));
    const modalTitle     = document.getElementById('menuDayModalTitle');
    const modalFechaDisp = document.getElementById('modal-fecha-display');
    const modalFechaIso  = document.getElementById('modal-fecha-iso');
    const modalIdMenu    = document.getElementById('modal-id-menu');
    const modalEstado    = document.getElementById('modal-estado');
    const modalBadge     = document.getElementById('modal-menu-badge');
    const modalAlert     = document.getElementById('modal-alert');
    const modalSaveBtn   = document.getElementById('modal-save-btn');
    const modalDeleteBtn = document.getElementById('modal-delete-btn');
    const modalRacionesPlan = document.getElementById('modal-raciones-plan');
    const modalRacionesPrep = document.getElementById('modal-raciones-prep');
    const modalRacionesDisp = document.getElementById('modal-raciones-disp');

    let currentYear, currentMonth;

    function pad(n)           { return String(n).padStart(2, '0'); }
    function toIso(y, m, d)   { return `${y}-${pad(m + 1)}-${pad(d)}`; }

    const MONTHS_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                       'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    const DAYS_ES   = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];

    /* ── Poblar los <select> de platos del modal ── */
    function buildPlatoSelects() {
      document.querySelectorAll('.modal-plato-select').forEach(sel => {
        const orden = parseInt(sel.dataset.orden);
        sel.innerHTML = '<option value="">— Sin plato —</option>';

        platosDisp.forEach(p => {
          const tipo = p.tipo_plato || '';
          let show   = false;

          if (orden === 1              && tipo === 'entrada') show = true;
          if (orden >= 2 && orden <= 4 && tipo === 'fondo')   show = true;
          if (orden === 5              && tipo === 'postre')   show = true;

          if (show) {
            const opt      = document.createElement('option');
            opt.value      = p.id_plato;
            opt.textContent = p.nombre + (p.tipo_dieta ? ` (${p.tipo_dieta})` : '');
            sel.appendChild(opt);
          }
        });
      });
    }

    /* ── Renderizar el calendario mensual ── */
    function renderCalendar(year, month) {
      currentYear  = year;
      currentMonth = month;

      document.getElementById('calMonthLabel').textContent = `${MONTHS_ES[month]} ${year}`;
      const container = document.getElementById('jc-calendar');
      container.innerHTML = '';

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const grid = document.createElement('div');
      grid.className = 'cal-grid';

      DAYS_ES.forEach(d => {
        const h       = document.createElement('div');
        h.className   = 'cal-header-cell';
        h.textContent = d;
        grid.appendChild(h);
      });

      const firstDay = new Date(year, month, 1).getDay();
      const offset   = (firstDay + 6) % 7; // lunes como primer día
      for (let i = 0; i < offset; i++) {
        const blank   = document.createElement('div');
        blank.className = 'cal-day empty';
        grid.appendChild(blank);
      }

      const daysInMonth = new Date(year, month + 1, 0).getDate();

      for (let d = 1; d <= daysInMonth; d++) {
        const iso  = toIso(year, month, d);
        const cell = document.createElement('div');
        const dt   = new Date(year, month, d);
        dt.setHours(0, 0, 0, 0);

        const past  = dt < today;
        const isT   = dt.getTime() === today.getTime();
        const hasMn = !!menusPorFecha[iso];

        cell.className = 'cal-day'
          + (hasMn ? ' has-menu' : '')
          + (isT   ? ' is-today' : '')
          + (past  ? ' is-past'  : '');

        cell.innerHTML = `<div class="cal-day-num">${d}</div>`;

        if (hasMn) {
          const m = menusPorFecha[iso];
          cell.innerHTML += `<div class="cal-day-label">${m.estado || 'activo'}</div><div class="cal-day-dot"></div>`;
        } else if (!past) {
          cell.innerHTML += `<div class="cal-day-label" style="color:#adb5bd;">Sin menú</div>`;
        }

        if (!past || hasMn) {
          cell.addEventListener('click', () => openDayModal(iso, hasMn ? menusPorFecha[iso] : null));
        }

        grid.appendChild(cell);
      }

      container.appendChild(grid);
    }

    /* ── Abrir modal para un día ── */
    function openDayModal(iso, menuData) {
      const [y, m, d]        = iso.split('-');
      modalTitle.textContent = `Menú del ${d}/${m}/${y}`;
      modalFechaDisp.value   = `${d}/${m}/${y}`;
      modalFechaIso.value    = iso;
      modalAlert.classList.add('d-none');

      if (menuData) {
        modalIdMenu.value      = menuData.id_menu || '';
        modalEstado.value      = menuData.estado  || 'activo';
        modalBadge.textContent = '✅ Menú existente';
        modalBadge.className   = 'badge fs-6 px-3 py-2 bg-success';
        modalDeleteBtn.classList.remove('d-none');

        const detalles = menuData.detalles || [];
        for (let orden = 1; orden <= 5; orden++) {
          const det = detalles.find(x => x.orden === orden);
          const sel = document.getElementById(`modal-plato-${orden}`);
          if (sel) sel.value = det ? det.id_plato : '';
        }

        const jornada = menuData.jornada || {};
        modalRacionesPlan.value = jornada.raciones_planificadas || 100;
        modalRacionesPrep.value = jornada.raciones_preparadas   || 0;
        modalRacionesDisp.value = jornada.raciones_disponibles  || 0;
      } else {
        modalIdMenu.value      = '';
        modalEstado.value      = 'activo';
        modalBadge.textContent = '🆕 Nuevo menú';
        modalBadge.className   = 'badge fs-6 px-3 py-2 bg-warning text-dark';
        modalDeleteBtn.classList.add('d-none');
        document.querySelectorAll('.modal-plato-select').forEach(s => s.value = '');
        modalRacionesPlan.value = 100;
        modalRacionesPrep.value = 0;
        modalRacionesDisp.value = 0;
      }

      modal.show();
    }

    function showAlert(type, msg) {
      modalAlert.className   = `alert alert-${type} mt-3`;
      modalAlert.textContent = msg;
      modalAlert.classList.remove('d-none');
    }

    /* ── Guardar menú ── */
    modalSaveBtn.addEventListener('click', async function () {
      const iso      = modalFechaIso.value;
      const idMenu   = modalIdMenu.value;
      const estado   = modalEstado.value;
      const detalles = [];

      document.querySelectorAll('.modal-plato-select').forEach(sel => {
        if (sel.value) {
          detalles.push({ orden: parseInt(sel.dataset.orden), id_plato: parseInt(sel.value) });
        }
      });

      const payload = {
        fecha:                iso,
        id_menu:              idMenu || null,
        estado,
        detalles,
        raciones_planificadas: parseInt(modalRacionesPlan.value) || 100,
        raciones_preparadas:   parseInt(modalRacionesPrep.value) || 0,
        raciones_disponibles:  parseInt(modalRacionesDisp.value) || 0,
      };

      try {
        const res  = await fetch('/jc/menu/guardar', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(payload),
        });
        const data = await res.json();

        if (data.success) {
          menusPorFecha[iso] = data.menu;
          showAlert('success', '✅ Menú guardado correctamente.');
          setTimeout(() => { modal.hide(); renderCalendar(currentYear, currentMonth); }, 800);
        } else {
          showAlert('danger', '❌ Error: ' + (data.error || 'No se pudo guardar'));
        }
      } catch (err) {
        showAlert('danger', '❌ Error de conexión.');
      }
    });

    /* ── Eliminar menú ── */
    modalDeleteBtn.addEventListener('click', async function () {
      if (!confirm('¿Eliminar el menú de este día?')) return;

      const idMenu = modalIdMenu.value;
      const iso    = modalFechaIso.value;

      try {
        const res  = await fetch('/jc/menu/eliminar', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ id_menu: idMenu }),
        });
        const data = await res.json();

        if (data.success) {
          delete menusPorFecha[iso];
          showAlert('success', '🗑 Menú eliminado.');
          setTimeout(() => { modal.hide(); renderCalendar(currentYear, currentMonth); }, 800);
        } else {
          showAlert('danger', '❌ Error: ' + (data.error || 'No se pudo eliminar'));
        }
      } catch {
        showAlert('danger', '❌ Error de conexión.');
      }
    });

    /* ── Navegación mes anterior / siguiente ── */
    document.getElementById('prevMonthBtn').addEventListener('click', () => {
      currentMonth--;
      if (currentMonth < 0) { currentMonth = 11; currentYear--; }
      renderCalendar(currentYear, currentMonth);
    });

    document.getElementById('nextMonthBtn').addEventListener('click', () => {
      currentMonth++;
      if (currentMonth > 11) { currentMonth = 0; currentYear++; }
      renderCalendar(currentYear, currentMonth);
    });

    /* ── Re-render al mostrar el pane ── */
    document.getElementById('content-planificacion')?.addEventListener('pane:shown', () => {
      renderCalendar(currentYear, currentMonth);
    });

    /* ── Arranque inicial ── */
    buildPlatoSelects();
    const now = new Date();
    renderCalendar(now.getFullYear(), now.getMonth());

  })();
});


/* =============================================================================
   MERMAS_JC.HTML — Calendario de mermas + modales de registro (ingrediente / plato)
   ============================================================================= */
document.addEventListener('DOMContentLoaded', function () {
  (function () {

    // Datos del servidor
    const mermasPorFecha = _parseBlob('mermas-por-fecha-jc-data', {});

    // Salida rápida si el pane no existe
    if (!document.getElementById('jc-mermas-calendar')) return;

    const modalIng  = new bootstrap.Modal(document.getElementById('mermaIngModal'));
    const modalPlat = new bootstrap.Modal(document.getElementById('mermaPlModal'));

    const miFecha    = document.getElementById('mi-fecha');
    const miLote     = document.getElementById('mi-lote');
    const miCantidad = document.getElementById('mi-cantidad');
    const miCosto    = document.getElementById('mi-costo');
    const miMotivo   = document.getElementById('mi-motivo');
    const miAlert    = document.getElementById('mi-alert');
    const miSaveBtn  = document.getElementById('mi-save-btn');

    const mpFecha    = document.getElementById('mp-fecha');
    const mpJornada  = document.getElementById('mp-jornada');
    const mpCantidad = document.getElementById('mp-cantidad');
    const mpCosto    = document.getElementById('mp-costo');
    const mpMotivo   = document.getElementById('mp-motivo');
    const mpAlert    = document.getElementById('mp-alert');
    const mpSaveBtn  = document.getElementById('mp-save-btn');

    const toggleBtn = document.getElementById('toggleMermasJCBtn');
    const rows      = Array.from(document.querySelectorAll('.merma-jc-row'));
    const shownEl   = document.getElementById('shownMermasJC');

    let expanded = false;

    /* ── Utilidades de fecha ── */
    function pad(n)     { return String(n).padStart(2, '0'); }
    function toIso(dt)  { return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`; }
    function weekdayEs(dt) {
      return ['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'][dt.getDay()];
    }

    /* ── Alertas dentro de modales ── */
    function showAlert(el, type, msg) {
      el.className   = `alert alert-${type} mt-3`;
      el.textContent = msg;
      el.classList.remove('d-none');
    }
    function clearAlert(el) {
      el.className   = 'alert mt-3 d-none';
      el.textContent = '';
    }

    /* ── Construir el calendario de mermas (últimos 30 días) ── */
    function buildCalendar() {
      const container = document.getElementById('jc-mermas-calendar');
      if (!container) return;

      container.innerHTML = '';

      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const days = [];
      for (let i = 29; i >= 0; i--) {
        const dt = new Date(today);
        dt.setDate(today.getDate() - i);
        dt.setHours(0, 0, 0, 0);
        days.push(dt);
      }

      const MONTHS_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                         'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
      const DAYS_ES   = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];

      // Agrupar días por mes
      const groups = [];
      let currentKey = null, currentGroup = null;

      days.forEach(dt => {
        const key = `${dt.getFullYear()}-${dt.getMonth()}`;
        if (key !== currentKey) {
          currentKey   = key;
          currentGroup = { year: dt.getFullYear(), month: dt.getMonth(), days: [] };
          groups.push(currentGroup);
        }
        currentGroup.days.push(dt);
      });

      groups.forEach(group => {
        const title       = document.createElement('h6');
        title.className   = 'fw-bold mb-2 mt-3';
        title.textContent = `${MONTHS_ES[group.month]} ${group.year}`;
        container.appendChild(title);

        const grid      = document.createElement('div');
        grid.className  = 'cal-mermas-grid';

        DAYS_ES.forEach(d => {
          const h       = document.createElement('div');
          h.className   = 'cal-m-header';
          h.textContent = d;
          grid.appendChild(h);
        });

        const firstDayWeekIndex = (new Date(group.year, group.month, 1).getDay() + 6) % 7;
        const firstVisibleDay   = group.days[0].getDate();
        const leadingBlanks     = Math.max(0, (firstDayWeekIndex + firstVisibleDay - 1) % 7);

        for (let i = 0; i < leadingBlanks; i++) {
          const blank   = document.createElement('div');
          blank.className = 'cal-m-day empty';
          grid.appendChild(blank);
        }

        group.days.forEach(dt => {
          const iso     = toIso(dt);
          const hasMr   = !!mermasPorFecha[iso];
          const isToday = dt.getTime() === today.getTime();

          const cell      = document.createElement('div');
          cell.className  = 'cal-m-day'
            + (hasMr   ? ' has-merma' : '')
            + (isToday ? ' is-today'  : '');

          const dayNum  = dt.getDate();
          const weekday = weekdayEs(dt);
          cell.innerHTML = `<div class="cal-m-num">${dayNum}</div><div class="cal-m-weekday">${weekday}</div>`;

          if (hasMr) {
            const cnt = mermasPorFecha[iso].count || '';
            cell.innerHTML += `<div class="cal-m-label">${cnt} merma${cnt !== 1 ? 's' : ''}</div><div class="cal-m-dot"></div>`;
          } else if (dt <= today) {
            cell.innerHTML += `<div class="cal-m-label" style="color:#adb5bd;">Sin merma</div>`;
          }

          cell.addEventListener('click', () => openDayMermaOptions(iso));
          grid.appendChild(cell);
        });

        container.appendChild(grid);
      });
    }

    /* ── Elegir tipo de merma al hacer clic en un día ── */
    function openDayMermaOptions(iso) {
      miFecha.value = iso;
      mpFecha.value = iso;

      const choice = window.confirm(
        `Día: ${iso}\n\n¿Registrar merma de INGREDIENTE?\nOK = Ingrediente\nCancelar = Platos`
      );

      if (choice) { clearAlert(miAlert); modalIng.show(); }
      else        { clearAlert(mpAlert); modalPlat.show(); }
    }

    /* ── API pública para abrir modal desde botones externos ── */
    window.openMermaModal = function (dia, tipo) {
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);

      const iso = dia === 'hoy' ? toIso(hoy) : dia;
      miFecha.value = iso;
      mpFecha.value = iso;

      if (tipo === 'ingrediente') { clearAlert(miAlert); modalIng.show(); }
      else                        { clearAlert(mpAlert); modalPlat.show(); }
    };

    /* ── Recalcular costo automáticamente al cambiar lote o cantidad ── */
    function recalcCost() {
      const selected  = miLote.options[miLote.selectedIndex];
      const costoUnit = parseFloat(selected?.dataset?.costo || 0) || 0;
      const qty       = parseFloat(miCantidad.value) || 0;
      if (costoUnit > 0 && qty > 0) miCosto.value = Math.round(costoUnit * qty);
    }

    miLote?.addEventListener('change', recalcCost);
    miCantidad?.addEventListener('input', recalcCost);

    /* ── Guardar merma de ingrediente ── */
    miSaveBtn?.addEventListener('click', async () => {
      const payload = {
        fecha:        miFecha.value,
        id_lote:      parseInt(miLote.value),
        cantidad:     parseFloat(miCantidad.value),
        costo_perdido: parseFloat(miCosto.value) || 0,
        motivo:       miMotivo.value,
      };

      if (!payload.fecha || !payload.id_lote || !payload.cantidad) {
        showAlert(miAlert, 'warning', '⚠️ Completa fecha, lote y cantidad.');
        return;
      }

      try {
        const res  = await fetch('/jc/merma/ingrediente/registrar', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(payload),
        });
        const data = await res.json();

        if (data.success) {
          mermasPorFecha[payload.fecha] = { count: (mermasPorFecha[payload.fecha]?.count || 0) + 1 };
          showAlert(miAlert, 'success', '✅ Merma de ingrediente registrada correctamente.');
          setTimeout(() => { modalIng.hide(); buildCalendar(); }, 700);
        } else {
          showAlert(miAlert, 'danger', '❌ ' + (data.error || 'No se pudo registrar'));
        }
      } catch (err) {
        showAlert(miAlert, 'danger', '❌ Error de conexión.');
      }
    });

    /* ── Guardar merma de platos ── */
    mpSaveBtn?.addEventListener('click', async () => {
      const payload = {
        fecha:             mpFecha.value,
        id_jornada:        parseInt(mpJornada.value) || null,
        cantidad_raciones: parseInt(mpCantidad.value) || 0,
        costo_perdido:     parseFloat(mpCosto.value) || 0,
        motivo:            mpMotivo.value,
      };

      if (!payload.fecha || !payload.cantidad_raciones) {
        showAlert(mpAlert, 'warning', '⚠️ Completa fecha y cantidad de raciones.');
        return;
      }

      try {
        const res  = await fetch('/jc/merma/plato/registrar', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify(payload),
        });
        const data = await res.json();

        if (data.success) {
          mermasPorFecha[payload.fecha] = { count: (mermasPorFecha[payload.fecha]?.count || 0) + 1 };
          showAlert(mpAlert, 'success', '✅ Merma de platos registrada correctamente.');
          setTimeout(() => { modalPlat.hide(); buildCalendar(); }, 700);
        } else {
          showAlert(mpAlert, 'danger', '❌ ' + (data.error || 'No se pudo registrar'));
        }
      } catch (err) {
        showAlert(mpAlert, 'danger', '❌ Error de conexión.');
      }
    });

    /* ── Toggle tabla de mermas recientes ── */
    toggleBtn?.addEventListener('click', () => {
      expanded              = !expanded;
      toggleBtn.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';

      let shown = 0;
      rows.forEach((row, index) => {
        const visible = expanded || index < 10;
        row.classList.toggle('d-none', !visible);
        if (visible) shown++;
      });
      if (shownEl) shownEl.textContent = shown;
    });

    /* ── Re-render al mostrar el pane ── */
    document.getElementById('content-mermas')?.addEventListener('pane:shown', () => {
      buildCalendar();
    });

    /* ── Arranque inicial ── */
    buildCalendar();

  })();
});