# 📊 Servicio de Extracción de Métricas de Redes Sociales

Servicio profesional con **interfaz web** para extraer métricas de **Facebook** (API v24.0) y **YouTube** (yt-dlp) y exportarlas a Excel con formato profesional.

## 🚀 Características

- ✅ **Interfaz Web Moderna** - Dashboard intuitivo con soporte para Facebook y YouTube
- ✅ Extracción de posts y videos de Facebook con métricas completas
- ✅ Extracción de videos de YouTube con estadísticas detalladas
- ✅ Exportación a Excel con formato profesional
- ✅ Parámetros dinámicos por sesión (sin modificar config)
- ✅ Rango de fechas configurable en la interfaz
- ✅ Arquitectura modular y escalable
- ✅ Manejo robusto de errores
- ✅ Configuración centralizada
- ✅ Paginación automática para grandes volúmenes de datos

## 📋 Requisitos

- Python 3.8+
- yt-dlp (instalado globalmente o en el entorno)
- Token de acceso de Facebook válido

## 🔧 Instalación

1. **Clonar o descargar los archivos del servicio**

2. **Instalar dependencias de Python:**
```bash
pip install -r requirements.txt
```

3. **Instalar yt-dlp (si no está instalado):**
```bash
pip install yt-dlp
# o
brew install yt-dlp  # en macOS
```

4. **Configurar el servicio:**
Editar `config.py` con tus credenciales:

```python
# Facebook
FACEBOOK_PAGE_ID = "tu_page_id"
FACEBOOK_ACCESS_TOKEN = "tu_token_de_acceso"

# YouTube
YOUTUBE_CHANNEL_ID = "tu_canal_id"
# o
YOUTUBE_PLAYLIST_ID = "tu_playlist_id"

# General
DAYS_BACK = 10  # Días hacia atrás para obtener datos
OUTPUT_FILE = "metricas_redes_sociales.xlsx"
```

## 🎯 Uso

### Versión Web (Recomendado)

Ejecutar el servidor Flask:
```bash
python app_simple.py
```

Luego acceder a:
```
http://localhost:5000
```

**Características de la interfaz web:**
- Selector de plataforma (Facebook / YouTube)
- Campo para ingresar Page ID / Channel ID
- Campo para token de acceso (solo Facebook)
- Selector de rango de fechas dinámico
- Descarga directa de Excel
- Indicador de progreso durante la extracción

### Extracción completa (Facebook + YouTube)
```bash
python main.py
# o
python main.py all
```

### Solo Facebook
```bash
python main.py facebook
```

### Solo YouTube
```bash
python main.py youtube
```

## 📁 Estructura del Proyecto

```
├── app_simple.py          # Servidor web Flask (interfaz moderna)
├── main.py                 # Punto de entrada del servicio CLI
├── config.py              # Configuración centralizada
├── facebook_service.py    # Servicio de extracción de Facebook
├── youtube_service.py     # Servicio de extracción de YouTube
├── excel_service.py       # Servicio de exportación a Excel
├── outputs/               # Carpeta para archivos Excel generados
└── requirements.txt       # Dependencias del proyecto
```

## 📊 Métricas Extraídas

### Facebook - Posts
- ID y URL del post
- Fecha de creación
- Mensaje/contenido
- Likes (reacciones totales)
- Comentarios (cantidad + detalle completo)
- Compartidos

### Facebook - Videos
- ID y URL del video
- Fecha de creación
- Descripción
- Insights de video (métricas disponibles en API v24.0)

### YouTube - Videos
- ID y URL del video
- Título
- Descripción
- Fecha de publicación
- Duración
- Vistas
- Likes
- Comentarios (cantidad)
- Canal y suscriptores
- Categoría
- Tags

## 📈 Formato de Salida

El servicio genera un archivo Excel con:
- ✅ Hojas separadas por plataforma (Facebook, YouTube, Consolidado)
- ✅ Encabezados con formato profesional
- ✅ Columnas auto-ajustadas
- ✅ Primera fila congelada
- ✅ Colores corporativos

## 🔐 Obtener Token de Facebook

1. Ir a [Facebook Developers](https://developers.facebook.com/)
2. Crear una aplicación
3. Ir a Tools → Graph API Explorer
4. Seleccionar tu página
5. Generar token con permisos:
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `read_insights`

## 🎥 Configurar YouTube

### Por Canal:
```python
YOUTUBE_CHANNEL_ID = "UCxxxxxxxxxxxxxx"
```

### Por Playlist:
```python
YOUTUBE_PLAYLIST_ID = "PLxxxxxxxxxxxxxx"
```

### Por URL específica:
Modificar `youtube_service.py` método `get_video_by_url()` para URLs individuales.

## ⚙️ Configuración Avanzada

### Interfaz Web - Parámetros por Sesión
En la versión web (`app_simple.py`), **NO es necesario modificar config.py**. Los parámetros se envían dinámicamente:

- **Page ID**: Se especifica en la interfaz
- **Token de Acceso**: Se envía en la solicitud (no se almacena)
- **Rango de fechas**: "Días hacia atrás" se calcula en tiempo real
- **Channel ID (YouTube)**: Se especifica en la interfaz

### Cambiar rango de fechas (CLI):
```python
# En config.py
DAYS_BACK = 30  # Últimos 30 días (para main.py)
```

### Cambiar límite de paginación:
```python
# En config.py
FACEBOOK_PAGE_LIMIT = 50  # Posts/videos por página
```

### Exportar en una sola hoja:
```python
# En main.py, cambiar:
success = service.run_full_extraction(separate_sheets=False)
```

## 🐛 Solución de Problemas

### Error: "Token inválido"
- Verificar que el token de Facebook no haya expirado
- Regenerar token desde Graph API Explorer
- Verificar permisos del token

### Error: "yt-dlp no encontrado"
```bash
pip install --upgrade yt-dlp
```

### Error: "No se pudieron obtener métricas"
- Verificar conectividad a internet
- Confirmar que el ID de página/canal es correcto
- Revisar logs para detalles específicos

## 📝 Notas Importantes

- **API v24.0 de Facebook**: Las métricas disponibles corresponden a esta versión específica. No se agregan métricas de versiones superiores.
- **Rate Limits**: Facebook tiene límites de tasa. El servicio maneja errores automáticamente.
- **YouTube**: yt-dlp extrae datos públicos sin necesidad de API key.
- **Datos históricos**: Facebook y YouTube tienen diferentes políticas de retención de datos.
- **Parámetros dinámicos**: En la interfaz web, los parámetros se envían por sesión sin modificar `config.py`. Esto permite múltiples usuarios con diferentes Page IDs y tokens.
- **Rango de fechas en interfaz web**: El selector "Días hacia atrás" calcula dinámicamente las fechas sin depender del valor en config.py

## 🔄 Mantenimiento

### Actualizar yt-dlp regularmente:
```bash
pip install --upgrade yt-dlp
```

### Renovar tokens de Facebook:
Los tokens se renuevan a cada hora.

## 📞 Soporte

Para problemas o mejoras, revisar:
- [Documentación de Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Documentación de yt-dlp](https://github.com/yt-dlp/yt-dlp)

## 📜 Licencia

Este código es de uso interno. Mantener confidenciales los tokens y credenciales.

