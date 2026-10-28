"""Genera registros verificables a partir del motor, sin emular resultados."""
import sys
import json
from pathlib import Path
from datetime import date

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from motor import procesar

casos = [
    {'archivo':'01_aritmetica_basica.pseudo','titulo':'Asignación y precedencia aritmética','entradas':[],
     'esperado':'Resultado: 18','estado':'correcto'},
    {'archivo':'02_parentesis_decimales.pseudo','titulo':'Paréntesis y números decimales','entradas':[],
     'esperado':'Total: 5','estado':'correcto'},
    {'archivo':'03_entrada_edad.pseudo','titulo':'Entrada de número entero','entradas':['21'],
     'esperado':'Edad ingresada: 21','estado':'correcto'},
    {'archivo':'04_entrada_nombre.pseudo','titulo':'Entrada y salida de texto','entradas':['Ana'],
     'esperado':'Hola, Ana!','estado':'correcto'},
    {'archivo':'05_condicion_verdadera.pseudo','titulo':'Condición verdadera','entradas':[],
     'esperado':'Es mayor de edad','estado':'correcto'},
    {'archivo':'06_condicion_falsa.pseudo','titulo':'Condición falsa','entradas':[],
     'esperado':'Reprobado','estado':'correcto'},
    {'archivo':'07_error_lexico.pseudo','titulo':'Detección de símbolo inválido','entradas':[],
     'esperado':'Error léxico, línea 3, carácter @','estado':'error', 'categoria':'Error lexico','linea':3},
    {'archivo':'08_error_sintactico.pseudo','titulo':'Falta de punto y coma','entradas':[],
     'esperado':'Error sintáctico, línea 4, falta ;','estado':'error','categoria':'Error sintactico','linea':4},
    {'archivo':'09_division_cero.pseudo','titulo':'Control de división entre cero','entradas':[],
     'esperado':'Error de ejecución: división entre cero','estado':'error','categoria':'Error de ejecucion','fragmento':'Division entre cero'},
    {'archivo':'10_variable_sin_declarar.pseudo','titulo':'Control de variable no declarada','entradas':[],
     'esperado':'Error de ejecución: variable no declarada','estado':'error','categoria':'Error de ejecucion','fragmento':'no esta declarada'},
]
registros=[]
for i,c in enumerate(casos,1):
    codigo=(BASE/'ejemplos'/c['archivo']).read_text(encoding='utf-8')
    r=procesar(codigo,c['entradas'])
    aprobado=r['estado']==c['estado']
    if c['estado']=='correcto':
        aprobado=aprobado and '\n'.join(r.get('salida',[]))==c['esperado']
    else:
        aprobado=(aprobado and r['error']['categoria']==c['categoria']
                  and ('linea' not in c or r['error']['linea']==c['linea'])
                  and ('fragmento' not in c or c['fragmento'] in r['mensaje']))
    registros.append({**c, 'numero':i, 'codigo':codigo, 'resultado':r,
                      'resultado_obtenido':'\n'.join(r['salida']) if c['estado']=='correcto' else r['mensaje'],
                      'aprobada':aprobado})

(BASE/'documentacion'/'registros_pruebas.json').write_text(json.dumps(registros,ensure_ascii=False,indent=2),encoding='utf-8')

salida=['# Registro de las diez pruebas obligatorias',
        '',f'Fecha de ejecución: {date(2026,10,28).isoformat()}.',
        'Generación: `python documentacion/generar_registros.py` sobre el motor real.',
        'Una prueba de error es aprobada si se detecta el error previsto, no si ejecuta código inválido.',
        '',f'**Resultado general: {sum(c["aprobada"] for c in registros)}/10 aprobadas.**','']
for c in registros:
    salida.extend([f'## Prueba {c["numero"]:02d}: {c["titulo"]}','',
                   '**Código ingresado**','', '```text',c['codigo'].rstrip(),'```','',
                   '**Datos de entrada:** '+(', '.join(repr(x) for x in c['entradas']) if c['entradas'] else 'No aplica.'),'',
                   '**Resultado esperado:** '+c['esperado'],'',
                   '**Resultado obtenido (registro de ejecución):**','', '```text',c['resultado_obtenido'],'```','',
                   '**Estado de prueba:** '+('APROBADA' if c['aprobada'] else 'FALLIDA'), '', '---',''])

codigo_demo=(BASE/'ejemplos'/'01_aritmetica_basica.pseudo').read_text(encoding='utf-8')
resp=procesar(codigo_demo,solo_analizar=True)
salida += ['# Evidencia del análisis léxico', '',
           'Se analizaron los tokens del programa `01_aritmetica_basica.pseudo`.','',
           '| # | Lexema | Clase | Línea | Columna |','|---:|---|---|---:|---:|']
for i,t in enumerate(resp['tokens'],1):
    lex=t['lexema'].replace('|','\\|')
    salida.append(f'| {i} | `{lex}` | `{t["tipo"]}` | {t["linea"]} | {t["columna"]} |')
salida += ['',f'Total: {len(resp["tokens"])} tokens.',
           'En `documentacion/GRAMATICA.md` se documentan las expresiones regulares y el autómata del identificador.']
(BASE/'documentacion'/'PRUEBAS.md').write_text('\n'.join(salida)+'\n',encoding='utf-8')
print('Pruebas ejecutadas y registradas:',sum(c['aprobada'] for c in registros),'/',len(registros))
if not all(c['aprobada'] for c in registros):
    raise SystemExit('Se detectaron pruebas fallidas')
