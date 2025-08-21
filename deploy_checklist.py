#!/usr/bin/env python3
"""
CosmoFinder Production Deployment Checklist
Bu script production'a çıkmadan önce gerekli kontrolleri yapar
"""

import os
import sys
from dotenv import load_dotenv
import redis
from pymongo import MongoClient
import stripe

def check_environment_variables():
    """Environment variables kontrolü"""
    print("🔍 Environment Variables Kontrolü...")
    
    load_dotenv()
    
    required_vars = [
        'JWT_SECRET',
        'MONGO_URI',
        'REDIS_URL',
        'STRIPE_SECRET_KEY',
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_') or value.startswith('test_'):
            missing_vars.append(var)
            print(f"  ❌ {var}: {value}")
        else:
            print(f"  ✅ {var}: {'*' * min(len(value), 10)}...")
    
    if missing_vars:
        print(f"\n❌ Eksik veya test environment variables: {', '.join(missing_vars)}")
        return False
    
    print("  ✅ Tüm environment variables mevcut")
    return True

def check_security():
    """Güvenlik kontrolü"""
    print("\n🔒 Güvenlik Kontrolü...")
    
    jwt_secret = os.getenv('JWT_SECRET', '')
    if len(jwt_secret) < 32:
        print(f"  ❌ JWT_SECRET çok kısa: {len(jwt_secret)} karakter")
        return False
    
    if jwt_secret.isalnum():
        print("  ⚠️  JWT_SECRET sadece alfanumerik karakterler içeriyor")
    
    print("  ✅ JWT_SECRET güvenli")
    return True

def check_database_connection():
    """Database bağlantı kontrolü"""
    print("\n🗄️  Database Bağlantı Kontrolü...")
    
    try:
        # MongoDB
        mongo_uri = os.getenv('MONGO_URI')
        client = MongoClient(mongo_uri)
        db = client.get_database()
        db.command('ping')
        print("  ✅ MongoDB bağlantısı başarılı")
        
        # Redis
        redis_url = os.getenv('REDIS_URL')
        r = redis.from_url(redis_url)
        r.ping()
        print("  ✅ Redis bağlantısı başarılı")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database bağlantı hatası: {e}")
        return False

def check_stripe():
    """Stripe konfigürasyon kontrolü"""
    print("\n💳 Stripe Konfigürasyon Kontrolü...")
    
    stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
    
    if stripe_key.startswith('sk_test_'):
        print("  ⚠️  Test Stripe key kullanılıyor")
        return False
    elif stripe_key.startswith('sk_live_'):
        print("  ✅ Production Stripe key kullanılıyor")
        return True
    else:
        print("  ❌ Geçersiz Stripe key formatı")
        return False

def check_google_oauth():
    """Google OAuth kontrolü"""
    print("\n🔐 Google OAuth Kontrolü...")
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("  ❌ Google OAuth credentials eksik")
        return False
    
    if client_secret == 'your_client_secret_here':
        print("  ❌ Google Client Secret placeholder")
        return False
    
    print("  ✅ Google OAuth credentials mevcut")
    return True

def check_production_settings():
    """Production ayarları kontrolü"""
    print("\n🏭 Production Ayarları Kontrolü...")
    
    env = os.getenv('FLASK_ENV', 'development')
    debug = os.getenv('FLASK_DEBUG', 'True')
    
    if env != 'production':
        print(f"  ❌ FLASK_ENV: {env} (production olmalı)")
        return False
    
    if debug.lower() == 'true':
        print("  ❌ FLASK_DEBUG: True (False olmalı)")
        return False
    
    print("  ✅ Production ayarları doğru")
    return True

def main():
    """Ana kontrol fonksiyonu"""
    print("🚀 CosmoFinder Production Deployment Checklist")
    print("=" * 50)
    
    checks = [
        check_environment_variables,
        check_security,
        check_database_connection,
        check_stripe,
        check_google_oauth,
        check_production_settings
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
        except Exception as e:
            print(f"  ❌ {check.__name__} hatası: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Sonuç: {passed}/{total} kontrol geçti")
    
    if passed == total:
        print("🎉 Tüm kontroller geçti! Production'a çıkabilirsiniz.")
        return 0
    else:
        print("⚠️  Bazı kontroller başarısız. Production'a çıkmadan önce düzeltin.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
