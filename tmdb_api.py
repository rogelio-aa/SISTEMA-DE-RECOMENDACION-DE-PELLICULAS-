"""
Módulo para interactuar con la API de TMDB (The Movie Database)
"""
import os
import requests
from typing import Dict, List, Optional, Any
import time
import json

# Clave de API para TMDB
TMDB_API_KEY = "94eb0cb3b1b5adc962c78da5381ad356"  # Clave de ejemplo, reemplazar en producción
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"

# Tamaños de imagen disponibles
POSTER_SIZES = ["w92", "w154", "w185", "w342", "w500", "w780", "original"]
BACKDROP_SIZES = ["w300", "w780", "w1280", "original"]
PROFILE_SIZES = ["w45", "w185", "h632", "original"]

# Caché para reducir llamadas a la API
CACHE_DIR = "data/cache"
CACHE_EXPIRY = 24 * 60 * 60  # 24 horas en segundos

class TMDBApi:
    """
    Clase para interactuar con la API de TMDB
    """
    def __init__(self, api_key: str = TMDB_API_KEY, language: str = "es-ES"):
        self.api_key = api_key
        self.language = language
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Asegura que el directorio de caché existe"""
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def _get_cache_path(self, endpoint: str, params: Dict) -> str:
        """Genera una ruta de caché única para una solicitud"""
        # Crear un identificador único basado en el endpoint y los parámetros
        param_str = "_".join(f"{k}_{v}" for k, v in sorted(params.items()))
        cache_id = f"{endpoint.replace('/', '_')}_{param_str}"
        return os.path.join(CACHE_DIR, f"{cache_id}.json")
    
    def _get_from_cache(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Intenta obtener datos desde la caché"""
        cache_path = self._get_cache_path(endpoint, params)
        
        if not os.path.exists(cache_path):
            return None
        
        # Verificar si la caché ha expirado
        if time.time() - os.path.getmtime(cache_path) > CACHE_EXPIRY:
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _save_to_cache(self, endpoint: str, params: Dict, data: Dict):
        """Guarda datos en la caché"""
        cache_path = self._get_cache_path(endpoint, params)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error al guardar en caché: {e}")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Realiza una solicitud a la API de TMDB con manejo de caché"""
        if params is None:
            params = {}
        
        # Añadir parámetros comunes
        params["api_key"] = self.api_key
        params["language"] = self.language
        
        # Intentar obtener desde caché
        cached_data = self._get_from_cache(endpoint, params)
        if cached_data:
            return cached_data
        
        # Realizar solicitud a la API
        url = f"{TMDB_BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        
        # Verificar respuesta
        if response.status_code == 200:
            data = response.json()
            # Guardar en caché
            self._save_to_cache(endpoint, params, data)
            return data
        else:
            # Manejar errores
            print(f"Error en solicitud a TMDB: {response.status_code}")
            print(response.text)
            return {"error": response.status_code, "message": response.text}
    
    def search_movies(self, query: str, page: int = 1) -> Dict:
        """
        Busca películas por título
        
        Args:
            query: Texto de búsqueda
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con resultados de búsqueda
        """
        endpoint = "/search/movie"
        params = {
            "query": query,
            "page": page,
            "include_adult": "false"
        }
        
        return self._make_request(endpoint, params)
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """
        Obtiene detalles completos de una película
        
        Args:
            movie_id: ID de la película en TMDB
            
        Returns:
            Diccionario con detalles de la película
        """
        endpoint = f"/movie/{movie_id}"
        params = {
            "append_to_response": "credits,videos,images,recommendations,similar"
        }
        
        return self._make_request(endpoint, params)
    
    def get_popular_movies(self, page: int = 1) -> Dict:
        """
        Obtiene películas populares
        
        Args:
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con películas populares
        """
        endpoint = "/movie/popular"
        params = {"page": page}
        
        return self._make_request(endpoint, params)
    
    def get_top_rated_movies(self, page: int = 1) -> Dict:
        """
        Obtiene películas mejor valoradas
        
        Args:
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con películas mejor valoradas
        """
        endpoint = "/movie/top_rated"
        params = {"page": page}
        
        return self._make_request(endpoint, params)
    
    def get_now_playing_movies(self, page: int = 1) -> Dict:
        """
        Obtiene películas en cartelera
        
        Args:
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con películas en cartelera
        """
        endpoint = "/movie/now_playing"
        params = {"page": page}
        
        return self._make_request(endpoint, params)
    
    def get_upcoming_movies(self, page: int = 1) -> Dict:
        """
        Obtiene próximos estrenos
        
        Args:
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con próximos estrenos
        """
        endpoint = "/movie/upcoming"
        params = {"page": page}
        
        return self._make_request(endpoint, params)
    
    def discover_movies(self, 
                       year: Optional[int] = None,
                       genre_ids: Optional[List[int]] = None,
                       sort_by: str = "popularity.desc",
                       page: int = 1) -> Dict:
        """
        Descubre películas con filtros avanzados
        
        Args:
            year: Año de lanzamiento
            genre_ids: Lista de IDs de géneros
            sort_by: Criterio de ordenación
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con películas descubiertas
        """
        endpoint = "/discover/movie"
        params = {
            "sort_by": sort_by,
            "page": page,
            "include_adult": "false",
            "include_video": "false"
        }
        
        if year:
            params["primary_release_year"] = year
        
        if genre_ids:
            params["with_genres"] = ",".join(map(str, genre_ids))
        
        return self._make_request(endpoint, params)
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Dict:
        """
        Obtiene recomendaciones basadas en una película
        
        Args:
            movie_id: ID de la película en TMDB
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con películas recomendadas
        """
        endpoint = f"/movie/{movie_id}/recommendations"
        params = {"page": page}
        
        return self._make_request(endpoint, params)
    
    def get_movie_similar(self, movie_id: int, page: int = 1) -> Dict:
        """
        Obtiene películas similares
        
        Args:
            movie_id: ID de la película en TMDB
            page: Número de página para resultados paginados
            
        Returns:
            Diccionario con películas similares
        """
        endpoint = f"/movie/{movie_id}/similar"
        params = {"page": page}
        
        return self._make_request(endpoint, params)
    
    def get_genres(self) -> Dict:
        """
        Obtiene lista de géneros de películas
        
        Returns:
            Diccionario con géneros de películas
        """
        endpoint = "/genre/movie/list"
        
        return self._make_request(endpoint)
    
    def get_poster_url(self, poster_path: str, size: str = "w500") -> Optional[str]:
        """
        Genera URL para un póster de película
        
        Args:
            poster_path: Ruta relativa del póster
            size: Tamaño del póster (w92, w154, w185, w342, w500, w780, original)
            
        Returns:
            URL completa del póster o None si no hay póster
        """
        if not poster_path:
            return None
        
        if size not in POSTER_SIZES:
            size = "w500"  # Tamaño predeterminado
        
        return f"{TMDB_IMAGE_BASE_URL}{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = "w1280") -> Optional[str]:
        """
        Genera URL para una imagen de fondo
        
        Args:
            backdrop_path: Ruta relativa de la imagen de fondo
            size: Tamaño de la imagen (w300, w780, w1280, original)
            
        Returns:
            URL completa de la imagen de fondo o None si no hay imagen
        """
        if not backdrop_path:
            return None
        
        if size not in BACKDROP_SIZES:
            size = "w1280"  # Tamaño predeterminado
        
        return f"{TMDB_IMAGE_BASE_URL}{size}{backdrop_path}"
    
    def get_profile_url(self, profile_path: str, size: str = "w185") -> Optional[str]:
        """
        Genera URL para una imagen de perfil (actores, directores)
        
        Args:
            profile_path: Ruta relativa de la imagen de perfil
            size: Tamaño de la imagen (w45, w185, h632, original)
            
        Returns:
            URL completa de la imagen de perfil o None si no hay imagen
        """
        if not profile_path:
            return None
        
        if size not in PROFILE_SIZES:
            size = "w185"  # Tamaño predeterminado
        
        return f"{TMDB_IMAGE_BASE_URL}{size}{profile_path}"
    
    def format_movie_data(self, movie: Dict) -> Dict:
        """
        Formatea los datos de una película para uso en la aplicación
        
        Args:
            movie: Datos crudos de la película desde la API
            
        Returns:
            Diccionario con datos formateados
        """
        # Extraer géneros si están disponibles
        genres = []
        if "genres" in movie:
            genres = [genre["name"] for genre in movie["genres"]]
        elif "genre_ids" in movie:
            # Obtener géneros desde IDs (requiere una llamada adicional)
            all_genres = self.get_genres().get("genres", [])
            genre_map = {g["id"]: g["name"] for g in all_genres}
            genres = [genre_map.get(gid, "") for gid in movie["genre_ids"] if gid in genre_map]
        
        # Construir objeto de película formateado
        formatted_movie = {
            "id": movie["id"],
            "title": movie["title"],
            "original_title": movie.get("original_title", ""),
            "overview": movie.get("overview", ""),
            "poster_url": self.get_poster_url(movie.get("poster_path")),
            "backdrop_url": self.get_backdrop_url(movie.get("backdrop_path")),
            "release_date": movie.get("release_date", ""),
            "genres": genres,
            "vote_average": movie.get("vote_average", 0),
            "vote_count": movie.get("vote_count", 0),
            "popularity": movie.get("popularity", 0)
        }
        
        # Extraer año de la fecha de lanzamiento
        if formatted_movie["release_date"]:
            try:
                formatted_movie["year"] = int(formatted_movie["release_date"].split("-")[0])
            except (ValueError, IndexError):
                formatted_movie["year"] = None
        else:
            formatted_movie["year"] = None
        
        return formatted_movie
