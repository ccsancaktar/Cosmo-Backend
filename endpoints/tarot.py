from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from models import Reading
from redis_manager import redis_manager
from tokens import spend_tokens_for_reading
from prompts.multilingual import get_prompt_by_language
from tarot_data import get_random_tarot_cards
from g4f import Client

def register_tarot_routes(app):
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
            language = data.get('language', 'tr')
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
            cache_key = f'tarot:{data["soru"]}:{language}:{user_id}'
            
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
            
            print(f'Tarot prompt: {prompt}')
            
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
                print(f'Tarot G4F hatası: {str(g4f_error)}')
                # Fallback yorum
                yorum = f'🔮 Tarot Falı Yorumu 🔮\n\nSoru: {data["soru"]}\n\nSeçilen Kartlar:\n1. {cards[0]["name"]}: {cards[0]["meaning"]}\n2. {cards[1]["name"]}: {cards[1]["meaning"]}\n3. {cards[2]["name"]}: {cards[2]["meaning"]}\n\nBu üç kart, sorduğunuz konuda önemli mesajlar vermektedir.\nKartların birleşimi, hayatınızda yeni fırsatlar ve değişimlerin yaklaştığını işaret ediyor.\n\nGeçmişten gelen deneyimleriniz, bugünkü durumunuzu şekillendiriyor ve geleceğe dair umutlu adımlar atmanızı sağlıyor.'
            
            # Reading'i kaydet
            reading = Reading(
                user_id=user_id,
                reading_type='tarot',
                input_data=data,
                result=yorum
            )
            
            reading.save()
            
            # Cache'e kaydet
            redis_manager.set(cache_key, yorum, ttl=3600)  # 1 saat
            
            return jsonify({
                'success': True,
                'cards': cards,
                'yorum': yorum,
                'from_cache': False,
                'reading_id': str(reading._id),
                'language': language
            })
            
        except Exception as e:
            print(f'Tarot falı hatası: {str(e)}')
            return jsonify({'error': 'Tarot falı oluşturulurken bir hata oluştu'}), 500
