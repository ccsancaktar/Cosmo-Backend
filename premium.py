from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, PremiumSubscription, PREMIUM_PRICES
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

premium_bp = Blueprint('premium', __name__)

@premium_bp.route('/status', methods=['GET'])
@jwt_required()
def get_premium_status():
    """Kullanıcının premium durumunu getir"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        subscription = PremiumSubscription.find_active_by_user_id(user_id)
        
        if subscription:
            return jsonify({
                'has_premium': True,
                'plan_type': subscription.plan_type,
                'days_remaining': subscription.days_remaining(),
                'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
                'auto_renew': subscription.auto_renew
            }), 200
        else:
            return jsonify({
                'has_premium': False,
                'plan_type': None,
                'days_remaining': None,
                'end_date': None,
                'auto_renew': False
            }), 200
        
    except Exception as e:
        return jsonify({'error': f'Premium durum hatası: {str(e)}'}), 500

@premium_bp.route('/plans', methods=['GET'])
def get_premium_plans():
    """Premium planları getir"""
    try:
        plans = [
            {
                'id': 'premium_monthly',
                'name': 'Premium Aylık',
                'price': PREMIUM_PRICES['premium_monthly'],
                'period': 'ay',
                'features': [
                    'Sınırsız fal çekme',
                    'Reklamsız deneyim',
                    'Tüm fal türleri',
                    'Detaylı yorumlar',
                    'Fal geçmişi',
                    'Öncelikli destek'
                ]
            },
            {
                'id': 'premium_yearly',
                'name': 'Premium Yıllık',
                'price': PREMIUM_PRICES['premium_yearly'],
                'period': 'yıl',
                'discount': '17%',
                'features': [
                    'Premium özellikleri',
                    'Yıllık %17 indirim',
                    'Özel içerikler'
                ]
            },
            {
                'id': 'premium_plus_monthly',
                'name': 'Premium+ Aylık',
                'price': PREMIUM_PRICES['premium_plus_monthly'],
                'period': 'ay',
                'features': [
                    'Premium özellikleri',
                    'Özel fal uzmanı',
                    'Video fal seansları',
                    'Özel astroloji raporları',
                    'VIP özel günler'
                ]
            },
            {
                'id': 'premium_plus_yearly',
                'name': 'Premium+ Yıllık',
                'price': PREMIUM_PRICES['premium_plus_yearly'],
                'period': 'yıl',
                'discount': '17%',
                'features': [
                    'Premium+ özellikleri',
                    'Yıllık %17 indirim',
                    'Özel VIP içerikler'
                ]
            }
        ]
        
        return jsonify({
            'plans': plans,
            'message': 'Premium planları başarıyla getirildi'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Plan listesi hatası: {str(e)}'}), 500

@premium_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_premium():
    """Premium üyelik satın al"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'Plan ID gereklidir'}), 400
        
        # Plan bilgilerini al
        plan_info = get_plan_info(plan_id)
        if not plan_info:
            return jsonify({'error': 'Geçersiz plan'}), 400
        
        # Ödeme işlemi burada yapılacak (Stripe, PayPal vb.)
        # Şimdilik simüle ediyoruz
        payment_successful = True  # Bu kısım ödeme sistemi entegrasyonu ile değişecek
        
        if payment_successful:
            # Mevcut aktif üyeliği iptal et
            existing_subscription = PremiumSubscription.find_active_by_user_id(user_id)
            if existing_subscription:
                existing_subscription.is_active = False
                existing_subscription.save()
            
            # Yeni üyelik oluştur
            start_date = datetime.now()
            end_date = start_date + timedelta(days=plan_info['days'])
            
            subscription = PremiumSubscription(
                user_id=user_id,
                plan_type=plan_info['plan_type'],
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                auto_renew=True
            )
            subscription.save()
            
            return jsonify({
                'message': 'Premium üyelik başarıyla aktifleştirildi',
                'plan_type': plan_info['plan_type'],
                'end_date': end_date.isoformat(),
                'days_remaining': plan_info['days']
            }), 200
        else:
            return jsonify({'error': 'Ödeme başarısız'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Premium üyelik hatası: {str(e)}'}), 500

@premium_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_premium():
    """Premium üyeliği iptal et"""
    try:
        user_id = get_jwt_identity()
        
        subscription = PremiumSubscription.find_active_by_user_id(user_id)
        if not subscription:
            return jsonify({'error': 'Aktif premium üyeliğiniz bulunmuyor'}), 404
        
        subscription.auto_renew = False
        subscription.save()
        
        return jsonify({
            'message': 'Premium üyeliğiniz iptal edildi',
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Üyelik iptal hatası: {str(e)}'}), 500

@premium_bp.route('/reactivate', methods=['POST'])
@jwt_required()
def reactivate_premium():
    """Premium üyeliği yeniden aktifleştir"""
    try:
        user_id = get_jwt_identity()
        
        subscription = PremiumSubscription.find_active_by_user_id(user_id)
        if not subscription:
            return jsonify({'error': 'Aktif premium üyeliğiniz bulunmuyor'}), 404
        
        subscription.auto_renew = True
        subscription.save()
        
        return jsonify({
            'message': 'Premium üyeliğiniz yeniden aktifleştirildi'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Üyelik yeniden aktifleştirme hatası: {str(e)}'}), 500

def get_plan_info(plan_id):
    """Plan ID'sine göre plan bilgilerini getir"""
    plan_info = {
        'premium_monthly': {
            'plan_type': 'premium',
            'days': 30,
            'price': PREMIUM_PRICES['premium_monthly']
        },
        'premium_yearly': {
            'plan_type': 'premium',
            'days': 365,
            'price': PREMIUM_PRICES['premium_yearly']
        },
        'premium_plus_monthly': {
            'plan_type': 'premium_plus',
            'days': 30,
            'price': PREMIUM_PRICES['premium_plus_monthly']
        },
        'premium_plus_yearly': {
            'plan_type': 'premium_plus',
            'days': 365,
            'price': PREMIUM_PRICES['premium_plus_yearly']
        }
    }
    
    return plan_info.get(plan_id)

def get_premium_prompt(reading_type):
    """Premium kullanıcılar için detaylı prompt"""
    premium_prompts = {
        'yildizname': """
        Sen deneyimli bir astrolog ve yıldızname uzmanısın. Aşağıdaki bilgilere göre ÇOK DETAYLI ve KAPSAMLI bir yıldızname yorumu yap:

        İsim: {isim}
        Anne Adı: {anneAdi}
        Doğum Tarihi: {dogumTarihi}
        Doğum Yeri: {dogumYeri}
        Doğum Saati: {dogumSaati}

        Lütfen şu konuları kapsayan ÇOK DETAYLI bir yıldızname yorumu yap:

        **🌟 KİŞİLİK ANALİZİ** (4-5 cümle)
        - Burç özellikleri ve karakter analizi
        - Astrolojik açıdan kişilik yapısı
        - Güçlü ve zayıf yönler
        - Kişisel gelişim alanları

        **💼 KARİYER VE İŞ HAYATI** (4-5 cümle)
        - Meslek uyumluluğu ve öneriler
        - Kariyer fırsatları ve gelişim alanları
        - İş hayatındaki zorluklar ve çözümler
        - Finansal durum ve para yönetimi

        **❤️ AŞK VE İLİŞKİLER** (4-5 cümle)
        - Romantik uyumluluk analizi
        - İlişki dinamikleri ve gelecek
        - Evlilik ve aile hayatı
        - Duygusal ihtiyaçlar ve beklentiler

        **🏥 SAĞLIK DURUMU** (3-4 cümle)
        - Dikkat edilmesi gereken sağlık konuları
        - Astrolojik sağlık önerileri
        - Enerji seviyesi ve yaşam tarzı

        **🏠 AİLE VE SOSYAL HAYAT** (3-4 cümle)
        - Aile ilişkileri ve dinamikleri
        - Sosyal çevre ve arkadaşlıklar
        - Toplumsal uyum ve iletişim

        **⚠️ DİKKAT EDİLMESİ GEREKENLER** (3-4 cümle)
        - Uyarılar ve öneriler
        - Dikkatli olunması gereken dönemler
        - Risk faktörleri ve önlemler

        **🔮 GELECEK DÖNEMLER** (4-5 cümle)
        - Önümüzdeki 3-6 ay detaylı analizi
        - Fırsatlar ve zorluklar
        - Uzun vadeli planlar ve hedefler
        - Astrolojik döngüler ve etkileri

        **💫 RUHSAL GELİŞİM** (3-4 cümle)
        - Ruhsal yol ve kader analizi
        - Kişisel gelişim önerileri
        - Manevi arayışlar ve anlam

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz. Astrolojik terimleri açıklayarak yaz. Her bölümü detaylı ve kapsamlı şekilde ele al.
        """,
        
        'tarot': """
        Sen deneyimli bir tarot uzmanısın. Aşağıdaki bilgilere göre ÇOK DETAYLI bir tarot yorumu yap:

        Çekilen Kartlar: {cards}

        Lütfen şu konuları kapsayan ÇOK DETAYLI bir tarot yorumu yap:

        🎴 KARTLARIN GENEL ANLAMI (4-5 cümle)
        - Kartların birbirleriyle uyumu ve etkileşimi
        - Genel enerji ve tema analizi
        - Kartların kombinasyonunun özel anlamı

        💼 KARİYER VE İŞ HAYATI (4-5 cümle)
        - İş hayatındaki fırsatlar ve zorluklar
        - Kariyer gelişimi ve yükselme şansları
        - Finansal durum ve para yönetimi
        - İş ortamı ve çalışma koşulları

        ❤️ AŞK VE İLİŞKİLER (4-5 cümle)
        - Romantik durum detaylı analizi
        - İlişki dinamikleri ve gelecek
        - Evlilik ve aile hayatı
        - Duygusal ihtiyaçlar ve beklentiler

        🏥 SAĞLIK VE ENERJİ (3-4 cümle)
        - Enerji seviyesi ve sağlık durumu
        - Dikkat edilmesi gereken sağlık konuları
        - Yaşam tarzı önerileri

        👥 SOSYAL HAYAT (3-4 cümle)
        - Arkadaşlık ve sosyal çevre
        - Aile ilişkileri ve dinamikleri
        - Toplumsal uyum ve iletişim

        🔮 GELECEK TAHMİNLERİ (4-5 cümle)
        - Önümüzdeki dönemler detaylı analizi
        - Fırsatlar ve uyarılar
        - Uzun vadeli planlar ve hedefler
        - Zaman çizelgesi ve önemli tarihler

        💡 PRATİK ÖNERİLER (3-4 cümle)
        - Yapılması gerekenler ve eylemler
        - Dikkat edilmesi gereken noktalar
        - Kişisel gelişim önerileri

        🎭 DUYGUSAL DURUM (3-4 cümle)
        - Mevcut duygusal durum analizi
        - İç dünya ve ruhsal durum
        - Stres faktörleri ve çözümler

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz. Her kartın anlamını detaylı açıkla ve kartların birbirleriyle etkileşimini analiz et.
        """,
        
        'coffee': """
        Sen deneyimli bir kahve falı uzmanısın. Aşağıdaki bilgilere göre ÇOK DETAYLI bir kahve falı yorumu yap:

        Fincan Fotoğrafı: {image_description}

        Lütfen şu konuları kapsayan ÇOK DETAYLI bir kahve falı yorumu yap:

        ☕ FİNCANIN GENEL GÖRÜNÜMÜ (4-5 cümle)
        - Fincanın genel enerjisi ve atmosferi
        - Kahve kalıntılarının dağılımı ve yoğunluğu
        - Fincanın farklı bölgelerindeki enerji akışı

        💼 KARİYER VE İŞ HAYATI (4-5 cümle)
        - İş hayatındaki gelişmeler ve değişimler
        - Kariyer fırsatları ve yükselme şansları
        - Finansal durum ve para yönetimi
        - İş ortamı ve çalışma koşulları

        ❤️ AŞK VE İLİŞKİLER (4-5 cümle)
        - Romantik durum detaylı analizi
        - İlişki dinamikleri ve gelecek
        - Evlilik ve aile hayatı
        - Duygusal ihtiyaçlar ve beklentiler

        👥 SOSYAL HAYAT (3-4 cümle)
        - Arkadaşlık ve sosyal çevre
        - Yeni tanışmalar ve ilişkiler
        - Aile ilişkileri ve dinamikleri

        🏥 SAĞLIK VE ENERJİ (3-4 cümle)
        - Enerji seviyesi ve sağlık durumu
        - Dikkat edilmesi gereken sağlık konuları
        - Yaşam tarzı önerileri

        🔮 GELECEK TAHMİNLERİ (4-5 cümle)
        - Önümüzdeki dönemler detaylı analizi
        - Beklenen gelişmeler ve olaylar
        - Uzun vadeli planlar ve hedefler
        - Zaman çizelgesi ve önemli tarihler

        💡 PRATİK ÖNERİLER (3-4 cümle)
        - Yapılması gerekenler ve eylemler
        - Dikkat edilmesi gereken noktalar
        - Kişisel gelişim önerileri

        🎭 DUYGUSAL DURUM (3-4 cümle)
        - Mevcut duygusal durum analizi
        - İç dünya ve ruhsal durum
        - Stres faktörleri ve çözümler

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz. Fincanın farklı bölgelerindeki sembolleri detaylı açıkla ve her sembolün anlamını analiz et.
        """
    }
    
    return premium_prompts.get(reading_type, "")

def get_free_prompt(reading_type):
    """Ücretsiz kullanıcılar için detaylı prompt"""
    free_prompts = {
        'yildizname': """
        Sen deneyimli bir astrolog ve yıldızname uzmanısın. Aşağıdaki bilgilere göre detaylı bir yıldızname yorumu yap:

        İsim: {isim}
        Anne Adı: {anneAdi}
        Doğum Tarihi: {dogumTarihi}
        Doğum Yeri: {dogumYeri}
        Doğum Saati: {dogumSaati}

        Lütfen şu konuları kapsayan detaylı bir yıldızname yorumu yap:

        **🌟 KİŞİLİK ANALİZİ** (2-3 cümle)
        - Burç özellikleri ve karakter analizi
        - Astrolojik açıdan kişilik yapısı

        **💼 KARİYER VE İŞ HAYATI** (2-3 cümle)
        - Meslek uyumluluğu
        - Kariyer fırsatları ve gelişim alanları

        **❤️ AŞK VE İLİŞKİLER** (2-3 cümle)
        - Romantik uyumluluk
        - İlişki dinamikleri ve gelecek

        **🏥 SAĞLIK DURUMU** (2-3 cümle)
        - Dikkat edilmesi gereken sağlık konuları
        - Astrolojik sağlık önerileri

        **🔮 GELECEK DÖNEMLER** (2-3 cümle)
        - Önümüzdeki 3-6 ay
        - Fırsatlar ve zorluklar

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """,
        
        'tarot': """
        Sen deneyimli bir tarot uzmanısın. Aşağıdaki bilgilere göre detaylı bir tarot yorumu yap:

        Çekilen Kartlar: {cards}

        Lütfen şu konuları kapsayan detaylı bir tarot yorumu yap:

        🎴 KARTLARIN GENEL ANLAMI (2-3 cümle)
        - Kartların birbirleriyle uyumu
        - Genel enerji ve tema

        💼 KARİYER VE İŞ HAYATI (2-3 cümle)
        - İş hayatındaki fırsatlar
        - Kariyer gelişimi ve zorluklar

        ❤️ AŞK VE İLİŞKİLER (2-3 cümle)
        - Romantik durum analizi
        - İlişki dinamikleri

        🏥 SAĞLIK VE ENERJİ (2-3 cümle)
        - Enerji seviyesi ve sağlık
        - Dikkat edilmesi gerekenler

        🔮 GELECEK TAHMİNLERİ (2-3 cümle)
        - Önümüzdeki dönemler
        - Fırsatlar ve uyarılar

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """,
        
        'coffee': """
        Sen deneyimli bir kahve falı uzmanısın. Aşağıdaki bilgilere göre detaylı bir kahve falı yorumu yap:

        Fincan Fotoğrafı: {image_description}

        Lütfen şu konuları kapsayan detaylı bir kahve falı yorumu yap:

        ☕ FİNCANIN GENEL GÖRÜNÜMÜ (2-3 cümle)
        - Fincanın genel enerjisi
        - Kahve kalıntılarının dağılımı

        💼 KARİYER VE İŞ HAYATI (2-3 cümle)
        - İş hayatındaki gelişmeler
        - Kariyer fırsatları

        ❤️ AŞK VE İLİŞKİLER (2-3 cümle)
        - Romantik durum analizi
        - İlişki dinamikleri

        👥 SOSYAL HAYAT (2-3 cümle)
        - Arkadaşlık ve sosyal çevre
        - Yeni tanışmalar

        🔮 GELECEK TAHMİNLERİ (2-3 cümle)
        - Önümüzdeki dönemler
        - Beklenen gelişmeler

        Yorumu Türkçe olarak, samimi ve anlaşılır bir dille yaz.
        """
    }
    
    return free_prompts.get(reading_type, "") 