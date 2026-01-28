"""
Servicio de extracción de métricas de YouTube
"""
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import YOUTUBE_CHANNEL_ID, YOUTUBE_PLAYLIST_ID, DAYS_BACK


class YouTubeMetricsService:
    """Servicio para extraer métricas de videos de YouTube usando yt-dlp"""
    
    def __init__(self):
        self.channel_id = YOUTUBE_CHANNEL_ID
        self.playlist_id = YOUTUBE_PLAYLIST_ID
        self.days_back = DAYS_BACK
        
    def _run_ytdlp(self, url: str, extra_args: List[str] = None) -> Optional[Dict]:
        """
        Ejecuta yt-dlp y retorna el resultado en formato JSON
        
        Args:
            url: URL del canal, playlist o video
            extra_args: Argumentos adicionales para yt-dlp
            
        Returns:
            Datos extraídos en formato diccionario
        """
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-download",
            "--no-warnings",
            "--skip-download"
        ]
        
        if extra_args:
            cmd.extend(extra_args)
        
        cmd.append(url)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"⚠️ Error ejecutando yt-dlp: {result.stderr}")
                return None
            
            # yt-dlp puede retornar múltiples JSONs (uno por línea)
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        videos.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return videos if videos else None
            
        except subprocess.TimeoutExpired:
            print("⚠️ Timeout al ejecutar yt-dlp")
            return None
        except Exception as e:
            print(f"⚠️ Error ejecutando yt-dlp: {e}")
            return None
    
    def _is_video_recent(self, video_data: Dict) -> bool:
        """
        Verifica si un video está dentro del rango de fechas
        
        Args:
            video_data: Datos del video
            
        Returns:
            True si el video está dentro del rango
        """
        upload_date = video_data.get("upload_date")
        if not upload_date:
            return True  # Si no hay fecha, incluirlo
        
        try:
            video_date = datetime.strptime(upload_date, "%Y%m%d")
            cutoff_date = datetime.now() - timedelta(days=self.days_back)
            return video_date >= cutoff_date
        except Exception:
            return True  # En caso de error, incluirlo
    
    def get_channel_videos(self) -> List[Dict]:
        """
        Obtiene videos recientes de un canal de YouTube
        
        Returns:
            Lista de videos del canal
        """
        if not self.channel_id:
            print("⚠️ No se ha configurado YOUTUBE_CHANNEL_ID")
            return []
        
        print(f"🎬 Obteniendo videos del canal de YouTube...")
        channel_url = f"https://www.youtube.com/channel/{self.channel_id}/videos"
        
        # Limitar a los últimos N videos
        videos = self._run_ytdlp(
            channel_url,
            ["--playlist-end", "50"]  # Últimos 50 videos
        )
        
        if not videos:
            return []
        
        # Filtrar por fecha
        recent_videos = [v for v in videos if self._is_video_recent(v)]
        print(f"   ✓ {len(recent_videos)} videos recientes encontrados")
        
        return recent_videos
    
    def get_playlist_videos(self) -> List[Dict]:
        """
        Obtiene videos de una playlist de YouTube
        
        Returns:
            Lista de videos de la playlist
        """
        if not self.playlist_id:
            print("⚠️ No se ha configurado YOUTUBE_PLAYLIST_ID")
            return []
        
        print(f"📋 Obteniendo videos de la playlist de YouTube...")
        playlist_url = f"https://www.youtube.com/playlist?list={self.playlist_id}"
        
        videos = self._run_ytdlp(playlist_url)
        
        if not videos:
            return []
        
        # Filtrar por fecha
        recent_videos = [v for v in videos if self._is_video_recent(v)]
        print(f"   ✓ {len(recent_videos)} videos recientes encontrados")
        
        return recent_videos
    
    def get_video_by_url(self, video_url: str) -> Optional[Dict]:
        """
        Obtiene información de un video específico por URL
        
        Args:
            video_url: URL del video de YouTube
            
        Returns:
            Datos del video
        """
        result = self._run_ytdlp(video_url)
        return result[0] if result and len(result) > 0 else None
    
    def extract_metrics(self, video_data: Dict) -> Dict:
        """
        Extrae métricas relevantes de un video de YouTube
        
        Args:
            video_data: Datos completos del video
            
        Returns:
            Diccionario con métricas organizadas
        """
        # Formatear fecha
        upload_date = video_data.get("upload_date", "")
        if upload_date:
            try:
                date_obj = datetime.strptime(upload_date, "%Y%m%d")
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_date = upload_date
        else:
            formatted_date = ""
        
        # Formatear duración
        duration = video_data.get("duration", 0)
        duration_formatted = f"{duration // 60}:{duration % 60:02d}" if duration else "0:00"
        
        metrics = {
            "plataforma": "YouTube",
            "tipo": "Video",
            "id": video_data.get("id", ""),
            "titulo": video_data.get("title", ""),
            "url": video_data.get("webpage_url", ""),
            "fecha_creacion": formatted_date,
            "descripcion": video_data.get("description", "")[:500],  # Limitar descripción
            "duracion": duration_formatted,
            "vistas": video_data.get("view_count", 0),
            "likes": video_data.get("like_count", 0),
            "comentarios_count": video_data.get("comment_count", 0),
            "canal": video_data.get("channel", ""),
            "canal_id": video_data.get("channel_id", ""),
            "suscriptores_canal": video_data.get("channel_follower_count", 0),
            "categoria": video_data.get("categories", [""])[0] if video_data.get("categories") else "",
            "tags": ", ".join(video_data.get("tags", [])[:10]),  # Primeros 10 tags
        }
        
        return metrics
    
    def get_all_metrics(self) -> List[Dict]:
        """
        Obtiene todas las métricas de videos de YouTube
        
        Returns:
            Lista con todas las métricas recopiladas
        """
        print("\n" + "="*60)
        print("📊 INICIANDO EXTRACCIÓN DE MÉTRICAS DE YOUTUBE")
        print("="*60 + "\n")
        
        all_metrics = []
        all_videos = []
        
        # Obtener videos del canal
        if self.channel_id:
            channel_videos = self.get_channel_videos()
            all_videos.extend(channel_videos)
        
        # Obtener videos de playlist
        if self.playlist_id:
            playlist_videos = self.get_playlist_videos()
            # Evitar duplicados por ID
            existing_ids = {v.get("id") for v in all_videos}
            for video in playlist_videos:
                if video.get("id") not in existing_ids:
                    all_videos.append(video)
        
        # Procesar métricas
        for i, video in enumerate(all_videos, 1):
            print(f"   Procesando video {i}/{len(all_videos)}...", end="\r")
            metrics = self.extract_metrics(video)
            all_metrics.append(metrics)
        
        if all_videos:
            print(f"   ✓ {len(all_videos)} videos procesados correctamente")
        
        print(f"\n✅ Total de métricas de YouTube obtenidas: {len(all_metrics)}\n")
        return all_metrics
