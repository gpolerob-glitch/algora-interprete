"""Servidor web del interprete educativo (Python 3.10+).
Compatible con ejecucion local y Render (variables de entorno HOST / PORT).
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import mimetypes
import os

from motor import procesar

BASE = Path(__file__).resolve().parent
ESTATICOS = BASE / 'static'
EJEMPLOS = BASE / 'ejemplos'


class Servidor(BaseHTTPRequestHandler):
    def responder(self, codigo, cuerpo, tipo='application/json; charset=utf-8'):
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo, ensure_ascii=False).encode('utf-8')
        elif isinstance(cuerpo, str):
            cuerpo = cuerpo.encode('utf-8')
        self.send_response(codigo)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(cuerpo)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        ruta = urlparse(self.path).path
        if ruta == '/health':
            self.responder(200, {'estado': 'ok'})
            return
        if ruta == '/api/ejemplos':
            ejemplos = [
                {'nombre': p.stem.replace('_', ' ').title(), 'archivo': p.name,
                 'codigo': p.read_text(encoding='utf-8')}
                for p in sorted(EJEMPLOS.glob('*.pseudo'))
            ]
            self.responder(200, ejemplos)
            return
        archivos = {'/': 'index.html', '/index.html': 'index.html',
                    '/app.js': 'app.js', '/styles.css': 'styles.css'}
        if ruta not in archivos:
            self.responder(404, {'error': 'Ruta no encontrada'})
            return
        p = ESTATICOS / archivos[ruta]
        self.responder(200, p.read_bytes(), mimetypes.guess_type(p.name)[0] or 'application/octet-stream')

    def do_POST(self):
        ruta = urlparse(self.path).path
        if ruta not in ('/api/analizar', '/api/ejecutar'):
            self.responder(404, {'error': 'Ruta no encontrada'})
            return
        try:
            tam = int(self.headers.get('Content-Length', '0'))
            if tam > 100_000 or tam <= 0:
                self.responder(413, {'error': 'Solicitud vacia o demasiado grande'})
                return
            datos = json.loads(self.rfile.read(tam))
            codigo = datos.get('codigo', '')
            entradas = datos.get('entradas', [])
            if not isinstance(codigo, str) or not isinstance(entradas, list) or len(entradas) > 500:
                self.responder(400, {'error': 'Formato de solicitud incorrecto'})
                return
            resultado = procesar(codigo, entradas, solo_analizar=ruta == '/api/analizar')
            self.responder(200, resultado)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError, TypeError):
            self.responder(400, {'error': 'JSON o parametros invalidos'})


def main():
    parser = argparse.ArgumentParser(description='Interprete educativo de pseudocodigo')
    parser.add_argument('--puerto', type=int, default=int(os.environ.get('PORT', '8000')))
    parser.add_argument('--host', default=os.environ.get('HOST', '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'))
    args = parser.parse_args()
    servidor = ThreadingHTTPServer((args.host, args.puerto), Servidor)
    print(f'Interprete educativo escuchando en {args.host}:{args.puerto}', flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == '__main__':
    main()
