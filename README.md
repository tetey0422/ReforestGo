# 🌱 ReforestGo

**Planta, Suma y Transforma el Planeta**

ReforestGo es una aplicación web gamificada desarrollada con Django que permite a los usuarios registrar sus siembras de árboles, verificar árboles de otros usuarios, ganar puntos, subir de nivel y contribuir activamente a la reforestación del planeta.

## 🌟 Características Principales

- **🌳 Registro de Siembras**: Los usuarios pueden registrar árboles plantados con foto, ubicación GPS y descripción
- **🗺️ Mapa Interactivo**: Visualiza todas las siembras en un mapa global con marcadores personalizados
- **🔍 Sistema de Verificación**: Usuarios de nivel 3+ pueden verificar árboles plantados por otros
- **🏆 Sistema de Puntos y Niveles**: Gamificación completa con avatares, logros y ranking
- **💨 Cálculo de Oxígeno**: Estima el oxígeno producido por tus árboles plantados
- **📊 Estadísticas Personales**: Visualiza tu impacto ambiental y progreso
- **🎨 Sistema de Avatares**: Desbloquea avatares especiales al subir de nivel
- **🌍 Zonas Automáticas**: Detección automática de zonas geográficas de reforestación

## 📋 Requisitos del Sistema

- **Python**: 3.10+ (recomendado 3.13)
- **pip**: Para gestión de paquetes
- **SQLite3**: Base de datos (incluida con Python)
- **Navegador moderno**: Chrome, Firefox, Edge, Safari

## 🚀 Instalación y Configuración

### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/tetey0422/ReforestGo.git
cd ReforestGo
```

### 2️⃣ Crear Entorno Virtual
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS / Linux
python3 -m venv env
source env/bin/activate
```

### 3️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta_super_segura_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 5️⃣ Aplicar Migraciones
```bash
python manage.py migrate
```

### 6️⃣ Crear Usuario Administrador
```bash
python manage.py createsuperuser
```

### 7️⃣ Ejecutar el Servidor
```bash
python manage.py runserver
```

Accede a la aplicación en: **http://localhost:8000**

## 📁 Estructura del Proyecto

```
ReforestGo/
├── core/                      # App principal Django
│   ├── models.py             # Modelos: Usuario, Siembra, Verificación
│   ├── views.py              # Vistas y lógica de negocio
│   ├── urls.py               # Rutas de la aplicación
│   ├── admin.py              # Panel de administración
│   └── management/           # Comandos personalizados
│       └── commands/
│           ├── actualizar_oxigeno.py
│           ├── asignar_verificador.py
│           └── generar_zonas_automaticas.py
├── ReforestGo/               # Configuración del proyecto
│   ├── settings.py           # Configuración principal
│   ├── urls.py               # URLs globales
│   └── wsgi.py              # WSGI para producción
├── templates/                # Plantillas HTML
│   ├── base.html            # Plantilla base
│   ├── index.html           # Página principal
│   ├── mapa.html            # Mapa interactivo
│   ├── registrar_siembra.html
│   ├── verificar_arbol.html
│   └── ...
├── static/                   # Archivos estáticos (CSS, JS, imágenes)
├── media/                    # Archivos subidos por usuarios
│   └── siembras/            # Fotos de árboles
├── db.sqlite3               # Base de datos SQLite
├── manage.py                # CLI de Django
└── requirements.txt         # Dependencias Python
```

## 🎮 Comandos Personalizados

ReforestGo incluye comandos de gestión personalizados:

```bash
# Actualizar cálculo de oxígeno de todas las siembras
python manage.py actualizar_oxigeno

# Asignar verificadores automáticamente a siembras
python manage.py asignar_verificador

# Generar zonas geográficas automáticas
python manage.py generar_zonas_automaticas
```

## 🎨 Paleta de Colores

| Color | HEX | Uso |
|-------|-----|-----|
| 🌲 Verde Bosque | `#2E7D32` | Logo, encabezados, elementos principales |
| 🌿 Verde Claro | `#66BB6A` | Botones de acción, hover, estados activos |
| 🏔️ Tierra/Marrón | `#8D6E63` | Elementos neutros, fondos secundarios |
| ☀️ Crema Luz | `#FFF9C4` | Fondo general, zonas de texto |
| 🌊 Azul Cielo | `#29B6F6` | Enlaces, llamadas a la acción |
| ⚫ Gris Oscuro | `#424242` | Texto principal, contraste |

## 👥 Roles y Permisos

- **Usuario Normal (Nivel 1-2)**: Puede registrar siembras y ver el mapa
- **Verificador (Nivel 3+)**: Puede verificar árboles de otros usuarios
- **Administrador**: Acceso completo al panel de administración

## 🔒 Seguridad

- Autenticación basada en sesiones de Django
- CSRF protection habilitado
- Validación de imágenes subidas
- Límites de tamaño de archivos
- Sanitización de datos de usuario

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Con cobertura (si tienes coverage instalado)
coverage run manage.py test
coverage report
```

## 📊 Scripts Útiles

Ubicados en `scripts/`:
- `init_data.py`: Inicializar datos de prueba
- `test_verificacion.py`: Probar sistema de verificación

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Convenciones de Código
- Seguir PEP 8 para Python
- Comentarios en español
- Nombres de variables descriptivos
- Documentar funciones complejas

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📧 Contacto

- **Repositorio**: [github.com/tetey0422/ReforestGo](https://github.com/tetey0422/ReforestGo)
- **Issues**: [github.com/tetey0422/ReforestGo/issues](https://github.com/tetey0422/ReforestGo/issues)

---

**¡Únete a la reforestación del planeta! 🌍🌱**
