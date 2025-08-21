#!/usr/bin/env python3
"""
Redis kurulum ve test script'i
Bu script Redis bağlantısını test eder ve gerekli ayarları yapar
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def check_redis_installation():
    """Redis kurulu mu kontrol et"""
    try:
        result = subprocess.run(['redis-server', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Redis kurulu:", result.stdout.strip())
            return True
        else:
            print("❌ Redis kurulu değil")
            return False
    except FileNotFoundError:
        print("❌ Redis kurulu değil")
        return False

def install_redis_macos():
    """macOS'ta Redis kur"""
    try:
        print("🍎 macOS'ta Redis kuruluyor...")
        subprocess.run(['brew', 'install', 'redis'], check=True)
        print("✅ Redis başarıyla kuruldu")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Redis kurulum hatası: {e}")
        return False
    except FileNotFoundError:
        print("❌ Homebrew kurulu değil. Önce Homebrew kurun: https://brew.sh/")
        return False

def install_redis_ubuntu():
    """Ubuntu/Debian'da Redis kur"""
    try:
        print("🐧 Ubuntu/Debian'da Redis kuruluyor...")
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'redis-server'], check=True)
        print("✅ Redis başarıyla kuruldu")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Redis kurulum hatası: {e}")
        return False

def install_redis_centos():
    """CentOS/RHEL'de Redis kur"""
    try:
        print("🔴 CentOS/RHEL'de Redis kuruluyor...")
        subprocess.run(['sudo', 'yum', 'install', '-y', 'redis'], check=True)
        print("✅ Redis başarıyla kuruldu")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Redis kurulum hatası: {e}")
        return False

def start_redis_service():
    """Redis servisini başlat"""
    try:
        print("🚀 Redis servisi başlatılıyor...")
        
        # macOS için
        if sys.platform == "darwin":
            subprocess.run(['brew', 'services', 'start', 'redis'], check=True)
            print("✅ Redis servisi başlatıldı")
        # Linux için
        elif sys.platform.startswith('linux'):
            subprocess.run(['sudo', 'systemctl', 'start', 'redis'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'redis'], check=True)
            print("✅ Redis servisi başlatıldı ve otomatik başlatma aktif")
        else:
            print("⚠️  Bu işletim sistemi için manuel Redis başlatma gerekli")
            return False
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Redis servis başlatma hatası: {e}")
        return False

def test_redis_connection():
    """Redis bağlantısını test et"""
    try:
        print("🔍 Redis bağlantısı test ediliyor...")
        
        # Redis CLI ile test
        result = subprocess.run(['redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis bağlantısı başarılı")
            return True
        else:
            print("❌ Redis bağlantısı başarısız")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Redis bağlantı zaman aşımı")
        return False
    except Exception as e:
        print(f"❌ Redis test hatası: {e}")
        return False

def test_python_redis():
    """Python Redis kütüphanesini test et"""
    try:
        print("🐍 Python Redis kütüphanesi test ediliyor...")
        
        # Redis manager'ı import et
        from redis_manager import redis_manager
        
        # Bağlantıyı test et
        if redis_manager.is_connected:
            print("✅ Python Redis bağlantısı başarılı")
            
            # Basit test işlemleri
            test_key = "test:connection"
            test_value = "Hello Redis!"
            
            # Set test
            if redis_manager.set(test_key, test_value, 60):
                print("✅ Redis set işlemi başarılı")
            else:
                print("❌ Redis set işlemi başarısız")
                return False
            
            # Get test
            retrieved_value = redis_manager.get(test_key)
            if retrieved_value == test_value:
                print("✅ Redis get işlemi başarılı")
            else:
                print("❌ Redis get işlemi başarısız")
                return False
            
            # Delete test
            if redis_manager.delete(test_key):
                print("✅ Redis delete işlemi başarılı")
            else:
                print("❌ Redis delete işlemi başarısız")
                return False
            
            return True
        else:
            print("❌ Python Redis bağlantısı başarısız")
            return False
            
    except ImportError as e:
        print(f"❌ Redis kütüphanesi import hatası: {e}")
        print("💡 'pip install redis' komutunu çalıştırın")
        return False
    except Exception as e:
        print(f"❌ Python Redis test hatası: {e}")
        return False

def create_env_template():
    """Redis environment variables template'i oluştur"""
    env_content = """# Redis Konfigürasyonu
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# MongoDB Konfigürasyonu
MONGO_URI=mongodb://localhost:27017/FAL_APP

# JWT Konfigürasyonu
JWT_SECRET=your-super-secret-key-here
JWT_EXPIRE=365d

# Flask Konfigürasyonu
FLASK_ENV=development
FLASK_DEBUG=False
PORT=5050
"""
    
    env_file = ".env.redis.template"
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Redis environment template oluşturuldu: {env_file}")
        print("💡 Bu dosyayı .env olarak kopyalayın ve gerekli değerleri doldurun")
    except Exception as e:
        print(f"❌ Template oluşturma hatası: {e}")

def main():
    """Ana fonksiyon"""
    print("🚀 Redis Kurulum ve Test Script'i")
    print("=" * 50)
    
    # 1. Redis kurulu mu kontrol et
    if not check_redis_installation():
        print("\n📦 Redis kuruluyor...")
        
        if sys.platform == "darwin":
            if not install_redis_macos():
                print("❌ Redis kurulumu başarısız")
                return
        elif sys.platform.startswith('linux'):
            if not install_redis_ubuntu():
                if not install_redis_centos():
                    print("❌ Redis kurulumu başarısız")
                    return
        else:
            print("❌ Bu işletim sistemi için otomatik kurulum desteklenmiyor")
            print("💡 Manuel olarak Redis kurun: https://redis.io/download")
            return
    
    # 2. Redis servisini başlat
    if not start_redis_service():
        print("❌ Redis servis başlatma başarısız")
        return
    
    # 3. Biraz bekle
    print("⏳ Redis servisinin başlaması bekleniyor...")
    time.sleep(3)
    
    # 4. Redis bağlantısını test et
    if not test_redis_connection():
        print("❌ Redis bağlantı testi başarısız")
        return
    
    # 5. Python Redis kütüphanesini test et
    if not test_python_redis():
        print("❌ Python Redis testi başarısız")
        return
    
    # 6. Environment template oluştur
    create_env_template()
    
    print("\n🎉 Redis kurulum ve testi tamamlandı!")
    print("✅ Redis servisi çalışıyor")
    print("✅ Python Redis kütüphanesi çalışıyor")
    print("✅ Backend Redis entegrasyonu hazır")
    
    print("\n📋 Sonraki adımlar:")
    print("1. .env dosyasında Redis ayarlarını kontrol edin")
    print("2. Backend'i yeniden başlatın: python run.py")
    print("3. /api/health endpoint'ini test edin")
    print("4. /api/redis/stats endpoint'ini test edin")

if __name__ == "__main__":
    main()
