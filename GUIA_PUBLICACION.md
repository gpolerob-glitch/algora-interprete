# Guía sencilla para compartir ALGORA

## Paso 1: subir a GitHub

- Entra a https://github.com/new e inicia sesión.
- Nombre sugerido: `algora-interprete`. Crea el repositorio sin README inicial.
- Desde VS Code abre **esta carpeta** (`ALGORA_Para_Publicar`), abre la terminal y ejecuta:

```powershell
git init
git add .
git commit -m "Primera version de ALGORA"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/algora-interprete.git
git push -u origin main
```

Sustituye `TU_USUARIO` por tu nombre de usuario de GitHub. Si Git pide
autenticación, inicia sesión con el navegador. En Windows también puedes usar
VS Code > Control de código fuente > Publicar en GitHub.

## Paso 2: publicar la app en Render

- Visita https://dashboard.render.com y crea una cuenta o inicia sesión.
- Elige **New > Blueprint**.
- Conecta GitHub y selecciona `algora-interprete`.
- Render detectará `render.yaml`. Confirma el servicio `algora-interprete`
  con plan **Free** y realiza el despliegue.
- Cuando diga **Live**, abre la dirección real terminada en `.onrender.com`.

También puedes crear **New > Web Service**, con `Python 3`, build command
`python -m unittest discover -s tests -v` y start command `python app.py`.

## Paso 3: compartir con el compañero

Comparte la URL pública generada por Render. El compañero solo necesita
un navegador y conexión a internet; no instala Python.

## Paso 4: hacer modificaciones

1. Corrige el código desde VS Code.
2. Ejecuta `python -m unittest discover -s tests -v`.
3. Ejecuta `git add .`, `git commit -m "Mejoras"` y `git push`.
4. Render desplegará la nueva versión, conservando la URL.

En el plan gratuito el servicio puede dormir tras 15 minutos sin tráfico;
la siguiente visita lo despierta y puede tardar alrededor de un minuto.
