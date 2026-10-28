# ALGORA - Intérprete educativo de pseudocódigo

Aplicación web local desarrollada para el curso de **Autómatas y Lenguajes Formales**. Permite editar y ejecutar un lenguaje de pseudocódigo con palabras reservadas en español, mostrar tokens y localizar errores léxicos, sintácticos y de ejecución.

## Requisitos previos

- Python **3.10 o superior**.
- Navegador moderno (Chrome, Edge o Firefox).
- No requiere `pip install` ni bases de datos. El servidor utiliza bibliotecas estándar de Python.

## Cómo iniciarlo

1. Descarga o clona el repositorio de GitHub y abre la carpeta `Interprete_Educativo`.
2. Abre una terminal en esa carpeta y ejecuta:
   ```bash
   python app.py
   ```
   En Windows también puede funcionar `py app.py` o hacer doble clic en `INICIAR_WINDOWS.bat`.
3. Abre en el navegador **http://localhost:8000**.
4. Selecciona un ejemplo de la barra izquierda o escribe tu programa, y presiona **Analizar** para ver tokens o **Ejecutar programa** para procesarlo.
5. Para parar el servidor usa `Ctrl + C` en la terminal.

Si el puerto 8000 está ocupado, inicia `python app.py --puerto 8080` y abre `http://localhost:8080`.

## Ejemplo

```text
Algoritmo Saludo
    Definir nombre Como Texto;
    Leer(nombre);
    Escribir("Hola, ", nombre, "!");
FinAlgoritmo
```

El navegador solicita un nombre al ejecutar y lo presenta en la consola. Las palabras reservadas incluyen `Algoritmo`, `FinAlgoritmo`, `Definir`, `Como`, `Entero`, `Decimal`, `Texto`, `Leer`, `Escribir`, `Si`, `SiNo`, `Entonces` y `FinSi`.

## Componentes

| Archivo / carpeta | Función |
|---|---|
| `app.py` | Servidor web local; endpoints `/api/analizar`, `/api/ejecutar` y `/api/ejemplos`. |
| `motor.py` | Tokenizador regex, parser descendente recursivo, AST e intérprete. |
| `static/index.html` | Interfaz con editor, consola, tokens y documentación resumida. |
| `static/styles.css` | Presentación responsiva. |
| `static/app.js` | Interacción del navegador, solicitudes HTTP y entrada de usuario. |
| `ejemplos/*.pseudo` | Programas de demostración y errores deliberados. |
| `tests/test_interprete.py` | Pruebas automáticas obligatorias y adicionales. |
| `documentacion/GRAMATICA.md` | Reglas, expresiones regulares, GIC, ejemplos y semántica. |
| `documentacion/PRUEBAS.md` | Evidencias registradas de los casos obligatorios. |
| `evidencias/` | Capturas de la aplicación ejecutando pruebas. |

## Pruebas

Ejecutar desde la carpeta principal:

```bash
python -m unittest discover -s tests -v
```

Incluye 20 pruebas automáticas; las diez primeras cubren los requisitos de la entrega y las otras comprueban situaciones adicionales. Los ejemplos con errores deben **reportarlos correctamente**: que el sistema rechace un programa inválido es una prueba aprobada.

## Tecnologías

- **Python 3**: servidor HTTP, expresiones regulares y motor de interpretación.
- **HTML5**: interfaz y formularios.
- **CSS3**: diseño adaptable a distintos tamaños de pantalla.
- **JavaScript**: editor, comunicación con la API y captura de entradas.
- **unittest**: pruebas automatizadas.
- **Git y GitHub**: control de versiones y entrega del repositorio.

## Restricciones de seguridad

No usa `eval()` ni `exec()` para ejecutar el pseudocódigo. El intérprete solo ejecuta el árbol sintáctico reconocido por su propia gramática. Escapa el contenido visual mediante `textContent` en el navegador. Las variables son locales a cada ejecución.

## Alcance

Admite declaración, asignación, números enteros/decimales, texto, expresiones, entrada/salida, condicionales anidados y comentarios. No incluye ciclos, arreglos, funciones ni lectura/escritura de archivos, dado que no son obligatorios en esta fase.

## Publicar en GitHub

Crea un repositorio vacío llamado `algora-interprete` en GitHub. Desde esta carpeta ejecuta:

```bash
git init
git add .
git commit -m "Proyecto: interprete educativo Algora"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/algora-interprete.git
git push -u origin main
```

Reemplaza `TU_USUARIO` por tu usuario real. **No existe un enlace público hasta que publiques el repositorio.** En el PDF entregable debes sustituir el campo pendiente por el URL del repositorio ya creado.

## Publicar en Render y compartir el enlace

El servidor detecta la variable de entorno `PORT` de Render y escucha en `0.0.0.0`.
El archivo `render.yaml` configura un servicio Python de plan gratuito con despliegue
automático por commit, prueba automática durante el build y verificación en `/health`.

1. Crea un repositorio en GitHub y sube **el contenido de esta carpeta**
   (`app.py`, `motor.py`, `render.yaml`, `static/`, `tests/`, etc.) al nivel raíz del repositorio.
2. En https://dashboard.render.com elige **New > Blueprint** y conecta tu repositorio.
3. Confirma la creación del servicio `algora-interprete` en el plan **Free**.
4. Render ejecutará las 20 pruebas, iniciará `python app.py` y mostrará una
   URL `https://<nombre>.onrender.com` para compartir.
5. El primer acceso tras 15 minutos de inactividad puede tardar en cargar por
   la suspensión automática del plan gratuito.

Si prefieres **New > Web Service** en lugar de Blueprint, usa:
- Runtime: `Python 3`
- Root Directory: vacío cuando `app.py` está en la raíz del repositorio
- Build Command: `python -m unittest discover -s tests -v`
- Start Command: `python app.py`
- Plan: `Free`
- Health Check Path (opcional): `/health`

### Actualizar la aplicación publicada

Edita los archivos en tu copia local y ejecuta en la raíz del repositorio:

```bash
git add .
git commit -m "Correcciones del interprete"
git push
```

Render iniciará un nuevo despliegue en la misma URL si el repositorio de
GitHub está conectado a Render y Auto-Deploy está en **On Commit**.

## Nota sobre el despliegue público

Este proyecto es una herramienta educativa. No hay cuentas de usuario ni
almacenamiento persistente. Las variables y entradas se procesan en cada
ejecución. Para exponerlo a mayor tráfico se recomienda incorporar límites
por IP y controles adicionales de uso.
