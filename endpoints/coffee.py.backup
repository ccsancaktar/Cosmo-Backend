from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from models import Reading
from redis_manager import redis_manager
from tokens import spend_tokens_for_reading
from prompts.multilingual import get_prompt_by_language
from g4f import Client

def register_coffee_routes(app):
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
            
            # Dil parametresini al (varsayılan: Türkçe)
            language = data.get('language', 'tr')
            if language not in ['tr', 'en', 'de']:
                language = 'tr'
            
            # Premium durumunu kontrol et
            is_premium = user.has_active_premium()
            
            # Premium değilse token kontrolü yap
            if not is_premium:
                success, message = spend_tokens_for_reading(user_id, 'coffee')
                if not success:
                    return jsonify({'error': message}), 400
                # Token harcandıktan sonra kullanıcı bilgilerini güncelle
                user = User.find_by_id(user_id)
            
            # Cache key oluştur (dil parametresi ile)
            cache_key = f'coffee:{data["soru"]}:{language}:{user_id}'
            
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
            
            # Çok dilli prompt sistemi kullan
            prompt = get_prompt_by_language(
                'coffee',
                language,
                soru=data['soru']
            )
            
            print(f'Coffee prompt: {prompt}')
            
            # G4F ile yanıt al
            try:
                print(f'G4F çağrısı yapılıyor...')
                client = Client()
                response = client.chat.completions.create(
                    model='gpt-4',
                    messages=[{'role': 'user', 'content': prompt}],
                    web_search=False
                )
                
                yorum = response.choices[0].message.content
                print(f'G4F yanıtı: {yorum[:100]}...')
            except Exception as g4f_error:
                print(f'Coffee G4F hatası: {str(g4f_error)}')
                # Fallback yorum
                yorum = f'☕ Kahve Falı Yorumu ☕\n\nSoru: {data["soru"]}\n\nKahve fincanınızdaki işaretlere göre, hayatınızda önemli mesajlar bulunmaktadır.\nGeleneksel kahve falı bilgeliği, sorduğunuz konuda size rehberlik etmektedir.\n\nGeçmişten gelen etkiler, bugünkü durumunuzu şekillendirmekte ve geleceğe dair ipuçları vermektedir.\n\nKahve falının rehberliğinde, hayatınızda yeni fırsatlar ve değişimler yaklaşmaktadır.'
            
            # Reading'i kaydet
            reading = Reading(
                user_id=user_id,
                reading_type='coffee',
                input_data=data,
                result=yorum
            )
            
            reading.save()
            
            # Cache'e kaydet
            redis_manager.set(cache_key, yorum, ttl=3600)  # 1 saat
            
            return jsonify({
                'success': True,
                'yorum': yorum,
                'from_cache': False,
                'reading_id': str(reading._id),
                'language': language
            })
            
        except Exception as e:
            print(f'Kahve falı hatası: {str(e)}')
            return jsonify({'error': 'Kahve falı oluşturulurken bir hata oluştu'}), 500
