from flask import Flask, request, jsonify, send_from_directory
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
from redis_manager import redis_manager
from notifications import NotificationService
from scheduler import setup_scheduler, stop_scheduler
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
app.register_blueprint(tokens_bp, url_prefix='/api/tokens')
app.register_blueprint(premium_bp, url_prefix='/api/premium')
app.register_blueprint(payment_bp, url_prefix='/api/payment')

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

@app.route('/api/yildizname', methods=['POST'])
@jwt_required()
@fal_rate_limit()
def yildizname():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['isim', 'anneAdi', 'dogumTarihi', 'dogumYeri', 'dogumSaati']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 422
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'yildizname')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # Cache key oluştur
        cache_key = f"yildizname:{data['isim']}:{data['anneAdi']}:{data['dogumTarihi']}:{data['dogumYeri']}:{data['dogumSaati']}"
        
        # Cache'den kontrol et
        cached_result = redis_manager.get(cache_key)
        if cached_result:
            return jsonify({
                'success': True,
                'yorum': cached_result,
                'from_cache': True,
                'reading_id': 'cached'
            })
        
        # Premium durumuna göre prompt seç
        if is_premium:
            prompt = get_premium_prompt('yildizname').format(
                isim=data['isim'],
                anneAdi=data['anneAdi'],
                dogumTarihi=data['dogumTarihi'],
                dogumYeri=data['dogumYeri'],
                dogumSaati=data['dogumSaati']
            )
        else:
            prompt = get_free_prompt('yildizname').format(
                isim=data['isim'],
                anneAdi=data['anneAdi'],
                dogumTarihi=data['dogumTarihi'],
                dogumYeri=data['dogumYeri'],
                dogumSaati=data['dogumSaati']
            )
        
        # G4F ile yanıt al
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        
        yorum = response.choices[0].message.content
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='yildizname',
            input_data=data,
            result=yorum
        )
        
        reading.save()
        
        # Cache'e kaydet
        redis_manager.set(cache_key, yorum, expire=3600)  # 1 saat
        
        return jsonify({
            'success': True,
            'yorum': yorum,
            'from_cache': False,
            'reading_id': str(reading._id)
        })
        
    except Exception as e:
        print(f"Yıldızname falı hatası: {str(e)}")
        return jsonify({'error': 'Yıldızname falı oluşturulurken bir hata oluştu'}), 500

@app.route('/api/rune', methods=['POST'])
@jwt_required()
@fal_rate_limit()
def rune():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['soru']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 422
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'rune')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # Cache key oluştur
        cache_key = f"rune:{data['soru']}:{user_id}"
        
        # Cache'den kontrol et
        cached_result = redis_manager.get(cache_key)
        if cached_result:
            return jsonify({
                'success': True,
                'yorum': cached_result,
                'from_cache': True,
                'reading_id': 'cached'
            })
        
        # Rune'ları seç
        runes = get_random_runes(3)
        
        # Premium durumuna göre prompt seç
        if is_premium:
            prompt = get_premium_prompt('rune').format(
                soru=data['soru'],
                runes=', '.join([rune['name'] for rune in runes])
            )
        else:
            prompt = get_free_prompt('rune').format(
                soru=data['soru'],
                runes=', '.join([rune['name'] for rune in runes])
            )
        
        # G4F ile yanıt al
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        
        yorum = response.choices[0].message.content
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='rune',
            input_data=data,
            result=yorum
        )
        
        reading.save()
        
        # Cache'e kaydet
        redis_manager.set(cache_key, yorum, expire=3600)  # 1 saat
        
        return jsonify({
            'success': True,
            'runes': runes,
            'yorum': yorum,
            'from_cache': False,
            'reading_id': str(reading._id)
        })
        
    except Exception as e:
        print(f"Rune falı hatası: {str(e)}")
        return jsonify({'error': 'Rune falı oluşturulurken bir hata oluştu'}), 500



@app.route('/api/chinese', methods=['POST'])
@jwt_required()
def chinese_fortune():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['dogumTarihi', 'dogumSaati']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 422
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'chinese')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # Ba Zi hesapla
        print(f"Chinese API - Dogum tarihi: {data['dogumTarihi']}, Dogum saati: {data['dogumSaati']}")
        ba_zi_result = calculate_ba_zi(data['dogumTarihi'], data['dogumSaati'])
        
        if not ba_zi_result or 'error' in ba_zi_result:
            error_msg = ba_zi_result.get('error', 'Doğum tarihi ve saati hesaplanamadı') if ba_zi_result else 'Doğum tarihi ve saati hesaplanamadı'
            return jsonify({'error': error_msg}), 422
        
        # Element sayılarını hesapla
        element_counts = {}
        for element in ELEMENTS:
            element_counts[element] = 0
        
        for pillar in ['year', 'month', 'day', 'hour']:
            if pillar in ba_zi_result:
                element = ba_zi_result[pillar]['element']
                element_counts[element] += 1
        
        # Çin falı için prompt oluştur
        print(f"Ba Zi result: {ba_zi_result}")
        prompt = f"""
        Sen deneyimli bir Çin astrolojisi uzmanısın. Aşağıdaki bilgilere göre detaylı bir Çin falı yorumu yap:

        Doğum Tarihi: {data['dogumTarihi']}
        Doğum Saati: {data['dogumSaati']}

        Ba Zi Analizi:
        Yıl Elementi: {ba_zi_result.get('year_element', 'Bilinmiyor')}
        Ay Elementi: {ba_zi_result.get('month_element', 'Bilinmiyor')}
        Gün Elementi: {ba_zi_result.get('day_element', 'Bilinmiyor')}
        Saat Elementi: {ba_zi_result.get('hour_element', 'Bilinmiyor')}

        Element Dağılımı:
        {format_element_counts(element_counts)}

        Lütfen şu konuları kapsayan detaylı bir Çin falı yorumu yap:

        **🌟 KİŞİLİK ÖZELLİKLERİ VE KARAKTER ANALİZİ** (3-4 cümle)
        - Element kombinasyonuna göre kişilik yapısı
        - Güçlü ve zayıf yönler
        - Karakter özellikleri ve davranış kalıpları

        **💼 KARİYER VE İŞ HAYATI** (3-4 cümle)
        - Meslek uyumluluğu ve öneriler
        - Kariyer fırsatları ve gelişim alanları
        - İş hayatındaki zorluklar ve çözümler

        **❤️ AŞK VE İLİŞKİLER** (3-4 cümle)
        - Romantik uyumluluk analizi
        - İlişki dinamikleri ve gelecek
        - Duygusal ihtiyaçlar ve beklentiler

        **🏥 SAĞLIK DURUMU** (3-4 cümle)
        - Element dengesine göre sağlık önerileri
        - Dikkat edilmesi gereken sağlık konuları
        - Yaşam tarzı önerileri

        **⚖️ ELEMENT DENGESİ VE EKSİKLİKLERİ** (3-4 cümle)
        - Element dağılımının analizi
        - Eksik elementlerin etkileri
        - Dengeleme önerileri

        **🔮 GELECEK DÖNEMLERDEKİ FIRSATLAR** (3-4 cümle)
        - Önümüzdeki dönemlerdeki fırsatlar
        - Element döngülerinin etkileri
        - Uzun vadeli planlar ve hedefler

        **🛤️ GENEL YAŞAM YOLU VE KADER** (3-4 cümle)
        - Yaşam amacı ve misyon
        - Karmik dersler ve öğrenmeler
        - Ruhsal gelişim yolu

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """
        
        # G4F ile yanıt al
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
            )
            
            yorum = response.choices[0].message.content
            print(f"Chinese Fortune - Generated content length: {len(yorum) if yorum else 0}")
            print(f"Chinese Fortune - First 200 chars: {yorum[:200] if yorum else 'EMPTY'}")  # Debug
        except Exception as g4f_error:
            print(f"G4F hatası: {str(g4f_error)}")
            # Fallback yorum
            yorum = f"""
            Çin falı yorumu:
            
            Doğum tarihi: {data['dogumTarihi']}
            Doğum saati: {data['dogumSaati']}
            
            Ba Zi analizi sonucunda:
            - Yıl elementi: {ba_zi_result.get('year_element', 'Bilinmiyor')}
            - Ay elementi: {ba_zi_result.get('month_element', 'Bilinmiyor')}
            - Gün elementi: {ba_zi_result.get('day_element', 'Bilinmiyor')}
            - Saat elementi: {ba_zi_result.get('hour_element', 'Bilinmiyor')}
            
            Element dağılımı: {element_counts}
            
            Bu element kombinasyonuna göre kişilik özellikleri, kariyer yönelimi, aşk hayatı ve genel yaşam yolu analiz edilmiştir.
            """
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='chinese',
            input_data=data,
            result=yorum
        )
        
        reading.save()
        
        return jsonify({
            'success': True,
            'ba_zi': ba_zi_result,
            'element_counts': element_counts,
            'yorum': yorum,
            'reading_id': str(reading._id)
        })
        
    except Exception as e:
        import traceback
        print(f"Çin falı hatası: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Çin falı oluşturulurken bir hata oluştu: {str(e)}'}), 500

@app.route('/api/coffee', methods=['POST'])
@jwt_required()
def coffee_fortune():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['soru']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 422
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'coffee')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # Çok dilli prompt sistemi kullan
        prompt = get_prompt_by_language(
            'coffee', 
            language, 
            soru=data['soru']
        )
        
        # G4F ile yanıt al
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        
        yorum = response.choices[0].message.content
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='coffee',
            input_data=data,
            result=yorum
        )
        
        reading.save()
        
        return jsonify({
            'success': True,
            'yorum': yorum,
            'reading_id': str(reading._id),
            'language': language
        })
        
    except Exception as e:
        print(f"Kahve falı hatası: {str(e)}")
        return jsonify({'error': 'Kahve falı oluşturulurken bir hata oluştu'}), 500

@app.route('/api/tarot', methods=['POST'])
@jwt_required()
def tarot():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['soru']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 422
        
        # Dil parametresini al (varsayılan: Türkçe)
        language = data.get('lang', 'tr')
        if language not in ['tr', 'en', 'de']:
            language = 'tr'
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'tarot')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # Cache key oluştur (dil parametresi ile)
        cache_key = f"tarot:{data['soru']}:{language}:{user_id}"
        
        # Cache'den kontrol et
        cached_result = redis_manager.get(cache_key)
        if cached_result:
            return jsonify({
                'success': True,
                'yorum': cached_result,
                'from_cache': True,
                'reading_id': 'cached',
                'language': language
            })
        
        # Tarot kartlarını seç
        cards = get_random_tarot_cards(3)
        
        # Çok dilli prompt sistemi kullan
        prompt = get_prompt_by_language(
            'tarot', 
            language, 
            soru=data['soru'],
            cards=cards
        )
        
        # G4F ile yanıt al
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
            )
            
            yorum = response.choices[0].message.content
        except Exception as g4f_error:
            print(f"Tarot G4F hatası: {str(g4f_error)}")
            # Fallback yorum
            yorum = f"""
🔮 Tarot Falı Yorumu 🔮

Soru: {data['soru']}

Seçilen Kartlar:
1. {card_names[0]}: {card_descriptions[0]}
2. {card_names[1]}: {card_descriptions[1]}
3. {card_names[2]}: {card_descriptions[2]}

Bu üç kart, sorduğunuz konuda önemli mesajlar vermektedir. 
Kartların birleşimi, hayatınızda yeni fırsatların ve değişimlerin yaklaştığını işaret ediyor.
Geçmişten gelen deneyimleriniz, bugünkü durumunuzu şekillendiriyor ve geleceğe dair umutlu adımlar atmanızı sağlıyor.
            """
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='tarot',
            input_data=data,
            result=yorum
        )
        
        reading.save()
        
        # Cache'e kaydet
        redis_manager.set(cache_key, yorum, expire=3600)  # 1 saat
        
        return jsonify({
            'success': True,
            'cards': cards,
            'yorum': yorum,
            'from_cache': False,
            'reading_id': str(reading._id),
            'language': language
        })
        
    except Exception as e:
        print(f"Tarot hatası: {str(e)}")
        return jsonify({'error': 'Tarot falı oluşturulurken bir hata oluştu'}), 500

@app.route('/api/daily', methods=['POST'])
@jwt_required()
@daily_fal_rate_limit()
def daily_burc_yorumu():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Request'ten doğum tarihi al
        data = request.get_json() or {}
        dogum_tarihi = data.get('dogumTarihi')
        
        # Dil parametresini al (varsayılan: Türkçe)
        language = data.get('lang', 'tr')
        if language not in ['tr', 'en', 'de']:
            language = 'tr'
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'daily')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # Doğum tarihini kontrol et - önce request'ten, sonra user'dan
        birth_date = None
        zodiac_sign = None
        
        if dogum_tarihi:
            # Frontend'ten gelen doğum tarihini kullan
            try:
                birth_date = datetime.strptime(dogum_tarihi, '%Y-%m-%d').date()
                zodiac_sign = calculate_zodiac_sign(dogum_tarihi)
                
                # Kullanıcı profilini güncelle
                user.birth_date = birth_date
                user.zodiac_sign = zodiac_sign
                user.save()
                
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Geçersiz doğum tarihi formatı. YYYY-MM-DD formatında girin.',
                    'type': 'invalid_date_format'
                }), 422
        else:
            # Kullanıcının mevcut doğum tarihi ve burç bilgisini kontrol et
            birth_date = user.birth_date
            zodiac_sign = user.zodiac_sign
        
        if not birth_date:
            return jsonify({
                'success': False,
                'error': 'Doğum tarihiniz bulunamadı. Günlük burç yorumu için profil bilgilerinizi güncelleyin.',
                'type': 'missing_birth_date'
            }), 422
        
        if not zodiac_sign:
            return jsonify({
                'success': False,
                'error': 'Burç bilginiz bulunamadı. Lütfen profil bilgilerinizi güncelleyin.',
                'type': 'missing_zodiac_sign'
            }), 422
        
        # Bugünün tarihini al
        today = datetime.now().strftime('%d %B %Y')
        
        # Çok dilli prompt sistemi kullan
        prompt = get_prompt_by_language(
            'daily', 
            language, 
            tarih=today,
            burc=zodiac_sign
        )
        
        # G4F ile yanıt al
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        
        yorum = response.choices[0].message.content
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='daily_burc_yorumu',
            input_data={'zodiac_sign': zodiac_sign, 'date': today},
            result=yorum
        )
        
        reading.save()
        
        return jsonify({
            'success': True,
            'zodiac_sign': zodiac_sign,
            'date': today,
            'yorum': yorum,
            'reading_id': str(reading._id),
            'language': language
        })
        
    except Exception as e:
        print(f"Günlük burç yorumu hatası: {str(e)}")
        return jsonify({'error': 'Günlük burç yorumu oluşturulurken bir hata oluştu'}), 500

@app.route('/api/kabala', methods=['POST'])
@jwt_required()
def kabala_fortune():
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        
        # Gerekli alanları kontrol et
        required_fields = ['isim', 'dogumTarihi']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} alanı gereklidir'}), 422
        
        # Dil parametresini al (varsayılan: Türkçe)
        language = data.get('lang', 'tr')
        if language not in ['tr', 'en', 'de']:
            language = 'tr'
        
        # Premium durumunu kontrol et
        is_premium = user.has_active_premium()
        
        # Premium değilse token kontrolü yap
        if not is_premium:
            success, message = spend_tokens_for_reading(user_id, 'kabala')
            if not success:
                return jsonify({'error': message}), 400
            # Token harcandıktan sonra kullanıcı bilgilerini güncelle
            user = User.find_by_id(user_id)
        
        # İbrani harf değerleri
        hebrew_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
            'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90, 'ק': 100,
            'ר': 200, 'ש': 300, 'ת': 400
        }
        
        # İsimi İbrani harflere çevir (basit çeviri)
        name_to_hebrew = {
            'a': 'א', 'b': 'ב', 'c': 'ג', 'd': 'ד', 'e': 'ה', 'f': 'ו', 'g': 'ז', 'h': 'ח',
            'i': 'י', 'j': 'י', 'k': 'כ', 'l': 'ל', 'm': 'מ', 'n': 'נ', 'o': 'ע', 'p': 'פ',
            'q': 'ק', 'r': 'ר', 's': 'ש', 't': 'ת', 'u': 'ו', 'v': 'ו', 'w': 'ו', 'x': 'ס',
            'y': 'י', 'z': 'ז'
        }
        
        # İsimi İbrani harflere çevir
        hebrew_name = ''
        for letter in data['isim'].lower():
            if letter in name_to_hebrew:
                hebrew_name += name_to_hebrew[letter]
        
        # İbrani numeroloji hesapla
        name_value = sum(hebrew_values.get(letter, 0) for letter in hebrew_name)
        reduced_value = sum(int(digit) for digit in str(name_value))
        while reduced_value > 9:
            reduced_value = sum(int(digit) for digit in str(reduced_value))
        
        # Rastgele sefirot seç (1-3 tane)
        sefirot_list = [
            {'key': 'keter', 'name': 'Keter (Taç)', 'hebrew': 'א', 'meaning': 'İlahi irade, yüksek bilinç'},
            {'key': 'hokmah', 'name': 'Hokmah (Bilgelik)', 'hebrew': 'ב', 'meaning': 'Erkek enerji, yaratıcı güç'},
            {'key': 'binah', 'name': 'Binah (Anlayış)', 'hebrew': 'ג', 'meaning': 'Kadın enerji, analitik düşünce'},
            {'key': 'hesed', 'name': 'Hesed (Merhamet)', 'hebrew': 'ד', 'meaning': 'Sevgi, cömertlik, bağışlama'},
            {'key': 'gevurah', 'name': 'Gevurah (Güç)', 'hebrew': 'ה', 'meaning': 'Adalet, disiplin, güç'},
            {'key': 'tiferet', 'name': 'Tiferet (Güzellik)', 'hebrew': 'ו', 'meaning': 'Denge, uyum, güzellik'},
            {'key': 'netzach', 'name': 'Netzach (Zafer)', 'hebrew': 'ז', 'meaning': 'Dayanıklılık, zafer, süreklilik'},
            {'key': 'hod', 'name': 'Hod (İhtişam)', 'hebrew': 'ח', 'meaning': 'Teşekkür, övgü, alçakgönüllülük'},
            {'key': 'yesod', 'name': 'Yesod (Temel)', 'hebrew': 'ט', 'meaning': 'Temel, köprü, bağlantı'},
            {'key': 'malkhut', 'name': 'Malkhut (Krallık)', 'hebrew': 'י', 'meaning': 'Dünyevi tezahür, krallık'}
        ]
        
        import random
        selected_sefirot = random.sample(sefirot_list, random.randint(1, 3))
        
        # Kabala falı için prompt oluştur
        sefirot_info = '\n'.join([
            f"- {sef['name']} ({sef['hebrew']}): {sef['meaning']}"
            for sef in selected_sefirot
        ])
        
        # Çok dilli prompt sistemi kullan
        prompt = get_prompt_by_language(
            'kabala', 
            language, 
            isim=data['isim'],
            dogumTarihi=data['dogumTarihi'],
            hebrew_name=hebrew_name,
            name_value=name_value,
            reduced_value=reduced_value,
            selected_sefirot=selected_sefirot
        )
        
        # G4F ile yanıt al
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
            )
            
            yorum = response.choices[0].message.content
        except Exception as g4f_error:
            print(f"Kabala G4F hatası: {str(g4f_error)}")
            # Fallback yorum
            yorum = f"""
            Kabala falı yorumu:
            
            İsim: {data['isim']}
            Doğum tarihi: {data['dogumTarihi']}
            
            İbrani isim analizi:
            - İbrani harfler: {hebrew_name}
            - İsim değeri: {name_value}
            - İndirgenmiş değer: {reduced_value}
            
            Seçilen sefirotlar:
            {sefirot_info}
            
            Bu Kabala analizi, ruhsal yolunuz ve kaderiniz hakkında önemli bilgiler sunmaktadır.
            """
        
        # Reading'i kaydet
        reading = Reading(
            user_id=user_id,
            reading_type='kabala',
            input_data=data,
            result=yorum
        )
        
        reading.save()
        
        return jsonify({
            'success': True,
            'hebrew_name': hebrew_name,
            'name_value': name_value,
            'reduced_value': reduced_value,
            'selected_sefirot': selected_sefirot,
            'yorum': yorum,
            'reading_id': str(reading._id),
            'language': language
        })
        
    except Exception as e:
        print(f"Kabala falı hatası: {str(e)}")
        return jsonify({'error': 'Kabala falı oluşturulurken bir hata oluştu'}), 500

def get_element_info(element):
    """Element bilgilerini döndür"""
    if element in ELEMENTS:
        return ELEMENTS[element]["characteristics"]
    return "Bilinmeyen element"

def get_element_name_tr(element):
    """Element adını Türkçe döndür"""
    if element in ELEMENTS:
        return ELEMENTS[element]["name_tr"]
    return element

def format_element_counts(element_counts):
    """Element sayılarını formatla"""
    return ", ".join([f"{element}({count})" for element, count in element_counts.items()])



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