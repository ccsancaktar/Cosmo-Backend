from flask import Flask, request, jsonify, send_from_directory
from monitoring import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import os
from dotenv import load_dotenv
from g4f.client import Client
import json
import time
from datetime import datetime, timedelta
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from models import db, User, Reading, calculate_zodiac_sign
from auth import auth_bp
from readings import readings_bp
from tokens import tokens_bp, spend_tokens_for_reading, add_registration_bonus
from premium import premium_bp, get_premium_prompt, get_free_prompt
from payment_system import payment_bp
from rune_data import get_random_runes
from chinese_data import calculate_ba_zi, ELEMENTS
from tarot_data import get_random_tarot_cards, get_card_description
from prompts.multilingual import get_prompt_by_language
from rate_limiting import create_limiter, fal_rate_limit, daily_fal_rate_limit, get_rate_limit_info
from monitoring import monitoring_bp
from redis_manager import redis_manager
from notifications import NotificationService
from scheduler import setup_scheduler, stop_scheduler

# Import all fortune endpoint modules
from endpoints.yildizname import register_yildizname_routes
from endpoints.tarot import register_tarot_routes
from endpoints.rune import register_rune_routes
from endpoints.chinese import register_chinese_routes
from endpoints.daily import register_daily_routes
from endpoints.coffee import register_coffee_routes
from endpoints.kabala import register_kabala_routes

import atexit

# .env dosyasını yükle
load_dotenv('.env')

# Sentry konfigürasyonu
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment=os.getenv('FLASK_ENV', 'development')
    )

app = Flask(__name__)

# Kritik environment variables kontrolü
required_env_vars = ['JWT_SECRET', 'MONGO_URI']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f'Missing required environment variables: {", ".join(missing_vars)}')

# Konfigürasyon
jwt_secret = os.getenv('JWT_SECRET')
app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=365)

# Extensions
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))
jwt = JWTManager(app)

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Rate limiting'i başlat
limiter = create_limiter(app)

# Blueprint'leri kaydet
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(readings_bp, url_prefix='/api/readings')
limiter.exempt(tokens_bp)
app.register_blueprint(tokens_bp, url_prefix='/api/tokens')
app.register_blueprint(premium_bp, url_prefix='/api/premium')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(monitoring_bp, url_prefix="/api/monitoring")

# Register all fortune routes
register_yildizname_routes(app)
register_tarot_routes(app)
register_rune_routes(app)
register_chinese_routes(app)
register_daily_routes(app)
register_coffee_routes(app)
register_kabala_routes(app)

# Notification service'i başlat
notification_service = NotificationService()

# Scheduler'ı başlat
setup_scheduler()

# Uygulama kapanırken scheduler'ı durdur
atexit.register(stop_scheduler)

# G4F client'ını başlat
client = Client(
    timeout=300,
    max_retries=5
)

# Notification blueprint'i oluştur
from flask import Blueprint
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/register', methods=['POST'])
@jwt_required()
def register_push_token():
    """Push token'ı kaydet"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        push_token = data.get('push_token')
        
        if not push_token:
            return jsonify({'error': 'Push token gereklidir'}), 400
        
        # Kullanıcının push token'ını güncelle
        user = User.find_by_id(user_id)
        if user:
            user.push_token = push_token
            user.save()
            
            return jsonify({
                'message': 'Push token başarıyla kaydedildi',
                'push_token': push_token
            }), 200
        else:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Push token kayıt hatası: {str(e)}'}), 500

# Notification blueprint'ini kaydet
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

@app.route('/health', methods=['GET'])
def health_check_root():
    """Ana health check endpoint'i"""
    try:
        # Redis bağlantısını kontrol et (ping yerine)
        redis_status = redis_manager.is_connected
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'redis': 'connected' if redis_status else 'disconnected',
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sistem sağlık durumu kontrolü"""
    try:
        # Redis bağlantısını kontrol et (ping yerine is_connected)
        redis_status = redis_manager.is_connected
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'redis': 'connected' if redis_status else 'disconnected',
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 500


@app.route('/api/redis/stats', methods=['GET'])
def get_redis_stats():
    """Redis istatistiklerini getir (admin için)"""
    try:
        from cache_utils import cache_utils
        
        # Detaylı cache istatistikleri
        cache_stats = cache_utils.get_cache_stats()
        redis_stats = redis_manager.get_stats()
        
        return jsonify({
            'redis_stats': redis_stats,
            'cache_stats': cache_stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis/flush', methods=['POST'])
def flush_redis_cache():
    """Redis cache'ini temizle (sadece development'ta)"""
    try:
        if os.getenv('FLASK_ENV') == 'development':
            success = redis_manager.flush_db()
            if success:
                return jsonify({'message': 'Redis cache temizlendi'})
            else:
                return jsonify({'error': 'Cache temizleme başarısız'}), 500
        else:
            return jsonify({'error': 'Bu endpoint sadece development modunda kullanılabilir'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate-limits', methods=['GET'])
@jwt_required()
def get_user_rate_limits():
    """Kullanıcının rate limit bilgilerini getir"""
    try:
        user_id = get_jwt_identity()
        
        # Tüm endpoint'ler için rate limit bilgilerini getir
        endpoints = ['yildizname', 'rune', 'tarot', 'chinese', 'coffee', 'kabala', 'daily']
        rate_limits = {}
        
        for endpoint in endpoints:
            rate_limits[endpoint] = get_rate_limit_info(user_id, endpoint)
        
        return jsonify({
            'user_id': user_id,
            'rate_limits': rate_limits,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assets/tarot/<filename>', methods=['GET'])
def serve_tarot_image(filename):
    """Tarot kartı resimlerini serve et"""
    try:
        return send_from_directory('assets/tarot', filename)
    except Exception as e:
        return jsonify({'error': f'Resim bulunamadı: {str(e)}'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=os.getenv('HOST', '0.0.0.0'), port=port, debug=debug_mode, threaded=True) 