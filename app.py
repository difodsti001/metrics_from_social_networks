"""
Aplicación Web para el Servicio de Extracción de Métricas
Framework: Flask
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime, timedelta
from facebook_service import FacebookMetricsService
from youtube_service import YouTubeMetricsService
from excel_service import ExcelExportService
import config

app = Flask(__name__)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
UPLOAD_FOLDER = '/home/claude/outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/extract', methods=['POST'])
def extract_metrics():
    """
    Endpoint para extraer métricas según los parámetros enviados
    """
    try:
        data = request.json
        platform = data.get('platform')
        
        if platform == 'facebook':
            return extract_facebook(data)
        elif platform == 'youtube':
            return extract_youtube(data)
        else:
            return jsonify({
                'success': False,
                'error': 'Plataforma no válida'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def extract_facebook(data):
    """Extrae métricas de Facebook"""
    # Obtener parámetros
    page_id = data.get('page_id', config.FACEBOOK_PAGE_ID)
    access_token = data.get('access_token', config.FACEBOOK_ACCESS_TOKEN)
    days_back = int(data.get('days_back', config.DAYS_BACK))
    
    # Validaciones
    if not page_id or not access_token:
        return jsonify({
            'success': False,
            'error': 'Faltan parámetros: page_id o access_token'
        }), 400
    
    # Calcular fechas
    since_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    until_date = datetime.now().strftime("%Y-%m-%d")
    
    # Crear servicio temporal con los parámetros
    fb_service = FacebookMetricsService()
    fb_service.page_id = page_id
    fb_service.access_token = access_token
    
    # Actualizar fechas temporalmente
    fb_service.since_date = since_date
    fb_service.until_date = until_date
    
    try:
        # Extraer métricas
        metrics = fb_service.get_all_metrics()
        
        if not metrics:
            return jsonify({
                'success': False,
                'error': 'No se obtuvieron métricas de Facebook'
            }), 404
        
        # Generar archivo Excel
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
    # Obtener parámetros
    channel_id = data.get('channel_id', config.YOUTUBE_CHANNEL_ID)
    days_back = int(data.get('days_back', config.DAYS_BACK))
    
    # Validaciones
    if not channel_id:
        return jsonify({
            'success': False,
            'error': 'Falta parámetro: channel_id'
        }), 400
    
    # Crear servicio temporal con los parámetros
    yt_service = YouTubeMetricsService()
    yt_service.channel_id = channel_id
    yt_service.days_back = days_back
    
    try:
        # Extraer métricas
        metrics = yt_service.get_all_metrics()
        
        if not metrics:
            return jsonify({
                'success': False,
                'error': 'No se obtuvieron métricas de YouTube. Verifica el ID del canal.'
            }), 404
        
        # Generar archivo Excel
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
        return jsonify({
            'success': False,
            'error': f'Error al extraer de YouTube: {str(e)}'
        }), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Descarga el archivo Excel generado"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
    app.run(host='0.0.0.0', port=5000, debug=True)