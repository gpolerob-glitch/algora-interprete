'use strict';
const editor = document.getElementById('editor');
const terminal = document.getElementById('terminal');
const tokensBody = document.getElementById('tokens');
const formEntrada = document.getElementById('form-entrada');
const valorEntrada = document.getElementById('valor-entrada');
const etiquetaEntrada = document.getElementById('etiqueta-entrada');
let entradas = [];
let programaActual = '';
let ejecucionActiva = false;

function lineaConsola(contenido, estilo='normal') {
  const div = document.createElement('div');
  div.className = `console-line ${estilo}`;
  div.textContent = contenido;
  terminal.appendChild(div);
  terminal.scrollTop = terminal.scrollHeight;
}
function limpiarTerminal() { terminal.replaceChildren(); formEntrada.hidden = true; }
function editarLineas() {
  const n = Math.max(editor.value.split('\n').length, 1);
  document.getElementById('line-count').textContent = `${n} líneas`;
  document.getElementById('line-numbers').textContent = Array.from({length:n}, (_,i)=>i+1).join('\n');
}
function mostrarTokens(lista=[]) {
  tokensBody.replaceChildren();
  document.getElementById('token-count').textContent = `${lista.length} tokens`;
  if (!lista.length) {
    const tr=document.createElement('tr'), td=document.createElement('td');
    td.colSpan=3; td.className='token-empty'; td.textContent='Sin tokens disponibles.';
    tr.appendChild(td); tokensBody.appendChild(tr); return;
  }
  lista.forEach(t => {
    const tr=document.createElement('tr');
    const lex=document.createElement('td'); lex.textContent=t.lexema; lex.className='token-lexema';
    const typ=document.createElement('td'); const chip=document.createElement('span');
    chip.className='token-chip'; chip.textContent=t.tipo; typ.appendChild(chip);
    const ln=document.createElement('td'); ln.textContent=t.linea;
    tr.append(lex,typ,ln); tokensBody.appendChild(tr);
  });
}
async function solicitud(ruta, cuerpo) {
  const res=await fetch(ruta,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cuerpo)});
  const data=await res.json();
  if(!res.ok) throw new Error(data.error || 'No se pudo consultar el servidor.');
  return data;
}
function presentarResultado(datos) {
  mostrarTokens(datos.tokens || []);
  limpiarTerminal();
  if (datos.error) {
    lineaConsola(`✕ ${datos.error.categoria} · línea ${datos.error.linea}, columna ${datos.error.columna}`, 'console-error');
    lineaConsola(datos.error.mensaje, 'console-error-detail');
  } else if (datos.estado==='analizado') {
    lineaConsola('✓ Análisis léxico y sintáctico completado.', 'console-success');
    lineaConsola(`${datos.nombre_algoritmo} · ${datos.tokens.length} tokens · ${datos.cantidad_instrucciones} instrucciones de nivel superior`, 'console-muted');
  } else {
    lineaConsola(`✓ ${datos.nombre_algoritmo} · salida del programa`, 'console-success');
    (datos.salida || []).forEach(s => lineaConsola(s, 'console-output'));
    if (datos.estado==='correcto') {
      lineaConsola('— Fin de la ejecución —', 'console-muted');
    } else if (datos.estado==='esperando_entrada') {
      const v=datos.entrada_solicitada;
      lineaConsola(`? Leer ${v.nombre} (${v.tipo})`, 'console-input-prompt');
      etiquetaEntrada.textContent = `Ingrese ${v.nombre} · tipo ${v.tipo}`;
      valorEntrada.value='';
      valorEntrada.placeholder = v.tipo==='TEXTO' ? 'Escribe cualquier texto…' : (v.tipo==='ENTERO' ? 'Ej. 18' : 'Ej. 15.5');
      formEntrada.hidden=false;
      valorEntrada.focus();
    }
  }
}
async function ejecutar(continuar=false) {
  try {
    if (!continuar) { entradas=[]; programaActual=editor.value; }
    const datos=await solicitud('/api/ejecutar', {codigo:programaActual, entradas});
    ejecucionActiva = datos.estado==='esperando_entrada';
    presentarResultado(datos);
  } catch(error) { limpiarTerminal(); lineaConsola(`No se pudo ejecutar: ${error.message}`, 'console-error'); }
}
async function analizar() {
  ejecucionActiva=false;
  try { presentarResultado(await solicitud('/api/analizar',{codigo:editor.value})); }
  catch(error) { limpiarTerminal(); lineaConsola(`No se pudo analizar: ${error.message}`, 'console-error'); }
}
formEntrada.addEventListener('submit', e => {
  e.preventDefault();
  if (!ejecucionActiva) return;
  entradas.push(valorEntrada.value);
  ejecutar(true);
});
editor.addEventListener('input', editarLineas);
editor.addEventListener('scroll', () => document.getElementById('line-numbers').scrollTop=editor.scrollTop);
editor.addEventListener('keydown', e => {
  if(e.key==='Tab') {
    e.preventDefault(); const a=editor.selectionStart,b=editor.selectionEnd;
    editor.setRangeText('    ',a,b,'end'); editarLineas();
  }
  if(e.ctrlKey && e.key==='Enter') { e.preventDefault(); ejecutar(); }
});
document.getElementById('btn-ejecutar').addEventListener('click',()=>ejecutar());
document.getElementById('btn-analizar').addEventListener('click',analizar);
document.getElementById('btn-limpiar').addEventListener('click',()=>{editor.value='';editarLineas();mostrarTokens();limpiarTerminal();ejecucionActiva=false;editor.focus();});
document.getElementById('btn-borrar-salida').addEventListener('click',()=>{limpiarTerminal();ejecucionActiva=false;});
for(const btn of document.querySelectorAll('[data-vista]')) {
  btn.addEventListener('click',()=>{
    document.querySelectorAll('[data-vista]').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.vista').forEach(v => v.hidden = true);
    document.getElementById(`vista-${btn.dataset.vista}`).hidden=false;
  });
}
async function cargarEjemplos() {
  try {
    const res=await fetch('/api/ejemplos'); const ejemplos=await res.json();
    const contenedor=document.getElementById('lista-ejemplos');
    ejemplos.forEach((ej,i)=>{
      const b=document.createElement('button'); b.className='example-item';
      const ico=document.createElement('span'); ico.className='example-icon'; ico.textContent=String(i+1).padStart(2,'0');
      const tit=document.createElement('span'); tit.textContent=ej.nombre.replace(/^\d+ /,'');
      b.append(ico,tit);
      b.addEventListener('click',()=>{
        editor.value=ej.codigo; editarLineas(); limpiarTerminal(); mostrarTokens(); ejecucionActiva=false;
        document.querySelector('[data-vista="laboratorio"]').click();
        contenedor.querySelectorAll('.example-item').forEach(x=>x.classList.remove('selected'));
        b.classList.add('selected');
      });
      contenedor.appendChild(b);
    });
    if(ejemplos.length) contenedor.firstChild.click();
  } catch(err) { lineaConsola('No se pudo cargar la lista de ejemplos.', 'console-error'); }
}
editarLineas(); cargarEjemplos();
