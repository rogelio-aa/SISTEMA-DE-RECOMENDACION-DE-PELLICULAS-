
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Instancia global para evitar recálculos innecesarios
tfidf = TfidfVectorizer(stop_words='english')
cosine_sim_content = None
movie_indices = None

def prepare_content_similarity(movies_df: pd.DataFrame):
    """
    Precalcula la matriz de similitud de contenido basada en géneros.
    
    Args:
        movies_df: DataFrame con información de películas (incluyendo 'genres').
    """
    global cosine_sim_content, movie_indices
    
    # Reemplazar NaN en géneros con cadena vacía
    movies_df['genres'] = movies_df['genres'].fillna('')
    
    # Calcular matriz TF-IDF
    tfidf_matrix = tfidf.fit_transform(movies_df['genres'])
    
    # Calcular matriz de similitud de coseno
    cosine_sim_content = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # Crear un mapeo inverso de IDs de película a índices del DataFrame
    movie_indices = pd.Series(movies_df.index, index=movies_df['movieId']).drop_duplicates()

def get_content_recommendations(movie_id: int, movies_df: pd.DataFrame, num_recommendations: int = 10) -> List[Dict[str, Any]]:
    """
    Genera recomendaciones basadas en similitud de contenido (géneros).
    
    Args:
        movie_id: ID de la película base.
        movies_df: DataFrame de películas.
        num_recommendations: Número de recomendaciones a devolver.
        
    Returns:
        Lista de diccionarios con películas recomendadas y su puntuación de similitud.
    """
    global cosine_sim_content, movie_indices
    
    if cosine_sim_content is None or movie_indices is None:
        print("Error: La similitud de contenido no ha sido preparada. Llama a prepare_content_similarity primero.")
        prepare_content_similarity(movies_df) # Intentar preparar si no está listo
        if cosine_sim_content is None or movie_indices is None:
             return []

    if movie_id not in movie_indices:
        print(f"Advertencia: movie_id {movie_id} no encontrado en movie_indices para recomendaciones de contenido.")
        return []

    idx = movie_indices[movie_id]

    # Obtener las puntuaciones de similitud de todas las películas con esa película
    sim_scores = list(enumerate(cosine_sim_content[idx]))

    # Ordenar las películas según las puntuaciones de similitud
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Obtener las puntuaciones de las N películas más similares (excluyendo la propia película)
    sim_scores = sim_scores[1:num_recommendations+1]

    # Obtener los índices de las películas
    movie_indices_rec = [i[0] for i in sim_scores]
    
    # Obtener los IDs de las películas
    recommended_movie_ids = movies_df['movieId'].iloc[movie_indices_rec].tolist()
    
    # Crear la lista de resultados
    recommendations = []
    for i, score in enumerate(sim_scores):
        rec_movie_id = recommended_movie_ids[i]
        movie_details = movies_df[movies_df['movieId'] == rec_movie_id].iloc[0]
        recommendations.append({
            'movieId': int(rec_movie_id),
            'title': movie_details['title'],
            'genres': movie_details['genres'],
            'content_similarity_score': float(score[1])
        })
        
    return recommendations

def get_collaborative_recommendations(movie_id: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame, num_recommendations: int = 10) -> List[Dict[str, Any]]:
    """
    Genera recomendaciones de películas basadas en similitud de calificaciones de usuarios (filtrado colaborativo).
    
    Args:
        movie_id: ID de la película base para las recomendaciones
        movies_df: DataFrame con información de películas
        ratings_df: DataFrame con calificaciones de usuarios
        num_recommendations: Número de recomendaciones a devolver
        
    Returns:
        Lista de diccionarios con información de películas recomendadas y puntuación de similitud.
    """
    # Verificar si la película existe
    if movie_id not in movies_df['movieId'].values:
        print(f"Advertencia: movie_id {movie_id} no encontrado en movies_df para recomendaciones colaborativas.")
        return []
    
    # Crear matriz de calificaciones de usuario-película (considerar optimizar esto)
    # Filtrar usuarios/películas con pocas calificaciones podría mejorar la calidad
    user_item_matrix = ratings_df.pivot_table(index='userId', columns='movieId', values='rating')
    
    # Rellenar NaNs con 0 (o la media de calificación del usuario/película)
    user_item_matrix_filled = user_item_matrix.fillna(0)
    
    # Calcular similitud entre películas (correlación de Pearson)
    try:
        # Asegurarse de que hay varianza suficiente para calcular correlación
        if movie_id not in user_item_matrix_filled.columns or user_item_matrix_filled[movie_id].std() == 0:
             print(f"Advertencia: No hay suficientes datos o varianza para {movie_id} en recomendaciones colaborativas.")
             return []
             
        movie_similarity = user_item_matrix_filled.corrwith(user_item_matrix_filled[movie_id])
    except Exception as e:
        print(f"Error calculando correlación para {movie_id}: {e}")
        return []

    # Eliminar NaNs y la propia película
    similar_movies = movie_similarity.dropna().drop(movie_id, errors='ignore')
    
    # Considerar un umbral mínimo de calificaciones para las películas recomendadas
    # ratings_count = ratings_df.groupby('movieId').size()
    # min_ratings_threshold = 10 # Ejemplo
    # valid_movies = ratings_count[ratings_count >= min_ratings_threshold].index
    # similar_movies = similar_movies[similar_movies.index.isin(valid_movies)]

    # Ordenar y obtener las N mejores
    top_similar_ids = similar_movies.sort_values(ascending=False).head(num_recommendations).index.tolist()
    
    # Obtener detalles y puntuaciones
    recommendations = []
    valid_movie_data = movies_df[movies_df['movieId'].isin(top_similar_ids)]
    
    for rec_movie_id in top_similar_ids:
        if rec_movie_id in similar_movies.index and rec_movie_id in valid_movie_data['movieId'].values:
            movie_details = valid_movie_data[valid_movie_data['movieId'] == rec_movie_id].iloc[0]
            recommendations.append({
                'movieId': int(rec_movie_id),
                'title': movie_details['title'],
                'genres': movie_details['genres'],
                'collaborative_similarity_score': float(similar_movies[rec_movie_id])
            })
            
    return recommendations

def get_hybrid_recommendations(movie_id: int, movies_df: pd.DataFrame, ratings_df: pd.DataFrame, num_recommendations: int = 10, weight_content: float = 0.5, weight_collab: float = 0.5) -> List[Dict[str, Any]]:
    """
    Genera recomendaciones híbridas combinando contenido y filtrado colaborativo.
    
    Args:
        movie_id: ID de la película base.
        movies_df: DataFrame de películas.
        ratings_df: DataFrame de calificaciones.
        num_recommendations: Número total de recomendaciones a devolver.
        weight_content: Peso para las recomendaciones basadas en contenido.
        weight_collab: Peso para las recomendaciones colaborativas.
        
    Returns:
        Lista de diccionarios con películas recomendadas y puntuación híbrida.
    """
    # Preparar similitud de contenido si no está lista
    global cosine_sim_content
    if cosine_sim_content is None:
        prepare_content_similarity(movies_df)
        
    # Obtener recomendaciones de ambos métodos (pedir más para tener margen)
    content_recs = get_content_recommendations(movie_id, movies_df, num_recommendations * 2)
    collab_recs = get_collaborative_recommendations(movie_id, movies_df, ratings_df, num_recommendations * 2)
    
    # Combinar y calcular puntuación híbrida
    hybrid_scores: Dict[int, float] = {}
    movie_details_map: Dict[int, Dict[str, Any]] = {}

    # Procesar recomendaciones de contenido
    for rec in content_recs:
        mid = rec['movieId']
        if mid not in hybrid_scores:
            hybrid_scores[mid] = 0.0
            movie_details_map[mid] = {'movieId': mid, 'title': rec['title'], 'genres': rec['genres']}
        hybrid_scores[mid] += rec['content_similarity_score'] * weight_content

    # Procesar recomendaciones colaborativas
    for rec in collab_recs:
        mid = rec['movieId']
        if mid not in hybrid_scores:
            hybrid_scores[mid] = 0.0
            movie_details_map[mid] = {'movieId': mid, 'title': rec['title'], 'genres': rec['genres']}
        hybrid_scores[mid] += rec['collaborative_similarity_score'] * weight_collab
        
    # Eliminar la película original si aparece
    if movie_id in hybrid_scores:
        del hybrid_scores[movie_id]

    # Ordenar por puntuación híbrida
    sorted_recs = sorted(hybrid_scores.items(), key=lambda item: item[1], reverse=True)
    
    # Formatear salida final
    final_recommendations = []
    for mid, score in sorted_recs[:num_recommendations]:
        details = movie_details_map.get(mid, {'movieId': mid, 'title': 'N/A', 'genres': 'N/A'}) # Fallback
        details['hybrid_score'] = float(score)
        final_recommendations.append(details)
        
    return final_recommendations

# Ejemplo de uso (requiere cargar los dataframes primero)
# movies = load_movies()
# ratings = load_ratings()
# prepare_content_similarity(movies)
# recommendations = get_hybrid_recommendations(1, movies, ratings)
# print(recommendations)

