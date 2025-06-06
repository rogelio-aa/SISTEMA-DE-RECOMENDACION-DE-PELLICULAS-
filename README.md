# Sistema de Recomendación de Películas - Versión Global

## Descripción General
Este sistema de recomendación de películas utiliza la API de TMDB (The Movie Database) para proporcionar acceso a un catálogo de millones de películas con imágenes de alta calidad, información detallada y recomendaciones personalizadas.

## Características Principales
- **Catálogo global** con millones de películas actuales y antiguas
- **Imágenes de alta calidad** para todas las películas (carteles, fondos, fotos del reparto)
- **Interfaz moderna** con tema claro/oscuro personalizable
- **Búsqueda avanzada** con filtros por año, género y popularidad
- **Paginación infinita** para explorar todo el catálogo
- **Secciones especializadas** (populares, mejor valoradas, estrenos, próximamente)
- **Visualización detallada** de películas con sinopsis, reparto y trailers
- **Recomendaciones personalizadas** basadas en similitud entre películas
- **Arquitectura escalable** con sistema de caché para optimizar rendimiento

## Estructura del Proyecto
```
movie_recommender_pro/
│
├── app/
│   ├── main.py                # Punto de entrada FastAPI
│   ├── tmdb_api.py            # Cliente para API de TMDB
│   ├── templates/
│   │   └── index.html         # Interfaz web principal
│   └── static/
│       ├── style.css          # Estilos con soporte para temas
│       ├── script.js          # Interacción del frontend y APIs
│       └── images/            # Imágenes estáticas del sistema
│
├── data/
│   └── cache/                 # Caché de respuestas de API
│
├── tests/                     # Pruebas unitarias y de integración
│
├── Dockerfile                 # Configuración para containerización
├── docker-compose.yml         # Orquestación de servicios
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación principal
```

## Requisitos
- Python 3.8+
- FastAPI
- Requests
- Redis (opcional, para caché distribuida)
- Docker (para despliegue)

## Instalación y Ejecución

### Método 1: Ejecución Local
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
uvicorn app.main:app --reload
```

### Método 2: Usando Docker
```bash
# Construir y ejecutar con Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f
```

## Uso de la API
El sistema proporciona los siguientes endpoints:

- `GET /api/movies/popular` - Películas populares
- `GET /api/movies/top_rated` - Películas mejor valoradas
- `GET /api/movies/now_playing` - Películas en cartelera
- `GET /api/movies/upcoming` - Próximos estrenos
- `GET /api/movies/search` - Búsqueda de películas
- `GET /api/movies/discover` - Descubrimiento con filtros
- `GET /api/movies/{movie_id}` - Detalles de una película
- `GET /api/movies/{movie_id}/recommendations` - Recomendaciones
- `GET /api/genres` - Lista de géneros

## Optimizaciones de Rendimiento
- **Sistema de caché** para reducir llamadas a la API externa
- **Carga diferida** de imágenes para mejorar tiempos de carga
- **Paginación eficiente** para manejar grandes volúmenes de datos
- **Formato optimizado** de respuestas para reducir transferencia de datos

## Atribuciones
Este proyecto utiliza datos de [The Movie Database (TMDB)](https://www.themoviedb.org/), pero no está respaldado ni certificado por TMDB.

## Licencia
Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
