"""
Configuración del Servicio de Métricas de Redes Sociales
"""
from datetime import datetime, timedelta

# === CONFIGURACIÓN FACEBOOK ===
FACEBOOK_PAGE_ID = "804578252729420"
FACEBOOK_ACCESS_TOKEN = " "
FACEBOOK_API_VERSION = "v24.0"
FACEBOOK_BASE_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

# === CONFIGURACIÓN YOUTUBE ===
YOUTUBE_CHANNEL_ID = "UCnZy-XRcW6ggpIVl8zPLx3g"
YOUTUBE_PLAYLIST_ID = ""  

# === CONFIGURACIÓN GENERAL ===
# Días hacia atrás para obtener datos
DAYS_BACK = 2
SINCE_DATE = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")
UNTIL_DATE = datetime.now().strftime("%Y-%m-%d")

# Archivo de salida
OUTPUT_FILE = "metricas_redes_sociales.xlsx"

# Límites de paginación
FACEBOOK_PAGE_LIMIT = 100
