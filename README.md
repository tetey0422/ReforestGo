# ReforestGo

Aplicación web Django (backend en Python + plantillas HTML) para el proyecto ReforestGo.

## Descripción
Proyecto web desarrollado con Django. Contiene el código del backend en Python y plantillas HTML para la interfaz. Este README explica cómo preparar el entorno, ejecutar la aplicación en desarrollo y buenas prácticas para contribuir.

## Requisitos
- Python 3.10+ (recomendado 3.11)
- pip
- virtualenv (opcional)
- node (si agregas assets frontend)

Las dependencias de Python están en `requirements.txt`.

## Instalación (local)
1. Clona el repo:
   git clone https://github.com/tetey0422/ReforestGo.git
   cd ReforestGo

2. Crea y activa un entorno virtual:
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows (PowerShell)

3. Instala dependencias:
   pip install -r requirements.txt

4. Variables de entorno
   Crea un archivo `.env` en la raíz. Ejemplo mínimo:
   ```
   SECRET_KEY=tu_secret_key_segura
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   ```

   El proyecto usa `python-dotenv` si tu settings.py lo carga (revisa `ReforestGo/settings.py`).

5. Migraciones y usuario administrador:
   python manage.py migrate
   python manage.py createsuperuser

6. Ejecutar en modo desarrollo:
   python manage.py runserver

## Estructura recomendada
- ReforestGo/ (paquete Django principal)
- app/ o src/ (si separas lógica)
- templates/ (HTML)
- static/ (CSS/JS/imágenes)
- requirements.txt
- .env (no versionar)
- tests/

## Comandos útiles
- Ejecutar tests:
  pytest

- Formato y lint:
  black .
  ruff .

- Crear un build (si añades frontend con node):
  npm install
  npm run build

## Contribuir
- Abre un issue antes de cambios grandes.
- Crea una rama con nombre claro: `feature/<desc>` o `fix/<desc>`.
- Sigue el formateo y linting del proyecto.
- Añade tests cuando sea posible.

## Licencia
Este repositorio usa la licencia MIT (archivo LICENSE en la raíz).
