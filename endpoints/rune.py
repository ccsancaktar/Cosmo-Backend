from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from models import Reading
from redis_manager import redis_manager
from tokens import spend_tokens_for_reading
from prompts.multilingual import get_prompt_by_language
from rune_data import get_random_runes
from g4f import Client

def register_rune_routes(app):
    @app.route('/api/rune', methods=['POST'])
    @jwt_required()
    def rune():
        try:
            user_id = get_jwt_identity()
            user = User.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
            
            data = request.get_json()
            
            required_fields = ['soru']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} alanı gereklidir'}), 422
            
            language = data.get('language', 'tr')
            if language not in ['tr', 'en', 'de']:
                language = 'tr'
            
            is_premium = user.has_active_premium()
            
            if not is_premium:
                success, message = spend_tokens_for_reading(user_id, 'rune')
                if not success:
                    return jsonify({'error': message}), 400
                user = User.find_by_id(user_id)
            
            cache_key = f'rune:{data["soru"]}:{language}:{user_id}'
            
            cached_result = redis_manager.get(cache_key)
            if cached_result:
                return jsonify({
                    'success': True,
                    'yorum': cached_result,
                    'from_cache': True,
                    'reading_id': 'cached',
                    'language': language
                })
            
            runes = get_random_runes(3)
            
            prompt = get_prompt_by_language(
                'rune',
                language,
                soru=data['soru'],
                runes=runes
            )
            
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
                print(f'Rune G4F hatası: {str(g4f_error)}')
                yorum = f'🔮 Rune Falı Yorumu 🔮\n\nSoru: {data["soru"]}\n\nSeçilen Rune\'lar:\n1. {runes[0]["name"]}: {runes[0]["meaning"]}\n2. {runes[1]["name"]}: {runes[1]["meaning"]}\n3. {runes[2]["name"]}: {runes[2]["meaning"]}\n\nBu üç rune, sorduğunuz konuda önemli mesajlar vermektedir.\nRune\'ların birleşimi, hayatınızda yeni fırsatların ve değişimlerin yaklaştığını işaret ediyor.\n\nGeçmişten gelen deneyimleriniz, bugünkü durumunuzu şekillendiriyor ve geleceğe dair umutlu adımlar atmanızı sağlıyor.'
            
            reading = Reading(
                user_id=user_id,
                reading_type='rune',
                input_data=data,
                result=yorum
            )
            
            reading.save()
            
            redis_manager.set(cache_key, yorum, ttl=3600)
            
            return jsonify({
                'success': True,
                'runes': runes,
                'yorum': yorum,
                'from_cache': False,
                'reading_id': str(reading._id),
                'language': language
            })
            
        except Exception as e:
            print(f'Rune falı hatası: {str(e)}')
            return jsonify({'error': 'Rune falı oluşturulurken bir hata oluştu'}), 500
