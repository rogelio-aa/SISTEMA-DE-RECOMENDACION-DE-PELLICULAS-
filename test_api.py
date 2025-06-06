import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPI(unittest.TestCase):
    """Pruebas de integración para la API del sistema de recomendación"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.client = TestClient(app)
    
    def test_get_movies(self):
        """Prueba el endpoint para obtener películas"""
        response = self.client.get("/api/movies")
        
        # Verificar código de estado
        self.assertEqual(response.status_code, 200)
        
        # Verificar estructura de respuesta
        data = response.json()
        self.assertIn("movies", data)
        self.assertIsInstance(data["movies"], list)
        
        # Verificar que hay películas
        self.assertGreater(len(data["movies"]), 0)
        
        # Verificar estructura de una película
        movie = data["movies"][0]
        self.assertIn("movieId", movie)
        self.assertIn("title", movie)
        self.assertIn("genres", movie)
    
    def test_get_recommendations(self):
        """Prueba el endpoint para obtener recomendaciones"""
        # Obtener una película existente
        movies_response = self.client.get("/api/movies")
        movies = movies_response.json()["movies"]
        movie_id = movies[0]["movieId"]
        
        # Obtener recomendaciones para esa película
        response = self.client.get(f"/api/recommendations/{movie_id}")
        
        # Verificar código de estado
        self.assertEqual(response.status_code, 200)
        
        # Verificar estructura de respuesta
        data = response.json()
        self.assertIn("recommendations", data)
        self.assertIsInstance(data["recommendations"], list)
    
    def test_invalid_movie_id(self):
        """Prueba el comportamiento con un ID de película inválido"""
        response = self.client.get("/api/recommendations/999999")
        
        # Verificar código de estado de error
        self.assertEqual(response.status_code, 404)
        
        # Verificar mensaje de error
        data = response.json()
        self.assertIn("detail", data)
    
    def test_num_recommendations_parameter(self):
        """Prueba el parámetro de número de recomendaciones"""
        # Obtener una película existente
        movies_response = self.client.get("/api/movies")
        movies = movies_response.json()["movies"]
        movie_id = movies[0]["movieId"]
        
        # Obtener un número específico de recomendaciones
        num_recommendations = 5
        response = self.client.get(f"/api/recommendations/{movie_id}?num_recommendations={num_recommendations}")
        
        # Verificar código de estado
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el número de recomendaciones es correcto
        data = response.json()
        self.assertLessEqual(len(data["recommendations"]), num_recommendations)

if __name__ == '__main__':
    unittest.main()
