from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import time
import os
import subprocess
from models import db
import json

monitoring_bp = Blueprint('monitoring', __name__)

# System metrics
def get_system_metrics():
    """Sistem metriklerini topla"""
    try:
        # CPU kullanımı
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
        cpu_percent = subprocess.check_output(cpu_cmd, shell=True).decode().strip()
        
        # Memory kullanımı
        mem_cmd = "free | grep Mem | awk '{printf(\"%.2f\", $3/$2 * 100.0)}'"
        memory_percent = subprocess.check_output(mem_cmd, shell=True).decode().strip()
        
        # Disk kullanımı
        disk_cmd = "df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1"
        disk_percent = subprocess.check_output(disk_cmd, shell=True).decode().strip()
        
        return {
            'cpu_percent': float(cpu_percent),
            'memory_percent': float(memory_percent),
            'disk_percent': float(disk_percent),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}

# Application metrics
def get_app_metrics():
    """Uygulama metriklerini topla"""
    try:
        # User metrics - MongoDB için
        total_users = db.users.count_documents({})
        active_users_24h = db.users.count_documents({
            'last_login': {'$gte': datetime.utcnow() - timedelta(days=1)}
        })
        
        # Reading metrics - MongoDB için
        total_readings = db.readings.count_documents({})
        readings_24h = db.readings.count_documents({
            'created_at': {'$gte': datetime.utcnow() - timedelta(days=1)}
        })
        
        # Premium metrics
        premium_users = db.users.count_documents({'is_premium': True})
        premium_conversion_rate = round((premium_users / total_users * 100), 2) if total_users > 0 else 0
        
        return {
            'users': {
                'total': total_users,
                'active_24h': active_users_24h,
                'premium': premium_users,
                'premium_rate': premium_conversion_rate
            },
            'readings': {
                'total': total_readings,
                'last_24h': readings_24h,
                'avg_per_user': round(total_readings / total_users, 2) if total_users > 0 else 0
            }
        }
    except Exception as e:
        return {'error': str(e)}

# Performance metrics
def get_performance_metrics():
    """Performans metriklerini topla"""
    try:
        # Redis performance
        from redis_manager import redis_manager
        redis_stats = redis_manager.get_stats()
        
        # Cache performance
        from cache_utils import cache_utils
        cache_stats = cache_utils.get_cache_stats()
        
        return {
            'redis': redis_stats,
            'cache': cache_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}

# Business metrics
def get_business_metrics():
    """İş metriklerini topla"""
    try:
        total_readings = db.readings.count_documents({})
        
        # Fal yöntemleri dağılımı - MongoDB için
        pipeline = [
            {'$group': {'_id': '$method', 'count': {'$sum': 1}}}
        ]
        reading_methods = list(db.readings.aggregate(pipeline))
        method_distribution = {item['_id']: item['count'] for item in reading_methods}
        
        # Token kullanımı
        pipeline = [
            {'$group': {'_id': None, 'total_tokens': {'$sum': '$tokens_spent'}}}
        ]
        result = list(db.readings.aggregate(pipeline))
        total_tokens_spent = result[0]['total_tokens'] if result else 0
        
        # Premium revenue
        premium_users = db.users.count_documents({'is_premium': True})
        premium_revenue = premium_users * 29.99  # Aylık premium ücret
        
        return {
            'readings_by_method': method_distribution,
            'tokens': {
                'total_spent': total_tokens_spent,
                'avg_per_reading': round(total_tokens_spent / total_readings, 2) if total_readings > 0 else 0
            },
            'revenue': {
                'monthly_premium': premium_revenue,
                'premium_users': premium_users
            }
        }
    except Exception as e:
        return {'error': str(e)}

# Main monitoring endpoint
@monitoring_bp.route('/dashboard', methods=['GET'])
def get_monitoring_dashboard():
    """Ana monitoring dashboard endpoint'i"""
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Tüm metrikleri topla
        metrics = {
            'timestamp': timestamp,
            'system': get_system_metrics(),
            'application': get_app_metrics(),
            'performance': get_performance_metrics(),
            'business': get_business_metrics()
        }
        
        return jsonify({
            'status': 'success',
            'data': metrics
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Health check endpoint
@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """Detaylı health check"""
    try:
        # Database connection - MongoDB için
        db.command('ping')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Redis connection
    from redis_manager import redis_manager
    redis_status = 'healthy' if redis_manager.is_connected else 'unhealthy'
    
    # System resources
    system_metrics = get_system_metrics()
    
    overall_status = 'healthy'
    if db_status != 'healthy' or redis_status != 'healthy':
        overall_status = 'unhealthy'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': db_status,
            'redis': redis_status
        },
        'system': system_metrics
    }), 200 if overall_status == 'healthy' else 503


# Rate Limiting metrics
def get_rate_limiting_metrics():
    """Rate limiting metriklerini topla"""
    try:
        # Basit rate limiting metrikleri (şimdilik mock data)
        rate_limits = {
            "api_calls": {
                "total_requests": 1250,
                "blocked_requests": 23,
                "current_window": 45
            },
            "user_requests": {
                "total_requests": 890,
                "blocked_requests": 12,
                "active_users": 67
            },
            "ip_requests": {
                "total_requests": 2100,
                "blocked_requests": 89,
                "blocked_ips": 15
            }
        }
        
        return rate_limits
    except Exception as e:
        return {'error': str(e)}

# Ana monitoring fonksiyonuna rate limiting ekle
def get_monitoring_dashboard():
    """Ana monitoring dashboard endpoint'i"""
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Tüm metrikleri topla
        metrics = {
            'timestamp': timestamp,
            'system': get_system_metrics(),
            'application': get_app_metrics(),
            'performance': get_performance_metrics(),
            'business': get_business_metrics(),
            'rate_limiting': get_rate_limiting_metrics()  # Yeni eklenen
        }
        
        return jsonify({
            'status': 'success',
            'data': metrics
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
