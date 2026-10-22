/* Agente Virtual de QA · interfaz del MVP
   Una sola conversación: tus pedidos, lo que hace el agente, sus entregables y las decisiones
   que te pide, todo en el mismo hilo. Sin estado propio: todo sale de /api/estado (los archivos
   de qa/ y tests/) y de /api/eventos (la actividad del agente en vivo). */

(function () {
  'use strict';

  // ------------------------------------------------------------ utilidades
  const $ = (sel, raiz = document) => raiz.querySelector(sel);
  const $$ = (sel, raiz = document) => [...raiz.querySelectorAll(sel)];
  const el = (etiqueta, atributos = {}, ...hijos) => {
    const nodo = document.createElement(etiqueta);
    for (const [k, v] of Object.entries(atributos)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === 'class') nodo.className = v;
      else if (k === 'html') nodo.innerHTML = v;
      else if (k.startsWith('on')) nodo.addEventListener(k.slice(2), v);
      else nodo.setAttribute(k, v === true ? '' : v);
    }
    for (const h of hijos.flat()) {
      if (h === null || h === undefined || h === false) continue;
      nodo.append(h instanceof Node ? h : document.createTextNode(String(h)));
    }
    return nodo;
  };
  const escapar = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const md = (texto) => (window.marked ? window.marked.parse(texto || '', { gfm: true, breaks: false }) : `<pre>${escapar(texto)}</pre>`);
  const SVG = (cuerpo) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${cuerpo}</svg>`;
  const ICONO = {
    check: SVG('<path d="M5 12.5l4.5 4.5L19 7"/>'),
    cruz: SVG('<path d="M6 6l12 12M18 6L6 18"/>'),
    rombo: SVG('<path d="M12 3l9 9-9 9-9-9z"/>'),
    reloj: SVG('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    archivo: SVG('<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>'),
    alerta: SVG('<path d="M12 3l10 18H2z"/><path d="M12 10v4M12 17h.01"/>'),
    flecha: SVG('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    play: SVG('<path d="M7 5v14l11-7z"/>'),
    sol: SVG('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
    luna: SVG('<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>'),
    auto: SVG('<circle cx="12" cy="12" r="9"/><path d="M12 3v18M12 3a9 9 0 0 1 0 18" fill="currentColor" stroke="none"/>'),
    historia: SVG('<path d="M4 5h16v12H9l-5 4z"/><path d="M8 9h8M8 12h5"/>'),
    explorar: SVG('<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>'),
    plan: SVG('<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>'),
    ejecutar: SVG('<circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l6-3.5z"/>'),
    analizar: SVG('<circle cx="11" cy="11" r="6"/><path d="M15.5 15.5L20 20M8.5 11h5M11 8.5v5"/>'),
    reportar: SVG('<path d="M5 21V4"/><path d="M5 5h12l-2.5 3.5L17 12H5"/>'),
    chispa: SVG('<path d="M12 3c.6 4.2 3.8 7.4 9 9-5.2 1.6-8.4 4.8-9 9-.6-4.2-3.8-7.4-9-9 5.2-1.6 8.4-4.8 9-9z" fill="currentColor" stroke="none"/>'),
  };
  const icono = (nombre, clase = '') => el('span', { class: clase, html: ICONO[nombre] || '' });
  const formatoSegundos = (s) => { s = Math.max(0, Math.round(s)); const m = Math.floor(s / 60); return `${m}:${String(s % 60).padStart(2, '0')}`; };
  const normalizar = (t) => (t || '').replace(/\s+/g, ' ').trim();

  const api = {
    async llamar(metodo, ruta, cuerpo) {
      const r = await fetch(ruta, {
        method: metodo,
        headers: cuerpo !== undefined ? { 'Content-Type': 'application/json' } : {},
        body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
      });
      const datos = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(datos.detail || `Error ${r.status}`);
      return datos;
    },
    get: (ruta) => api.llamar('GET', ruta),
    post: (ruta, cuerpo = {}) => api.llamar('POST', ruta, cuerpo),
    put: (ruta, cuerpo) => api.llamar('PUT', ruta, cuerpo),
    del: (ruta) => api.llamar('DELETE', ruta),
  };

  // ------------------------------------------------------------ estado de la interfaz
  const ui = {
    estado: null,
    docs: {},                // caché de documentos: nombre -> {markdown, existe, ruta}
    cargandoDocs: new Set(),
    excluidos: new Set(),    // casos desmarcados antes de aprobar
    editandoPlan: false,
    abiertos: new Set(),     // secciones plegables que la persona abrió (sobreviven al repintado)
    ultimoEvento: 0,
    turnoActual: null,
    ultimoTexto: '',
    presentacionPedida: null, // modo para el que ya se pidió la presentación en esta carga
  };

  const PASOS_UI = {
    'explorar-app': { icono: 'explorar', verbo: 'Explorar la aplicación' },
    'disenar-plan': { icono: 'plan', verbo: 'Diseñar el plan' },
    'ejecutar-pruebas': { icono: 'ejecutar', verbo: 'Ejecutar las pruebas' },
    'analizar-fallos': { icono: 'analizar', verbo: 'Analizar los fallos' },
    'reportar': { icono: 'reportar', verbo: 'Generar el reporte' },
  };
  const pasoPorId = (id) => (ui.estado ? ui.estado.pasos.find((p) => p.id === id) : null) || null;
  const nombrePaso = (id) => (pasoPorId(id) || {}).nombre || id || '';
  const numeroPaso = (id) => (pasoPorId(id) || {}).numero || '';

  // ------------------------------------------------------------ carga de datos
  async function cargarEstado() {
    try {
      const estado = await api.get('/api/estado');
      const anterior = ui.estado;
      ui.estado = estado;
      if (!anterior || JSON.stringify(huella(anterior)) !== JSON.stringify(huella(estado))) ui.docs = {};
      pintarTodo();
    } catch (e) {
      aviso(`No se pudo leer el estado del ciclo: ${e.message}`, true);
    }
  }
  const huella = (e) => [e.exploracion.modificado, e.historia.modificado, e.plan.modificado, e.plan.aprobado, e.resultados.modificado,
    e.defectos.lista.map((d) => d.id + d.estado), e.reporte.modificado, e.pruebas.map((p) => p.nombre), e.agente.ocupado];

  async function documento(nombre) {
    if (ui.docs[nombre]) return ui.docs[nombre];
    if (ui.cargandoDocs.has(nombre)) return null;
    ui.cargandoDocs.add(nombre);
    try {
      ui.docs[nombre] = await api.get(`/api/documento/${nombre}`);
      pintarEntregables();
    } finally {
      ui.cargandoDocs.delete(nombre);
    }
    return ui.docs[nombre];
  }

  // ------------------------------------------------------------ pintado general
  function pintarTodo() {
    pintarCabecera();
    pintarProgreso();
    pintarPresentacion();
    pintarEntregables();
    pintarSiguiente();
    pintarRedactor();
  }

  function pintarCabecera() {
    const e = ui.estado;
    const modo = $('#modo');
    modo.textContent = e.modo === 'demo' ? 'Modo demo' : 'Agente real';
    modo.title = e.modo === 'demo' ? 'Ciclo de ejemplo: sin llamadas a la API ni navegador. Para el agente real: python3 -m app' : 'Claude Agent SDK sobre este repositorio';
    modo.className = `modo ${e.modo}`;
    $('#app-nombre').textContent = e.aplicacion.nombre;
    $('#app-url').textContent = e.aplicacion.url;
  }

  function pintarProgreso() {
    const e = ui.estado;
    const nodos = [];
    e.pasos.forEach((p) => {
      const estadoIcono = p.estado === 'hecho' ? ICONO.check : p.estado === 'decision' ? ICONO.rombo : '';
      nodos.push(el('button', { class: `progreso-paso ${p.estado}`, type: 'button', title: `${p.numero}. ${p.nombre}: ${textoEstadoPaso(p)}`, onclick: () => irAlEntregable(p.id) },
        el('div', { class: 'barra' }), el('span', {}, el('span', { html: estadoIcono }), `${p.numero}. ${p.nombre}`)));
      if (p.decision) {
        const lista = p.id === 'disenar-plan' ? (e.plan.existe && e.plan.aprobado) : (e.defectos.existe && e.defectos.pendientes === 0);
        const texto = p.id === 'disenar-plan' ? 'Tu aprobación' : 'Tu confirmación';
        nodos.push(el('div', { class: `progreso-compuerta ${lista ? 'lista' : p.estado === 'decision' ? 'pendiente' : ''}`, title: `Decisión de la persona: ${texto}` },
          el('span', { class: 'rombo', 'aria-hidden': 'true' }), el('span', {}, texto)));
      }
    });
    $('#progreso').replaceChildren(...nodos);
  }
  const textoEstadoPaso = (p) => ({ pendiente: p.disponible ? 'listo para correr' : 'pendiente', en_curso: 'trabajando', hecho: 'hecho', decision: 'esperando tu decisión' }[p.estado]);

  // ------------------------------------------------------------ piezas reutilizables
  const metrica = (valor, texto, clase = '') => el('div', { class: `metrica ${clase}` }, el('b', {}, valor), el('span', {}, texto));
  const recibo = (items) => el('div', { class: 'recibo' }, ...items.filter(Boolean).map(([ruta, detalle]) =>
    el('span', { class: 'recibo-item' }, icono('archivo'), el('code', {}, ruta), detalle ? el('span', {}, detalle) : null)));
  const chipPrioridad = (p) => el('span', { class: `chip chip-${(p || '').toLowerCase().replace('í', 'i')}` }, p || '—');
  const chipResultado = (r) => !r ? el('span', { class: 'meta' }, '—')
    : el('span', { class: `chip ${r === 'PASÓ' ? 'chip-ok' : r === 'FALLÓ' ? 'chip-fallo' : 'chip-bloqueado'}` },
      el('span', { html: r === 'PASÓ' ? ICONO.check : r === 'FALLÓ' ? ICONO.cruz : ICONO.reloj }), r);
  const descargar = (nombre, texto = 'Descargar .md') => el('a', { class: 'boton boton-chico', href: `/api/documento/${nombre}/descargar`, download: true }, texto);
  const botonPaso = (id, texto, clase = 'boton boton-primario', argumentos = () => '') => {
    const p = pasoPorId(id); const e = ui.estado;
    return el('button', { class: clase, type: 'button', disabled: !p || !p.disponible || e.agente.ocupado, title: p && !p.disponible ? motivoBloqueo(p) : null, onclick: () => correrPaso(id, argumentos()) }, texto);
  };
  function motivoBloqueo(paso) {
    const e = ui.estado;
    return { 'disenar-plan': 'Primero explora la aplicación (paso 1).',
      'ejecutar-pruebas': e.plan.existe ? 'Aprueba el plan (paso 2) para poder ejecutar.' : 'Primero diseña y aprueba el plan (paso 2).',
      'analizar-fallos': 'Primero ejecuta las pruebas (paso 3).',
      'reportar': e.defectos.existe ? `Faltan ${e.defectos.pendientes} defecto(s) por decidir (paso 4).` : 'Primero analiza los fallos (paso 4).' }[paso.id] || null;
  }
  // Sección plegable que recuerda si la persona la abrió
  function plegable(clave, titulo, cuerpo, meta = null) {
    const d = el('details', { class: 'plegable', open: ui.abiertos.has(clave) },
      el('summary', {}, titulo, meta ? el('span', { class: 'meta' }, meta) : null),
      el('div', { class: 'plegable-cuerpo' }, cuerpo));
    d.addEventListener('toggle', () => { if (d.open) ui.abiertos.add(clave); else ui.abiertos.delete(clave); });
    return d;
  }
  function cuerpoDocumento(nombre) {
    const doc = ui.docs[nombre];
    if (!doc) { documento(nombre); return el('p', { class: 'meta' }, 'Cargando…'); }
    return el('div', { class: 'documento documento-ancho', html: md(doc.markdown) });
  }
  const tarjeta = (clase, cabecera, ...cuerpo) => el('section', { class: `tarjeta ${clase}` }, cabecera, ...cuerpo);
  const cabecera = (iconoNombre, titulo, meta = [], acciones = []) => el('div', { class: 'tarjeta-cabecera' },
    el('div', {}, el('h2', {}, icono(iconoNombre), titulo), meta.length ? el('div', { class: 'meta', style: 'margin-top:3px' }, ...meta) : null),
    acciones.length ? el('div', { class: 'tarjeta-acciones' }, ...acciones.filter(Boolean)) : null);

  // ------------------------------------------------------------ entregables dentro del hilo
  // Cada entregable se deriva del estado y se coloca después del turno del agente que lo produjo.
  function pintarEntregables() {
    const e = ui.estado;
    if (!e) return;
    colocar('entregable-exploracion', 'explorar-app', e.exploracion.existe ? tarjetaExploracion() : null);
    colocar('entregable-historia', 'explorar-app', e.historia.existe ? tarjetaHistoria() : null);
    colocar('entregable-plan', 'disenar-plan', e.plan.existe ? tarjetaPlan() : null);
    colocar('entregable-resultados', 'ejecutar-pruebas', e.resultados.existe ? tarjetaResultados() : null);
    colocar('entregable-defectos', 'analizar-fallos', e.defectos.existe ? tarjetaDefectos() : null);
    colocar('entregable-reporte', 'reportar', e.reporte.existe ? tarjetaReporte() : null);
  }
  const ORDEN = ['entregable-exploracion', 'entregable-historia', 'entregable-plan', 'entregable-resultados', 'entregable-defectos', 'entregable-reporte'];
  function colocar(id, pasoOrigen, nodo) {
    const hilo = $('#hilo');
    const previo = $(`#${id}`);
    if (previo) previo.remove();
    if (!nodo) return;
    const li = el('li', { class: 'entregable', id }, nodo);
    const turnos = $$(`.turno.agente[data-paso="${pasoOrigen}"]`, hilo);
    let ancla = turnos[turnos.length - 1];
    // Varios entregables tras el mismo turno (exploración e historia) conservan el orden.
    const vecinos = ORDEN.slice(0, ORDEN.indexOf(id)).map((x) => $(`#${x}`)).filter(Boolean);
    for (const v of vecinos) if (ancla ? v.compareDocumentPosition(ancla) & Node.DOCUMENT_POSITION_PRECEDING : true) ancla = v;
    if (ancla) ancla.after(li);
    else { const b = $('#presentacion-hilo'); if (b) b.after(li); else hilo.prepend(li); }
  }
  function irAlEntregable(paso) {
    const id = { 'explorar-app': 'entregable-exploracion', 'disenar-plan': 'entregable-plan', 'ejecutar-pruebas': 'entregable-resultados', 'analizar-fallos': 'entregable-defectos', 'reportar': 'entregable-reporte' }[paso];
    const nodo = $(`#${id}`) || $('#siguiente');
    if (nodo) nodo.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ---- Exploración
  function tarjetaExploracion() {
    const e = ui.estado;
    return tarjeta('', cabecera('explorar', 'Exploración de la aplicación', [`qa/exploracion.md · ${e.exploracion.modificado}`],
      [descargar('exploracion'), botonPaso('explorar-app', 'Explorar de nuevo', 'boton boton-chico', () => e.aplicacion.url)]),
      el('div', { class: 'tarjeta-cuerpo' }, el('p', { class: 'decision-texto' }, 'El mapa de pantallas, los elementos con su localizador y los flujos observados. El plan y las pruebas se escriben a partir de esto.')),
      plegable('exploracion', 'Ver la exploración completa', cuerpoDocumento('exploracion')));
  }

  // ---- Historia de usuario
  function tarjetaHistoria() {
    const e = ui.estado;
    const doc = ui.docs.historia;
    if (!doc) documento('historia');
    const criterios = doc ? doc.markdown.split('\n').filter((l) => /^\s*[-*]\s+\S/.test(l)).map((l) => l.trim().slice(1).trim()) : [];
    const texto = doc ? doc.markdown.replace(/^#.*$/m, '').split(/## Criterios/)[0].trim() : '';
    return tarjeta('', cabecera('historia', `Historia de usuario: ${e.historia.titulo}`, [`${e.historia.criterios} criterio(s) de aceptación · qa/historia-de-usuario.md`],
      [el('button', { class: 'boton boton-chico', type: 'button', onclick: () => abrirHistoria(doc) }, 'Editar'),
        el('button', { class: 'boton boton-chico', type: 'button', disabled: e.plan.existe, title: e.plan.existe ? 'El plan ya partió de esta historia' : null, onclick: () => quitarHistoria() }, 'Quitar')]),
      el('div', { class: 'tarjeta-cuerpo' },
        texto ? el('p', { class: 'decision-texto' }, texto) : null,
        criterios.length ? el('ol', { class: 'historia-criterios' }, ...criterios.map((c) => el('li', {}, c))) : null,
        el('p', { class: 'meta', style: 'margin-top:8px' }, e.plan.existe ? 'El plan de abajo partió de esta historia.' : 'El plan partirá de esta historia: al menos un caso por criterio.')));
  }

  // ---- Plan (con la primera decisión humana)
  function tarjetaPlan() {
    const e = ui.estado;
    const casos = e.casos;
    const aprobado = e.plan.aprobado;
    const incluidos = casos.filter((c) => !ui.excluidos.has(c.id));
    const comp = e.plan.comparacion;
    const porPrioridad = Object.entries(e.plan.por_prioridad || {}).map(([p, n]) => `${n} ${p}`).join(', ');
    const meta = [el('span', { class: `chip ${aprobado ? 'chip-ok' : 'chip-pendiente'}` }, el('span', { html: aprobado ? ICONO.check : ICONO.rombo }), aprobado ? 'Aprobado' : 'Pendiente de tu aprobación'),
      ` ${casos.length} casos (${porPrioridad}) · qa/plan-de-pruebas.md`];
    const acciones = [descargar('plan')];
    if (!aprobado && !ui.editandoPlan) acciones.push(el('button', { class: 'boton boton-chico', type: 'button', onclick: () => { ui.editandoPlan = true; documento('plan'); pintarEntregables(); } }, 'Editar texto'));
    if (aprobado) acciones.push(el('button', { class: 'boton boton-chico', type: 'button', disabled: e.agente.ocupado, onclick: () => desaprobarPlan() }, 'Volver a abrir'));
    acciones.push(botonPaso('disenar-plan', 'Diseñar de nuevo', 'boton boton-chico'));

    let cuerpo;
    if (ui.editandoPlan && !aprobado) {
      const doc = ui.docs.plan;
      if (!doc) cuerpo = el('div', { class: 'tarjeta-cuerpo' }, el('p', { class: 'meta' }, 'Cargando…'));
      else {
        const editor = el('textarea', { class: 'editor', spellcheck: 'false', 'aria-label': 'Texto del plan' });
        editor.value = doc.markdown;
        cuerpo = el('div', { class: 'tarjeta-cuerpo' },
          el('p', { class: 'meta', style: 'margin-bottom:8px' }, 'Edita el plan en markdown. La tabla de casos conserva sus siete columnas; la copia generada por el agente no cambia, así se mide cuánto aceptaste sin editar.'),
          editor,
          el('div', { class: 'tarjeta-acciones', style: 'margin-top:10px' },
            el('button', { class: 'boton boton-primario', type: 'button', onclick: () => guardarPlan(editor.value) }, 'Guardar cambios'),
            el('button', { class: 'boton', type: 'button', onclick: () => { ui.editandoPlan = false; pintarEntregables(); } }, 'Cancelar')));
      }
    } else {
      cuerpo = el('div', { class: 'tarjeta-cuerpo sin-relleno' }, el('div', { class: 'tabla-marco' }, tablaCasos(casos, !aprobado)));
    }

    const decision = aprobado
      ? el('div', { class: 'decision-fila' }, icono('check'),
        el('span', { class: 'decision-texto' }, `Aprobaste ${casos.length} casos${comp ? `: ${comp.aceptados.length} sin cambios, ${comp.editados.length} editados, ${comp.rechazados.length} quitados, ${comp.anadidos.length} añadidos (${comp.porcentaje_aceptados}% aceptados sin edición, la métrica del hito 1)` : ''}.`))
      : el('div', { class: 'decision-fila' },
        el('button', { class: 'boton boton-primario boton-grande', type: 'button', disabled: e.agente.ocupado || incluidos.length === 0, onclick: () => aprobarPlan() }, icono('check'), `Aprobar el plan (${incluidos.length} ${incluidos.length === 1 ? 'caso' : 'casos'})`),
        el('span', { class: 'decision-texto' }, 'Desmarca los casos que no apliquen o edita el texto antes de aprobar. Nada se ejecuta sin tu aprobación, y podrás volver a abrir el plan.'));

    return tarjeta(aprobado ? 'resuelta' : 'decision',
      cabecera(aprobado ? 'check' : 'rombo', aprobado ? 'Plan de pruebas aprobado' : 'Plan de pruebas: necesita tu aprobación', meta, acciones),
      cuerpo, decision,
      plegable('plan-doc', 'Ver el plan como documento', cuerpoDocumento('plan')));
  }

  function tablaCasos(casos, seleccionable) {
    const resultados = Object.fromEntries((ui.estado.resultados.filas || []).map((f) => [f.id, f.resultado]));
    const conResultado = ui.estado.resultados.existe;
    return el('table', { class: 'casos' },
      el('thead', {}, el('tr', {},
        seleccionable ? el('th', { scope: 'col' }, 'Incluir') : null,
        el('th', { scope: 'col' }, 'ID'), el('th', { scope: 'col' }, 'Título'), el('th', { scope: 'col' }, 'Prioridad'), el('th', { scope: 'col' }, 'Usuario'),
        el('th', { scope: 'col' }, 'Pasos'), el('th', { scope: 'col' }, 'Resultado esperado'),
        conResultado ? el('th', { scope: 'col' }, 'Resultado') : null)),
      el('tbody', {}, ...casos.map((c) => {
        const excluido = ui.excluidos.has(c.id);
        return el('tr', { class: excluido ? 'excluido' : '' },
          seleccionable ? el('td', { class: 'sel' }, el('input', {
            type: 'checkbox', checked: !excluido, 'aria-label': `Incluir ${c.id}`,
            onchange: (ev) => { if (ev.target.checked) ui.excluidos.delete(c.id); else ui.excluidos.add(c.id); pintarEntregables(); pintarSiguiente(); },
          })) : null,
          el('td', { class: 'id' }, el('span', {}, c.id)),
          el('td', {}, c.titulo),
          el('td', {}, chipPrioridad(c.prioridad)),
          el('td', { class: 'mono' }, c.usuario),
          el('td', { class: 'pasos-celda' }, c.pasos.replace(/\s+(\d+\.)/g, '\n$1')),
          el('td', {}, c.resultado),
          conResultado ? el('td', {}, chipResultado(resultados[c.id])) : null);
      })));
  }

  // ---- Resultados
  function tarjetaResultados() {
    const e = ui.estado; const r = e.resultados;
    const pruebas = el('div', { class: 'pruebas' }, el('p', { class: 'meta' }, 'Cargando…'));
    api.get('/api/pruebas').then(({ pruebas: lista }) => {
      pruebas.replaceChildren(...lista.map((p) => el('details', {}, el('summary', {}, p.archivo, el('span', { class: 'meta' }, p.casos.join(' '))), el('pre', {}, p.contenido))));
    }).catch(() => pruebas.replaceChildren(el('p', { class: 'meta' }, 'No se pudieron cargar las pruebas.')));
    return tarjeta('', cabecera('ejecutar', 'Resultados de la ejecución', [`${r.pasaron} de ${r.ejecutados} casos pasaron · qa/resultados.md · ${r.modificado}`],
      [r.reporte_html ? el('a', { class: 'boton boton-chico', href: '/reporte-html/index.html', target: '_blank', rel: 'noopener' }, 'Reporte HTML de Playwright') : null,
        descargar('resultados'), botonPaso('ejecutar-pruebas', 'Ejecutar de nuevo', 'boton boton-chico')]),
      el('div', { class: 'tarjeta-cuerpo' },
        el('div', { class: 'metricas' }, metrica(r.ejecutados, 'casos ejecutados'), metrica(r.pasaron, 'pasaron', 'ok'), metrica(r.fallaron, 'fallaron', 'fallo'), metrica(r.bloqueados, 'bloqueados', 'bloq')),
        el('div', { style: 'margin-top:12px' }, recibo([[`tests/ (${e.pruebas.length} archivos)`, 'corren sin el agente: npx playwright test'], e.evidencias.length ? [`qa/evidencia/`, `${e.evidencias.length} captura(s) de los fallos`] : null]))),
      plegable('resultados-doc', 'Ver los resultados completos (salida de Playwright)', cuerpoDocumento('resultados')),
      plegable('pruebas', 'Ver las pruebas generadas', pruebas, `${e.pruebas.length} archivos`));
  }

  // ---- Defectos (con la segunda decisión humana)
  function tarjetaDefectos() {
    const e = ui.estado; const d = e.defectos;
    if (d.sin_defectos) {
      return tarjeta('resuelta', cabecera('check', 'Sin defectos en este ciclo', ['Todas las pruebas ejecutadas pasaron.'], [botonPaso('analizar-fallos', 'Analizar de nuevo', 'boton boton-chico')]));
    }
    const resuelta = d.pendientes === 0;
    const meta = [el('span', { class: `chip ${resuelta ? 'chip-ok' : 'chip-pendiente'}` }, el('span', { html: resuelta ? ICONO.check : ICONO.rombo }), resuelta ? 'Todos decididos' : `${d.pendientes} por decidir`),
      ` ${d.confirmados} confirmado(s), ${d.descartados} descartado(s). Solo los confirmados cuentan para el semáforo.`];
    return tarjeta(resuelta ? 'resuelta' : 'decision',
      cabecera(resuelta ? 'check' : 'rombo', resuelta ? 'Defectos decididos' : `Defectos: necesita tu confirmación`, meta, [botonPaso('analizar-fallos', 'Analizar de nuevo', 'boton boton-chico')]),
      ...d.lista.map(tarjetaDefecto));
  }

  function tarjetaDefecto(def) {
    const e = ui.estado;
    const pendiente = def.estado === 'PENDIENTE DE CONFIRMACIÓN';
    const claseEstado = { CONFIRMADO: 'chip-confirmado', DESCARTADO: 'chip-descartado' }[def.estado] || 'chip-pendiente';
    const iconoEstado = { CONFIRMADO: ICONO.check, DESCARTADO: ICONO.cruz }[def.estado] || ICONO.rombo;
    const acciones = pendiente
      ? [el('button', { class: 'boton boton-primario', type: 'button', disabled: e.agente.ocupado, onclick: () => decidirDefecto(def, 'CONFIRMADO') }, 'Confirmar defecto'),
        el('button', { class: 'boton', type: 'button', disabled: e.agente.ocupado, onclick: () => decidirDefecto(def, 'DESCARTADO') }, 'Descartar'),
        el('span', { class: 'meta' }, 'Reversible')]
      : [el('button', { class: 'boton boton-chico', type: 'button', disabled: e.agente.ocupado, onclick: () => decidirDefecto(def, 'PENDIENTE DE CONFIRMACIÓN', '', true) }, 'Deshacer la decisión')];
    const detalle = el('details', { open: ui.abiertos.has(`def-${def.id}`) }, el('summary', {}, 'Ver el defecto completo (pasos para reproducir)'), el('div', { class: 'documento' }));
    detalle.addEventListener('toggle', () => {
      if (detalle.open) ui.abiertos.add(`def-${def.id}`); else ui.abiertos.delete(`def-${def.id}`);
      if (detalle.open && !detalle.dataset.cargado) {
        api.get(`/api/defectos/${def.id}`).then((x) => { detalle.querySelector('.documento').innerHTML = md(x.markdown); detalle.dataset.cargado = '1'; })
          .catch(() => { detalle.querySelector('.documento').textContent = 'No se pudo cargar el defecto.'; });
      }
    });
    if (detalle.open) detalle.dispatchEvent(new Event('toggle'));
    return el('div', { class: 'defecto', id: `defecto-${def.id}` },
      el('div', { class: 'defecto-cuerpo' },
        el('h3', {}, el('span', { class: 'mono' }, def.id), def.titulo),
        el('div', { class: 'defecto-chips' },
          el('span', { class: `chip chip-${def.severidad.toLowerCase().replace('í', 'i')}` }, el('span', { html: ICONO.alerta }), `Severidad ${def.severidad}`),
          el('span', { class: `chip ${claseEstado}` }, el('span', { html: iconoEstado }), def.estado.charAt(0) + def.estado.slice(1).toLowerCase()),
          def.casos ? el('span', { class: 'chip mono' }, def.casos) : null),
        el('dl', { class: 'defecto-campos' },
          def.resultado_esperado ? [el('dt', {}, 'Esperado'), el('dd', {}, def.resultado_esperado)] : null,
          def.resultado_obtenido ? [el('dt', {}, 'Obtenido'), el('dd', {}, def.resultado_obtenido)] : null,
          def.motivo ? [el('dt', {}, 'Motivo'), el('dd', {}, def.motivo)] : null),
        detalle,
        el('div', { class: 'defecto-acciones' }, ...acciones)),
      el('div', { class: 'defecto-evidencia' },
        el('h4', {}, 'Evidencia'),
        ...(def.capturas.length ? def.capturas.map((c) => el('img', {
          src: rutaEvidencia(c), alt: `Captura de pantalla del fallo ${def.id}`, loading: 'lazy',
          onclick: () => { $('#imagen-grande').src = rutaEvidencia(c); $('#dialogo-imagen').showModal(); },
        })) : [el('p', { class: 'meta' }, 'Sin captura')]),
        el('span', { class: 'meta' }, def.evidencia || '')));
  }
  const rutaEvidencia = (ruta) => (window.QA_RUTAS_EVIDENCIA && window.QA_RUTAS_EVIDENCIA[ruta]) || ('/evidencia/' + ruta.replace(/^qa\/evidencia\//, '').split('/').map(encodeURIComponent).join('/'));

  // ---- Reporte
  function tarjetaReporte() {
    const e = ui.estado;
    const textoSemaforo = { rojo: 'No publicar', amarillo: 'Publicar con riesgo conocido', verde: 'Publicar' }[e.reporte.semaforo];
    return tarjeta('', cabecera('reportar', 'Reporte del ciclo', [`qa/reporte.md · ${e.reporte.modificado}`],
      [e.resultados.reporte_html ? el('a', { class: 'boton boton-chico', href: '/reporte-html/index.html', target: '_blank', rel: 'noopener' }, 'Reporte HTML de Playwright') : null,
        descargar('reporte', 'Descargar reporte'), botonPaso('reportar', 'Generar de nuevo', 'boton boton-chico')]),
      textoSemaforo ? el('div', { class: `semaforo ${e.reporte.semaforo}`, role: 'status' },
        el('span', { class: 'luces', 'aria-hidden': 'true' }, el('span', { class: 'luz r' }), el('span', { class: 'luz a' }), el('span', { class: 'luz v' })),
        el('div', {}, el('b', {}, textoSemaforo), el('div', { class: 'meta' }, `Semáforo de la versión: ${e.defectos.confirmados} defecto(s) confirmado(s), ${e.resultados.pasaron} de ${e.resultados.ejecutados} casos pasaron.`))) : null,
      plegable('reporte-doc', 'Ver el reporte completo', cuerpoDocumento('reporte')));
  }

  // ------------------------------------------------------------ ¿Qué sigue? (siempre al final del hilo)
  function pintarSiguiente() {
    const e = ui.estado;
    const previo = $('#siguiente');
    if (previo) previo.remove();
    if (e.agente.ocupado) return;
    let titulo, texto, acciones = [];
    if (!e.exploracion.existe) {
      const campo = el('input', { class: 'campo campo-mono', type: 'url', value: e.aplicacion.url, 'aria-label': 'URL a explorar' });
      titulo = 'Paso 1 · Entiende la aplicación';
      texto = 'El agente abrirá la aplicación en el navegador, la recorrerá con los usuarios de prueba y dejará un mapa de pantallas, elementos y flujos. De ahí salen el plan y las pruebas.';
      acciones = [campo, botonPaso('explorar-app', 'Explorar la aplicación', 'boton boton-primario boton-grande', () => campo.value.trim())];
    } else if (!e.plan.existe) {
      titulo = 'Paso 2 · Diseña el plan de pruebas';
      texto = e.historia.existe
        ? `El plan partirá de la historia «${e.historia.titulo}» (${e.historia.criterios} criterios de aceptación) y de la exploración. Tú lo apruebas antes de que nada se ejecute.`
        : 'El agente propondrá entre 6 y 10 casos a partir de los requisitos y la exploración. Si prefieres, puede partir de una historia de usuario con sus criterios de aceptación. Tú apruebas el plan antes de que nada se ejecute.';
      acciones = [botonPaso('disenar-plan', e.historia.existe ? 'Diseñar el plan desde la historia' : 'Diseñar el plan', 'boton boton-primario boton-grande'),
        el('button', { class: 'boton', type: 'button', onclick: () => abrirHistoria(ui.docs.historia) }, icono('historia'), e.historia.existe ? 'Cambiar la historia' : 'Partir de una historia de usuario')];
    } else if (!e.plan.aprobado) {
      const n = e.casos.filter((c) => !ui.excluidos.has(c.id)).length;
      titulo = 'Tu decisión · Aprobar el plan';
      texto = 'Revisa los casos en la tarjeta del plan: desmarca los que no apliquen o edita el texto. Cuando apruebes, el agente podrá escribir y correr las pruebas.';
      acciones = [el('button', { class: 'boton boton-primario boton-grande', type: 'button', disabled: n === 0, onclick: () => aprobarPlan() }, icono('check'), `Aprobar el plan (${n})`),
        el('button', { class: 'boton', type: 'button', onclick: () => irAlEntregable('disenar-plan') }, 'Ver el plan', icono('flecha'))];
    } else if (!e.resultados.existe) {
      titulo = 'Paso 3 · Ejecuta las pruebas';
      texto = 'El agente convierte cada caso aprobado en una prueba de Playwright, las corre contra la aplicación y guarda una captura de cada fallo. Las pruebas quedan en tests/ y corren sin el agente.';
      acciones = [botonPaso('ejecutar-pruebas', 'Ejecutar las pruebas', 'boton boton-primario boton-grande')];
    } else if (!e.defectos.existe) {
      titulo = 'Paso 4 · Analiza los fallos';
      texto = e.resultados.fallaron > 0
        ? `${e.resultados.fallaron} prueba(s) fallaron. El agente clasificará cada fallo como defecto de la aplicación, prueba frágil o problema de ambiente, y documentará los defectos con su evidencia para que los confirmes.`
        : 'Todas las pruebas pasaron. El agente lo deja registrado y podrás pasar al reporte.';
      acciones = [botonPaso('analizar-fallos', 'Analizar los fallos', 'boton boton-primario boton-grande')];
    } else if (e.defectos.pendientes > 0) {
      titulo = `Tu decisión · ${e.defectos.pendientes} defecto(s) por confirmar`;
      texto = 'Confirma los defectos reales o descártalos con un motivo, desde la tarjeta de defectos. Solo los confirmados cuentan para el semáforo del reporte.';
      acciones = [el('button', { class: 'boton boton-primario boton-grande', type: 'button', onclick: () => irAlEntregable('analizar-fallos') }, 'Ir a los defectos', icono('flecha'))];
    } else if (!e.reporte.existe) {
      titulo = 'Paso 5 · Genera el reporte';
      texto = 'El agente escribe el semáforo de la versión, la cobertura por prioridad, los defectos confirmados y las métricas del ciclo (casos aceptados sin edición, pruebas corregidas, duración).';
      acciones = [botonPaso('reportar', 'Generar el reporte', 'boton boton-primario boton-grande')];
    } else {
      titulo = 'Ciclo completo';
      texto = 'El reporte está arriba. Las pruebas quedan en el repositorio y corren sin el agente con npx playwright test. Puedes empezar otro ciclo; el actual se archiva en qa/historial/.';
      acciones = [el('button', { class: 'boton boton-primario boton-grande', type: 'button', onclick: () => reiniciarCiclo() }, icono('play'), 'Empezar otro ciclo'), descargar('reporte', 'Descargar reporte')];
    }
    const hilo = $('#hilo');
    const pegado = hilo.scrollHeight - hilo.scrollTop - hilo.clientHeight < 160;
    // Archivos del ciclo de ejemplo (modo demo) con el agente real: avisar y ofrecer empezar de cero.
    const avisoEjemplo = e.modo !== 'demo' && e.ciclo_ejemplo
      ? el('div', { class: 'aviso-ejemplo' }, icono('alerta', 'aviso-ejemplo-icono'),
          el('span', {}, 'Estos archivos vienen del ciclo de ejemplo del modo demo, no del agente real. Para que el agente explore y pruebe de verdad, empieza un ciclo nuevo: el ejemplo se archiva en qa/historial/. '),
          el('button', { class: 'boton boton-chico', type: 'button', onclick: () => reiniciarCiclo() }, 'Empezar ciclo nuevo'))
      : null;
    hilo.append(el('li', { class: 'siguiente', id: 'siguiente' }, avisoEjemplo, el('h2', {}, titulo), el('p', {}, texto), el('div', { class: 'siguiente-acciones' }, ...acciones)));
    if (pegado) hilo.scrollTop = hilo.scrollHeight;
  }

  // ------------------------------------------------------------ el hilo: turnos y eventos
  function turnoSistema(texto) { return el('li', { class: 'turno sistema' }, el('div', { class: 'burbuja' }, texto)); }
  function turnoUsuario(titulo, prompt) {
    return el('li', { class: 'turno usuario' }, el('div', { class: 'burbuja' }, titulo, prompt && prompt !== titulo ? el('code', {}, prompt) : null));
  }
  function turnoAgente(paso) {
    const acciones = el('details', { class: 'acciones' }, el('summary', {}, el('span', { class: 'acciones-resumen' }, 'Trabajando…'), el('span', { class: 'giro' })), el('ol', { class: 'acciones-lista' }));
    const actual = el('div', { class: 'accion-actual' }, el('span', { class: 'giro' }), el('span', {}, 'Empezando…'));
    const turno = el('li', { class: 'turno agente', 'data-paso': paso || '' },
      el('span', { class: 'avatar', 'aria-hidden': 'true', html: ICONO.chispa }),
      el('div', { class: 'burbuja' }, el('div', { class: 'turno-autor' }, el('b', {}, 'Agente'), el('span', {}, etiquetaPaso(paso))), acciones, actual));
    turno.acciones = acciones; turno.actual = actual; turno.n = 0;
    return turno;
  }
  const etiquetaPaso = (paso) => (paso === 'inicio' ? 'Presentación' : paso ? `Paso ${numeroPaso(paso)} · ${nombrePaso(paso)}` : '');

  // La presentación del agente es la salida de su skill /inicio: no hay texto fijo en la interfaz.
  // El servidor la guarda; si no la tiene, se le pide una vez y el agente se presenta en vivo.
  function turnoPresentacion(texto) {
    return el('li', { class: 'turno agente', id: 'presentacion-hilo', 'data-paso': 'inicio' },
      el('span', { class: 'avatar', 'aria-hidden': 'true', html: ICONO.chispa }),
      el('div', { class: 'burbuja' }, el('div', { class: 'turno-autor' }, el('b', {}, 'Agente'), el('span', {}, etiquetaPaso('inicio'))),
        el('div', { class: 'agente-texto', html: md(texto) })));
  }
  function pintarPresentacion() {
    const e = ui.estado;
    const p = e.presentacion;
    if (p && p.texto) {
      if (!$('#presentacion-hilo')) $('#hilo').prepend(turnoPresentacion(p.texto));
      return;
    }
    if (p) return; // la última presentación falló: el error quedó en el hilo; se vuelve a pedir al reiniciar el servidor
    if (e.agente.ocupado || ui.presentacionPedida === e.modo) return;
    ui.presentacionPedida = e.modo;
    api.post('/api/presentacion').catch((err) => aviso(`No se pudo pedir la presentación del agente: ${err.message}`, true));
  }

  function conectarEventos() {
    const fuente = new EventSource('/api/eventos');
    fuente.onmessage = (ev) => {
      const evento = JSON.parse(ev.data);
      if (evento.n <= ui.ultimoEvento) return;
      ui.ultimoEvento = evento.n;
      if (evento.tipo === 'estado') { cargarEstado(); return; }
      pintarEvento(evento);
      if (evento.tipo === 'inicio' || evento.tipo === 'fin') cargarEstado();
    };
    fuente.onerror = () => { $('#redactor-pie').textContent = 'Reconectando con el servidor…'; };
  }

  function pintarEvento(ev) {
    const hilo = $('#hilo');
    const pegado = hilo.scrollHeight - hilo.scrollTop - hilo.clientHeight < 160;
    const siguiente = $('#siguiente');
    if (ev.tipo === 'inicio') {
      ui.turnoActual = turnoAgente(ev.paso);
      ui.ultimoTexto = '';
      if (ev.paso === 'inicio') {
        // El agente se presenta: sin turno de la persona y siempre al principio del hilo.
        const previa = $('#presentacion-hilo'); if (previa) previa.remove();
        hilo.prepend(ui.turnoActual);
      } else {
        hilo.append(turnoUsuario(ev.paso && PASOS_UI[ev.paso] ? PASOS_UI[ev.paso].verbo : ev.prompt, ev.prompt));
        hilo.append(ui.turnoActual);
      }
      if (siguiente) siguiente.remove();
      pintarEntregables();
      if (pegado) hilo.scrollTop = hilo.scrollHeight;
      return;
    }
    const turno = ui.turnoActual;
    if (!turno) {
      if (['sistema', 'decision', 'error'].includes(ev.tipo)) { const t = turnoSistema(ev.texto); if (siguiente) siguiente.before(t); else hilo.append(t); }
      if (pegado) hilo.scrollTop = hilo.scrollHeight;
      return;
    }
    const lista = $('.acciones-lista', turno);
    const burbuja = $('.burbuja', turno);
    const anotar = (clase, contenido) => {
      lista.append(el('li', { class: `accion ${clase}` }, el('span', {}), el('span', {}, contenido)));
      turno.n += 1;
      $('.acciones-resumen', turno.acciones).textContent = `${turno.n} ${turno.n === 1 ? 'acción' : 'acciones'}`;
    };
    switch (ev.tipo) {
      case 'herramienta': anotar('', ev.resumen); $('span:last-child', turno.actual).textContent = ev.resumen; break;
      case 'salida':
        lista.append(el('li', { class: 'accion' }, el('details', { class: `salida-comando ${ev.ok ? '' : 'falla'}` },
          el('summary', {}, ev.ok ? 'Salida del comando' : 'Salida del comando (con errores)'), el('pre', {}, ev.texto))));
        break;
      case 'texto': burbuja.append(el('div', { class: 'agente-texto', html: md(ev.texto) })); ui.ultimoTexto = normalizar(ev.texto); break;
      case 'sistema': anotar('sistema', ev.texto); break;
      case 'stderr': if (/error|Error|ERR/.test(ev.texto)) anotar('error', ev.texto); break;
      case 'error': burbuja.append(el('div', { class: 'error-agente' }, el('strong', {}, 'Error del agente'), ev.texto)); break;
      case 'decision': anotar('sistema', ev.texto); break;
      case 'fin': {
        turno.actual.remove();
        const giro = $('.giro', turno.acciones); if (giro) giro.remove();
        if (turno.n === 0) turno.acciones.remove();
        if (ev.resumen && normalizar(ev.resumen) !== ui.ultimoTexto) {
          burbuja.append(ev.ok ? el('div', { class: 'agente-texto', html: md(ev.resumen) })
            : el('div', { class: 'error-agente' }, el('strong', {}, ev.cancelado ? 'Paso detenido' : 'El paso no terminó'), el('div', { html: md(ev.resumen) }),
              ev.cancelado ? null : el('div', { class: 'meta', style: 'margin-top:6px' }, 'Qué hacer: revisa el mensaje y vuelve a correr el paso; los archivos escritos hasta aquí se conservan.')));
        }
        const meta = [ev.duracion_ms != null ? formatoSegundos(ev.duracion_ms / 1000) : null, ev.turnos != null ? `${ev.turnos} turnos` : null,
          ev.costo_usd != null ? `USD ${ev.costo_usd.toFixed(3)}` : null].filter(Boolean).join(' · ');
        burbuja.append(el('div', { class: `turno-pie ${ev.ok ? 'ok' : 'falla'}` }, icono(ev.ok ? 'check' : 'alerta'), ev.ok ? 'Listo' : (ev.cancelado ? 'Detenido' : 'No terminó'), meta ? el('span', { class: 'meta' }, meta) : null));
        if (ev.paso === 'inicio' && ev.ok) turno.id = 'presentacion-hilo'; // ya está en el hilo: no se vuelve a pintar desde el estado
        ui.turnoActual = null;
        break;
      }
      default: anotar('sistema', ev.texto || JSON.stringify(ev));
    }
    if (pegado) hilo.scrollTop = hilo.scrollHeight;
  }

  // ------------------------------------------------------------ redactor
  function pintarRedactor() {
    const e = ui.estado;
    $('#mensaje').disabled = e.agente.ocupado;
    $('#btn-enviar').hidden = e.agente.ocupado;
    $('#btn-cancelar').hidden = !e.agente.ocupado;
    actualizarPie();
  }
  function actualizarPie() {
    const e = ui.estado;
    if (!e) return;
    const pie = $('#redactor-pie');
    pie.className = `redactor-pie ${e.agente.ocupado ? 'trabajando' : ''}`;
    let texto;
    if (e.agente.ocupado && e.agente.actual) texto = `Trabajando en ${e.agente.actual.paso === 'inicio' ? 'su presentación' : e.agente.actual.paso ? nombrePaso(e.agente.actual.paso).toLowerCase() : 'tu mensaje'} · ${formatoSegundos(Date.now() / 1000 - e.agente.actual.inicio)}`;
    else if (e.modo === 'demo') texto = 'En espera · modo demo: las respuestas son un ejemplo, sin API ni navegador';
    else texto = `En espera · solo navega ${e.aplicacion.url} y escribe en qa/ y tests/`;
    pie.replaceChildren(el('span', { class: 'punto', 'aria-hidden': 'true' }), texto);
  }

  // ------------------------------------------------------------ acciones
  async function correrPaso(id, argumentos = '') {
    try {
      await api.post(`/api/pasos/${id}`, { argumentos: argumentos || '' });
      ui.excluidos.clear(); ui.editandoPlan = false;
      await cargarEstado();
    } catch (e) { aviso(e.message, true); }
  }
  async function aprobarPlan() {
    try {
      const r = await api.post('/api/plan/aprobar', { excluir: [...ui.excluidos] });
      ui.excluidos.clear(); ui.editandoPlan = false; delete ui.docs.plan;
      aviso(`Plan aprobado con ${r.casos.length} casos. Ya puedes ejecutar las pruebas.`);
      await cargarEstado();
    } catch (e) { aviso(e.message, true); }
  }
  async function desaprobarPlan() {
    try { await api.post('/api/plan/desaprobar'); delete ui.docs.plan; aviso('Plan abierto de nuevo. El paso 3 queda bloqueado hasta que apruebes.'); await cargarEstado(); }
    catch (e) { aviso(e.message, true); }
  }
  async function guardarPlan(markdown) {
    try { ui.docs.plan = await api.put('/api/documento/plan', { markdown }); ui.editandoPlan = false; aviso('Plan guardado.'); await cargarEstado(); }
    catch (e) { aviso(e.message, true); }
  }
  function decidirDefecto(def, estado, motivo = '', directo = false) {
    const enviar = async (m) => {
      try {
        await api.post(`/api/defectos/${def.id}/estado`, { estado, motivo: m || '' });
        aviso(`${def.id}: ${estado === 'PENDIENTE DE CONFIRMACIÓN' ? 'vuelve a pendiente' : estado.toLowerCase()}.`);
        await cargarEstado();
      } catch (e) { aviso(e.message, true); }
    };
    if (directo || estado === 'CONFIRMADO') return enviar(motivo);
    const dialogo = $('#dialogo-motivo');
    $('#motivo-titulo').textContent = `Descartar ${def.id}`;
    $('#motivo-texto').textContent = `${def.titulo}. El motivo queda registrado en el defecto y se lista en el reporte.`;
    $('#motivo').value = '';
    $('#form-motivo').onsubmit = (ev) => { ev.preventDefault(); dialogo.close(); enviar($('#motivo').value.trim()); };
    dialogo.showModal();
    $('#motivo').focus();
  }
  function confirmar(titulo, texto, textoBoton = 'Continuar') {
    return new Promise((resolver) => {
      const dialogo = $('#dialogo-confirmar');
      $('#confirmar-titulo').textContent = titulo; $('#confirmar-texto').textContent = texto; $('#btn-confirmar-ok').textContent = textoBoton;
      const cerrar = (v) => { dialogo.close(); resolver(v); };
      $('#form-confirmar').onsubmit = (ev) => { ev.preventDefault(); cerrar(true); };
      $('#btn-confirmar-cerrar').onclick = () => cerrar(false);
      dialogo.oncancel = () => resolver(false);
      dialogo.showModal();
    });
  }
  async function reiniciarCiclo() {
    const ok = await confirmar('¿Empezar un ciclo nuevo?', 'Los archivos del ciclo actual se archivan en qa/historial/ (no se borran) y los requisitos se conservan.', 'Empezar ciclo nuevo');
    if (!ok) return;
    try {
      const r = await api.post('/api/ciclo/reiniciar');
      ui.docs = {}; ui.excluidos.clear(); ui.editandoPlan = false; ui.abiertos.clear(); ui.ultimoEvento = 0; ui.turnoActual = null;
      $('#hilo').replaceChildren();
      aviso(r.archivado_en ? `Ciclo archivado en ${r.archivado_en}.` : 'Ciclo reiniciado.');
      await cargarEstado();
    } catch (e) { aviso(e.message, true); }
  }
  async function abrirRequisitos() {
    try { const doc = await api.get('/api/documento/requisitos'); $('#requisitos-texto').value = doc.markdown; $('#dialogo-requisitos').showModal(); }
    catch (e) { aviso(e.message, true); }
  }
  async function abrirHistoria(doc) {
    if (!doc && ui.estado.historia.existe) doc = await documento('historia').catch(() => null);
    const texto = doc ? doc.markdown : '';
    const titulo = (texto.match(/^#\s*(.+)$/m) || [, ''])[1];
    const cuerpo = texto.replace(/^#.*$/m, '').split(/## Criterios[^\n]*/)[0].trim();
    const criterios = texto.split('\n').filter((l) => /^\s*[-*]\s+\S/.test(l)).map((l) => l.trim().slice(1).trim()).join('\n');
    $('#historia-titulo').value = titulo; $('#historia-texto').value = cuerpo; $('#historia-criterios').value = criterios;
    $('#dialogo-historia').showModal();
    $('#historia-titulo').focus();
  }
  async function guardarHistoria() {
    try {
      await api.post('/api/historia', { titulo: $('#historia-titulo').value, texto: $('#historia-texto').value, criterios: $('#historia-criterios').value.split('\n') });
      $('#dialogo-historia').close(); delete ui.docs.historia;
      aviso('Historia guardada. El plan partirá de ella.');
      await cargarEstado();
    } catch (e) { aviso(e.message, true); }
  }
  async function quitarHistoria() {
    try { await api.del('/api/historia'); delete ui.docs.historia; aviso('Historia quitada; el plan partirá de los requisitos.'); await cargarEstado(); }
    catch (e) { aviso(e.message, true); }
  }
  async function enviarMensaje(texto) {
    try { await api.post('/api/agente/mensaje', { prompt: texto }); await cargarEstado(); } catch (e) { aviso(e.message, true); }
  }

  // ------------------------------------------------------------ tema
  function aplicarTema(valor) {
    if (window.QA_SIN_TEMA) { $('#btn-tema').hidden = true; return; }   // la vista previa publicada sigue el tema del visor
    try { if (valor) localStorage.setItem('qa-tema', valor); else localStorage.removeItem('qa-tema'); } catch (e) { /* sin almacenamiento */ }
    if (valor) document.documentElement.dataset.theme = valor; else delete document.documentElement.dataset.theme;
    const btn = $('#btn-tema');
    btn.innerHTML = valor === 'dark' ? ICONO.luna : valor === 'light' ? ICONO.sol : ICONO.auto;
    btn.title = valor === 'dark' ? 'Tema oscuro (clic: seguir al sistema)' : valor === 'light' ? 'Tema claro (clic: oscuro)' : 'Tema del sistema (clic: claro)';
  }
  function alternarTema() {
    if (window.QA_SIN_TEMA) return;
    const actual = document.documentElement.dataset.theme || '';
    aplicarTema(actual === '' ? 'light' : actual === 'light' ? 'dark' : '');
  }

  // ------------------------------------------------------------ avisos
  let temporizadorToast;
  function aviso(texto, esError = false) {
    const t = $('#toast');
    t.textContent = texto; t.className = `toast ${esError ? 'error' : ''}`; t.hidden = false;
    clearTimeout(temporizadorToast);
    temporizadorToast = setTimeout(() => { t.hidden = true; }, esError ? 7000 : 3500);
  }

  // ------------------------------------------------------------ arranque
  aplicarTema(document.documentElement.dataset.theme || '');
  $('#btn-tema').addEventListener('click', alternarTema);
  $('#btn-reiniciar').addEventListener('click', reiniciarCiclo);
  $('#btn-aplicacion').addEventListener('click', abrirRequisitos);
  $('#btn-requisitos-cerrar').addEventListener('click', () => $('#dialogo-requisitos').close());
  $('#form-requisitos').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    try { await api.put('/api/documento/requisitos', { markdown: $('#requisitos-texto').value }); $('#dialogo-requisitos').close(); aviso('Requisitos guardados.'); await cargarEstado(); }
    catch (e) { aviso(e.message, true); }
  });
  $('#btn-historia-cerrar').addEventListener('click', () => $('#dialogo-historia').close());
  $('#form-historia').addEventListener('submit', (ev) => { ev.preventDefault(); guardarHistoria(); });
  $('#btn-motivo-cerrar').addEventListener('click', () => $('#dialogo-motivo').close());
  $('#btn-cancelar').addEventListener('click', async () => {
    try { await api.post('/api/agente/cancelar'); aviso('Paso detenido. Los archivos escritos hasta ahora se conservan.'); } catch (e) { aviso(e.message, true); }
  });
  $('#form-mensaje').addEventListener('submit', (ev) => {
    ev.preventDefault();
    const campo = $('#mensaje'); const texto = campo.value.trim();
    if (!texto) return;
    campo.value = ''; enviarMensaje(texto);
  });

  cargarEstado().then(() => conectarEventos());
  setInterval(actualizarPie, 1000);
  setInterval(() => { if (ui.estado && ui.estado.agente.ocupado) cargarEstado(); }, 5000);
})();
