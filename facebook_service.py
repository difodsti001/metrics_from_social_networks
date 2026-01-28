"""
Servicio de extracción de métricas de Facebook
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import (
    DAYS_BACK,
    FACEBOOK_PAGE_ID,
    FACEBOOK_ACCESS_TOKEN,
    FACEBOOK_BASE_URL,
    FACEBOOK_PAGE_LIMIT
)


SINCE_DATE = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")
UNTIL_DATE = datetime.now().strftime("%Y-%m-%d")

class FacebookMetricsService:
    """Servicio para extraer métricas de posts y videos de Facebook"""
    
    def __init__(self):
        self.page_id = FACEBOOK_PAGE_ID
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.base_url = FACEBOOK_BASE_URL
        self.since_date = SINCE_DATE
        self.until_date = UNTIL_DATE
        
    def _fb_get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Realiza una llamada GET a la API de Facebook
        
        Args:
            endpoint: Endpoint de la API
            params: Parámetros de la petición
            
        Returns:
            Respuesta JSON de la API
        """
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.access_token
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en petición a Facebook: {e}")
            return {}
    
    def get_posts(self) -> List[Dict]:
        """
        Obtiene los posts recientes de la página
        
        Returns:
            Lista de posts con su información básica
        """
        print("📄 Obteniendo posts de Facebook...")
        posts = []
        params = {
            "fields": "id,created_time,message",
            "since": self.since_date,
            "until": self.until_date,
            "limit": FACEBOOK_PAGE_LIMIT
        }
        
        data = self._fb_get(f"{self.page_id}/posts", params)
        posts.extend(data.get("data", []))
        
        # Paginación
        while "paging" in data and "next" in data["paging"]:
            try:
                response = requests.get(data["paging"]["next"])
                data = response.json()
                posts.extend(data.get("data", []))
            except Exception as e:
                print(f"⚠️ Error en paginación de posts: {e}")
                break
                
        print(f"   ✓ {len(posts)} posts encontrados")
        return posts
    
    def get_videos(self) -> List[Dict]:
        """
        Obtiene videos recientes de la página
        
        Returns:
            Lista de videos con su información básica
        """
        print("🎥 Obteniendo videos de Facebook...")
        videos = []
        params = {
            "fields": "id,created_time,description",
            "since": self.since_date,
            "until": self.until_date,
            "limit": FACEBOOK_PAGE_LIMIT
        }
        
        data = self._fb_get(f"{self.page_id}/videos", params)
        videos.extend(data.get("data", []))
        
        # Paginación
        while "paging" in data and "next" in data["paging"]:
            try:
                response = requests.get(data["paging"]["next"])
                data = response.json()
                videos.extend(data.get("data", []))
            except Exception as e:
                print(f"⚠️ Error en paginación de videos: {e}")
                break
                
        print(f"   ✓ {len(videos)} videos encontrados")
        return videos
    
    def get_post_comments(self, post_id: str) -> List[Dict]:
        """
        Obtiene todos los comentarios de un post
        
        Args:
            post_id: ID del post
            
        Returns:
            Lista de comentarios
        """
        comments = []
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "fields": "from{name,id},message,created_time",
            "limit": 100,
            "access_token": self.access_token
        }
        
        while url:
            try:
                resp = requests.get(url, params=params).json()
                data = resp.get("data", [])
                comments.extend(data)
                url = resp.get("paging", {}).get("next", None)
                params = None  # next ya incluye el token
            except Exception as e:
                print(f"⚠️ Error obteniendo comentarios: {e}")
                break
                
        return comments
    
    def get_post_metrics(self, post: Dict) -> Optional[Dict]:
        """
        Obtiene métricas detalladas de un post
        
        Args:
            post: Diccionario con información del post
            
        Returns:
            Diccionario con métricas del post
        """
        post_id = post.get("id")
        fields = "reactions.summary(total_count),comments.summary(true),shares"
        
        try:
            data = self._fb_get(post_id, {"fields": fields})
            post_suffix = post_id.split("_")[1] if "_" in post_id else post_id
            
            metrics = {
                "plataforma": "Facebook",
                "tipo": "Post",
                "id": post_id,
                "url": f"https://www.facebook.com/{self.page_id}/posts/{post_suffix}",
                "fecha_creacion": post.get("created_time"),
                "mensaje": post.get("message", ""),
                "likes": data.get("reactions", {}).get("summary", {}).get("total_count", 0),
                "comentarios_count": data.get("comments", {}).get("summary", {}).get("total_count", 0),
                "compartidos": data.get("shares", {}).get("count", 0)
            }
            
            # Obtener comentarios individuales
            raw_comments = self.get_post_comments(post_id)
            comments_formatted = "\n— ".join([
                f"{c.get('from', {}).get('name', 'Usuario')} ({c.get('created_time', '')}): {c.get('message', '')}"
                for c in raw_comments
            ])
            metrics["comentarios_detalle"] = comments_formatted if comments_formatted else "Sin comentarios"
            
            return metrics
            
        except Exception as e:
            print(f"⚠️ No se pudieron obtener métricas del post {post_id}: {e}")
            return None
    
    def get_video_metrics(self, video: Dict) -> Optional[Dict]:
        """
        Obtiene métricas detalladas de un video
        
        Args:
            video: Diccionario con información del video
            
        Returns:
            Diccionario con métricas del video
        """
        video_id = video.get("id")
        fields = "video_insights"
        
        try:
            data = self._fb_get(video_id, {"fields": fields})
            insights = data.get("video_insights", {}).get("data", [])
            
            metrics = {
                "plataforma": "Facebook",
                "tipo": "Video",
                "id": video_id,
                "url": f"https://www.facebook.com/{self.page_id}/videos/{video_id}",
                "fecha_creacion": video.get("created_time"),
                "descripcion": video.get("description", "")
            }
            
            # Extraer insights disponibles
            for item in insights:
                name = item.get("name")
                values = item.get("values", [])
                if values and "value" in values[0]:
                    metrics[name] = values[0]["value"]
            
            return metrics
            
        except Exception as e:
            print(f"⚠️ No se pudieron obtener métricas del video {video_id}: {e}")
            return None
    
    def get_all_metrics(self) -> List[Dict]:
        """
        Obtiene todas las métricas de posts y videos
        
        Returns:
            Lista con todas las métricas recopiladas
        """
        print("\n" + "="*60)
        print("📊 INICIANDO EXTRACCIÓN DE MÉTRICAS DE FACEBOOK")
        print("="*60 + "\n")
        
        all_metrics = []
        
        # Procesar posts
        posts = self.get_posts()
        for i, post in enumerate(posts, 1):
            print(f"   Procesando post {i}/{len(posts)}...", end="\r")
            metrics = self.get_post_metrics(post)
            if metrics:
                all_metrics.append(metrics)
        
        if posts:
            print(f"   ✓ {len(posts)} posts procesados correctamente")
        
        # Procesar videos
        videos = self.get_videos()
        for i, video in enumerate(videos, 1):
            print(f"   Procesando video {i}/{len(videos)}...", end="\r")
            metrics = self.get_video_metrics(video)
            if metrics:
                all_metrics.append(metrics)
        
        if videos:
            print(f"   ✓ {len(videos)} videos procesados correctamente")
        
        print(f"\n✅ Total de métricas de Facebook obtenidas: {len(all_metrics)}\n")
        return all_metrics
