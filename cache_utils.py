from redis_manager import redis_manager
from typing import Any, Optional, Dict, List
import hashlib
import json
from datetime import timedelta

class CacheUtils:
    """Redis cache için utility fonksiyonları"""
    
    @staticmethod
    def generate_cache_key(prefix: str, **kwargs) -> str:
        """Cache key oluştur"""
        # Key-value çiftlerini sırala ve hash'le
        sorted_items = sorted(kwargs.items())
        key_string = f"{prefix}:{':'.join([f'{k}={v}' for k, v in sorted_items])}"
        
        # Hash oluştur (key uzunluğunu sınırla)
        hash_object = hashlib.md5(key_string.encode())
        return f"{prefix}:{hash_object.hexdigest()[:16]}"
    
    @staticmethod
    def cache_fal_result(reading_type: str, user_data: Dict[str, Any], result: str, ttl: int = 86400) -> bool:
        """Fal sonucunu cache'le"""
        try:
            cache_key = CacheUtils.generate_cache_key(
                f"fal:{reading_type}",
                **user_data
            )
            return redis_manager.set(cache_key, result, ttl)
        except Exception as e:
            print(f"Cache hatası: {e}")
            return False
    
    @staticmethod
    def get_cached_fal_result(reading_type: str, user_data: Dict[str, Any]) -> Optional[str]:
        """Cache'den fal sonucu al"""
        try:
            cache_key = CacheUtils.generate_cache_key(
                f"fal:{reading_type}",
                **user_data
            )
            return redis_manager.get(cache_key)
        except Exception as e:
            print(f"Cache get hatası: {e}")
            return None
    
    @staticmethod
    def cache_user_data(user_id: str, data_type: str, data: Any, ttl: int = 3600) -> bool:
        """Kullanıcı verisini cache'le"""
        try:
            cache_key = f"user:{user_id}:{data_type}"
            return redis_manager.set(cache_key, data, ttl)
        except Exception as e:
            print(f"User cache hatası: {e}")
            return False
    
    @staticmethod
    def get_cached_user_data(user_id: str, data_type: str) -> Optional[Any]:
        """Cache'den kullanıcı verisi al"""
        try:
            cache_key = f"user:{user_id}:{data_type}"
            return redis_manager.get(cache_key)
        except Exception as e:
            print(f"User cache get hatası: {e}")
            return None
    
    @staticmethod
    def invalidate_user_cache(user_id: str, pattern: str = "*") -> bool:
        """Kullanıcının belirli pattern'e uyan cache'lerini temizle"""
        try:
            if not redis_manager.is_connected:
                return False
            
            # Pattern'e uyan key'leri bul
            search_pattern = f"user:{user_id}:{pattern}"
            keys = redis_manager.redis_client.keys(search_pattern)
            
            if keys:
                # Key'leri sil
                deleted_count = redis_manager.redis_client.delete(*keys)
                print(f"User cache temizlendi: {deleted_count} key")
                return True
            
            return True
        except Exception as e:
            print(f"Cache invalidation hatası: {e}")
            return False
    
    @staticmethod
    def cache_api_response(endpoint: str, params: Dict[str, Any], response: Any, ttl: int = 1800) -> bool:
        """API response'unu cache'le"""
        try:
            cache_key = CacheUtils.generate_cache_key(
                f"api:{endpoint}",
                **params
            )
            return redis_manager.set(cache_key, response, ttl)
        except Exception as e:
            print(f"API cache hatası: {e}")
            return False
    
    @staticmethod
    def get_cached_api_response(endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Cache'den API response'u al"""
        try:
            cache_key = CacheUtils.generate_cache_key(
                f"api:{endpoint}",
                **params
            )
            return redis_manager.get(cache_key)
        except Exception as e:
            print(f"API cache get hatası: {e}")
            return None
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Cache istatistiklerini getir"""
        try:
            if not redis_manager.is_connected:
                return {"status": "disconnected"}
            
            # Redis info'dan cache istatistiklerini al
            info = redis_manager.redis_client.info()
            
            # Cache hit/miss oranını hesapla
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                "status": "connected",
                "total_commands": info.get('total_commands_processed', 0),
                "cache_hits": hits,
                "cache_misses": misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "used_memory": info.get('used_memory_human', 'N/A'),
                "connected_clients": info.get('connected_clients', 0)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def clear_expired_cache() -> bool:
        """Expired cache'leri temizle (Redis otomatik yapıyor ama manuel de yapılabilir)"""
        try:
            if not redis_manager.is_connected:
                return False
            
            # Redis otomatik olarak expired key'leri temizliyor
            # Bu fonksiyon sadece manuel temizlik için
            return True
        except Exception as e:
            print(f"Cache temizleme hatası: {e}")
            return False

# Global instance
cache_utils = CacheUtils()
