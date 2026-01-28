// Elementos del DOM
const platformBtns = document.querySelectorAll('.platform-btn');
const facebookForm = document.getElementById('facebook-form');
const youtubeForm = document.getElementById('youtube-form');
const fbExtractionForm = document.getElementById('fb-extraction-form');
const ytExtractionForm = document.getElementById('yt-extraction-form');
const resultsContainer = document.getElementById('results');
const loadingOverlay = document.getElementById('loading');
const downloadBtn = document.getElementById('download-btn');

let currentDownloadUrl = null;

// Cargar configuración inicial
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // Llenar valores por defecto de Facebook
        if (config.facebook.page_id) {
            document.getElementById('fb-page-id').value = config.facebook.page_id;
        }
        if (config.facebook.days_back) {
            document.getElementById('fb-days-back').value = config.facebook.days_back;
        }
        
        // Llenar valores por defecto de YouTube
        if (config.youtube.channel_id) {
            document.getElementById('yt-channel-id').value = config.youtube.channel_id;
        }
        if (config.youtube.days_back) {
            document.getElementById('yt-days-back').value = config.youtube.days_back;
        }
    } catch (error) {
        console.error('Error cargando configuración:', error);
    }
}

// Cambiar entre plataformas
platformBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const platform = btn.dataset.platform;
        
        // Actualizar botones activos
        platformBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Mostrar/ocultar formularios
        if (platform === 'facebook') {
            facebookForm.classList.remove('hidden');
            youtubeForm.classList.add('hidden');
        } else {
            facebookForm.classList.add('hidden');
            youtubeForm.classList.remove('hidden');
        }
        
        // Ocultar resultados
        resultsContainer.classList.add('hidden');
    });
});

// Manejo del formulario de Facebook
fbExtractionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        platform: 'facebook',
        page_id: document.getElementById('fb-page-id').value.trim(),
        access_token: document.getElementById('fb-access-token').value.trim(),
        days_back: document.getElementById('fb-days-back').value
    };
    
    await extractMetrics(formData);
});

// Manejo del formulario de YouTube
ytExtractionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        platform: 'youtube',
        channel_id: document.getElementById('yt-channel-id').value.trim(),
        days_back: document.getElementById('yt-days-back').value
    };
    
    await extractMetrics(formData);
});

// Función principal para extraer métricas
async function extractMetrics(data) {
    // Mostrar loading
    loadingOverlay.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    
    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        // Ocultar loading
        loadingOverlay.classList.add('hidden');
        
        if (result.success) {
            showSuccess(result);
        } else {
            showError(result.error);
        }
        
    } catch (error) {
        loadingOverlay.classList.add('hidden');
        showError('Error de conexión: ' + error.message);
    }
}

// Mostrar resultado exitoso
function showSuccess(result) {
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const resultStats = document.getElementById('result-stats');
    
    resultIcon.textContent = '✅';
    resultTitle.textContent = 'Extracción Exitosa';
    resultMessage.textContent = result.message;
    resultStats.textContent = `Total de registros: ${result.total_records}`;
    
    // Guardar URL de descarga
    currentDownloadUrl = result.download_url;
    
    // Mostrar resultados
    resultsContainer.classList.remove('hidden');
    
    // Scroll suave hacia resultados
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Mostrar error
function showError(errorMessage) {
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const resultStats = document.getElementById('result-stats');
    
    resultIcon.textContent = '❌';
    resultTitle.textContent = 'Error en la Extracción';
    resultMessage.textContent = errorMessage;
    resultStats.textContent = '';
    
    // Ocultar botón de descarga
    downloadBtn.style.display = 'none';
    
    // Mostrar resultados
    resultsContainer.classList.remove('hidden');
    
    // Scroll suave hacia resultados
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Restaurar botón después de 3 segundos
    setTimeout(() => {
        downloadBtn.style.display = 'flex';
    }, 3000);
}

// Manejo del botón de descarga
downloadBtn.addEventListener('click', () => {
    if (currentDownloadUrl) {
        window.location.href = currentDownloadUrl;
    }
});

// Inicializar
loadConfig();

// Tooltips
document.querySelectorAll('.tooltip').forEach(tooltip => {
    tooltip.addEventListener('click', (e) => {
        e.preventDefault();
        alert(tooltip.getAttribute('title'));
    });
});

// Validación en tiempo real
document.getElementById('fb-page-id').addEventListener('input', (e) => {
    const value = e.target.value;
    if (value && !/^\d+$/.test(value)) {
        e.target.style.borderColor = 'var(--error-color)';
    } else {
        e.target.style.borderColor = 'var(--border-color)';
    }
});

document.getElementById('yt-channel-id').addEventListener('input', (e) => {
    const value = e.target.value;
    if (value && !value.startsWith('UC')) {
        e.target.style.borderColor = 'var(--error-color)';
    } else {
        e.target.style.borderColor = 'var(--border-color)';
    }
});

// Prevenir envío múltiple
let isSubmitting = false;

function preventMultipleSubmit(formElement) {
    formElement.addEventListener('submit', (e) => {
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        isSubmitting = true;
        
        // Resetear después de 5 segundos por si algo falla
        setTimeout(() => {
            isSubmitting = false;
        }, 5000);
    });
}

preventMultipleSubmit(fbExtractionForm);
preventMultipleSubmit(ytExtractionForm);
