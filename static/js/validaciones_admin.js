/* =============================================================================
   validaciones_admin.js — KitchenMetrics
   Módulos: INVENTARIO · MERMAS · USUARIOS
   (RESERVAS fue movido a dashboard.js)
   ============================================================================= */


/* -----------------------------------------------------------------------------
   INVENTARIO — includes_dashboard/inventario.html
   Búsqueda por nombre/unidad, toggle expand
   ----------------------------------------------------------------------------- */
(function () {
  const searchInput  = document.getElementById('inventarioSearch');
  const clearBtn     = document.getElementById('clearInventarioSearch');
  const toggleBtn    = document.getElementById('toggleInventarioBtn');
  const rows         = Array.from(document.querySelectorAll('.ingrediente-row'));
  const shownCountEl = document.getElementById('shownInventarioCount');
  const totalCountEl = document.getElementById('totalInventarioCount');

  let expanded = false;

  function applyFilter() {
    const term = (searchInput.value || '').trim().toLowerCase();
    let shown  = 0;

    rows.forEach((row, index) => {
      const nombre  = row.dataset.nombre || '';
      const unidad  = row.dataset.unidad || '';
      const matchesSearch = !term || nombre.includes(term) || unidad.includes(term);
      const matchesExpand = expanded || index < 10;

      const visible = matchesSearch && matchesExpand;
      row.classList.toggle('d-none', !visible);
      if (visible) shown++;
    });

    if (shownCountEl) shownCountEl.textContent = shown;
    if (totalCountEl) totalCountEl.textContent = rows.length;
  }

  if (searchInput) searchInput.addEventListener('input', applyFilter);

  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      searchInput.value = '';
      expanded          = false;
      if (toggleBtn) toggleBtn.textContent = 'Mostrar más';
      applyFilter();
    });
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      expanded              = !expanded;
      toggleBtn.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';
      applyFilter();
    });
  }

  applyFilter();
})();


/* -----------------------------------------------------------------------------
   MERMAS — includes_dashboard/mermas.html
   Inicialización de gráficas (Chart.js), lazy loading con pane:shown,
   toggle expand de tabla de mermas recientes
   ----------------------------------------------------------------------------- */
(function () {
  var chartsInitialized = false;

  function initMermaCharts() {
    if (chartsInitialized) return;
    chartsInitialized = true;

    var dailyData  = JSON.parse(document.getElementById('waste-daily-data').textContent  || '[]');
    var motiveData = JSON.parse(document.getElementById('waste-motive-data').textContent || '[]');

    var dailyCanvas  = document.getElementById('chart-merma-diaria');
    var motiveCanvas = document.getElementById('chart-merma-motivo');

    if (dailyCanvas && window.Chart) {
      new Chart(dailyCanvas, {
        type: 'line',
        data: {
          labels:   dailyData.map(function (x) { return x.label; }),
          datasets: [{
            label:           '% Desperdicio diario',
            data:            dailyData.map(function (x) { return x.porcentaje_merma; }),
            borderColor:     '#df3320',
            backgroundColor: 'rgba(223,51,32,0.07)',
            borderWidth:     2,
            pointRadius:     4,
            pointBackgroundColor: '#df3320',
            fill:    true,
            tension: 0.35,
          }],
        },
        options: {
          responsive:          true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
          scales:  { y: { beginAtZero: true } },
        },
      });
    }

    if (motiveCanvas && window.Chart) {
      new Chart(motiveCanvas, {
        type: 'bar',
        data: {
          labels:   motiveData.map(function (x) { return x.motivo; }),
          datasets: [{
            label:           'Costo perdido ($)',
            data:            motiveData.map(function (x) { return x.costo; }),
            backgroundColor: ['#df3320', '#e67e22', '#f1c40f', '#3498db', '#9b59b6'],
            borderRadius:    6,
          }],
        },
        options: {
          responsive:          true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } },
          scales:  { y: { beginAtZero: true } },
        },
      });
    }
  }

  // Carga diferida al mostrar el pane; si no hay pane, inicializa directo
  var pane = document.getElementById('content-mermas');
  if (pane) {
    pane.addEventListener('pane:shown', initMermaCharts, { once: true });
  } else {
    setTimeout(initMermaCharts, 500);
  }

  // Toggle tabla de mermas recientes
  var toggleBtn  = document.getElementById('toggleMermasBtn');
  var rows       = Array.from(document.querySelectorAll('.merma-row'));
  var shownCount = document.getElementById('shownMermasCount');
  var expanded   = false;

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      expanded              = !expanded;
      toggleBtn.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';
      var shown = 0;
      rows.forEach(function (row, index) {
        var visible = expanded || index < 10;
        row.classList.toggle('d-none', !visible);
        if (visible) shown++;
      });
      if (shownCount) shownCount.textContent = shown;
    });
  }
})();


/* -----------------------------------------------------------------------------
   USUARIOS — includes_dashboard/usuarios.html
   Búsqueda, toggle expand, poblar modales de edición y eliminación,
   navegación entre sub-secciones dinámicas
   ----------------------------------------------------------------------------- */
(function () {
  const searchInput  = document.getElementById('usuariosSearch');
  const clearBtn     = document.getElementById('clearUsuariosSearch');
  const toggleBtn    = document.getElementById('toggleUsuariosBtn');
  const rows         = Array.from(document.querySelectorAll('.usuario-row'));
  const shownCountEl = document.getElementById('shownUsersCount');
  const totalCountEl = document.getElementById('totalUsersCount');

  const editForm       = document.getElementById('editUserForm');
  const editRol        = document.getElementById('edit_id_rol');
  const editRut        = document.getElementById('edit_rut');
  const editNombre     = document.getElementById('edit_nombre');
  const editApellido   = document.getElementById('edit_apellido');
  const editEmail      = document.getElementById('edit_email');
  const editContrasena = document.getElementById('edit_contrasena');
  const editFaltas     = document.getElementById('edit_faltas');
  const editEstado     = document.getElementById('edit_estado');

  const dynamicBtns     = Array.from(document.querySelectorAll('.user-view-btn'));
  const dynamicSections = Array.from(document.querySelectorAll('.user-dynamic-section'));

  const deleteForm = document.getElementById('deleteUserForm');
  const deleteName = document.getElementById('deleteUserName');

  let expanded = false;

  function applyFilter() {
    const term = (searchInput.value || '').trim().toLowerCase();
    let shown  = 0;

    rows.forEach((row, index) => {
      const name  = row.dataset.name  || '';
      const rut   = row.dataset.rut   || '';
      const email = row.dataset.email || '';

      const matchesSearch = !term || name.includes(term) || rut.includes(term) || email.includes(term);
      const matchesExpand = expanded || index < 10;

      const visible = matchesSearch && matchesExpand;
      row.classList.toggle('d-none', !visible);
      if (visible) shown++;
    });

    if (shownCountEl) shownCountEl.textContent = shown;
    if (totalCountEl) totalCountEl.textContent = rows.length;
  }

  if (searchInput) searchInput.addEventListener('input', applyFilter);

  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      searchInput.value = '';
      expanded          = false;
      if (toggleBtn) toggleBtn.textContent = 'Mostrar más';
      applyFilter();
    });
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      expanded              = !expanded;
      toggleBtn.textContent = expanded ? 'Mostrar menos' : 'Mostrar más';
      applyFilter();
    });
  }

  // Poblar modal de edición
  document.querySelectorAll('.edit-user-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      editForm.action       = `/admin/usuario/editar/${id}`;
      editRol.value         = btn.dataset.rol      || '';
      editRut.value         = btn.dataset.rut      || '';
      editNombre.value      = btn.dataset.nombre   || '';
      editApellido.value    = btn.dataset.apellido || '';
      editEmail.value       = btn.dataset.email    || '';
      editContrasena.value  = '';
      editFaltas.value      = btn.dataset.faltas   || 0;
      editEstado.value      = btn.dataset.estado   || 'activo';
    });
  });

  // Poblar modal de eliminación
  document.querySelectorAll('.delete-user-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id     = btn.dataset.id;
      const nombre = btn.dataset.nombre || '';
      if (deleteForm) deleteForm.action      = `/admin/usuario/eliminar/${id}`;
      if (deleteName) deleteName.textContent = nombre;
    });
  });

  // Navegación entre sub-secciones dinámicas
  function showSection(sectionName) {
    dynamicSections.forEach((section) => {
      section.classList.toggle('d-none', section.dataset.section !== sectionName);
    });
    dynamicBtns.forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.view === sectionName);
    });
  }

  dynamicBtns.forEach((btn) => {
    btn.addEventListener('click', () => showSection(btn.dataset.view));
  });

  showSection('resumen');
  applyFilter();
})();