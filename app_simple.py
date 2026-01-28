"""
Aplicación Web para el Servicio de Extracción de Métricas
Versión simplificada - HTML embebido
"""
from flask import Flask, request, jsonify, send_file, Response
import os
from datetime import datetime, timedelta
from facebook_service import FacebookMetricsService
from youtube_service import YouTubeMetricsService
from excel_service import ExcelExportService
import config

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extractor de Métricas - Redes Sociales</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary-color: #4267B2;
            --secondary-color: #FF0000;
            --success-color: #00C851;
            --error-color: #ff4444;
            --text-dark: #1c1e21;
            --text-light: #65676b;
            --bg-light: #f0f2f5;
            --border-color: #dddfe2;
            --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            --shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.15);
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--text-dark);
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        header h1 {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 1rem;
            opacity: 0.9;
            font-weight: 300;
        }
        .platform-selector {
            display: flex;
            gap: 0;
            padding: 20px;
            background: var(--bg-light);
        }
        .platform-btn {
            flex: 1;
            padding: 15px 20px;
            background: white;
            border: 2px solid var(--border-color);
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .platform-btn:first-child { border-radius: 8px 0 0 8px; }
        .platform-btn:last-child { border-radius: 0 8px 8px 0; }
        .platform-btn .icon { font-size: 1.5rem; }
        .platform-btn:hover {
            background: var(--bg-light);
            transform: translateY(-2px);
        }
        .platform-btn.active {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        .platform-btn.active:nth-child(2) {
            background: var(--secondary-color);
            border-color: var(--secondary-color);
        }
        .form-container { padding: 30px; }
        .form-container h2 {
            margin-bottom: 25px;
            font-size: 1.5rem;
            color: var(--text-dark);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text-dark);
            font-size: 0.95rem;
        }
        .tooltip {
            cursor: help;
            opacity: 0.6;
            margin-left: 5px;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(66, 103, 178, 0.1);
        }
        .form-group textarea {
            resize: vertical;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        .form-group small {
            display: block;
            margin-top: 5px;
            color: var(--text-light);
            font-size: 0.85rem;
        }
        .btn-primary, .btn-download {
            width: 100%;
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: var(--shadow);
        }
        .btn-primary:hover, .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }
        .btn-primary:active, .btn-download:active {
            transform: translateY(0);
        }
        .btn-icon { font-size: 1.2rem; }
        .btn-download {
            background: var(--success-color);
            margin-top: 15px;
        }
        .results-container {
            padding: 30px;
            background: var(--bg-light);
        }
        .result-card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            box-shadow: var(--shadow);
        }
        .result-icon {
            font-size: 4rem;
            margin-bottom: 15px;
        }
        .result-card h3 {
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: var(--text-dark);
        }
        .result-card p {
            color: var(--text-light);
            margin-bottom: 20px;
        }
        .result-stats {
            background: var(--bg-light);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
            color: var(--primary-color);
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .loading-overlay p {
            color: white;
            margin-top: 20px;
            font-size: 1.1rem;
        }
        footer {
            padding: 20px 30px;
            background: var(--bg-light);
            text-align: center;
            color: var(--text-light);
            font-size: 0.9rem;
        }
        .hidden { display: none !important; }
        @media (max-width: 768px) {
            body { padding: 10px; }
            header h1 { font-size: 1.5rem; }
            .platform-selector { flex-direction: column; }
            .platform-btn:first-child { border-radius: 8px 8px 0 0; }
            .platform-btn:last-child { border-radius: 0 0 8px 8px; }
            .form-container, .results-container { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Extractor de Métricas de Redes Sociales</h1>
            <p class="subtitle">Obtén métricas detalladas de Facebook y YouTube en formato Excel</p>
        </header>

        <div class="platform-selector">
            <button class="platform-btn active" data-platform="facebook">
                <span class="icon">📘</span> Facebook
            </button>
            <button class="platform-btn" data-platform="youtube">
                <span class="icon">📺</span> YouTube
            </button>
        </div>

        <div class="form-container" id="facebook-form">
            <h2>Configuración de Facebook</h2>
            <form id="fb-extraction-form">
                <div class="form-group">
                    <label for="fb-page-id">Page ID <span class="tooltip" title="ID de tu página de Facebook">ℹ️</span></label>
                    <input type="text" id="fb-page-id" name="page_id" placeholder="Ej: 804578252729420" required>
                </div>
                <div class="form-group">
                    <label for="fb-access-token">Token de Acceso <span class="tooltip" title="Token de acceso de la API de Facebook">ℹ️</span></label>
                    <textarea id="fb-access-token" name="access_token" rows="3" placeholder="Pega aquí tu token de acceso" required></textarea>
                </div>
                <div class="form-group">
                    <label for="fb-days-back">Días hacia atrás <span class="tooltip" title="Número de días desde hoy">ℹ️</span></label>
                    <input type="number" id="fb-days-back" name="days_back" value="10" min="1" max="90" required>
                </div>
                <button type="submit" class="btn-primary">
                    <span class="btn-icon">🚀</span> Extraer Métricas de Facebook
                </button>
            </form>
        </div>

        <div class="form-container hidden" id="youtube-form">
            <h2>Configuración de YouTube</h2>
            <form id="yt-extraction-form">
                <div class="form-group">
                    <label for="yt-channel-id">Channel ID <span class="tooltip" title="ID de tu canal de YouTube">ℹ️</span></label>
                    <input type="text" id="yt-channel-id" name="channel_id" placeholder="Ej: UCxxxxxxxxxxxxxx" required>
                    <small>Puedes encontrarlo en la URL de tu canal o en la configuración avanzada</small>
                </div>
                <div class="form-group">
                    <label for="yt-days-back">Días hacia atrás <span class="tooltip" title="Número de días desde hoy">ℹ️</span></label>
                    <input type="number" id="yt-days-back" name="days_back" value="10" min="1" max="90" required>
                </div>
                <button type="submit" class="btn-primary">
                    <span class="btn-icon">🚀</span> Extraer Métricas de YouTube
                </button>
            </form>
        </div>

        <div class="results-container hidden" id="results">
            <div class="result-card">
                <div class="result-icon" id="result-icon">✅</div>
                <h3 id="result-title">Extracción Exitosa</h3>
                <p id="result-message"></p>
                <div class="result-stats" id="result-stats"></div>
                <button class="btn-download" id="download-btn">
                    <span class="btn-icon">⬇️</span> Descargar Excel
                </button>
            </div>
        </div>

        <div class="loading-overlay hidden" id="loading">
            <div class="spinner"></div>
            <p>Extrayendo métricas, por favor espera...</p>
        </div>

        <footer>
            <p>💡 <strong>Nota:</strong> Las métricas de Facebook usan API v24.0. Para YouTube se requiere yt-dlp instalado.</p>
        </footer>
    </div>

    <script>
        const platformBtns = document.querySelectorAll('.platform-btn');
        const facebookForm = document.getElementById('facebook-form');
        const youtubeForm = document.getElementById('youtube-form');
        const fbExtractionForm = document.getElementById('fb-extraction-form');
        const ytExtractionForm = document.getElementById('yt-extraction-form');
        const resultsContainer = document.getElementById('results');
        const loadingOverlay = document.getElementById('loading');
        const downloadBtn = document.getElementById('download-btn');
        let currentDownloadUrl = null;

        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                const config = await response.json();
                if (config.facebook.page_id) {
                    document.getElementById('fb-page-id').value = config.facebook.page_id;
                }
                if (config.facebook.days_back) {
                    document.getElementById('fb-days-back').value = config.facebook.days_back;
                }
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

        platformBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const platform = btn.dataset.platform;
                platformBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                if (platform === 'facebook') {
                    facebookForm.classList.remove('hidden');
                    youtubeForm.classList.add('hidden');
                } else {
                    facebookForm.classList.add('hidden');
                    youtubeForm.classList.remove('hidden');
                }
                resultsContainer.classList.add('hidden');
            });
        });

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

        ytExtractionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                platform: 'youtube',
                channel_id: document.getElementById('yt-channel-id').value.trim(),
                days_back: document.getElementById('yt-days-back').value
            };
            await extractMetrics(formData);
        });

        async function extractMetrics(data) {
            loadingOverlay.classList.remove('hidden');
            resultsContainer.classList.add('hidden');
            try {
                const response = await fetch('/api/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
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

        function showSuccess(result) {
            document.getElementById('result-icon').textContent = '✅';
            document.getElementById('result-title').textContent = 'Extracción Exitosa';
            document.getElementById('result-message').textContent = result.message;
            document.getElementById('result-stats').textContent = `Total de registros: ${result.total_records}`;
            currentDownloadUrl = result.download_url;
            resultsContainer.classList.remove('hidden');
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        function showError(errorMessage) {
            document.getElementById('result-icon').textContent = '❌';
            document.getElementById('result-title').textContent = 'Error en la Extracción';
            document.getElementById('result-message').textContent = errorMessage;
            document.getElementById('result-stats').textContent = '';
            downloadBtn.style.display = 'none';
            resultsContainer.classList.remove('hidden');
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            setTimeout(() => { downloadBtn.style.display = 'flex'; }, 3000);
        }

        downloadBtn.addEventListener('click', () => {
            if (currentDownloadUrl) {
                window.location.href = currentDownloadUrl;
            }
        });

        loadConfig();
    </script>
</body>
</html>"""


@app.route('/')
def index():
    """Página principal"""
    return Response(HTML_TEMPLATE, mimetype='text/html')


@app.route('/api/extract', methods=['POST'])
def extract_metrics():
    """Endpoint para extraer métricas según los parámetros enviados"""
    try:
        data = request.json
        platform = data.get('platform')
        
        if platform == 'facebook':
            return extract_facebook(data)
        elif platform == 'youtube':
            return extract_youtube(data)
        else:
            return jsonify({'success': False, 'error': 'Plataforma no válida'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def extract_facebook(data):
    """Extrae métricas de Facebook"""
    page_id = data.get('page_id', config.FACEBOOK_PAGE_ID)
    access_token = data.get('access_token', config.FACEBOOK_ACCESS_TOKEN)
    days_back = int(data.get('days_back', config.DAYS_BACK))
    
    if not page_id or not access_token:
        return jsonify({'success': False, 'error': 'Faltan parámetros: page_id o access_token'}), 400
    
    since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    until_date = datetime.now().strftime("%Y-%m-%d")
    
    fb_service = FacebookMetricsService()
    fb_service.page_id = page_id
    fb_service.access_token = access_token
    fb_service.since_date = since_date
    fb_service.until_date = until_date
    
    try:
        metrics = fb_service.get_all_metrics()
        
        if not metrics:
            return jsonify({'success': False, 'error': 'No se obtuvieron métricas de Facebook'}), 404
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facebook_metricas_{timestamp}.xlsx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        excel_service = ExcelExportService(filepath)
        excel_service.export_metrics(metrics)
        
        return jsonify({
            'success': True,
            'message': f'Extracción exitosa: {len(metrics)} registros',
            'total_records': len(metrics),
            'filename': filename,
            'download_url': f'/api/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al extraer de Facebook: {str(e)}'}), 500


def extract_youtube(data):
    """Extrae métricas de YouTube"""
    channel_id = data.get('channel_id', config.YOUTUBE_CHANNEL_ID)
    days_back = int(data.get('days_back', config.DAYS_BACK))
    
    if not channel_id:
        return jsonify({'success': False, 'error': 'Falta parámetro: channel_id'}), 400
    
    yt_service = YouTubeMetricsService()
    yt_service.channel_id = channel_id
    yt_service.days_back = days_back
    
    try:
        metrics = yt_service.get_all_metrics()
        
        if not metrics:
            return jsonify({'success': False, 'error': 'No se obtuvieron métricas de YouTube. Verifica el ID del canal.'}), 404
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"youtube_metricas_{timestamp}.xlsx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        excel_service = ExcelExportService(filepath)
        excel_service.export_metrics(metrics)
        
        return jsonify({
            'success': True,
            'message': f'Extracción exitosa: {len(metrics)} registros',
            'total_records': len(metrics),
            'filename': filename,
            'download_url': f'/api/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al extraer de YouTube: {str(e)}'}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Descarga el archivo Excel generado"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Obtiene la configuración actual"""
    return jsonify({
        'facebook': {
            'page_id': config.FACEBOOK_PAGE_ID,
            'days_back': config.DAYS_BACK
        },
        'youtube': {
            'channel_id': config.YOUTUBE_CHANNEL_ID,
            'days_back': config.DAYS_BACK
        }
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Servidor Web Iniciado")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("💡 Presiona CTRL+C para detener el servidor")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
