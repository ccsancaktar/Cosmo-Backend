from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, jsonify
from functools import wraps
import time
from datetime import datetime, timedelta
from redis_manager import redis_manager

def create_limiter(app):
    """Flask-Limiter instance'ını oluştur"""
    import os
    
    # Production'da Redis, development'ta memory kullan
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        storage_uri = redis_url
        print(f"Using Redis for rate limiting: {redis_url}")
    else:
        storage_uri = "memory://"
        print("Using in-memory storage for rate limiting (not recommended for production)")
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["50000 per day", "5000 per hour"],  # Gerçekçi limitler
        storage_uri=storage_uri
    )
    return limiter

def user_rate_limit(max_requests, window_seconds, error_message="Rate limit exceeded"):
    """Kullanıcı bazlı rate limiting decorator'ı"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # JWT token'dan user ID'yi al
            from flask_jwt_extended import get_jwt_identity
            try:
                user_id = get_jwt_identity()
                if not user_id:
                    return jsonify({'error': 'Authentication required'}), 401
                
                # Rate limit key'i oluştur
                key = f"user_{user_id}_{f.__name__}"
                
                # Mevcut request sayısını kontrol et
                current_requests = redis_manager.get_counter(key) or 0
                
                if current_requests >= max_requests:
                    return jsonify({
                        'error': error_message,
                        'retry_after': window_seconds,
                        'limit': max_requests,
                        'window': f"{window_seconds} seconds"
                    }), 429
                
                # Request sayısını artır
                redis_manager.incr(key, window_seconds)
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Rate limiting error'}), 500
        
        return decorated_function
    return decorator

def ip_rate_limit(max_requests, window_seconds, error_message="Rate limit exceeded"):
    """IP bazlı rate limiting decorator'ı"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # IP adresini al
            ip = get_remote_address()
            
            # Rate limit key'i oluştur
            key = f"ip_{ip}_{f.__name__}"
            
            # Mevcut request sayısını kontrol et
            current_requests = redis_manager.get_counter(key) or 0
            
            if current_requests >= max_requests:
                return jsonify({
                    'error': error_message,
                    'retry_after': window_seconds,
                    'limit': max_requests,
                    'window': f"{window_seconds} seconds"
                }), 429
            
            # Request sayısını artır
            redis_manager.incr(key, window_seconds)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Fal yöntemleri için özel rate limit'ler
def fal_rate_limit():
    """Fal baktırma için rate limiting - Production'da daha agresif"""
    import os
    
    # Production'da daha sıkı limitler
    if os.getenv('FLASK_ENV') == 'production':
        return user_rate_limit(
            max_requests=5,  # 5 fal per hour in production
            window_seconds=3600,  # 1 saat
            error_message="Saatlik fal limiti aşıldı. Lütfen 1 saat sonra tekrar deneyin."
        )
    else:
        return user_rate_limit(
            max_requests=10,  # 10 fal per hour in development
            window_seconds=3600,  # 1 saat
            error_message="Çok fazla fal baktırdınız. Lütfen 1 saat bekleyin."
        )

def daily_fal_rate_limit():
    """Günlük fal için rate limiting - Production'da daha agresif"""
    import os
    
    # Production'da daha sıkı limitler
    if os.getenv('FLASK_ENV') == 'production':
        return user_rate_limit(
            max_requests=15,  # 15 fal per day in production
            window_seconds=86400,  # 24 saat
            error_message="Günlük fal limiti aşıldı. Lütfen yarın tekrar deneyin."
        )
    else:
        return user_rate_limit(
            max_requests=20,  # 20 fal per day in development
            window_seconds=86400,  # 24 saat
            error_message="Günlük falınızı zaten baktırdınız. Yarın tekrar deneyin."
        )

def auth_rate_limit():
    """Authentication için rate limiting - IP bazlı"""
    return ip_rate_limit(
        max_requests=10,  # 10 attempt per hour
        window_seconds=3600,  # 1 saat
        error_message="Çok fazla giriş denemesi. Lütfen 1 saat bekleyin."
    )

def registration_rate_limit():
    """Kayıt için rate limiting - IP bazlı"""
    return ip_rate_limit(
        max_requests=5,  # 5 registration per hour
        window_seconds=3600,  # 1 saat
        error_message="Çok fazla kayıt denemesi. Lütfen 1 saat bekleyin."
    )

# Rate limit bilgilerini getir
def get_rate_limit_info(user_id, endpoint):
    """Kullanıcının rate limit bilgilerini getir"""
    key = f"user_{user_id}_{endpoint}"
    current_requests = redis_manager.get(key) or 0
    
    # Endpoint'e göre limit'leri belirle
    limits = {
        'yildizname': {'max': 10, 'window': 3600},
        'rune': {'max': 10, 'window': 3600},
        'tarot': {'max': 10, 'window': 3600},
        'chinese': {'max': 10, 'window': 3600},
        'coffee': {'max': 10, 'window': 3600},
        'kabala': {'max': 10, 'window': 3600},
        'daily': {'max': 1, 'window': 86400}
    }
    
    limit_info = limits.get(endpoint, {'max': 10, 'window': 3600})
    
    return {
        'current': current_requests,
        'limit': limit_info['max'],
        'remaining': max(0, limit_info['max'] - current_requests),
        'reset_time': time.time() + limit_info['window']
    }
