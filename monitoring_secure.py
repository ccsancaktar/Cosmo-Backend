from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import time
import os
import psutil
from models import db
import json

monitoring_bp = Blueprint('monitoring', __name__)

# System metrics - SECURE VERSION using psutil instead of subprocess
def get_system_metrics():
    Sistem metriklerini topla - Güvenli versiyon
    try:
        # CPU kullanımı - psutil ile güvenli
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory kullanımı - psutil ile güvenli
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk kullanımı - psutil ile güvenli
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        return {
            'cpu_percent': round(cpu_percent, 2),
            'memory_percent': round(memory_percent, 2),
            'disk_percent': round(disk_percent, 2),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': f'System metrics error: {str(e)}'}

# Application metrics
def get_app_metrics():
    Uygulama metriklerini topla
    try:
        # User metrics - MongoDB için
        total_users = db.users.count_documents({})
        active_users_24h = db.users.count_documents({
            'last_login': {'': datetime.utcnow() - timedelta(days=1)}
        })
        
        # Reading metrics - MongoDB için
        total_readings = db.readings.count_documents({})
        readings_24h = db.readings.count_documents({
            'created_at': {'': datetime.utcnow() - timedelta(days=1)}
        })
        
        # Premium user metrics
        premium_users = db.users.count_documents({'is_premium': True})
        premium_rate = (premium_users / total_users * 100) if total_users > 0 else 0
        
        return {
            'users': {
                'total': total_users,
                'active_24h': active_users_24h,
                'premium': premium_users,
                'premium_rate': round(premium_rate, 2)
            },
            'readings': {
                'total': total_readings,
                'last_24h': readings_24h,
                'avg_per_user': round(readings_24h / total_users, 2) if total_users > 0 else 0
            }
        }
    except Exception as e:
        return {'error': f'App metrics error: {str(e)}'}

# Business metrics
def get_business_metrics():
    İş metriklerini topla
    try:
        # Reading by method
        readings_by_method = {}
        readings = db.readings.find({}, {'method': 1})
        for reading in readings:
            method = reading.get('method', 'unknown')
            readings_by_method[method] = readings_by_method.get(method, 0) + 1
        
        # Token metrics
        token_transactions = db.token_transactions.find({})
        total_spent = sum(t.get('amount', 0) for t in token_transactions)
        avg_per_reading = total_spent / len(list(db.readings.find())) if db.readings.count_documents({}) > 0 else 0
        
        # Revenue metrics
        premium_users = db.users.count_documents({'is_premium': True})
        monthly_premium = premium_users * 29.99  # Premium price
        
        return {
            'readings_by_method': readings_by_method,
            'tokens': {
                'total_spent': total_spent,
                'avg_per_reading': round(avg_per_reading, 2)
            },
            'revenue': {
                'premium_users': premium_users,
                'monthly_premium': round(monthly_premium, 2)
            }
        }
    except Exception as e:
        return {'error': f'Business metrics error: {str(e)}'}

# Performance metrics
def get_performance_metrics():
    Performans metriklerini topla
    try:
        from redis_manager import redis_manager
        from cache_utils import cache_utils
        
        # Redis metrics
        redis_info = redis_manager.info()
        redis_status = 'connected' if redis_manager.ping() else 'disconnected'
        
        # Cache metrics
        cache_hits = getattr(cache_utils, 'cache_hits', 0)
        cache_misses = getattr(cache_utils, 'cache_misses', 0)
        hit_rate = (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0
        
        return {
            'redis': {
                'status': redis_status,
                'connected_clients': redis_info.get('connected_clients', 0),
                'used_memory': redis_info.get('used_memory_human', '0B'),
                'total_commands_processed': redis_info.get('total_commands_processed', 0),
                'keyspace_hits': redis_info.get('keyspace_hits', 0),
                'keyspace_misses': redis_info.get('keyspace_misses', 0),
                'version': redis_info.get('redis_version', 'unknown')
            },
            'cache': {
                'status': redis_status,
                'cache_hits': cache_hits,
                'cache_misses': cache_misses,
                'hit_rate': f'{hit_rate:.2f}%',
                'connected_clients': redis_info.get('connected_clients', 0),
                'total_commands': redis_info.get('total_commands_processed', 0),
                'used_memory': redis_info.get('used_memory_human', '0B')
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': f'Performance metrics error: {str(e)}'}

# Rate limiting metrics
def get_rate_limiting_metrics():
    Rate limiting metriklerini topla
    try:
        from redis_manager import redis_manager
        
        # Rate limit keys
        rate_limit_keys = redis_manager.keys('rate_limit_*')
        rate_limit_count = len(rate_limit_keys)
        
        # User rate limits
        user_rate_limits = redis_manager.keys('user_*')
        user_rate_limit_count = len(user_rate_limits)
        
        return {
            'rate_limits': {
                'total': rate_limit_count,
                'user_based': user_rate_limit_count,
                'ip_based': rate_limit_count - user_rate_limit_count
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': f'Rate limiting metrics error: {str(e)}'}

# Health check endpoint
@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    Sistem sağlık kontrolü
    try:
        # Database health
        db_status = 'healthy'
        try:
            db.command('ping')
        except:
            db_status = 'unhealthy'
        
        # Redis health
        redis_status = 'healthy'
        try:
            from redis_manager import redis_manager
            redis_manager.ping()
        except:
            redis_status = 'unhealthy'
        
        # System metrics
        system_metrics = get_system_metrics()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': db_status,
                'redis': redis_status
            },
            'system': system_metrics
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Dashboard endpoint
@monitoring_bp.route('/dashboard', methods=['GET'])
def get_monitoring_dashboard():
    Monitoring dashboard
    try:
        # Collect all metrics
        system_metrics = get_system_metrics()
        app_metrics = get_app_metrics()
        business_metrics = get_business_metrics()
        performance_metrics = get_performance_metrics()
        rate_limiting_metrics = get_rate_limiting_metrics()
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'system': system_metrics,
                'application': app_metrics,
                'business': business_metrics,
                'performance': performance_metrics,
                'rate_limiting': rate_limiting_metrics
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# System status endpoint
@monitoring_bp.route('/status', methods=['GET'])
def get_system_status():
    Sistem durumu
    try:
        status = {
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': time.time(),
            'environment': os.getenv('FLASK_ENV', 'unknown'),
            'version': '1.0.0'
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
