/* Servidor simulado del modo demo, para correr la interfaz sin backend (vista previa publicada
   o el archivo demo-web.html abierto en cualquier navegador). Reproduce en JavaScript lo que
   hacen app/estado.py y app/demo.py: los archivos viven en memoria, el agente «trabaja» con un
   guion y las decisiones humanas se escriben en esos mismos archivos.
   Los marcadores __ARCHIVOS__ y __EVIDENCIA__ los rellena app/ejemplos/armar_demo_web.py. */
(function () {
  'use strict';
  const ARCHIVOS = __ARCHIVOS__;      // { ejemplos: {...}, tests: {...}, requisitos: '...' }
  const EVIDENCIA = __EVIDENCIA__;    // { 'carpeta/test-failed-1.png': 'data:image/png;base64,...' }
  const VELOCIDAD = window.QA_DEMO_VELOCIDAD ?? 0.45;
  const MODO = 'demo';

  window.QA_RUTAS_EVIDENCIA = {};
  for (const [ruta, uri] of Object.entries(EVIDENCIA)) window.QA_RUTAS_EVIDENCIA['qa/evidencia/' + ruta] = uri;

  // ------------------------------------------------------------ "disco"
  const repo = { archivos: {} };
  const limpiar = () => {
    repo.archivos = { 'qa/requisitos.md': ARCHIVOS.requisitos, 'tests/datos.ts': ARCHIVOS.tests['datos.ts'], 'tests/ejemplo.spec.ts': ARCHIVOS.tests['ejemplo.spec.ts'] };
  };
  limpiar();
  const leer = (ruta) => (ruta in repo.archivos ? repo.archivos[ruta] : null);
  const escribir = (ruta, texto) => { repo.archivos[ruta] = texto; };
  const borrar = (ruta) => { delete repo.archivos[ruta]; };
  const existe = (ruta) => ruta in repo.archivos;
  const listar = (prefijo) => Object.keys(repo.archivos).filter((r) => r.startsWith(prefijo)).sort();
  const ahora = () => { const d = new Date(); const p = (n) => String(n).padStart(2, '0'); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`; };
  const DOCS = { requisitos: 'qa/requisitos.md', historia: 'qa/historia-de-usuario.md', exploracion: 'qa/exploracion.md', plan: 'qa/plan-de-pruebas.md',
    'plan-generado': 'qa/plan-de-pruebas.generado.md', resultados: 'qa/resultados.md', reporte: 'qa/reporte.md' };
  const modificados = {};
  const marcar = (ruta) => { modificados[ruta] = ahora(); };
  const mtime = (ruta) => (existe(ruta) ? modificados[ruta] || ahora() : null);

  // ------------------------------------------------------------ estado (espejo de app/estado.py)
  const PASOS = [
    { id: 'explorar-app', numero: 1, nombre: 'Entiende', accion: 'Explorar la aplicación', comando: '/explorar-app', descripcion: 'Navega la aplicación y documenta pantallas, flujos y elementos.', salida: 'qa/exploracion.md', decision: null },
    { id: 'disenar-plan', numero: 2, nombre: 'Diseña', accion: 'Diseñar el plan', comando: '/disenar-plan', descripcion: 'Propone el plan y los casos de prueba.', salida: 'qa/plan-de-pruebas.md', decision: 'Tú apruebas el plan' },
    { id: 'ejecutar-pruebas', numero: 3, nombre: 'Ejecuta', accion: 'Ejecutar las pruebas', comando: '/ejecutar-pruebas', descripcion: 'Convierte el plan en pruebas de Playwright y las corre.', salida: 'tests/*.spec.ts · qa/resultados.md', decision: null },
    { id: 'analizar-fallos', numero: 4, nombre: 'Analiza', accion: 'Analizar los fallos', comando: '/analizar-fallos', descripcion: 'Clasifica cada fallo y documenta los defectos con evidencia.', salida: 'qa/defectos/DEF-*.md', decision: 'Tú confirmas cada defecto' },
    { id: 'reportar', numero: 5, nombre: 'Reporta', accion: 'Generar el reporte', comando: '/reportar', descripcion: 'Semáforo de la versión, defectos confirmados y métricas del ciclo.', salida: 'qa/reporte.md', decision: null },
  ];
  const aplicacion = () => {
    const t = leer(DOCS.requisitos) || '';
    const n = t.match(/^- Aplicación:\s*(.+)$/m); const u = t.match(/^- URL:\s*(\S+)/m);
    return { nombre: n ? n[1].trim() : 'Aplicación sin nombre', url: u ? u[1].trim() : '', requisitos_existen: !!t };
  };
  const filaCaso = (linea) => {
    if (!/^\|\s*CP-\d+/.test(linea)) return null;
    const celdas = linea.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
    if (celdas.length < 3) return null;
    while (celdas.length < 7) celdas.push('');
    const [id, titulo, prioridad, usuario, precondicion, pasos, resultado] = celdas;
    return { id, titulo, prioridad, usuario, precondicion, pasos, resultado };
  };
  const casosDe = (texto) => (texto ? texto.split('\n').map(filaCaso).filter(Boolean) : []);
  const ultimaLinea = (texto) => { const ls = texto.trim().split('\n').filter((l) => l.trim()); return ls.length ? ls[ls.length - 1].trim() : ''; };
  const igual = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  function compararPlanes() {
    const gen = casosDe(leer(DOCS['plan-generado'])); const apr = casosDe(leer(DOCS.plan));
    if (!gen.length) return null;
    const g = Object.fromEntries(gen.map((c) => [c.id, c])); const a = Object.fromEntries(apr.map((c) => [c.id, c]));
    const aceptados = Object.keys(g).filter((i) => a[i] && igual(a[i], g[i]));
    const editados = Object.keys(g).filter((i) => a[i] && !igual(a[i], g[i]));
    const rechazados = Object.keys(g).filter((i) => !a[i]);
    const anadidos = Object.keys(a).filter((i) => !g[i]);
    return { generados: gen.length, aceptados, editados, rechazados, anadidos, porcentaje_aceptados: Math.round(100 * aceptados.length / gen.length) };
  }
  function planInfo() {
    const texto = leer(DOCS.plan);
    if (texto === null) return { existe: false, aprobado: false, casos: [], por_prioridad: {} };
    const ultima = ultimaLinea(texto); const casos = casosDe(texto);
    const por = {}; for (const c of casos) por[c.prioridad || 'Sin prioridad'] = (por[c.prioridad || 'Sin prioridad'] || 0) + 1;
    const aprobado = ultima.toUpperCase().startsWith('ESTADO: APROBADO');
    return { existe: true, aprobado, estado: ultima, casos, por_prioridad: por, generado_existe: existe(DOCS['plan-generado']), modificado: mtime(DOCS.plan), comparacion: aprobado ? compararPlanes() : null };
  }
  function resultadosInfo() {
    const texto = leer(DOCS.resultados);
    if (texto === null) return { existe: false };
    const filas = [];
    for (const linea of texto.split('\n')) {
      if (!filaCaso(linea)) continue;
      const celdas = linea.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
      const r = celdas.find((c) => ['PASÓ', 'FALLÓ', 'BLOQUEADO'].includes(c.toUpperCase())) || '';
      filas.push({ id: celdas[0], titulo: celdas[1] || '', resultado: r.toUpperCase() });
    }
    return { existe: true, filas, pasaron: filas.filter((f) => f.resultado === 'PASÓ').length, fallaron: filas.filter((f) => f.resultado === 'FALLÓ').length,
      bloqueados: filas.filter((f) => f.resultado === 'BLOQUEADO').length, ejecutados: filas.length, modificado: mtime(DOCS.resultados), reporte_html: false };
  }
  const campo = (texto, nombre) => { const m = texto.match(new RegExp('^- ' + nombre.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ':\\s*(.*)$', 'm')); return m ? m[1].trim() : ''; };
  function defectoDe(ruta) {
    const texto = leer(ruta); const id = ruta.split('/').pop().replace(/\.md$/, '');
    const t = texto.match(/^#\s*(.+)$/m);
    let estado = campo(texto, 'Estado').toUpperCase();
    estado = ['PENDIENTE DE CONFIRMACIÓN', 'CONFIRMADO', 'DESCARTADO'].find((e) => estado.startsWith(e)) || 'PENDIENTE DE CONFIRMACIÓN';
    const sev = campo(texto, 'Severidad'); const nivel = ['Crítica', 'Alta', 'Media', 'Baja'].find((n) => sev.startsWith(n)) || sev;
    const capturas = [...texto.matchAll(/(qa\/evidencia\/[^\s·|)]+\.(?:png|jpg|jpeg))/g)].map((m) => m[1]);
    return { id, archivo: ruta, titulo: t ? t[1].trim().replace(/^DEF-\d+\s*·\s*/, '') : id, severidad: nivel, severidad_detalle: sev, casos: campo(texto, 'Casos de prueba'),
      estado, motivo: campo(texto, 'Motivo'), resultado_esperado: campo(texto, 'Resultado esperado'), resultado_obtenido: campo(texto, 'Resultado obtenido'),
      evidencia: campo(texto, 'Evidencia'), capturas, markdown: texto };
  }
  function defectosInfo() {
    const lista = listar('qa/defectos/DEF-').map(defectoDe);
    const sin = !lista.length && existe('qa/defectos/README.md');
    return { existe: lista.length > 0 || sin, lista, pendientes: lista.filter((d) => d.estado === 'PENDIENTE DE CONFIRMACIÓN').length,
      confirmados: lista.filter((d) => d.estado === 'CONFIRMADO').length, descartados: lista.filter((d) => d.estado === 'DESCARTADO').length, sin_defectos: sin, nota: sin ? leer('qa/defectos/README.md') : null };
  }
  function reporteInfo() {
    const texto = leer(DOCS.reporte);
    if (texto === null) return { existe: false };
    let semaforo = null, pos = Infinity;
    for (const [s, n] of [['🔴', 'rojo'], ['🟡', 'amarillo'], ['🟢', 'verde']]) { const i = texto.indexOf(s); if (i !== -1 && i < pos) { pos = i; semaforo = n; } }
    return { existe: true, semaforo, modificado: mtime(DOCS.reporte) };
  }
  const criteriosDeHistoria = () => (leer(DOCS.historia) || '').split('\n').filter((l) => /^\s*[-*]\s+\S/.test(l)).map((l) => l.trim().slice(1).trim());
  function historiaInfo() {
    const texto = leer(DOCS.historia);
    if (texto === null) return { existe: false };
    const t = texto.match(/^#\s*(.+)$/m);
    return { existe: true, titulo: t ? t[1].trim() : 'Historia de usuario', criterios: criteriosDeHistoria().length, modificado: mtime(DOCS.historia) };
  }
  const pruebas = () => listar('tests/').filter((r) => r.endsWith('.spec.ts')).map((r) => ({ archivo: r, nombre: r.split('/').pop(), contenido: leer(r), casos: [...new Set([...leer(r).matchAll(/\b(CP-\d+)\b/g)].map((m) => m[1]))].sort() }));
  const evidencias = () => listar('qa/evidencia/');

  let actual = null, ultimo = null, temporizadores = [];
  const ocupado = () => actual !== null;
  // Presentación del agente (skill /inicio): se pide una vez y se muestra al abrir la interfaz.
  let presentacion = null;
  const clavePresentacion = () => MODO;
  const presentacionActual = () => (presentacion && presentacion.clave === clavePresentacion() ? { texto: presentacion.texto, error: presentacion.error, fecha: presentacion.fecha } : null);
  function estado() {
    const plan = planInfo(), resultados = resultadosInfo(), defectos = defectosInfo(), reporte = reporteInfo();
    const expl = existe(DOCS.exploracion);
    const hechos = { 'explorar-app': expl, 'disenar-plan': plan.existe, 'ejecutar-pruebas': resultados.existe, 'analizar-fallos': defectos.existe, 'reportar': reporte.existe };
    const decisiones = { 'disenar-plan': plan.existe && !plan.aprobado, 'analizar-fallos': defectos.pendientes > 0 };
    const disponibles = { 'explorar-app': true, 'disenar-plan': expl, 'ejecutar-pruebas': plan.aprobado, 'analizar-fallos': resultados.existe, 'reportar': defectos.existe && defectos.pendientes === 0 };
    const enCurso = actual ? actual.paso : null;
    const pasos = PASOS.map((p) => {
      const est = enCurso === p.id ? 'en_curso' : decisiones[p.id] ? 'decision' : hechos[p.id] ? 'hecho' : 'pendiente';
      return { ...p, estado: est, hecho: hechos[p.id], disponible: disponibles[p.id] && !enCurso };
    });
    const actualPaso = (pasos.find((p) => ['decision', 'en_curso'].includes(p.estado)) || pasos.find((p) => !p.hecho) || { id: 'reportar' }).id;
    const { casos, ...planSinCasos } = plan;
    return { aplicacion: aplicacion(), repo: 'vista previa (sin servidor)', pasos, paso_actual: actualPaso, paso_en_curso: enCurso,
      exploracion: { existe: expl, modificado: mtime(DOCS.exploracion) }, historia: historiaInfo(), plan: { ...planSinCasos, n_casos: casos.length }, casos,
      resultados, defectos: { ...defectos, lista: defectos.lista.map(({ markdown, ...d }) => d) }, reporte, pruebas: pruebas().map(({ contenido, ...p }) => p), evidencias: evidencias(), historial: [],
      modo: MODO, agente: { ocupado: ocupado(), actual: actual, ultimo }, presentacion: presentacionActual() };
  }

  // ------------------------------------------------------------ decisiones (espejo de estado.py)
  const quitarEstadoFinal = (lineas) => { while (lineas.length && (!lineas[lineas.length - 1].trim() || lineas[lineas.length - 1].trim().toUpperCase().startsWith('ESTADO:') || lineas[lineas.length - 1].startsWith('Aprobado desde la interfaz'))) lineas.pop(); return lineas; };
  function aprobarPlan(markdown, excluir) {
    const texto = markdown ?? leer(DOCS.plan);
    if (texto === null) throw { status: 404, detail: 'No hay plan que aprobar; ejecuta primero el paso 2.' };
    const ex = new Set(excluir || []);
    const lineas = quitarEstadoFinal(texto.trimEnd().split('\n').filter((l) => { const f = filaCaso(l); return !(f && ex.has(f.id)); }));
    lineas.push('', `Aprobado desde la interfaz el ${ahora()}`, 'Estado: APROBADO');
    escribir(DOCS.plan, lineas.join('\n') + '\n'); marcar(DOCS.plan);
    return planInfo();
  }
  function desaprobarPlan() {
    const texto = leer(DOCS.plan); if (texto === null) return planInfo();
    const lineas = quitarEstadoFinal(texto.trimEnd().split('\n')); lineas.push('', 'Estado: PENDIENTE DE APROBACIÓN');
    escribir(DOCS.plan, lineas.join('\n') + '\n'); marcar(DOCS.plan); return planInfo();
  }
  function cambiarEstadoDefecto(id, est, motivo) {
    est = (est || '').toUpperCase().trim();
    if (!['PENDIENTE DE CONFIRMACIÓN', 'CONFIRMADO', 'DESCARTADO'].includes(est)) throw { status: 400, detail: 'Estado no válido' };
    const ruta = `qa/defectos/${id}.md`; if (!existe(ruta)) throw { status: 404, detail: `No existe el defecto ${id}` };
    let texto = leer(ruta).replace(/^- Motivo:.*\n?/m, '').replace(/^- Decidido desde la interfaz:.*\n?/m, '');
    let nueva = `- Estado: ${est}`; if ((motivo || '').trim()) nueva += `\n- Motivo: ${motivo.trim()}`; if (est !== 'PENDIENTE DE CONFIRMACIÓN') nueva += `\n- Decidido desde la interfaz: ${ahora()}`;
    texto = /^- Estado:.*$/m.test(texto) ? texto.replace(/^- Estado:.*$/m, nueva) : texto.trimEnd() + '\n' + nueva + '\n';
    escribir(ruta, texto); return defectoDe(ruta);
  }
  function guardarHistoria({ titulo, texto, criterios }) {
    const limpios = (criterios || []).map((c) => c.trim()).filter(Boolean);
    const lineas = [`# ${(titulo || '').trim() || 'Historia de usuario'}`, '', (texto || '').trim(), ''];
    if (limpios.length) lineas.push('## Criterios de aceptación', '', ...limpios.map((c) => `- ${c}`), '');
    escribir(DOCS.historia, lineas.join('\n')); marcar(DOCS.historia); return historiaInfo();
  }
  function reiniciar() {
    const movidos = Object.keys(repo.archivos).filter((r) => !['qa/requisitos.md', 'tests/datos.ts', 'tests/ejemplo.spec.ts'].includes(r));
    limpiar(); historial.length = 0;
    return { archivado_en: movidos.length ? 'qa/historial/' + ahora().replace(' ', '_').replace(':', '-') : null, movidos };
  }

  // ------------------------------------------------------------ eventos
  const historial = []; let secuencia = 0; const suscriptores = new Set();
  function publicar(ev) { const e = { n: ++secuencia, t: Date.now() / 1000, ...ev }; historial.push(e); if (historial.length > 600) historial.shift(); for (const s of suscriptores) s(e); return e; }
  window.EventSource = class {
    constructor() { this.onmessage = null; this.onerror = null; this.entrega = (e) => { if (this.onmessage) this.onmessage({ data: JSON.stringify(e) }); }; suscriptores.add(this.entrega); setTimeout(() => { for (const e of historial) this.entrega(e); }, 0); }
    addEventListener() {}
    close() { suscriptores.delete(this.entrega); }
  };

  // ------------------------------------------------------------ el "agente" (espejo de app/demo.py)
  const RESULTADOS = { 'CP-01': ['PASÓ', 2.1, 'tests/login.spec.ts'], 'CP-02': ['PASÓ', 1.4, 'tests/login.spec.ts'], 'CP-03': ['PASÓ', 1.3, 'tests/login.spec.ts'], 'CP-04': ['PASÓ', 3.0, 'tests/catalogo.spec.ts'],
    'CP-05': ['FALLÓ', 6.2, 'tests/catalogo.spec.ts'], 'CP-06': ['PASÓ', 2.8, 'tests/carrito.spec.ts'], 'CP-07': ['PASÓ', 4.1, 'tests/checkout.spec.ts'], 'CP-08': ['FALLÓ', 5.5, 'tests/checkout.spec.ts'],
    'CP-09': ['PASÓ', 1.9, 'tests/checkout.spec.ts'], 'CP-10': ['PASÓ', 1.7, 'tests/login.spec.ts'] };
  const ERRORES = {
    'CP-05': { evidencia: 'qa/evidencia/catalogo-Catalogo-CP-05-Catalogo-con-problem-user-imagenes-propias-y-orden-chromium', ubicacion: 'catalogo.spec.ts:38:7 › Catálogo › CP-05 · Catálogo con problem_user: imágenes propias y orden',
      mensaje: 'Error: expect(received).toBe(expected) // Object.is equality\n\nExpected: 6\nReceived: 1\n\n  20 |   expect(fuentes).toHaveLength(6);\n> 21 |   expect(new Set(fuentes).size).toBe(6); // seis imágenes distintas\n     |                                 ^\n    at verificarCatalogo (tests/catalogo.spec.ts:21:35)' },
    'CP-08': { evidencia: 'qa/evidencia/checkout-Checkout-CP-08-Checkout-completo-con-problem-user-chromium', ubicacion: 'checkout.spec.ts:43:7 › Checkout › CP-08 · Checkout completo con problem_user',
      mensaje: 'Error: expect(locator).toHaveValue(expected)\n\nLocator: getByTestId(\'lastName\')\nExpected string: "Pérez"\nReceived string: ""\nCall log:\n  - expect.toHaveValue with timeout 5000ms\n  - waiting for getByTestId(\'lastName\')\n    8 × locator resolved to <input type="text" id="last-name" data-test="lastName" name="lastName" placeholder="Last Name" value=""/>\n      - unexpected value ""\n\n  22 |   await page.getByTestId(\'postalCode\').fill(DATOS_CHECKOUT.codigoPostal);\n> 23 |   await expect(page.getByTestId(\'lastName\')).toHaveValue(DATOS_CHECKOUT.apellido);\n     |                                              ^\n    at checkoutCompleto (tests/checkout.spec.ts:23:46)' },
  };
  const DEFECTOS = { 'DEF-001': ['CP-08'], 'DEF-002': ['CP-05'] };
  const NOTA = '> Archivo de ejemplo del modo demo: no es una ejecución real de Playwright. Corre `python3 -m app` (sin `--demo`) para un ciclo real con el agente.\n\n';
  const resultadoDe = (caso) => RESULTADOS[caso.id] || (caso.precondicion.includes('[Criterio') ? ['PASÓ', 1.6, 'tests/historia.spec.ts (simulado)'] : ['BLOQUEADO', 0, '—']);
  const T = (texto, retraso = 0.9) => [retraso, { tipo: 'texto', texto }];
  const H = (resumen, nombre = 'demo', retraso = 0.6) => [retraso, { tipo: 'herramienta', nombre, resumen }];
  function guion(paso, app) {
    const url = app.url;
    return {
      'explorar-app': [H('Lee qa/requisitos.md', 'Read', 0.5), T('Leo los requisitos: cinco requisitos funcionales, cuatro escenarios obligatorios y cuatro usuarios de prueba. Abro la aplicación.'),
        H(`Navega a ${url}`, 'mcp__playwright__browser_navigate'), H('Lee la pantalla (snapshot de accesibilidad)', 'mcp__playwright__browser_snapshot'), H('Escribe «standard_user» en «Username»', 'mcp__playwright__browser_type'),
        H('Escribe «secret_sauce» en «Password»', 'mcp__playwright__browser_type'), H('Clic en «Login»', 'mcp__playwright__browser_click'), H('Lee la pantalla (snapshot de accesibilidad)', 'mcp__playwright__browser_snapshot'),
        T('Catálogo con seis productos, selector de orden y carrito. Los controles tienen atributo `data-test`; los uso como localizadores.'),
        H('Clic en «Add to cart» (Sauce Labs Backpack)', 'mcp__playwright__browser_click'), H('Clic en el ícono del carrito', 'mcp__playwright__browser_click'), H('Clic en «Checkout»', 'mcp__playwright__browser_click'),
        H('Rellena el formulario', 'mcp__playwright__browser_fill_form'), H('Clic en «Continue»', 'mcp__playwright__browser_click'), H('Clic en «Finish»', 'mcp__playwright__browser_click'),
        T('Checkout completo con standard_user: subtotal $29.99, impuesto $2.40, total $32.39 y confirmación «Thank you for your order!». Repito el recorrido con problem_user.'),
        H('Clic en «Open Menu» → «Logout»', 'mcp__playwright__browser_click'), H('Escribe «problem_user» en «Username»', 'mcp__playwright__browser_type'), H('Clic en «Login»', 'mcp__playwright__browser_click'),
        H('Lee la pantalla (snapshot de accesibilidad)', 'mcp__playwright__browser_snapshot'), H('Toma una captura de pantalla', 'mcp__playwright__browser_take_screenshot'),
        T('Con problem_user las seis tarjetas muestran la misma imagen y el selector de orden no reordena. Lo anoto como «por verificar en el paso 3», no como defecto.'),
        H('Rellena el formulario de checkout', 'mcp__playwright__browser_fill_form'), H('Clic en «Continue»', 'mcp__playwright__browser_click'),
        T('El campo Apellido quedó vacío después de escribir y aparece «Error: Last Name is required». Lo anoto también. Cierro el navegador y escribo la exploración.'),
        H('Cierra el navegador', 'mcp__playwright__browser_close'), H('Escribe qa/exploracion.md', 'Write')],
      'disenar-plan': [H('Lee qa/requisitos.md', 'Read', 0.5), H('Lee qa/exploracion.md', 'Read', 0.5),
        T('Diseño un caso por camino feliz de cada requisito, dos negativos de inicio de sesión, uno de campos vacíos en el checkout y los cuatro escenarios obligatorios. Los casos con problem_user llevan las mismas expectativas que con standard_user.'),
        H('Escribe qa/plan-de-pruebas.md', 'Write'), H('Escribe qa/plan-de-pruebas.generado.md (copia intacta para medir las ediciones)', 'Write')],
      'ejecutar-pruebas': [H('Lee qa/plan-de-pruebas.md', 'Read', 0.5), T('El plan dice `Estado: APROBADO`. Leo la exploración para los localizadores y genero un archivo de prueba por flujo.'),
        H('Lee qa/exploracion.md', 'Read', 0.4), H('Lee tests/ejemplo.spec.ts', 'Read', 0.4), H('Escribe tests/login.spec.ts', 'Write'), H('Escribe tests/catalogo.spec.ts', 'Write'), H('Escribe tests/carrito.spec.ts', 'Write'),
        H('Escribe tests/checkout.spec.ts', 'Write'), H('Ejecuta: npx playwright test --reporter=list,html', 'Bash', 0.8)],
      'analizar-fallos': [H('Lee qa/resultados.md', 'Read', 0.5), T('Reviso cada prueba fallida: el mensaje de Playwright y la captura de su carpeta de evidencia.'), H('Lee qa/evidencia/…/test-failed-1.png', 'Read'),
        T('Las dos fallas son defectos de la aplicación, no pruebas frágiles: las mismas pruebas pasan con standard_user y los localizadores resolvieron bien. No hay nada que corregir en las pruebas.'),
        H('Escribe qa/defectos/DEF-001.md', 'Write'), H('Escribe qa/defectos/DEF-002.md', 'Write')],
      'reportar': [H('Lee qa/plan-de-pruebas.md y qa/plan-de-pruebas.generado.md', 'Read', 0.5), H('Lee qa/resultados.md', 'Read', 0.4), H('Lee qa/defectos/DEF-*.md', 'Read', 0.4),
        T('Comparo el plan aprobado con el generado fila por fila para la métrica del hito 1, cuento la cobertura por prioridad y aplico la regla del semáforo sobre los defectos confirmados.'), H('Escribe qa/reporte.md', 'Write')],
    }[paso] || [];
  }
  function salidaPlaywright(casos) {
    const lineas = [`Running ${casos.length} tests using 1 worker`, '']; const fallidos = []; let total = 0;
    casos.forEach((caso, i) => {
      const [r, seg, archivo] = resultadoDe(caso); total += seg; const nombre = `${caso.id} · ${caso.titulo}`;
      if (r === 'FALLÓ') { const err = ERRORES[caso.id] || {}; const u = err.ubicacion || `${archivo.split('/').pop()} › ${nombre}`; lineas.push(`  ✘  ${i + 1} [chromium] › ${u} (${seg.toFixed(1)}s)`); fallidos.push([u, err.mensaje || '']); }
      else if (r === 'BLOQUEADO') lineas.push(`  -  ${i + 1} [chromium] › ${nombre} (caso añadido por la persona; el modo demo no lo ejecuta)`);
      else lineas.push(`  ✓  ${i + 1} [chromium] › ${archivo.split('/').pop()} › ${nombre} (${seg.toFixed(1)}s)`);
    });
    lineas.push('');
    for (const [u, m] of fallidos) { lineas.push(`  1) [chromium] › ${u}`, '', ...m.split('\n').map((l) => '    ' + l), ''); }
    const pasados = casos.filter((c) => resultadoDe(c)[0] === 'PASÓ').length; const bloq = casos.filter((c) => resultadoDe(c)[0] === 'BLOQUEADO').length;
    if (fallidos.length) { lineas.push(`  ${fallidos.length} failed`); for (const [u] of fallidos) lineas.push(`    [chromium] › ${u}`); }
    if (bloq) lineas.push(`  ${bloq} skipped`);
    lineas.push(`  ${pasados} passed (${total.toFixed(1)}s)`, '', 'To open last HTML report run:\n\n  npx playwright show-report qa/reporte-html');
    return lineas.join('\n');
  }
  function generarResultados(casos, salida) {
    const n = (r) => casos.filter((c) => resultadoDe(c)[0] === r).length; const total = casos.reduce((s, c) => s + resultadoDe(c)[1], 0);
    const md = [NOTA.trim(), '', '# Resultados de la ejecución', '', '## Resumen', '', `- Casos planificados: ${casos.length}`, `- Casos ejecutados: ${casos.length - n('BLOQUEADO')}`, `- Pasaron: ${n('PASÓ')}`, `- Fallaron: ${n('FALLÓ')}`, `- Bloqueados: ${n('BLOQUEADO')}`,
      `- Duración total: ${total.toFixed(1)} s`, `- Fecha y hora: ${ahora()}`, '', '## Tabla de resultados', '', '| ID | Título | Usuario | Resultado | Duración | Archivo de prueba | Evidencia |', '|----|--------|---------|-----------|----------|-------------------|-----------|'];
    for (const c of casos) { const [r, seg, archivo] = resultadoDe(c); md.push(`| ${c.id} | ${c.titulo} | ${c.usuario} | ${r} | ${seg.toFixed(1)} s | ${archivo} | ${r === 'FALLÓ' ? (ERRORES[c.id] || {}).evidencia || '—' : '—'} |`); }
    md.push('', '## Pruebas corregidas', '', `Ninguna: las ${casos.length} pruebas corrieron con los localizadores de la exploración sin ajustes.`, '', '## Salida de Playwright', '', '```', salida, '```', '');
    return md.join('\n');
  }
  function generarDefectos(casos) {
    const fallidos = new Set(casos.filter((c) => resultadoDe(c)[0] === 'FALLÓ').map((c) => c.id)); const creados = [];
    for (const [id, rel] of Object.entries(DEFECTOS)) if (rel.some((c) => fallidos.has(c))) { escribir(`qa/defectos/${id}.md`, ARCHIVOS.ejemplos[`${id}.md`]); creados.push(id); }
    if (!creados.length) escribir('qa/defectos/README.md', '# Defectos\n\nNo se encontraron defectos en este ciclo: todas las pruebas ejecutadas pasaron.\n');
    return creados;
  }
  function generarReporte() {
    const plan = planInfo(), casos = plan.casos, resultados = resultadosInfo(), defectos = defectosInfo(), app = aplicacion(), comp = compararPlanes() || {};
    const confirmados = defectos.lista.filter((d) => d.estado === 'CONFIRMADO'), descartados = defectos.lista.filter((d) => d.estado === 'DESCARTADO');
    let semaforo, regla;
    if (confirmados.some((d) => d.severidad === 'Crítica')) [semaforo, regla] = ['🔴 No publicar', 'hay al menos un defecto Crítico confirmado'];
    else if (confirmados.some((d) => d.severidad === 'Alta')) [semaforo, regla] = ['🟡 Publicar con riesgo conocido', 'hay defectos Altos confirmados y ninguno Crítico'];
    else [semaforo, regla] = ['🟢 Publicar', 'no hay defectos Críticos ni Altos confirmados'];
    const por = {};
    for (const c of casos) { const p = por[c.prioridad || 'Sin prioridad'] ||= { planificados: 0, pasaron: 0, fallaron: 0, bloqueados: 0 }; p.planificados++; const r = resultadoDe(c)[0]; p[r === 'PASÓ' ? 'pasaron' : r === 'FALLÓ' ? 'fallaron' : 'bloqueados']++; }
    const md = [NOTA.trim(), '', `# Reporte del ciclo · ${app.nombre}`, '', '## Resumen ejecutivo', '',
      `Se probaron los cinco requisitos funcionales de ${app.nombre} (${app.url}) con ${casos.length} casos aprobados por la persona: ${resultados.pasaron} pasaron, ${resultados.fallaron} fallaron${resultados.bloqueados ? ` y ${resultados.bloqueados} quedaron bloqueados` : ''}. La persona confirmó ${confirmados.length} defecto(s) y descartó ${descartados.length}. Recomendación: ${semaforo.split(' ').slice(1).join(' ').toLowerCase()}.`,
      '', '## Semáforo de la versión', '', `**${semaforo}** — regla aplicada: ${regla}.`, '', '## Cobertura', '', '| Prioridad | Planificados | Pasaron | Fallaron | Bloqueados |', '|---|---|---|---|---|'];
    for (const pr of ['Alta', 'Media', 'Baja']) if (por[pr]) md.push(`| ${pr} | ${por[pr].planificados} | ${por[pr].pasaron} | ${por[pr].fallaron} | ${por[pr].bloqueados} |`);
    md.push('', '## Defectos confirmados', '');
    if (confirmados.length) { md.push('| ID | Título | Severidad | Casos | Evidencia |', '|---|---|---|---|---|'); for (const d of confirmados) md.push(`| ${d.id} | ${d.titulo} | ${d.severidad} | ${d.casos} | ${d.evidencia} |`); } else md.push('Ninguno.');
    md.push('', '## Defectos descartados', '');
    if (descartados.length) for (const d of descartados) md.push(`- ${d.id} · ${d.titulo} — motivo: ${d.motivo || 'sin motivo registrado'}`); else md.push('Ninguno.');
    md.push('', '## Métricas del ciclo', '', `- Casos generados por el agente: ${comp.generados ?? casos.length}`,
      `- Casos aceptados sin edición: ${(comp.aceptados || []).length} (${comp.porcentaje_aceptados ?? 0}%) · editados: ${(comp.editados || []).length} · rechazados: ${(comp.rechazados || []).length} · añadidos por la persona: ${(comp.anadidos || []).length}`,
      '- Pruebas que el agente tuvo que corregir por localizador o espera: 0', `- Fin del ciclo: ${ahora()}`, '', '## Las pruebas quedan en el repositorio', '',
      'Las pruebas de `tests/` corren sin el agente: `npx playwright test`. El reporte HTML de la última ejecución se abre con `npx playwright show-report qa/reporte-html`.', '', '## Próximos pasos', '');
    if (confirmados.length) md.push(`1. Corregir ${confirmados.map((d) => d.id).join(', ')} y volver a correr solo esos casos: \`npx playwright test -g "${confirmados.flatMap((d) => d.casos.split(',').map((c) => c.trim())).join('|')}"\`.`);
    md.push('2. Añadir al plan el caso del botón «Add to cart» que no responde con problem_user, observado en la exploración.', '3. Incluir `performance_glitch_user` en el próximo ciclo para medir tiempos de carga.', '');
    return md.join('\n');
  }
  function generarPlanDesdeHistoria() {
    const h = historiaInfo(); const criterios = criteriosDeHistoria().length ? criteriosDeHistoria() : ['La funcionalidad descrita en la historia se completa sin errores']; const app = aplicacion();
    const negativos = ['obligatorio', 'requerido', 'vacío', 'vacio', 'inválid', 'invalid', 'incorrect', 'error', 'sin permiso', 'bloquead'];
    const filas = []; let n = 0;
    criterios.forEach((c, i) => {
      n++; const titulo = c.length <= 70 ? c : c.slice(0, 67).trimEnd() + '…';
      filas.push(`| CP-${String(n).padStart(2, '0')} | ${titulo} | ${i < 2 ? 'Alta' : 'Media'} | standard_user | [Criterio ${i + 1}] Sesión iniciada en ${app.url} | 1. Ir a la pantalla que cubre el criterio  2. Ejecutar la acción descrita  3. Observar el resultado | ${c} |`);
      if (negativos.some((p) => c.toLowerCase().includes(p))) { n++; filas.push(`| CP-${String(n).padStart(2, '0')} | ${titulo} (caso negativo) | Media | standard_user | [Criterio ${i + 1}] Sesión iniciada | 1. Ir a la pantalla que cubre el criterio  2. Provocar la condición contraria  3. Observar el mensaje | Se muestra un mensaje de error y no se completa la acción |`); }
    });
    return `# Plan de pruebas · ${app.nombre} · historia «${h.titulo}»\n\n> Plan de ejemplo del modo demo, derivado de la historia con una regla simple (un caso por criterio). En modo real el agente usa la exploración para escribir pasos y localizadores concretos.\n\n## Objetivo y alcance\n\nVerificar la historia «${h.titulo}» sobre ${app.nombre} (${app.url}) a través de sus criterios de aceptación:\n\n${criterios.map((c, i) => `${i + 1}. ${c}`).join('\n')}\n\n## Datos de prueba\n\n- Usuario: \`standard_user\` / \`secret_sauce\`.\n\n## Casos de prueba\n\n| ID | Título | Prioridad | Usuario | Precondición | Pasos | Resultado esperado |\n|----|--------|-----------|---------|--------------|-------|--------------------|\n${filas.join('\n')}\n\n## Riesgos y supuestos\n\n- Los criterios que no se puedan verificar en la aplicación se anotan aquí al ejecutar.\n\nEstado: PENDIENTE DE APROBACIÓN\n`;
  }
  // La presentación de la skill /inicio en su variante para la interfaz web (.claude/skills/inicio/SKILL.md).
  function saludo() {
    return `👋 Hola, soy el **Agente Virtual de QA**.\n\nPruebo aplicaciones web de principio a fin en cinco pasos:\n\n1. **Entiendo** la aplicación navegándola\n2. **Diseño** el plan de pruebas, a partir de los requisitos o de una historia de usuario · *tú apruebas el plan*\n3. **Ejecuto** las pruebas con Playwright\n4. **Analizo** los fallos y documento los defectos · *tú confirmas cada defecto*\n5. **Reporto** el estado de la versión\n\nCada paso lo inicias tú con el botón de abajo; yo nunca salto al siguiente por mi cuenta. Todo lo que produzco queda como archivos en \`qa/\` y \`tests/\`, aparece en esta conversación, y las pruebas siguen funcionando sin mí.\n\nAbajo, en «¿Qué sigue?», tienes siempre el siguiente paso.`;
  }
  const esperar = (s) => new Promise((r) => { const t = setTimeout(r, s * 1000 * VELOCIDAD); temporizadores.push(t); });
  async function correr(paso, prompt) {
    const inicio = Date.now() / 1000; const desde = secuencia;
    publicar({ tipo: 'inicio', paso, prompt, modo: MODO });
    publicar({ tipo: 'sistema', texto: 'Modo demo: ciclo de ejemplo, sin llamadas a la API ni navegador.' });
    const app = aplicacion(); let resumen = 'Paso desconocido.';
    try {
      if (paso === 'inicio') { await esperar(0.6); resumen = saludo(); }
      else if (!paso) { await esperar(0.6); resumen = /^\/inicio|^hola/i.test(prompt.trim()) ? saludo() : 'En modo demo solo ejecuto los cinco pasos del ciclo desde el hilo. Para conversar con el agente real, arranca la aplicación sin `--demo`.'; }
      else {
        for (const [retraso, ev] of guion(paso, app)) { await esperar(retraso); publicar(ev); }
        if (paso === 'explorar-app') { escribir(DOCS.exploracion, ARCHIVOS.ejemplos['exploracion.md']); marcar(DOCS.exploracion);
          resumen = 'Exploré Swag Labs con standard_user y problem_user: 7 pantallas, 3 flujos de inicio de sesión, catálogo, carrito y checkout completo.\nTodos los controles tienen atributo `data-test`; los localizadores quedaron en `qa/exploracion.md`.\nCon problem_user vi tres cosas distintas: la misma imagen en los seis productos, el selector de orden sin efecto y el campo Apellido del checkout que no conserva el texto.\nLas dejé como «por verificar en el paso 3», no como defectos.\nSiguiente paso: /disenar-plan'; }
        else if (paso === 'disenar-plan') {
          const h = historiaInfo(); let texto;
          if (h.existe) { publicar({ tipo: 'herramienta', nombre: 'Read', resumen: 'Lee qa/historia-de-usuario.md' }); texto = generarPlanDesdeHistoria(); } else texto = ARCHIVOS.ejemplos['plan-de-pruebas.md'];
          escribir(DOCS.plan, texto); escribir(DOCS['plan-generado'], texto); marcar(DOCS.plan);
          const casos = planInfo().casos; const tabla = casos.map((c) => `| ${c.id} | ${c.titulo} | ${c.prioridad} | ${c.usuario} |`).join('\n');
          resumen = `${h.existe ? `Partí de la historia de usuario «${h.titulo}» y de sus ${h.criterios} criterios de aceptación` : 'Partí de los requisitos y de la exploración'}. Diseñé ${casos.length} casos de prueba:\n\n| ID | Título | Prioridad | Usuario |\n|---|---|---|---|\n${tabla}\n\n¿Apruebas el plan? Puedes quitar casos o editar el texto antes de continuar. Nada se ejecuta hasta que apruebes.`; }
        else if (paso === 'ejecutar-pruebas') {
          const plan = planInfo();
          if (!plan.aprobado) resumen = 'El plan no dice `Estado: APROBADO`. Apruébalo antes de ejecutar las pruebas.';
          else {
            for (const [n, c] of Object.entries(ARCHIVOS.tests)) if (n !== 'datos.ts' && n !== 'ejemplo.spec.ts') escribir('tests/' + n, c);
            const casos = plan.casos; const salida = salidaPlaywright(casos); await esperar(1.2);
            publicar({ tipo: 'salida', nombre: 'Bash', ok: !casos.some((c) => resultadoDe(c)[0] === 'FALLÓ'), texto: salida });
            for (const c of casos) if (resultadoDe(c)[0] === 'FALLÓ' && ERRORES[c.id]) { const carpeta = ERRORES[c.id].evidencia.replace('qa/evidencia/', ''); escribir(`qa/evidencia/${carpeta}/test-failed-1.png`, '(png)'); }
            escribir(DOCS.resultados, generarResultados(casos, salida)); marcar(DOCS.resultados);
            publicar({ tipo: 'herramienta', nombre: 'Write', resumen: 'Escribe qa/resultados.md' });
            const p = casos.filter((c) => resultadoDe(c)[0] === 'PASÓ').length, f = casos.filter((c) => resultadoDe(c)[0] === 'FALLÓ').length;
            resumen = `Ejecuté ${casos.length} casos: ${p} pasaron y ${f} fallaron${f === 2 ? ' (los dos con problem_user, como anticipaba la exploración)' : ''}. La evidencia de cada fallo quedó en \`qa/evidencia/\` y los resultados en \`qa/resultados.md\`.\nSiguiente paso: /analizar-fallos`;
          }
        } else if (paso === 'analizar-fallos') {
          const creados = generarDefectos(planInfo().casos);
          if (!creados.length) resumen = 'No hubo pruebas fallidas en este ciclo; dejé la nota en `qa/defectos/README.md`.\nSiguiente paso: /reportar';
          else resumen = `Documenté ${creados.length} defecto(s) con evidencia:\n\n${defectosInfo().lista.map((d) => `- ${d.id} · ${d.titulo} · ${d.severidad}`).join('\n')}\n\n¿Confirmas estos defectos? Confírmalos o descártalos con un motivo y después genera el reporte.`;
        } else if (paso === 'reportar') {
          const d = defectosInfo();
          if (d.pendientes) resumen = `Hay ${d.pendientes} defecto(s) pendientes de confirmación. Decide cada uno antes del reporte.`;
          else { escribir(DOCS.reporte, generarReporte()); marcar(DOCS.reporte); const info = reporteInfo(); const comp = compararPlanes() || {};
            resumen = `Reporte listo en \`qa/reporte.md\`. Semáforo: **${{ rojo: '🔴 No publicar', amarillo: '🟡 Publicar con riesgo conocido', verde: '🟢 Publicar' }[info.semaforo] || ''}**. Defectos confirmados: ${d.confirmados}; descartados: ${d.descartados}. Casos aceptados sin edición: ${(comp.aceptados || []).length} de ${comp.generados || 0} (${comp.porcentaje_aceptados || 0}%). Las pruebas quedan en \`tests/\` y corren con \`npx playwright test\`.`; }
        }
      }
      ultimo = { tipo: 'fin', paso, ok: true, resumen, duracion_ms: Math.round((Date.now() / 1000 - inicio) * 1000), costo_usd: null, turnos: null };
    } catch (e) {
      ultimo = { tipo: 'fin', paso, ok: false, resumen: e && e.cancelado ? 'Paso cancelado desde la interfaz.' : `Error: ${e}`, cancelado: !!(e && e.cancelado), duracion_ms: Math.round((Date.now() / 1000 - inicio) * 1000) };
    }
    actual = null; publicar(ultimo); publicar({ tipo: 'estado' });
    if (paso === 'inicio' && !ultimo.cancelado) {
      presentacion = { clave: clavePresentacion(), fecha: ahora(), texto: ultimo.ok ? resumen : null, error: ultimo.ok ? null : resumen };
      // La interfaz la pinta desde el estado; sus eventos sobran en el historial que se reenvía al recargar.
      if (ultimo.ok) { const hasta = secuencia; const quedan = historial.filter((e) => !(desde < e.n && e.n <= hasta)); historial.length = 0; historial.push(...quedan); }
    }
  }
  function iniciar(paso, prompt) { if (ocupado()) throw { status: 409, detail: 'El agente ya está trabajando; espera a que termine o cancélalo.' }; actual = { paso, prompt, inicio: Date.now() / 1000 }; correr(paso, prompt); }
  function cancelar() { if (!ocupado()) return false; for (const t of temporizadores) clearTimeout(t); temporizadores = []; const paso = actual.paso; actual = null;
    ultimo = { tipo: 'fin', paso, ok: false, cancelado: true, resumen: 'Paso cancelado desde la interfaz.', duracion_ms: 0 }; publicar(ultimo); publicar({ tipo: 'estado' }); return true; }

  // ------------------------------------------------------------ enrutador de fetch
  const json = (datos, status = 200) => new Response(JSON.stringify(datos), { status, headers: { 'Content-Type': 'application/json' } });
  const error = (e) => json({ detail: e.detail || String(e) }, e.status || 500);
  window.fetch = async function (entrada, opciones = {}) {
    const url = new URL(typeof entrada === 'string' ? entrada : entrada.url, 'http://demo.local');
    const metodo = (opciones.method || 'GET').toUpperCase(); const ruta = url.pathname;
    let cuerpo = {}; try { cuerpo = opciones.body ? JSON.parse(opciones.body) : {}; } catch (e) { cuerpo = {}; }
    try {
      let m;
      if (ruta === '/api/salud') return new Response(`ok · modo ${MODO} · vista previa`);
      if (ruta === '/api/estado') return json(estado());
      if ((m = ruta.match(/^\/api\/documento\/([a-z-]+)$/))) {
        const n = m[1]; if (!(n in DOCS)) return json({ detail: 'Documento desconocido' }, 404);
        if (metodo === 'PUT') { if (!['requisitos', 'plan', 'historia'].includes(n)) return json({ detail: 'Solo se editan los requisitos, la historia y el plan' }, 400);
          escribir(DOCS[n], (cuerpo.markdown || '').trimEnd() + '\n'); marcar(DOCS[n]); publicar({ tipo: 'estado' }); }
        const t = leer(DOCS[n]); return json({ nombre: n, existe: t !== null, markdown: t || '', ruta: DOCS[n] });
      }
      if (ruta === '/api/plan/aprobar' && metodo === 'POST') { const p = aprobarPlan(cuerpo.markdown ?? null, cuerpo.excluir || []); publicar({ tipo: 'decision', texto: `Plan aprobado desde la interfaz con ${p.casos.length} casos.` }); publicar({ tipo: 'estado' }); const { casos, ...resto } = p; return json({ plan: resto, casos }); }
      if (ruta === '/api/plan/desaprobar' && metodo === 'POST') { const p = desaprobarPlan(); publicar({ tipo: 'estado' }); const { casos, ...resto } = p; return json({ plan: resto, casos }); }
      if (ruta === '/api/defectos') return json(defectosInfo());
      if ((m = ruta.match(/^\/api\/defectos\/(DEF-\d+)$/))) { const d = defectosInfo().lista.find((x) => x.id === m[1]); return d ? json(d) : json({ detail: 'No existe' }, 404); }
      if ((m = ruta.match(/^\/api\/defectos\/(DEF-\d+)\/estado$/)) && metodo === 'POST') { const d = cambiarEstadoDefecto(m[1], cuerpo.estado, cuerpo.motivo || ''); publicar({ tipo: 'decision', texto: `${m[1]} marcado como ${d.estado} desde la interfaz${cuerpo.motivo ? ': ' + cuerpo.motivo : '.'}` }); publicar({ tipo: 'estado' }); return json(d); }
      if (ruta === '/api/pruebas') return json({ pruebas: pruebas() });
      if ((m = ruta.match(/^\/api\/pasos\/([a-z-]+)$/)) && metodo === 'POST') {
        const est = estado(); const info = est.pasos.find((p) => p.id === m[1]); if (!info) return json({ detail: 'Paso desconocido' }, 404);
        if (ocupado()) return json({ detail: 'El agente ya está trabajando; espera a que termine o cancélalo.' }, 409);
        if (!info.disponible) return json({ detail: `El paso ${info.numero} todavía no está disponible: falta lo anterior o una decisión tuya.` }, 409);
        let args = (cuerpo.argumentos || '').trim();
        if (m[1] === 'explorar-app' && !args) args = est.aplicacion.url;
        if (m[1] === 'disenar-plan' && !args && est.historia.existe) args = 'a partir de la historia de usuario de qa/historia-de-usuario.md';
        const prompt = `${info.comando} ${args}`.trim(); iniciar(m[1], prompt); return json({ ok: true, paso: m[1], prompt }, 202);
      }
      if (ruta === '/api/presentacion' && metodo === 'POST') { if (ocupado()) return json({ detail: 'El agente ya está trabajando; espera a que termine o cancélalo.' }, 409); iniciar('inicio', '/inicio desde la interfaz web'); return json({ ok: true, paso: 'inicio' }, 202); }
      if (ruta === '/api/agente/mensaje' && metodo === 'POST') { let prompt = (cuerpo.prompt || '').trim(); if (!prompt) return json({ detail: 'Mensaje vacío' }, 400); if (prompt === '/inicio') prompt = '/inicio desde la interfaz web';
        if (ocupado()) return json({ detail: 'El agente ya está trabajando; espera a que termine o cancélalo.' }, 409);
        const paso = PASOS.map((p) => p.id).find((id) => prompt.startsWith('/' + id)) || null; iniciar(paso, prompt); return json({ ok: true, paso, prompt }, 202); }
      if (ruta === '/api/agente/cancelar' && metodo === 'POST') return json({ cancelado: cancelar() });
      if (ruta === '/api/ciclo/reiniciar' && metodo === 'POST') { if (ocupado()) return json({ detail: 'El agente está trabajando; cancélalo antes.' }, 409); const r = reiniciar(); publicar({ tipo: 'sistema', texto: 'Ciclo reiniciado desde la interfaz' + (r.archivado_en ? `; el anterior quedó en ${r.archivado_en}.` : '.') }); publicar({ tipo: 'estado' }); return json(r); }
      if (ruta === '/api/historia' && metodo === 'POST') { if (!((cuerpo.texto || '').trim() || (cuerpo.criterios || []).some((c) => c.trim()))) return json({ detail: 'Escribe la historia o al menos un criterio de aceptación' }, 400);
        const info = guardarHistoria(cuerpo); publicar({ tipo: 'decision', texto: `Historia de usuario guardada: ${info.titulo} (${info.criterios} criterios). El plan partirá de ella.` }); publicar({ tipo: 'estado' }); return json(info); }
      if (ruta === '/api/historia' && metodo === 'DELETE') { borrar(DOCS.historia); publicar({ tipo: 'estado' }); return json({ existe: false }); }
      return json({ detail: `Ruta no simulada: ${metodo} ${ruta}` }, 404);
    } catch (e) { return error(e); }
  };
})();
