from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Reading
from tokens import spend_tokens_for_reading
from prompts.multilingual import get_prompt_by_language
from g4f import Client
from datetime import datetime
from rate_limiting import daily_fal_rate_limit

# G4F client'ı başlat
client = Client()

def calculate_zodiac_sign(birth_date_str, language='tr'):
    """Doğum tarihine göre burç hesapla"""
    try:
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        month = birth_date.month
        day = birth_date.day
        
        if language == 'tr':
            if (month == 3 and day >= 21) or (month == 4 and day <= 19):
                return "Koç"
            elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
                return "Boğa"
            elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
                return "İkizler"
            elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
                return "Yengeç"
            elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
                return "Aslan"
            elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
                return "Başak"
            elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
                return "Terazi"
            elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
                return "Akrep"
            elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
                return "Yay"
            elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
                return "Oğlak"
            elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
                return "Kova"
            else:
                return "Balık"
        elif language == 'en':
            if (month == 3 and day >= 21) or (month == 4 and day <= 19):
                return "Aries"
            elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
                return "Taurus"
            elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
                return "Gemini"
            elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
                return "Cancer"
            elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
                return "Leo"
            elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
                return "Virgo"
            elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
                return "Libra"
            elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
                return "Scorpio"
            elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
                return "Sagittarius"
            elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
                return "Capricorn"
            elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
                return "Aquarius"
            else:
                return "Pisces"
        elif language == 'de':
            if (month == 3 and day >= 21) or (month == 4 and day <= 19):
                return "Widder"
            elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
                return "Stier"
            elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
                return "Zwillinge"
            elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
                return "Krebs"
            elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
                return "Löwe"
            elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
                return "Jungfrau"
            elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
                return "Waage"
            elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
                return "Skorpion"
            elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
                return "Schütze"
            elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
                return "Steinbock"
            elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
                return "Wassermann"
            else:
                return "Fische"
    except:
        return None

def register_daily_routes(app):
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
            language = data.get('language', 'tr')
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
                    zodiac_sign = calculate_zodiac_sign(dogum_tarihi, language)
                    
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
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    web_search=False
                )
                
                yorum = response.choices[0].message.content
            except Exception as g4f_error:
                print(f"Daily G4F hatası: {str(g4f_error)}")
                # Fallback yorum
                if language == 'tr':
                    yorum = f"Günlük fal yorumu: Bugün {today} tarihinde {zodiac_sign} burcu için günlük fal yorumu yapılmıştır. Bugün enerji dolu bir gün olacak ve önemli fırsatlar karşınıza çıkacak."
                elif language == 'en':
                    yorum = f"Daily horoscope: Today {today} for {zodiac_sign} zodiac sign, daily horoscope has been made. Today will be an energetic day and important opportunities will come your way."
                else:
                    yorum = f"Tageshoroskop: Heute {today} für {zodiac_sign} Sternzeichen, Tageshoroskop wurde erstellt. Heute wird ein energiereicher Tag sein und wichtige Gelegenheiten werden sich Ihnen bieten."
            
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
