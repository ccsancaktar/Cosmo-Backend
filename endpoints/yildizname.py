from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from models import Reading
from redis_manager import redis_manager
from tokens import spend_tokens_for_reading
from prompts.multilingual import get_prompt_by_language
from g4f import Client

def register_yildizname_routes(app):
    @app.route('/api/yildizname', methods=['POST'])
    @jwt_required()
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
            
            # Dil parametresini al (varsayılan: Türkçe)
            language = data.get('language', 'tr')
            if language not in ['tr', 'en', 'de']:
                language = 'tr'
            
            # Premium durumunu kontrol et
            is_premium = user.has_active_premium()
            
            # Premium değilse token kontrolü yap
            if not is_premium:
                success, message = spend_tokens_for_reading(user_id, 'yildizname')
                if not success:
                    return jsonify({'error': message}), 400
                # Token harcandıktan sonra kullanıcı bilgilerini güncelle
                user = User.find_by_id(user_id)
            
            # Cache key oluştur (dil parametresi ile)
            cache_key = f'yildizname:{data["isim"]}:{data["anneAdi"]}:{data["dogumTarihi"]}:{data["dogumYeri"]}:{data["dogumSaati"]}:{language}'
            
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
                'yildizname',
                language,
                isim=data['isim'],
                anneAdi=data['anneAdi'],
                dogumTarihi=data['dogumTarihi'],
                dogumYeri=data['dogumYeri'],
                dogumSaati=data['dogumSaati']
            )
            
            print(f'Yıldızname prompt: {prompt}')
            
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
                print(f'Yıldızname G4F hatası: {str(g4f_error)}')
                # Fallback yorum
                yorum = f'🌟 Yıldızname Falı Yorumu 🌟\n\nİsim: {data["isim"]}\nAnne Adı: {data["anneAdi"]}\nDoğum Tarihi: {data["dogumTarihi"]}\nDoğum Yeri: {data["dogumYeri"]}\nDoğum Saati: {data["dogumSaati"]}\n\nYıldızname falınıza göre, hayatınızda önemli dönüm noktaları bulunmaktadır.\nDoğum anınızdaki yıldız konumları, karakterinizi ve kaderinizi şekillendirmektedir.\n\nGeçmişten gelen etkiler, bugünkü durumunuzu etkilemekte ve geleceğe dair ipuçları vermektedir.\n\nYıldızların rehberliğinde, hayatınızda yeni fırsatlar ve değişimler yaklaşmaktadır.'
            
            # Reading'i kaydet
            reading = Reading(
                user_id=user_id,
                reading_type='yildizname',
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
            print(f'Yıldızname falı hatası: {str(e)}')
            return jsonify({'error': 'Yıldızname falı oluşturulurken bir hata oluştu'}), 500
