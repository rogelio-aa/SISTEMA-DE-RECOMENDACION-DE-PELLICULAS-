import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any

# Rutas de datos
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MOVIES_FILE = DATA_DIR / "movies.csv"
RATINGS_FILE = DATA_DIR / "ratings.csv"

# Caché para almacenar los DataFrames en memoria
_cache: Dict[str, Any] = {}

def load_movies() -> pd.DataFrame:
    """
    Carga y cachea el dataset de películas.
    
    Returns:
        DataFrame con información de películas
    """
    if "movies" not in _cache:
        if not os.path.exists(MOVIES_FILE):
            # Si no existe el archivo, crear un DataFrame vacío con la estructura correcta
            _cache["movies"] = pd.DataFrame({
                "movieId": [],
                "title": [],
                "genres": []
            })
        else:
            # Cargar desde el archivo CSV
            _cache["movies"] = pd.read_csv(MOVIES_FILE)
            
            # Asegurar que movieId sea de tipo entero
            _cache["movies"]["movieId"] = _cache["movies"]["movieId"].astype(int)
    
    return _cache["movies"]

def load_ratings() -> pd.DataFrame:
    """
    Carga y cachea el dataset de calificaciones.
    
    Returns:
        DataFrame con calificaciones de usuarios
    """
    if "ratings" not in _cache:
        if not os.path.exists(RATINGS_FILE):
            # Si no existe el archivo, crear un DataFrame vacío con la estructura correcta
            _cache["ratings"] = pd.DataFrame({
                "userId": [],
                "movieId": [],
                "rating": [],
                "timestamp": []
            })
        else:
            # Cargar desde el archivo CSV
            _cache["ratings"] = pd.read_csv(RATINGS_FILE)
            
            # Asegurar que los tipos de datos sean correctos
            _cache["ratings"]["userId"] = _cache["ratings"]["userId"].astype(int)
            _cache["ratings"]["movieId"] = _cache["ratings"]["movieId"].astype(int)
            _cache["ratings"]["rating"] = _cache["ratings"]["rating"].astype(float)
    
    return _cache["ratings"]

def clear_cache():
    """Limpia la caché de datos en memoria"""
    _cache.clear()
