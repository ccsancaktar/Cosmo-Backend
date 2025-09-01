from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User
from models import Reading
from redis_manager import redis_manager
from tokens import spend_tokens_for_reading
from g4f import Client

def register_kabala_routes(app):
    @app.route('/api/kabala', methods=['POST'])
    @jwt_required()
    def kabala():
        try:
            user_id = get_jwt_identity()
            user = User.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
            
            data = request.get_json()
            
            # Gerekli alanları kontrol et - SADECE isim ve dogumTarihi
            required_fields = ['isim', 'dogumTarihi']
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
                success, message = spend_tokens_for_reading(user_id, 'kabala')
                if not success:
                    return jsonify({'error': message}), 400
                # Token harcandıktan sonra kullanıcı bilgilerini güncelle
                user = User.find_by_id(user_id)
            
            # Cache key oluştur (dil parametresi ile)
            cache_key = f'kabala:{data["isim"]}:{data["dogumTarihi"]}:{language}:{user_id}'
            
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
            
            # Basit prompt oluştur
            prompt = f'Kabala falı yap: İsim: {data["isim"]}, Doğum Tarihi: {data["dogumTarihi"]}, İbrani harfler: {hebrew_name}, İsim değeri: {name_value}, Sefirotlar: {selected_sefirot}'
            
            print(f'Kabala prompt: {prompt}')
            
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
                print(f'Kabala G4F hatası: {str(g4f_error)}')
                # Fallback yorum
                sefirot_info = '\n'.join([f"- {sef['name']} ({sef['hebrew']}): {sef['meaning']}" for sef in selected_sefirot])
                yorum = f'🔮 Kabala Falı Yorumu 🔮\n\nİsim: {data["isim"]}\nDoğum Tarihi: {data["dogumTarihi"]}\n\nİbrani isim analizi:\n- İbrani harfler: {hebrew_name}\n- İsim değeri: {name_value}\n- İndirgenmiş değer: {reduced_value}\n\nSeçilen sefirotlar:\n{sefirot_info}\n\nBu Kabala analizi, ruhsal yolunuz ve kaderiniz hakkında önemli bilgiler sunmaktadır.'
            
            # Reading'i kaydet
            reading = Reading(
                user_id=user_id,
                reading_type='kabala',
                input_data=data,
                result=yorum
            )
            
            reading.save()
            
            # Cache'e kaydet
            cache_data = {"yorum": yorum, "hebrew_name": hebrew_name, "name_value": name_value, "reduced_value": reduced_value, "selected_sefirot": selected_sefirot}
            redis_manager.set(cache_key, str(cache_data), ttl=3600)  # 1 saat
            
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
            print(f'Kabala falı hatası: {str(e)}')
            return jsonify({'error': 'Kabala falı oluşturulurken bir hata oluştu'}), 500
