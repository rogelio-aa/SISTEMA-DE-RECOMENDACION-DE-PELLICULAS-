from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import os
import pandas as pd
from starlette.requests import Request

from app.tmdb_api import TMDBApi
from app.data_loader import load_movies, load_ratings # Import data loading functions
from app.recommender import prepare_content_similarity, get_hybrid_recommendations # Import new recommender functions

# Inicializar FastAPI
app = FastAPI(
    title="VINCENT - Sistema de Recomendación de Películas Avanzado",
    description="API para el sistema de recomendación de películas VINCENT, combinando TMDB y lógica híbrida.",
    version="3.0.0" # Version incrementada por mejoras
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Inicializar cliente de TMDB API
tmdb_api = TMDBApi()

# Cargar datos y preparar similitud al inicio (puede tardar un poco)
print("Cargando datos de películas y calificaciones...")
movies_df = load_movies()
ratings_df = load_ratings()
print("Preparando matriz de similitud de contenido...")
prepare_content_similarity(movies_df)
print("Datos y similitud preparados.")

# Dependencia para obtener el cliente de TMDB API
def get_tmdb_api():
    return tmdb_api

# Dependencias para obtener los DataFrames
def get_movies_df():
    return movies_df

def get_ratings_df():
    return ratings_df

# Rutas para la interfaz web
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Página principal del sistema de recomendación"""
    return templates.TemplateResponse("index.html", {"request": request})

# --- Endpoints existentes (Populares, Mejor valoradas, etc.) --- 
# (Se mantienen igual, usando TMDB directamente para estas listas)

@app.get("/api/movies/popular")
async def get_popular_movies(
    page: int = Query(1, ge=1),
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    result = tmdb.get_popular_movies(page)
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    movies = [tmdb.format_movie_data(movie) for movie in result.get("results", [])]
    return {
        "movies": movies,
        "page": result.get("page", 1),
        "total_pages": result.get("total_pages", 1),
        "total_results": result.get("total_results", 0)
    }

@app.get("/api/movies/top_rated")
async def get_top_rated_movies(
    page: int = Query(1, ge=1),
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    result = tmdb.get_top_rated_movies(page)
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    movies = [tmdb.format_movie_data(movie) for movie in result.get("results", [])]
    return {
        "movies": movies,
        "page": result.get("page", 1),
        "total_pages": result.get("total_pages", 1),
        "total_results": result.get("total_results", 0)
    }

@app.get("/api/movies/now_playing")
async def get_now_playing_movies(
    page: int = Query(1, ge=1),
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    result = tmdb.get_now_playing_movies(page)
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    movies = [tmdb.format_movie_data(movie) for movie in result.get("results", [])]
    return {
        "movies": movies,
        "page": result.get("page", 1),
        "total_pages": result.get("total_pages", 1),
        "total_results": result.get("total_results", 0)
    }

@app.get("/api/movies/upcoming")
async def get_upcoming_movies(
    page: int = Query(1, ge=1),
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    result = tmdb.get_upcoming_movies(page)
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    movies = [tmdb.format_movie_data(movie) for movie in result.get("results", [])]
    return {
        "movies": movies,
        "page": result.get("page", 1),
        "total_pages": result.get("total_pages", 1),
        "total_results": result.get("total_results", 0)
    }

@app.get("/api/movies/search")
async def search_movies(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    result = tmdb.search_movies(query, page)
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    movies = [tmdb.format_movie_data(movie) for movie in result.get("results", [])]
    return {
        "movies": movies,
        "page": result.get("page", 1),
        "total_pages": result.get("total_pages", 1),
        "total_results": result.get("total_results", 0)
    }

@app.get("/api/movies/discover")
async def discover_movies(
    year: Optional[int] = None,
    genre: Optional[str] = None,
    sort_by: str = Query("popularity.desc", regex="^(popularity|vote_average|release_date|revenue)\.(asc|desc)$"),
    page: int = Query(1, ge=1),
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    genre_ids = None
    if genre:
        try:
            genre_ids = [int(g) for g in genre.split(",") if g.strip().isdigit()]
        except ValueError:
             raise HTTPException(status_code=400, detail="Formato de ID de género inválido. Debe ser una lista de números separados por comas.")

    result = tmdb.discover_movies(year, genre_ids, sort_by, page)
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    movies = [tmdb.format_movie_data(movie) for movie in result.get("results", [])]
    return {
        "movies": movies,
        "page": result.get("page", 1),
        "total_pages": result.get("total_pages", 1),
        "total_results": result.get("total_results", 0)
    }

@app.get("/api/movies/{movie_id}")
async def get_movie_details(
    movie_id: int,
    tmdb: TMDBApi = Depends(get_tmdb_api)
):
    result = tmdb.get_movie_details(movie_id)
    if "error" in result or "id" not in result:
        # Intentar buscar por ID si TMDB falla (puede ser un ID local)
        local_movie = movies_df[movies_df["movieId"] == movie_id]
        if not local_movie.empty:
             # Si existe localmente, devolver datos básicos
             movie_data = local_movie.iloc[0].to_dict()
             # Intentar enriquecer con TMDB si es posible (ej. buscar por título)
             # Esto es opcional y puede añadir complejidad
             return movie_data 
        else:
             raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} no encontrada localmente ni en TMDB.")

    # Formatear datos de TMDB
    movie_data = tmdb.format_movie_data(result)
    
    # Añadir datos adicionales de TMDB
    if "credits" in result:
        movie_data["cast"] = result["credits"].get("cast", [])[:10]
        movie_data["crew"] = [p for p in result["credits"].get("crew", []) if p.get("job") == "Director"][:3]
    if "videos" in result and "results" in result["videos"]:
        movie_data["videos"] = [v for v in result["videos"]["results"] if v.get("site") == "YouTube" and v.get("type") == "Trailer"][:3]
    # Nota: Las recomendaciones y similares de TMDB se obtendrán del endpoint dedicado
    
    return movie_data

# --- Endpoint de Recomendación Híbrida --- 

@app.get("/api/movies/{movie_id}/recommendations")
async def get_hybrid_movie_recommendations(
    movie_id: int,
    num_recommendations: int = Query(10, ge=5, le=50), # Permitir entre 5 y 50 recomendaciones
    weight_content: float = Query(0.5, ge=0.0, le=1.0),
    weight_collab: float = Query(0.5, ge=0.0, le=1.0),
    movies: pd.DataFrame = Depends(get_movies_df),
    ratings: pd.DataFrame = Depends(get_ratings_df),
    tmdb: TMDBApi = Depends(get_tmdb_api) # Añadido para enriquecer resultados
):
    """
    Obtiene recomendaciones híbridas (contenido + colaborativo) para una película.
    """
    # Validar que los pesos sumen aproximadamente 1 (opcional, pero buena práctica)
    # if not (0.99 < weight_content + weight_collab < 1.01):
    #     raise HTTPException(status_code=400, detail="La suma de weight_content y weight_collab debe ser aproximadamente 1.")

    # Verificar si el movie_id existe en nuestro dataset local
    if movie_id not in movies["movieId"].values:
         # Intentar obtener detalles de TMDB para ver si existe allí
         tmdb_details = tmdb.get_movie_details(movie_id)
         if "error" in tmdb_details or "id" not in tmdb_details:
              raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} no encontrada en la base de datos local ni en TMDB.")
         else:
              # Si existe en TMDB pero no localmente, podríamos añadirla o devolver error
              # Por ahora, devolvemos error si no está en el dataset local para recomendaciones
              raise HTTPException(status_code=404, detail=f"Película con ID {movie_id} encontrada en TMDB pero no en el dataset local para generar recomendaciones.")

    print(f"Generando recomendaciones híbridas para movie_id: {movie_id}")
    recommendations = get_hybrid_recommendations(
        movie_id=movie_id,
        movies_df=movies,
        ratings_df=ratings,
        num_recommendations=num_recommendations,
        weight_content=weight_content,
        weight_collab=weight_collab
    )
    
    # Enriquecer las recomendaciones con datos de TMDB (poster, etc.)
    enriched_recommendations = []
    for rec in recommendations:
        try:
            # Intentar obtener detalles de TMDB para la película recomendada
            tmdb_rec_details = tmdb.get_movie_details(rec["movieId"])
            if "error" not in tmdb_rec_details and "id" in tmdb_rec_details:
                formatted_rec = tmdb.format_movie_data(tmdb_rec_details)
                formatted_rec["hybrid_score"] = rec["hybrid_score"] # Mantener la puntuación híbrida
                enriched_recommendations.append(formatted_rec)
            else:
                # Si falla TMDB, usar datos locales básicos si existen
                local_data_query = movies[movies["movieId"] == rec["movieId"]]
                if not local_data_query.empty:
                    local_data = local_data_query.iloc[0].to_dict()
                    local_data["hybrid_score"] = rec["hybrid_score"]
                    local_data["poster_url"] = None # Indicar que no hay póster
                    local_data["backdrop_url"] = None
                    enriched_recommendations.append(local_data)
                    print(f"Advertencia: No se pudieron obtener detalles de TMDB para la película recomendada ID {rec['movieId']}. Usando datos locales.")
                else:
                    print(f"Advertencia: No se encontraron detalles de TMDB ni datos locales para la película recomendada ID {rec['movieId']}. Omitiendo.")
        except Exception as e:
            print(f"Error al enriquecer la recomendación {rec['movieId']}: {e}. Usando datos locales si es posible.")
            local_data_query = movies[movies["movieId"] == rec["movieId"]]
            if not local_data_query.empty:
                local_data = local_data_query.iloc[0].to_dict()
                local_data["hybrid_score"] = rec["hybrid_score"]
                local_data["poster_url"] = None
                local_data["backdrop_url"] = None
                enriched_recommendations.append(local_data)
            else:
                 print(f"Error y sin datos locales para {rec['movieId']}. Omitiendo.")


    if not enriched_recommendations:
        # Si no hay recomendaciones, devolver TMDB como fallback (o lista vacía)
        print(f"No se generaron recomendaciones híbridas para {movie_id}. Usando fallback de TMDB.")
        tmdb_recs_result = tmdb.get_movie_recommendations(movie_id, page=1)
        if "error" not in tmdb_recs_result:
             enriched_recommendations = [tmdb.format_movie_data(m) for m in tmdb_recs_result.get("results", [])[:num_recommendations]]
        else:
             print(f"Fallback de TMDB también falló para {movie_id}.")
             # Podríamos devolver películas similares o populares como último recurso
             # O simplemente devolver una lista vacía
             pass # Devolver lista vacía por defecto

    return {"recommendations": enriched_recommendations}

@app.get("/api/genres")
async def get_genres(tmdb: TMDBApi = Depends(get_tmdb_api)):
    """Obtiene lista de géneros de películas"""
    result = tmdb.get_genres()
    if "error" in result:
        raise HTTPException(status_code=result["error"], detail=result["message"])
    return result

# Punto de entrada para ejecución directa
if __name__ == "__main__":
    import uvicorn
    # Ejecutar en 0.0.0.0 para ser accesible externamente si se expone el puerto
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Añadido reload=True para desarrollo

