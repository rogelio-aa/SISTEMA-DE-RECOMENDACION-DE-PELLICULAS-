import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class UserProfile:
    """
    Clase para gestionar perfiles de usuario, historial y preferencias
    """
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self.preferences = {
            "genres": [],
            "favorite_movies": [],
            "disliked_movies": [],
            "theme": "light"
        }
        self.watch_history = []
        self.custom_lists = {}
        self.created_at = datetime.now().isoformat()
        self.last_login = datetime.now().isoformat()
    
    def add_to_history(self, movie_id: str, title: str, rating: Optional[float] = None):
        """Añade una película al historial de visualización"""
        self.watch_history.append({
            "movie_id": movie_id,
            "title": title,
            "rating": rating,
            "watched_at": datetime.now().isoformat()
        })
    
    def add_to_list(self, list_name: str, movie_id: str, title: str):
        """Añade una película a una lista personalizada"""
        if list_name not in self.custom_lists:
            self.custom_lists[list_name] = []
        
        # Evitar duplicados
        if not any(movie["movie_id"] == movie_id for movie in self.custom_lists[list_name]):
            self.custom_lists[list_name].append({
                "movie_id": movie_id,
                "title": title,
                "added_at": datetime.now().isoformat()
            })
    
    def remove_from_list(self, list_name: str, movie_id: str) -> bool:
        """Elimina una película de una lista personalizada"""
        if list_name not in self.custom_lists:
            return False
        
        initial_length = len(self.custom_lists[list_name])
        self.custom_lists[list_name] = [
            movie for movie in self.custom_lists[list_name] 
            if movie["movie_id"] != movie_id
        ]
        
        return len(self.custom_lists[list_name]) < initial_length
    
    def update_preferences(self, preferences: Dict):
        """Actualiza las preferencias del usuario"""
        for key, value in preferences.items():
            if key in self.preferences:
                self.preferences[key] = value
    
    def to_dict(self) -> Dict:
        """Convierte el perfil a diccionario para almacenamiento"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "preferences": self.preferences,
            "watch_history": self.watch_history,
            "custom_lists": self.custom_lists,
            "created_at": self.created_at,
            "last_login": self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """Crea un perfil desde un diccionario"""
        profile = cls(data["user_id"], data["username"])
        profile.preferences = data["preferences"]
        profile.watch_history = data["watch_history"]
        profile.custom_lists = data["custom_lists"]
        profile.created_at = data["created_at"]
        profile.last_login = data["last_login"]
        return profile


class UserManager:
    """
    Gestor de usuarios para el sistema de recomendación
    """
    def __init__(self, storage_path: str = "data/users"):
        self.storage_path = storage_path
        self.users = {}
        self._ensure_storage_exists()
        self._load_users()
    
    def _ensure_storage_exists(self):
        """Asegura que el directorio de almacenamiento existe"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_user_file_path(self, user_id: str) -> str:
        """Obtiene la ruta del archivo de un usuario"""
        return os.path.join(self.storage_path, f"{user_id}.json")
    
    def _load_users(self):
        """Carga todos los usuarios desde el almacenamiento"""
        if not os.path.exists(self.storage_path):
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                user_id = filename[:-5]  # Eliminar .json
                self._load_user(user_id)
    
    def _load_user(self, user_id: str) -> Optional[UserProfile]:
        """Carga un usuario específico desde el almacenamiento"""
        file_path = self._get_user_file_path(user_id)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                user_data = json.load(f)
                user = UserProfile.from_dict(user_data)
                self.users[user_id] = user
                return user
        except Exception as e:
            print(f"Error loading user {user_id}: {e}")
            return None
    
    def save_user(self, user: UserProfile):
        """Guarda un usuario en el almacenamiento"""
        file_path = self._get_user_file_path(user.user_id)
        with open(file_path, 'w') as f:
            json.dump(user.to_dict(), f, indent=2)
        self.users[user.user_id] = user
    
    def create_user(self, username: str) -> UserProfile:
        """Crea un nuevo usuario"""
        user_id = f"user_{len(self.users) + 1}"
        user = UserProfile(user_id, username)
        self.save_user(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Obtiene un usuario por su ID"""
        if user_id in self.users:
            return self.users[user_id]
        return self._load_user(user_id)
    
    def update_last_login(self, user_id: str):
        """Actualiza la fecha de último inicio de sesión"""
        user = self.get_user(user_id)
        if user:
            user.last_login = datetime.now().isoformat()
            self.save_user(user)
    
    def get_all_users(self) -> List[UserProfile]:
        """Obtiene todos los usuarios"""
        return list(self.users.values())


class GroupRecommendation:
    """
    Clase para gestionar recomendaciones grupales
    """
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
    
    def get_group_recommendations(self, user_ids: List[str], limit: int = 10) -> List[Dict]:
        """
        Genera recomendaciones para un grupo de usuarios
        basadas en preferencias compartidas
        """
        # Obtener usuarios
        users = [self.user_manager.get_user(user_id) for user_id in user_ids]
        users = [user for user in users if user is not None]
        
        if not users:
            return []
        
        # Recopilar géneros preferidos
        all_genres = {}
        for user in users:
            for genre in user.preferences.get("genres", []):
                all_genres[genre] = all_genres.get(genre, 0) + 1
        
        # Ordenar géneros por popularidad en el grupo
        popular_genres = sorted(
            all_genres.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Recopilar películas favoritas
        favorite_movies = {}
        for user in users:
            for movie in user.preferences.get("favorite_movies", []):
                favorite_movies[movie["movie_id"]] = favorite_movies.get(movie["movie_id"], 0) + 1
        
        # Aquí se implementaría la lógica real de recomendación basada en los datos recopilados
        # Por ahora, devolvemos una estructura simulada
        
        return [
            {
                "movie_id": f"movie_{i}",
                "title": f"Película recomendada para grupo {i}",
                "genres": [genre for genre, _ in popular_genres[:3]],
                "group_score": 0.9 - (i * 0.05),
                "reason": "Basada en géneros y películas favoritas compartidas"
            }
            for i in range(1, limit + 1)
        ]
