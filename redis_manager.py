import redis
import os
import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import logging

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisManager:
    """Redis bağlantısı ve cache yönetimi için ana sınıf"""
    
    def __init__(self):
        self.redis_client = None
        self.is_connected = False
        self._connect()
    
    def _connect(self):
        """Redis bağlantısını kur"""
        try:
            # Environment variables'dan Redis konfigürasyonunu al
            redis_url = os.getenv('REDIS_URL')
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            if redis_url:
                # REDIS_URL varsa onu kullan
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=False,  # Binary data için
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            else:
                # Ayrı parametrelerle bağlan
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    db=redis_db,
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            
            # Bağlantıyı test et
            self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis bağlantısı başarılı")
            
        except Exception as e:
            logger.error(f"Redis bağlantı hatası: {e}")
            self.is_connected = False
            self.redis_client = None
    
    def _ensure_connection(self):
        """Bağlantı kopuksa yeniden bağlan"""
        if not self.is_connected or not self.redis_client:
            self._connect()
    
    def set(self, key: str, value: Any, ttl: Optional[Union[int, timedelta]] = None) -> bool:
        """Veriyi Redis'e kaydet"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return False
            
            # Value'yu pickle ile serialize et
            serialized_value = pickle.dumps(value)
            
            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                return self.redis_client.set(key, serialized_value)
                
        except Exception as e:
            logger.error(f"Redis set hatası: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Redis'den veri al"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return None
            
            value = self.redis_client.get(key)
            if value:
                # Önce pickle ile deserialize etmeye çalış
                try:
                    return pickle.loads(value)
                except (pickle.UnpicklingError, ValueError, EOFError):
                    # Pickle hatası varsa, düz string olarak dene
                    try:
                        return value.decode('utf-8')
                    except (UnicodeDecodeError, AttributeError):
                        # String decode hatası varsa, raw value'yu döndür
                        return value
            return None
            
        except Exception as e:
            logger.error(f"Redis get hatası: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Redis'den veri sil"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return False
            
            return bool(self.redis_client.delete(key))
            
        except Exception as e:
            logger.error(f"Redis delete hatası: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Key var mı kontrol et"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return False
            
            return bool(self.redis_client.exists(key))
            
        except Exception as e:
            logger.error(f"Redis exists hatası: {e}")
            return False
    
    def incr(self, key: str, ttl: Optional[int] = None) -> Optional[int]:
        """Counter'ı artır"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return None
            
            result = self.redis_client.incr(key)
            
            if ttl:
                self.redis_client.expire(key, ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Redis incr hatası: {e}")
            return None
    
    def get_counter(self, key: str) -> Optional[int]:
        """Rate limiting için counter değerini al (pickle kullanmadan)"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return None
            
            value = self.redis_client.get(key)
            if value is not None:
                # Sayısal değer olarak döndür
                try:
                    return int(value)
                except (ValueError, TypeError):
                    # Eğer int'e çevrilemezse None döndür
                    return None
            return None
            
        except Exception as e:
            logger.error(f"Redis get_counter hatası: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Key'e TTL ekle"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return False
            
            return bool(self.redis_client.expire(key, ttl))
            
        except Exception as e:
            logger.error(f"Redis expire hatası: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Key'in kalan TTL'ini al"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return -1
            
            return self.redis_client.ttl(key)
            
        except Exception as e:
            logger.error(f"Redis ttl hatası: {e}")
            return -1
    
    def flush_db(self) -> bool:
        """Tüm veritabanını temizle (sadece development'ta kullan)"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return False
            
            if os.getenv('FLASK_ENV') == 'development':
                self.redis_client.flushdb()
                logger.info("Redis veritabanı temizlendi")
                return True
            else:
                logger.warning("flush_db sadece development modunda kullanılabilir")
                return False
                
        except Exception as e:
            logger.error(f"Redis flush_db hatası: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Redis istatistiklerini al"""
        try:
            self._ensure_connection()
            if not self.is_connected:
                return {"status": "disconnected"}
            
            info = self.redis_client.info()
            return {
                "status": "connected",
                "version": info.get('redis_version'),
                "used_memory": info.get('used_memory_human'),
                "connected_clients": info.get('connected_clients'),
                "total_commands_processed": info.get('total_commands_processed'),
                "keyspace_hits": info.get('keyspace_hits'),
                "keyspace_misses": info.get('keyspace_misses')
            }
            
        except Exception as e:
            logger.error(f"Redis stats hatası: {e}")
            return {"status": "error", "message": str(e)}

# Global Redis manager instance
redis_manager = RedisManager()

# Cache decorator'ları
def cache_result(ttl: int = 3600):
    """Fonksiyon sonucunu cache'le"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Cache key oluştur
            cache_key = f"func:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Cache'den kontrol et
            cached_result = redis_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Fonksiyonu çalıştır
            result = func(*args, **kwargs)
            
            # Sonucu cache'le
            redis_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Belirli pattern'e uyan cache'leri temizle"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Fonksiyonu çalıştır
            result = func(*args, **kwargs)
            
            # Pattern'e uyan cache'leri temizle
            try:
                if redis_manager.is_connected:
                    keys = redis_manager.redis_client.keys(pattern)
                    if keys:
                        redis_manager.redis_client.delete(*keys)
                        logger.info(f"Cache temizlendi: {len(keys)} key")
            except Exception as e:
                logger.error(f"Cache temizleme hatası: {e}")
            
            return result
        return wrapper
    return decorator
