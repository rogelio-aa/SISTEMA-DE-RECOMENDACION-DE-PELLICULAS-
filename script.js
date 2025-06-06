// Configuración global
const API_BASE_URL = '/api';
let currentSection = 'popular';
let previousSection = null;
let searchQuery = '';

// Variables de paginación
const paginationState = {
    popular: { page: 1, totalPages: 1, loading: false },
    'top-rated': { page: 1, totalPages: 1, loading: false },
    'now-playing': { page: 1, totalPages: 1, loading: false },
    upcoming: { page: 1, totalPages: 1, loading: false },
    discover: { page: 1, totalPages: 1, loading: false },
    search: { page: 1, totalPages: 1, loading: false }
};

// Caché de géneros
let genresCache = {};

// Elementos DOM
document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const searchInput = document.getElementById('movie-search');
    const searchButton = document.getElementById('search-button');
    const navLinks = document.querySelectorAll('.nav-link');
    const themeToggle = document.getElementById('theme-toggle');
    const yearFilter = document.getElementById('year-filter');
    const genreFilter = document.getElementById('genre-filter');
    const sortFilter = document.getElementById('sort-filter');
    const applyFiltersButton = document.getElementById('apply-filters');
    const backButton = document.getElementById('back-button');
    const loadMoreButtons = document.querySelectorAll('.load-more-button');
    
    // Inicializar tema
    initTheme();
    
    // Inicializar filtros
    initFilters();
    
    // Cargar películas populares al inicio
    loadMovies('popular', 1);
    
    // Event listeners para navegación
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');
            changeSection(section);
        });
    });
    
    // Event listener para búsqueda
    searchButton.addEventListener('click', () => {
        handleSearch();
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Event listener para cambio de tema
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });
    
    // Event listener para aplicar filtros
    applyFiltersButton.addEventListener('click', () => {
        applyFilters();
    });
    
    // Event listener para botón de volver
    backButton.addEventListener('click', () => {
        hideMovieDetails();
    });
    
    // Event listeners para botones de cargar más
    loadMoreButtons.forEach(button => {
        button.addEventListener('click', () => {
            const sectionId = button.id.replace('load-more-', '');
            loadMoreMovies(sectionId);
        });
    });
    
    // Inicializar años para el filtro
    initYearFilter();
});

// Funciones principales
function initTheme() {
    // Verificar si hay un tema guardado en localStorage
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.getElementById('theme-toggle').checked = true;
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        document.getElementById('theme-toggle').checked = false;
    }
    
    // Mostrar el cuerpo después de establecer el tema para evitar parpadeo
    document.body.style.visibility = 'visible';
}

function initYearFilter() {
    const yearFilter = document.getElementById('year-filter');
    const currentYear = new Date().getFullYear();
    
    // Añadir años desde 1900 hasta el actual
    for (let year = currentYear; year >= 1900; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearFilter.appendChild(option);
    }
}

async function initFilters() {
    try {
        // Cargar géneros
        const response = await fetch(`${API_BASE_URL}/genres`);
        const data = await response.json();
        
        if (data && data.genres) {
            const genreFilter = document.getElementById('genre-filter');
            
            // Guardar géneros en caché
            data.genres.forEach(genre => {
                genresCache[genre.id] = genre.name;
                
                const option = document.createElement('option');
                option.value = genre.id;
                option.textContent = genre.name;
                genreFilter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar géneros:', error);
    }
}

function changeSection(section) {
    // Guardar sección anterior
    previousSection = currentSection;
    currentSection = section;
    
    // Actualizar navegación
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-section') === section) {
            link.classList.add('active');
        }
    });
    
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('hidden');
    });
    
    // Mostrar sección seleccionada
    const sectionElement = document.getElementById(`${section}-section`);
    if (sectionElement) {
        sectionElement.classList.remove('hidden');
    }
    
    // Mostrar u ocultar filtros según la sección
    const filtersSection = document.getElementById('filters-section');
    if (section === 'discover') {
        filtersSection.classList.remove('hidden');
    } else {
        filtersSection.classList.add('hidden');
    }
    
    // Cargar películas si no se han cargado previamente
    const moviesContainer = document.getElementById(`${section}-movies`);
    if (moviesContainer && moviesContainer.children.length === 0) {
        loadMovies(section, 1);
    }
    
    // Ocultar detalles de película si están visibles
    hideMovieDetails();
    
    // Scroll al inicio
    window.scrollTo(0, 0);
}

function handleSearch() {
    const query = document.getElementById('movie-search').value.trim();
    
    if (query.length < 2) {
        showNotification('Por favor, ingresa al menos 2 caracteres para buscar', 'error');
        return;
    }
    
    // Guardar consulta
    searchQuery = query;
    
    // Resetear paginación
    paginationState.search.page = 1;
    
    // Cambiar a sección de búsqueda
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('hidden');
    });
    
    const searchSection = document.getElementById('search-section');
    searchSection.classList.remove('hidden');
    
    // Actualizar título de sección
    const searchTitle = searchSection.querySelector('h2');
    searchTitle.textContent = `Resultados para: "${query}"`;
    
    // Limpiar resultados anteriores
    const searchMoviesContainer = document.getElementById('search-movies');
    searchMoviesContainer.innerHTML = '';
    
    // Cargar resultados
    loadSearchResults(query, 1);
    
    // Ocultar detalles de película si están visibles
    hideMovieDetails();
}

async function loadMovies(section, page, append = false) {
    // Evitar cargas duplicadas
    if (paginationState[section].loading) {
        return;
    }
    
    paginationState[section].loading = true;
    
    // Mostrar indicador de carga
    showLoading();
    
    try {
        let url;
        
        switch (section) {
            case 'popular':
                url = `${API_BASE_URL}/movies/popular?page=${page}`;
                break;
            case 'top-rated':
                url = `${API_BASE_URL}/movies/top_rated?page=${page}`;
                break;
            case 'now-playing':
                url = `${API_BASE_URL}/movies/now_playing?page=${page}`;
                break;
            case 'upcoming':
                url = `${API_BASE_URL}/movies/upcoming?page=${page}`;
                break;
            case 'discover':
                // Obtener valores de filtros
                const year = document.getElementById('year-filter').value;
                const genre = document.getElementById('genre-filter').value;
                const sortBy = document.getElementById('sort-filter').value;
                
                url = `${API_BASE_URL}/movies/discover?page=${page}`;
                
                if (year) {
                    url += `&year=${year}`;
                }
                
                if (genre) {
                    url += `&genre=${genre}`;
                }
                
                if (sortBy) {
                    url += `&sort_by=${sortBy}`;
                }
                break;
            default:
                hideLoading();
                paginationState[section].loading = false;
                return;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        // Actualizar estado de paginación
        paginationState[section].page = data.page;
        paginationState[section].totalPages = data.total_pages;
        
        // Obtener contenedor
        const container = document.getElementById(`${section}-movies`);
        
        // Limpiar contenedor si no es append
        if (!append) {
            container.innerHTML = '';
        }
        
        // Mostrar películas
        if (data.movies && data.movies.length > 0) {
            data.movies.forEach(movie => {
                const movieCard = createMovieCard(movie);
                container.appendChild(movieCard);
            });
            
            // Mostrar u ocultar botón de cargar más
            const loadMoreButton = document.getElementById(`load-more-${section}`);
            if (data.page < data.total_pages) {
                loadMoreButton.classList.remove('hidden');
            } else {
                loadMoreButton.classList.add('hidden');
            }
        } else {
            if (!append) {
                container.innerHTML = '<p class="no-results">No se encontraron películas</p>';
            }
        }
    } catch (error) {
        console.error(`Error al cargar películas (${section}):`, error);
        showNotification(`Error al cargar películas: ${error.message}`, 'error');
    } finally {
        hideLoading();
        paginationState[section].loading = false;
    }
}

async function loadSearchResults(query, page, append = false) {
    // Evitar cargas duplicadas
    if (paginationState.search.loading) {
        return;
    }
    
    paginationState.search.loading = true;
    
    // Mostrar indicador de carga
    showLoading();
    
    try {
        const url = `${API_BASE_URL}/movies/search?query=${encodeURIComponent(query)}&page=${page}`;
        const response = await fetch(url);
        const data = await response.json();
        
        // Actualizar estado de paginación
        paginationState.search.page = data.page;
        paginationState.search.totalPages = data.total_pages;
        
        // Obtener contenedor
        const container = document.getElementById('search-movies');
        
        // Limpiar contenedor si no es append
        if (!append) {
            container.innerHTML = '';
        }
        
        // Mostrar películas
        if (data.movies && data.movies.length > 0) {
            data.movies.forEach(movie => {
                const movieCard = createMovieCard(movie);
                container.appendChild(movieCard);
            });
            
            // Mostrar u ocultar botón de cargar más
            const loadMoreButton = document.getElementById('load-more-search');
            if (data.page < data.total_pages) {
                loadMoreButton.classList.remove('hidden');
            } else {
                loadMoreButton.classList.add('hidden');
            }
        } else {
            if (!append) {
                container.innerHTML = '<p class="no-results">No se encontraron películas para tu búsqueda</p>';
            }
        }
    } catch (error) {
        console.error('Error al buscar películas:', error);
        showNotification(`Error al buscar películas: ${error.message}`, 'error');
    } finally {
        hideLoading();
        paginationState.search.loading = false;
    }
}

function loadMoreMovies(section) {
    // Incrementar página
    const nextPage = paginationState[section].page + 1;
    
    if (section === 'search') {
        loadSearchResults(searchQuery, nextPage, true);
    } else {
        loadMovies(section, nextPage, true);
    }
}

function applyFilters() {
    // Resetear paginación
    paginationState.discover.page = 1;
    
    // Cargar películas con filtros
    loadMovies('discover', 1);
    
    // Cambiar a sección de descubrimiento
    changeSection('discover');
}

async function showMovieDetails(movieId) {
    // Mostrar indicador de carga
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const movie = await response.json();
        
        // Ocultar secciones de contenido
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Mostrar sección de detalles
        const detailsSection = document.getElementById('movie-details-section');
        detailsSection.classList.remove('hidden');
        
        // Generar HTML de detalles
        const detailsContent = document.getElementById('movie-details-content');
        detailsContent.innerHTML = generateMovieDetailsHTML(movie);
        
        // Cargar recomendaciones
        loadMovieRecommendations(movieId);
        
        // Scroll al inicio
        window.scrollTo(0, 0);
        
        // Añadir event listeners para trailers
        setTimeout(() => {
            const trailerButtons = document.querySelectorAll('.trailer-button');
            trailerButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const videoKey = button.getAttribute('data-video');
                    showTrailerModal(videoKey);
                });
            });
        }, 100);
    } catch (error) {
        console.error('Error al cargar detalles de película:', error);
        showNotification(`Error al cargar detalles: ${error.message}`, 'error');
        
        // Volver a la sección anterior
        if (previousSection) {
            changeSection(previousSection);
        } else {
            changeSection('popular');
        }
    } finally {
        hideLoading();
    }
}

function hideMovieDetails() {
    // Ocultar sección de detalles
    const detailsSection = document.getElementById('movie-details-section');
    detailsSection.classList.add('hidden');
    
    // Mostrar sección anterior
    if (currentSection) {
        const sectionElement = document.getElementById(`${currentSection}-section`);
        if (sectionElement) {
            sectionElement.classList.remove('hidden');
        }
    }
}

async function loadMovieRecommendations(movieId) {
    try {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}/recommendations`);
        const data = await response.json();
        
        const container = document.getElementById('movie-recommendations');
        container.innerHTML = '';
        
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(movie => {
                const movieCard = createMovieCard(movie, true);
                container.appendChild(movieCard);
            });
        } else {
            container.innerHTML = '<p class="no-results">No hay recomendaciones disponibles</p>';
        }
    } catch (error) {
        console.error('Error al cargar recomendaciones:', error);
        const container = document.getElementById('movie-recommendations');
        container.innerHTML = '<p class="error">Error al cargar recomendaciones</p>';
    }
}

function createMovieCard(movie, isSmall = false) {
    const card = document.createElement('div');
    card.className = `movie-card${isSmall ? ' small-card' : ''}`;
    card.setAttribute('data-id', movie.id);
    
    // Preparar URL del póster
    const posterUrl = movie.poster_url || '/static/images/no-poster.png';
    
    // Preparar géneros
    const genresList = movie.genres && movie.genres.length > 0 
        ? movie.genres.slice(0, 2).join(', ') 
        : 'Sin género';
    
    // Preparar año
    const year = movie.year || (movie.release_date ? movie.release_date.split('-')[0] : '');
    
    // Crear HTML de la tarjeta
    card.innerHTML = `
        <div class="movie-poster">
            <img src="${posterUrl}" alt="${movie.title}" loading="lazy" onerror="this.src='/static/images/no-poster.png'">
            <div class="movie-rating">
                <i class="fas fa-star"></i>
                <span>${movie.vote_average.toFixed(1)}</span>
            </div>
        </div>
        <div class="movie-card-content">
            <h3 class="movie-title">${movie.title}</h3>
            <div class="movie-year">${year}</div>
            <div class="movie-genres">${genresList}</div>
        </div>
    `;
    
    // Añadir event listener para mostrar detalles
    card.addEventListener('click', () => {
        showMovieDetails(movie.id);
    });
    
    return card;
}

function generateMovieDetailsHTML(movie) {
    // Preparar URL del póster y backdrop
    const posterUrl = movie.poster_url || '/static/images/no-poster.png';
    const backdropUrl = movie.backdrop_url;
    
    // Preparar géneros
    const genresHTML = movie.genres && movie.genres.length > 0 
        ? movie.genres.map(genre => `<span class="genre-tag">${genre}</span>`).join('') 
        : '<span class="genre-tag">Sin género</span>';
    
    // Preparar año y duración
    const year = movie.year || (movie.release_date ? movie.release_date.split('-')[0] : '');
    
    // Preparar reparto
    let castHTML = '<p>Información no disponible</p>';
    if (movie.cast && movie.cast.length > 0) {
        castHTML = `
            <div class="cast-list">
                ${movie.cast.slice(0, 6).map(person => `
                    <div class="cast-item">
                        <div class="cast-photo">
                            ${person.profile_path 
                                ? `<img src="https://image.tmdb.org/t/p/w185${person.profile_path}" alt="${person.name}" loading="lazy" onerror="this.src='/static/images/no-profile.png'">`
                                : `<div class="no-photo"><i class="fas fa-user"></i></div>`
                            }
                        </div>
                        <div class="cast-name">${person.name}</div>
                        <div class="cast-character">${person.character || ''}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Preparar directores
    let directorsHTML = '<p>Información no disponible</p>';
    if (movie.crew && movie.crew.length > 0) {
        directorsHTML = movie.crew.map(person => `<span>${person.name}</span>`).join(', ');
    }
    
    // Preparar trailers
    let trailersHTML = '';
    if (movie.videos && movie.videos.length > 0) {
        trailersHTML = `
            <div class="trailers-section">
                <h3>Trailers</h3>
                <div class="trailers-container">
                    ${movie.videos.map(video => `
                        <button class="trailer-button" data-video="${video.key}">
                            <i class="fas fa-play-circle"></i>
                            ${video.name}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Generar HTML completo
    return `
        <div class="movie-details">
            ${backdropUrl ? `<div class="movie-backdrop" style="background-image: url('${backdropUrl}')"></div>` : ''}
            <div class="movie-details-content">
                <div class="movie-poster-large">
                    <img src="${posterUrl}" alt="${movie.title}" onerror="this.src='/static/images/no-poster.png'">
                </div>
                <div class="movie-info">
                    <h2 class="movie-title">${movie.title}</h2>
                    <div class="movie-meta">
                        ${year ? `<span class="movie-year">${year}</span>` : ''}
                        <span class="movie-rating"><i class="fas fa-star"></i> ${movie.vote_average.toFixed(1)}/10</span>
                        <span class="movie-votes">(${movie.vote_count} votos)</span>
                    </div>
                    <div class="movie-genres">
                        ${genresHTML}
                    </div>
                    <div class="movie-overview">
                        <h3>Sinopsis</h3>
                        <p>${movie.overview || 'No hay sinopsis disponible'}</p>
                    </div>
                    <div class="movie-directors">
                        <h3>Dirección</h3>
                        ${directorsHTML}
                    </div>
                    <div class="movie-cast">
                        <h3>Reparto principal</h3>
                        ${castHTML}
                    </div>
                    ${trailersHTML}
                </div>
            </div>
        </div>
    `;
}

function showTrailerModal(videoKey) {
    const modal = document.getElementById('movie-modal');
    const modalContent = document.getElementById('modal-content');
    
    modalContent.innerHTML = `
        <div class="video-container">
            <iframe 
                width="100%" 
                height="100%" 
                src="https://www.youtube.com/embed/${videoKey}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
    `;
    
    modal.style.display = 'flex';
    
    // Cerrar modal al hacer clic en X
    const closeModal = document.querySelector('.close-modal');
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
        modalContent.innerHTML = '';
    });
    
    // Cerrar modal al hacer clic fuera del contenido
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            modalContent.innerHTML = '';
        }
    });
}

function showLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.classList.add('hidden');
}

function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Añadir al DOM
    document.body.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Ocultar después de un tiempo
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}
