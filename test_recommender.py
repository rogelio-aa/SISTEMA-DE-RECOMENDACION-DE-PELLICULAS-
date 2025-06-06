import unittest
from app.recommender import MovieRecommender
import pandas as pd
import numpy as np

class TestRecommender(unittest.TestCase):
    """Pruebas unitarias para el sistema de recomendación"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear datos de prueba
        movies_data = {
            'movieId': [1, 2, 3, 4, 5],
            'title': ['Película 1 (2020)', 'Película 2 (2019)', 'Película 3 (2018)', 
                     'Película 4 (2021)', 'Película 5 (2017)'],
            'genres': ['Action|Adventure', 'Comedy|Romance', 'Drama|Thriller', 
                      'Action|Sci-Fi', 'Comedy|Drama']
        }
        
        ratings_data = {
            'userId': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'movieId': [1, 2, 4, 1, 3, 5, 2, 3, 4],
            'rating': [5.0, 3.0, 4.0, 4.0, 5.0, 3.0, 2.0, 4.0, 5.0],
            'timestamp': [1000000, 1000001, 1000002, 1000003, 1000004, 
                         1000005, 1000006, 1000007, 1000008]
        }
        
        self.movies_df = pd.DataFrame(movies_data)
        self.ratings_df = pd.DataFrame(ratings_data)
        
        # Inicializar el recomendador con datos de prueba
        self.recommender = MovieRecommender()
        self.recommender.load_data(self.movies_df, self.ratings_df)
    
    def test_movie_similarity(self):
        """Prueba el cálculo de similitud entre películas"""
        # Verificar que la similitud de una película consigo misma es 1.0
        self.assertEqual(self.recommender.calculate_similarity(1, 1), 1.0)
        
        # Verificar que la similitud está entre 0 y 1
        similarity = self.recommender.calculate_similarity(1, 2)
        self.assertTrue(0 <= similarity <= 1)
    
    def test_get_recommendations(self):
        """Prueba la obtención de recomendaciones"""
        # Obtener recomendaciones para la película 1
        recommendations = self.recommender.get_recommendations(1, 3)
        
        # Verificar que devuelve el número correcto de recomendaciones
        self.assertLessEqual(len(recommendations), 3)
        
        # Verificar que las recomendaciones tienen el formato correcto
        for rec in recommendations:
            self.assertIn('movieId', rec)
            self.assertIn('title', rec)
            self.assertIn('genres', rec)
            self.assertIn('similarity_score', rec)
            self.assertTrue(0 <= rec['similarity_score'] <= 1)
    
    def test_unknown_movie(self):
        """Prueba el comportamiento con películas desconocidas"""
        # Intentar obtener recomendaciones para una película que no existe
        recommendations = self.recommender.get_recommendations(999, 3)
        
        # Verificar que devuelve una lista vacía
        self.assertEqual(recommendations, [])
    
    def test_collaborative_filtering(self):
        """Prueba el algoritmo de filtrado colaborativo"""
        # Verificar que las películas con patrones de calificación similares
        # tienen mayor similitud
        similarity_1_4 = self.recommender.calculate_similarity(1, 4)  # Ambas bien calificadas por usuarios 1 y 3
        similarity_1_5 = self.recommender.calculate_similarity(1, 5)  # Patrones diferentes
        
        self.assertGreater(similarity_1_4, similarity_1_5)

if __name__ == '__main__':
    unittest.main()
