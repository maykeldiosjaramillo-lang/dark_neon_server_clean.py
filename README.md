# 🎬 Dark Neon Video Server

Servidor web autocontenido con interfaz de terror/neón para gestionar y compartir contenido multimedia.

## 📦 Estructura del Proyecto

```
tu-repo/
├── dark_neon_server_clean.py  ← Servidor principal
├── requirements.txt           ← Dependencias Python
├── Procfile                   ← Configuración para Render/Heroku
├── .gitignore                 ← Archivos a ignorar
└── README.md                  ← Esta guía
```

## 🚀 Deploy en Render.com

### 1. Preparar Repositorio

```bash
# Crear repositorio
git init
git add .
git commit -m "Initial commit"

# Subir a GitHub
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```

### 2. Configurar en Render

1. Ve a [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Configuración:
   - **Name**: `dark-neon-server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python dark_neon_server_clean.py`
   - **Plan**: Free

5. Click **"Create Web Service"**

### 3. Variables de Entorno (Opcional)

En Render, ve a **Environment** y agrega:

```
PORT=10000
```

(Render asigna puerto automáticamente)

## 🔑 Claves de Acceso

| Tipo | Clave | Función |
|------|-------|---------|
| Usuario | `DEMO2026`, `TERROR`, `NEON` | Ver contenido seleccionado |
| Admin | `INTEGER` | Panel completo |
| Live Gore | `NOA999` | Galería de archivos |
| Descarga | `NOA` | Descargar archivos |

## 💻 Ejecución Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python dark_neon_server_clean.py

# Abrir navegador
http://localhost:8000
```

## 📁 Características

- ✅ Panel de administración
- ✅ Subida de archivos
- ✅ Descarga con YT-DLP
- ✅ Descarga con TikWM (TikTok)
- ✅ Scraper de sitios gore
- ✅ Live Gore Gallery
- ✅ Streaming optimizado
- ✅ Interfaz terror/neón

## 🔧 Administración

### Subir Contenido:

1. Accede con `INTEGER`
2. Opciones:
   - 📤 Subir desde PC
   - 📹 YT-DLP (YouTube, Instagram, etc.)
   - 📱 TikWM (TikTok)
   - 🔴 Scraper Gore
   - ⬇️ URL directa

### Gestionar:

1. Selecciona archivo
2. Edita información
3. Guarda cambios
4. Disponible para usuarios

## 🌐 Acceso Público

Después del deploy en Render:

```
https://tu-app.onrender.com
```

## 📝 Notas Importantes

### Para Render:

- ✅ Usa plan Free (suficiente)
- ✅ Se apaga después de 15 min de inactividad
- ✅ Primer acceso puede tardar ~30 seg
- ⚠️ Los archivos subidos se borran al reiniciar
- ⚠️ Usa almacenamiento externo para persistencia

### Almacenamiento:

Para persistir archivos, usa:
- Cloudinary (imágenes/videos)
- AWS S3
- Google Cloud Storage

## ⚙️ Configuración Avanzada

### Cambiar Puerto:

```python
# En dark_neon_server_clean.py
PORT = int(os.environ.get('PORT', 8000))
```

### Cambiar Claves:

```python
VALID_KEYS = ["TU_CLAVE_1", "TU_CLAVE_2"]
ADMIN_KEY = "TU_ADMIN_KEY"
```

## 🐛 Solución de Problemas

### Error al iniciar:

```bash
# Verificar dependencias
pip install -r requirements.txt

# Verificar puerto
lsof -i :8000
```

### Archivos no se guardan:

- En Render, los archivos se borran al reiniciar
- Usa almacenamiento externo

### Deploy falla:

```bash
# Verificar Procfile
cat Procfile

# Verificar requirements.txt
cat requirements.txt
```

## 📜 Licencia

Uso personal

## ⚠️ Advertencia

Contenido explícito - Solo +18 años
