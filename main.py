"""
Servicio Principal de Extracción de Métricas de Redes Sociales
Versión: 1.0
Plataformas: Facebook (API v24.0) y YouTube (yt-dlp)
"""
import sys
from typing import Optional
from facebook_service import FacebookMetricsService
from youtube_service import YouTubeMetricsService
from excel_service import ExcelExportService
from config import OUTPUT_FILE


class SocialMetricsService:
    """Servicio principal que coordina la extracción de métricas"""
    
    def __init__(self):
        self.facebook_service = FacebookMetricsService()
        self.youtube_service = YouTubeMetricsService()
        self.excel_service = ExcelExportService()
    
    def run_full_extraction(self, separate_sheets: bool = True) -> bool:
        """
        Ejecuta la extracción completa de métricas de todas las plataformas
        
        Args:
            separate_sheets: Si True, crea hojas separadas por plataforma
            
        Returns:
            True si el proceso fue exitoso
        """
        print("\n" + "="*60)
        print("🚀 SERVICIO DE EXTRACCIÓN DE MÉTRICAS DE REDES SOCIALES")
        print("="*60)
        print("📱 Plataformas: Facebook (API v24.0) + YouTube (yt-dlp)")
        print("="*60 + "\n")
        
        facebook_metrics = []
        youtube_metrics = []
        
        # Extracción de Facebook
        try:
            facebook_metrics = self.facebook_service.get_all_metrics()
        except Exception as e:
            print(f"❌ Error en extracción de Facebook: {e}")
        
        # Extracción de YouTube
        try:
            youtube_metrics = self.youtube_service.get_all_metrics()
        except Exception as e:
            print(f"❌ Error en extracción de YouTube: {e}")
        
        # Validar que hay datos para exportar
        if not facebook_metrics and not youtube_metrics:
            print("❌ No se obtuvieron métricas de ninguna plataforma")
            return False
        
        # Exportar a Excel
        if separate_sheets:
            success = self.excel_service.export_separate_sheets(
                facebook_metrics, 
                youtube_metrics
            )
        else:
            all_metrics = facebook_metrics + youtube_metrics
            success = self.excel_service.export_metrics(all_metrics)
        
        return success
    
    def run_facebook_only(self) -> bool:
        """Ejecuta solo la extracción de Facebook"""
        print("\n🔵 Extracción solo de Facebook\n")
        
        try:
            metrics = self.facebook_service.get_all_metrics()
            if metrics:
                return self.excel_service.export_metrics(metrics)
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_youtube_only(self) -> bool:
        """Ejecuta solo la extracción de YouTube"""
        print("\n🔴 Extracción solo de YouTube\n")
        
        try:
            metrics = self.youtube_service.get_all_metrics()
            if metrics:
                return self.excel_service.export_metrics(metrics)
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


def main():
    """Función principal del servicio"""
    # Crear instancia del servicio
    service = SocialMetricsService()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        platform = sys.argv[1].lower()
        
        if platform == "facebook":
            success = service.run_facebook_only()
        elif platform == "youtube":
            success = service.run_youtube_only()
        elif platform == "all":
            success = service.run_full_extraction(separate_sheets=True)
        else:
            print("❌ Plataforma no válida. Usa: facebook, youtube o all")
            sys.exit(1)
    else:
        # Por defecto, ejecutar extracción completa
        success = service.run_full_extraction(separate_sheets=True)
    
    # Código de salida
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
